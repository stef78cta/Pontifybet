"""Rânduri de tabel pentru rezumatul afișat după **Generează analiza**.

Separat de `app.py` ca testele să poată verifica ordinea coloanelor fără
a porni Streamlit (importul lui `app` apelează `st.set_page_config`).
"""

from __future__ import annotations

from typing import Any, Callable


def fill_missing_liga(
    rows: list[dict[str, Any]],
    listed: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    """Umple liga lipsă din tabelul de listare (același match_id)."""
    by_id = {
        str(m.get("match_id")): str(m.get("liga") or "")
        for m in (listed or [])
        if m.get("match_id") is not None
    }
    out: list[dict[str, Any]] = []
    for r in rows:
        rr = dict(r)
        if not str(rr.get("liga") or "").strip():
            rr["liga"] = by_id.get(str(rr.get("match_id")), "")
        out.append(rr)
    return out


def over05_summary_rows(
    rows: list[dict[str, Any]],
    *,
    fmt_prob: Callable[[Any], str],
    fmt_score: Callable[[Any], str],
) -> list[dict[str, Any]]:
    """Ordinea e deliberată: ora și liga înaintea echipei, fără scroll orizontal."""
    out: list[dict[str, Any]] = []
    for r in rows:
        if r.get("model_id") != "over05":
            continue
        out.append(
            {
                "Oră de începere": r.get("ora_bucuresti") or "—",
                "Ligă": r.get("liga") or "—",
                "Echipe": r["echipe"],
                "Recomandare": r.get("recommendation") or "—",
                "Nivel": r.get("risk_level") if r.get("risk_level") is not None else "—",
                "G0 model": r.get("model_g0") or "—",
                "Over 0.5": fmt_prob(r.get("p_over")) or "—",
                "P0": fmt_prob(r.get("p0_recalibrated")) or "—",
                "Confidence": fmt_score(r.get("confidence")) or "—",
                "Risk Score": fmt_score(r.get("risk_score")) or "—",
            }
        )
    return out


def validation_summary_rows(
    rows: list[dict[str, Any]],
    *,
    fmt_prob: Callable[[Any], str],
    fmt_score: Callable[[Any], str],
    color_status: Callable[[str], str],
) -> list[dict[str, Any]]:
    """Mută ora și liga la început ca să nu rămână duplicate la finalul tabelului."""
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "Oră de începere": r.get("ora_bucuresti") or "",
                "Ligă": r.get("liga") or "",
                "Echipe": r["echipe"],
                "Model": r["model"],
                "Recomandare (HK)": r.get("recommendation") or "",
                "Nivel (HH)": r.get("risk_level") if r.get("risk_level") is not None else "",
                "G0 model (HG)": r.get("model_g0") or "",
                "Over 0.5 (GP)": fmt_prob(r.get("p_over")),
                "P0 (GL)": fmt_prob(r.get("p0_recalibrated")),
                "Confidence (GT)": fmt_score(r.get("confidence")),
                "Risk Score (HE)": fmt_score(r.get("risk_score")),
                "Data Status": color_status(r["data_status"]),
                "G0 validare": r["g0"],
                "Motiv blocare": r["motiv"],
            }
        )
    return out
