"""Adaptor Cornere Multi-Line V14 — inputuri native + rezultate deja calculate.

Exportul este opțional și nu recalculează nimic: primește `CornersBundle` din
snapshot-ul fazei ANALYSIS, scrie inputurile native în intervalele lor
(`Input_Meci`, `Istoric_Nativ`, `Surse_Import`, `OOS_Predictii`) și copiază
rezultatele Python într-o zonă liberă verificată din `Input_Meci`.

Formulele originale rămân intacte: `Analiza_Linii`, `Motor_Meciuri`, `Core_Nativ`,
`Distributie` și `Dashboard` nu sunt în whitelist, iar amprenta de integritate
acoperă toate cele 85.647 de formule (până la rândul 1405).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from openpyxl.utils.cell import get_column_letter

from src.adapters.base import BaseAdapter
from src.engines.corners.engine import (
    RESULT_ZONE_HEADERS,
    python_result_writes,
)
from src.engines.corners.inputs import (
    DATA_START_ROW,
    HISTORY_COLUMNS,
    HISTORY_SHEET,
    INPUT_COLUMNS,
    INPUT_SHEET,
    MAX_HISTORY_ROWS,
    MAX_MATCHES,
    MAX_OOS_ROWS,
    MAX_SOURCES,
    OOS_COLUMNS,
    OOS_SHEET,
    SOURCE_COLUMNS,
    SOURCE_SHEET,
    build_overrides,
)
from src.models.match_data import MatchData


class CornersAdapter(BaseAdapter):
    model_id = "corners"

    def write_matches(
        self,
        matches: list[MatchData],
        dest: Path,
        *,
        artifacts: Any | None = None,
    ) -> Path:
        """Scrie o copie a șablonului V14 pentru meciurile date.

        @param matches - meciurile analizate (folosite doar pentru ordonare/etichete).
        @param artifacts - `CornersBundle` din snapshot. Fără el, exportul scrie
            doar identitatea meciurilor: nu recalculează și nu inventează inputuri.
        @returns - calea copiei salvate.
        @throws IntegrityError - la orice scriere în afara whitelist-ului sau la
            orice modificare de formulă detectată de amprentă.
        """
        self.prepare_copy(dest)
        writer = self.open_writer(dest)

        self._clear_demo_inputs(writer)

        bundle = artifacts
        if bundle is None:
            return writer.save()

        selected = [str(md.match_id) for md in matches]
        batches = [
            batch
            for batch in getattr(bundle, "batches", ())
            if any(item.match_id in selected for item in batch.matches)
        ]
        if not batches:
            return writer.save()

        # Un singur fișier nu poate găzdui simultan mai multe loturi de evaluare:
        # istoricul nativ al unui lot ar contamina mediile celuilalt. Exportăm
        # inputurile primului lot și semnalăm limita în zona de rezultate.
        primary = batches[0]
        for (sheet, coord), value in build_overrides(primary).items():
            writer.write(sheet, coord, value)

        results = [
            art.result
            for art in bundle.by_match.values()
            if art.result is not None and art.match_input.match_id in selected
        ]
        zone_rows: list[dict[str, Any]] = []
        if len(batches) > 1:
            zone_rows.append(
                {
                    "Match_ID": "NOTA",
                    "Meci": (
                        f"Analiza a folosit {len(batches)} loturi de evaluare; "
                        f"acest fișier conține inputurile native ale primului lot."
                    ),
                }
            )
        self._write_result_zone(writer, results, extra_rows=zone_rows)
        return writer.save()

    def _clear_demo_inputs(self, writer: Any) -> None:
        """Șterge inputurile demonstrative din copia de lucru.

        Fără acest pas, exemplele REPLAY din șablon ar rămâne în `Istoric_Nativ` și
        `Surse_Import` și ar contamina mediile native ale unei rulări LIVE.
        """
        blocks = (
            (INPUT_SHEET, INPUT_COLUMNS, MAX_MATCHES),
            (HISTORY_SHEET, HISTORY_COLUMNS, MAX_HISTORY_ROWS),
            (SOURCE_SHEET, SOURCE_COLUMNS, MAX_SOURCES),
            (OOS_SHEET, OOS_COLUMNS, MAX_OOS_ROWS),
        )
        for sheet, columns, rows in blocks:
            letters = [get_column_letter(index) for index in range(1, columns + 1)]
            for row in range(DATA_START_ROW, DATA_START_ROW + rows):
                for letter in letters:
                    writer.write(sheet, f"{letter}{row}", None)

    def _write_result_zone(
        self,
        writer: Any,
        results: list[Any],
        *,
        extra_rows: list[dict[str, Any]] | None = None,
    ) -> None:
        """Copiază rezultatele Python în zona liberă declarată în registry."""
        zone = self.cfg.get("result_zone") or {}
        sheet = str(zone.get("sheet") or INPUT_SHEET)
        first_row = int(zone.get("first_row", 107))
        columns = list(zone.get("columns") or [])
        if not columns:
            return
        if len(columns) < len(RESULT_ZONE_HEADERS):
            raise ValueError(
                "Zona de rezultate Cornere are mai puține coloane decât antetul "
                f"({len(columns)} < {len(RESULT_ZONE_HEADERS)})."
            )

        payload = python_result_writes(results)
        rows: list[dict[str, Any]] = [dict(zip(RESULT_ZONE_HEADERS, RESULT_ZONE_HEADERS))]
        rows.extend(extra_rows or [])
        rows.extend(payload)

        for offset, record in enumerate(rows):
            row = first_row + offset
            for column, letter in zip(RESULT_ZONE_HEADERS, columns):
                writer.write(sheet, f"{letter}{row}", record.get(column))
