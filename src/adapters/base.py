"""Baza adaptoarelor Excel — whitelist din registry YAML."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

from config.settings import REGISTRY_PATH, TEMPLATES_DIR
from src.excel.generator import SafeWorkbookWriter, copy_template
from src.excel.integrity import WorkbookFingerprint, get_template_baseline
from src.models.match_data import MatchData


def load_registry(path: Path | None = None) -> dict[str, Any]:
    p = path or REGISTRY_PATH
    return yaml.safe_load(p.read_text(encoding="utf-8"))


class BaseAdapter(ABC):
    """Adaptor: știe workbook, sheet, celule, unități, G-level."""

    model_id: str = ""

    def __init__(self, registry: dict[str, Any] | None = None) -> None:
        self.registry = registry or load_registry()
        if self.model_id not in self.registry.get("models", {}):
            raise KeyError(f"Model {self.model_id} lipsește din registry")
        self.cfg = self.registry["models"][self.model_id]

    @property
    def template_name(self) -> str:
        return self.cfg["template"]

    def template_path(self) -> Path:
        return TEMPLATES_DIR / self.template_name

    def build_whitelist(self) -> set[str]:
        sheet = self.cfg.get("input_sheet", "")
        cols = self.cfg.get("write_columns") or []
        whitelist: set[str] = set()
        for col in cols:
            whitelist.add(f"{sheet}!{col}")
        for field in self.cfg.get("fields", []):
            sh = field.get("sheet") or sheet
            cell = field.get("cell")
            col = field.get("column")
            if cell:
                whitelist.add(f"{sh}!{cell}")
            if col:
                whitelist.add(f"{sh}!{col}")
        # Foi de input suplimentare (ex. istoric nativ, surse, registru OOS).
        # Declarate explicit în registry, nu deduse: o foaie de calcul nu ajunge
        # niciodată în whitelist fără intervenție în configurație.
        for extra_sheet, extra_cols in (self.cfg.get("extra_write_columns") or {}).items():
            for col in extra_cols or []:
                whitelist.add(f"{extra_sheet}!{col}")
        return whitelist

    @property
    def integrity_max_rows(self) -> int:
        """Câte rânduri acoperă amprenta de integritate pentru acest model.

        Implicit 200, ca până acum. Cornere V14 are formule până la rândul 1405
        în `Analiza_Linii`, deci are nevoie de o valoare explicită mai mare;
        celelalte modele rămân neatinse.
        """
        return int(self.cfg.get("integrity_max_rows", 200))

    @abstractmethod
    def write_matches(self, matches: list[MatchData], dest: Path) -> Path:
        """Completează o copie a șablonului și returnează calea."""

    def prepare_copy(self, dest: Path) -> Path:
        return copy_template(self.template_name, dest)

    def open_writer(self, dest: Path) -> SafeWorkbookWriter:
        baseline = get_template_baseline(
            self.template_path(), max_rows=self.integrity_max_rows
        )
        return SafeWorkbookWriter(
            dest,
            self.build_whitelist(),
            template_baseline=baseline,
            max_rows=self.integrity_max_rows,
        )
