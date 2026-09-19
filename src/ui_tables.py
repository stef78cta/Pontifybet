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


def is_double_chance_shortlist(selection: dict[str, Any]) -> bool:
    """Selecțiile care intră în view-ul principal.

    Conform Excel: AA=YES (eligibil clasament) sau P0 final încă permisiv.
    Restul rămân calculate și vizibile în audit view, nu sunt șterse.
    """
    if str(selection.get("ranking_eligible") or "").upper() == "YES":
        return True
    return str(selection.get("p0_final") or "").upper() in {"PASS", "PRUDENT"}


def double_chance_summary_rows(
    rows: list[dict[str, Any]],
    *,
    fmt_prob: Callable[[Any], str],
    fmt_score: Callable[[Any], str],
    show_all: bool = True,
) -> list[dict[str, Any]]:
    """Un rând pe selecție 1X / X2 / 12, cu lanțul complet Excel.

    Controalele (Market Direction, Protected Strength, Draw Gate, P0 final) sunt
    coloane distincte de `Nivel` și `Verdict`: un control PRUDENT nu înseamnă
    verdict PRUDENT. `show_all=False` păstrează doar shortlist-ul.
    """
    out: list[dict[str, Any]] = []
    for r in rows:
        if r.get("model_id") != "double_chance":
            continue
        selections = r.get("dc_selections") or [
            {
                "selection": "",
                "verdict": r.get("recommendation"),
                "level": r.get("risk_level"),
                "release": r.get("model_g0"),
            }
        ]
        for sel in selections:
            if not show_all and not is_double_chance_shortlist(sel):
                continue
            out.append(
                {
                    "Oră de începere": r.get("ora_bucuresti") or "—",
                    "Ligă": r.get("liga") or "—",
                    "Echipe": r["echipe"],
                    "Selecție": sel.get("selection") or "—",
                    "Verdict": sel.get("verdict") or "—",
                    "Nivel": sel.get("level") if sel.get("level") is not None else "—",
                    "Scor": fmt_score(sel.get("score")) or "—",
                    "Scor brut": fmt_score(sel.get("risk_score_before_cap")) or "—",
                    "P_model": fmt_prob(sel.get("p_model")) or "—",
                    "P_adj": fmt_prob(sel.get("p_adj")) or "—",
                    "P_market": fmt_prob(sel.get("p_market")) or "—",
                    "P scoreline": fmt_prob(sel.get("p_scoreline")) or "—",
                    "P strength": fmt_prob(sel.get("p_strength")) or "—",
                    "P piață de-vig": fmt_prob(sel.get("p_market_component")) or "—",
                    "Pfail model": fmt_prob(sel.get("pfail_model")) or "—",
                    "Pfail piață": fmt_prob(sel.get("pfail_market")) or "—",
                    "Pfail DC": fmt_prob(sel.get("pfail_dc")) or "—",
                    "Haircut bază": fmt_prob(sel.get("haircut_base")) or "—",
                    "Haircut early": fmt_prob(sel.get("haircut_early")) or "—",
                    "Haircut total": fmt_prob(sel.get("haircut_total")) or "—",
                    "Market Direction": sel.get("market_direction") or "—",
                    "Protected Strength": sel.get("protected_strength") or "—",
                    "PS override": sel.get("protected_strength_override") or "—",
                    "Draw Gate": sel.get("draw_gate") or "—",
                    "P0 final": sel.get("p0_final") or "—",
                    "Confidence": sel.get("confidence") or "—",
                    "Stare date": sel.get("release") or r.get("model_g0") or "—",
                    "Eșantion": r.get("dc_sample_status") or "—",
                    "Prior": r.get("dc_prior_status") or "—",
                    "Shrinkage": r.get("dc_shrinkage_applied") or "—",
                    "Pondere date proprii": fmt_prob(r.get("dc_weight_current")) or "—",
                    "Pondere prior": fmt_prob(r.get("dc_weight_prior")) or "—",
                    "Eligibil AA": sel.get("ranking_eligible") or "—",
                    "DEFENSIV AE": sel.get("defensive_eligible") or "—",
                    "Motivație": sel.get("motivation") or "—",
                }
            )
    return out


def is_corners_shortlist(selection: dict[str, Any]) -> bool:
    """Selecțiile Cornere care intră în view-ul principal.

    Conform Excel: `Eligible` = 1, adică verdictul este DEFENSIV / PRUDENT /
    MODERAT / RIDICAT și linia poate primi rang. Restul rămân calculate și vizibile
    în audit view.
    """
    return bool(selection.get("eligible"))


def corners_summary_rows(
    rows: list[dict[str, Any]],
    *,
    fmt_prob: Callable[[Any], str],
    fmt_score: Callable[[Any], str],
    show_all: bool = True,
) -> list[dict[str, Any]]:
    """Un rând pe fiecare dintre cele 14 linii Cornere, în ordinea din workbook.

    Gate-urile (Failure, Tail, Defensive) sunt coloane distincte de `Nivel` și
    `Verdict`: un gate WATCH nu impune verdictul. `show_all=False` păstrează doar
    liniile eligibile, dar cele 14 rezultate rămân în snapshot.
    """
    out: list[dict[str, Any]] = []
    for r in rows:
        if r.get("model_id") != "corners":
            continue
        selections = r.get("corners_selections") or []
        if not selections:
            out.append(
                {
                    "Oră de începere": r.get("ora_bucuresti") or "—",
                    "Ligă": r.get("liga") or "—",
                    "Echipe": r["echipe"],
                    "Linie": "—",
                    "Verdict": r.get("recommendation") or "—",
                    "Nivel": r.get("risk_level") if r.get("risk_level") is not None else "—",
                    "Release": r.get("corners_release") or "—",
                    "Motiv": r.get("motiv") or r.get("corners_reason") or "—",
                }
            )
            continue
        for sel in selections:
            if not show_all and not is_corners_shortlist(sel):
                continue
            out.append(
                {
                    "Oră de începere": r.get("ora_bucuresti") or "—",
                    "Ligă": r.get("liga") or "—",
                    "Echipe": r["echipe"],
                    "Linie": sel.get("line") or "—",
                    "Verdict": sel.get("verdict") or "—",
                    "Nivel": sel.get("risk_level") if sel.get("risk_level") is not None else "—",
                    "Nivel brut": sel.get("risk_level_raw") if sel.get("risk_level_raw") is not None else "—",
                    "P_Raw": fmt_prob(sel.get("p_raw")) or "—",
                    "P_calibrat": fmt_prob(sel.get("p_calibrated")) or "—",
                    "P_FINAL": fmt_prob(sel.get("p_final")) or "—",
                    "Failure model": fmt_prob(sel.get("failure_model")) or "—",
                    "Failure Gate": sel.get("failure_gate") or "—",
                    "Risk Score": fmt_score(sel.get("risk_score")) or "—",
                    "Confidence Final": fmt_score(sel.get("confidence_final")) or "—",
                    "Confidence candidat": sel.get("candidate_confidence") or "—",
                    "Release": sel.get("release") or "—",
                    "G0": sel.get("g0") or "—",
                    "Tail Gate": sel.get("tail_gate") or "—",
                    "Defensive Gate": sel.get("defensive_gate") or "—",
                    "Candidat DEFENSIV": sel.get("defensive_candidate") or "—",
                    "Eligibil": "DA" if sel.get("eligible") else "NU",
                    "Builder": sel.get("builder") or "—",
                    "Rang în meci": sel.get("rank_in_match") if sel.get("rank_in_match") is not None else "—",
                    "Rang LIVE": sel.get("rank_live") if sel.get("rank_live") is not None else "—",
                    "OOS": sel.get("oos_status") or "—",
                    "Mu": fmt_score(sel.get("mu")) or "—",
                    "D": fmt_score(sel.get("d")) or "—",
                    "Distribuție": r.get("corners_distribution") or "—",
                    "Motiv": sel.get("reason") or "—",
                }
            )
    return out


def corners_top_live_rows(
    top_live: list[dict[str, Any]],
    *,
    fmt_prob: Callable[[Any], str],
    fmt_score: Callable[[Any], str],
) -> list[dict[str, Any]]:
    """Top LIVE Cornere: maximum o linie per meci, maximum zece rânduri."""
    return [
        {
            "Rang": entry.get("rank"),
            "Meci": entry.get("match") or "—",
            "Linie": entry.get("line") or "—",
            "Verdict": entry.get("verdict") or "—",
            "Nivel": entry.get("risk_level") if entry.get("risk_level") is not None else "—",
            "P_FINAL": fmt_prob(entry.get("p_final")) or "—",
            "Confidence Final": fmt_score(entry.get("confidence_final")) or "—",
            "Motiv": entry.get("reason") or "—",
        }
        for entry in top_live or []
    ]


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
