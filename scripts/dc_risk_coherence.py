"""Generează audit/risk_coherence_report.md.

Raport pur diagnostic: derivă, pentru fiecare regim de haircut, ce Pfail maxim mai
permite Nivel 1 / Nivel 2 în formula V2 nemodificată. Nu schimbă niciun verdict.

Coeficienții sunt citiți din workbook (Parametri), nu scriși în cod.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engines.double_chance import compute_double_chance  # noqa: E402

PARAM_CELLS = {
    "min_p_strong": "Parametri!B4",
    "min_p_prudent": "Parametri!B5",
    "max_draw_strong": "Parametri!B8",
    "haircut_a": "Parametri!B13",
    "haircut_b": "Parametri!B14",
    "haircut_c": "Parametri!B15",
    "early_extra": "Parametri!B25",
    "risk_fail_1x": "Parametri!B35",
    "risk_hc_1x": "Parametri!B36",
    "risk_fail_12": "Parametri!B37",
    "risk_hc_12": "Parametri!B38",
    "level1_max": "Parametri!B39",
    "level2_max": "Parametri!B40",
}


def _params() -> dict[str, float]:
    result = compute_double_chance({}, evaluate=list(PARAM_CELLS.values()))
    return {name: float(result.cells[cell]) for name, cell in PARAM_CELLS.items()}


def _max_pfail(level_max: float, haircut: float, fail_w: float, hc_w: float) -> float:
    """Cel mai mare Pfail_DC care încă rotunjește la un scor <= level_max.

    ROUND half-up: scorul brut trebuie să fie strict sub level_max + 0.5.
    """
    return (level_max + 0.5 - hc_w * haircut) / fail_w


def main() -> None:
    p = _params()
    regimes = [
        ("A", p["haircut_a"], False),
        ("A + early season", p["haircut_a"] + p["early_extra"], True),
        ("B", p["haircut_b"], False),
        ("B + early season", p["haircut_b"] + p["early_extra"], True),
        ("C", p["haircut_c"], False),
        ("C + early season", p["haircut_c"] + p["early_extra"], True),
    ]

    lines: list[str] = []
    add = lines.append
    add("# Risk coherence report – Șansă Dublă V2")
    add("")
    add("Raport **exclusiv diagnostic**. Formula V2 rămâne neschimbată; nimic de aici")
    add("nu modifică un verdict. Scopul este să arate ce frontieră de Pfail impune")
    add("efectiv Risk Score-ul, comparat cu pragurile probabilistice documentate.")
    add("")
    add("## Coeficienți citiți din workbook")
    add("")
    add("| Parametru | Celulă | Valoare |")
    add("| --- | --- | --- |")
    for name, cell in PARAM_CELLS.items():
        add(f"| {name} | `{cell}` | {p[name]} |")
    add("")
    add("## 1X / X2 – frontiera Pfail_DC")
    add("")
    add("Scor = ROUND(`B35`·Pfail_DC + `B36`·Haircut_Total + surcharges, 0), fără surcharges.")
    add("")
    add("| Regim haircut | Haircut_Total | Pfail_DC max pentru Nivel 1 | Pfail_DC max pentru Nivel 2 | P_model implicit la Nivel 1 | P_adj implicit la Nivel 1 |")
    add("| --- | --- | --- | --- | --- | --- |")
    for label, haircut, _ in regimes:
        l1 = _max_pfail(p["level1_max"], haircut, p["risk_fail_1x"], p["risk_hc_1x"])
        l2 = _max_pfail(p["level2_max"], haircut, p["risk_fail_1x"], p["risk_hc_1x"])
        p_model = 1 - l1
        add(
            f"| {label} | {haircut:.3f} | {l1:.4f} ({l1 * 100:.2f} pp) | "
            f"{l2:.4f} ({l2 * 100:.2f} pp) | {p_model:.4f} | {p_model - haircut:.4f} |"
        )
    add("")
    add("### Consecința matematică")
    add("")
    add(
        f"`Min_P_DC_Strong` = {p['min_p_strong']} nu este niciodată constrângerea activă pentru "
        "1X/X2."
    )
    add(
        "Verdictul DEFENSIV cere `M=1` (Nivel 1), iar Nivel 1 impune deja un P_adj mult "
        "peste prag:"
    )
    add("")
    for label, haircut, _ in regimes:
        l1 = _max_pfail(p["level1_max"], haircut, p["risk_fail_1x"], p["risk_hc_1x"])
        implied = (1 - l1) - haircut
        gap = implied - p["min_p_strong"]
        add(
            f"- Regim {label}: Nivel 1 forțează P_adj >= {implied:.4f}, adică "
            f"{gap * 100:.2f} pp peste pragul documentat de {p['min_p_strong']}."
        )
    add("")
    add("## 12 – frontiera Pfail_DC (egal)")
    add("")
    add("Scor = ROUND(`B37`·Pfail_DC + `B38`·Haircut_Total + surcharge Draw Gate, 0).")
    add("")
    add("| Regim haircut | Haircut_Total | Pdraw max pentru Nivel 1 | Pdraw max pentru Nivel 2 |")
    add("| --- | --- | --- | --- |")
    for label, haircut, _ in regimes:
        l1 = _max_pfail(p["level1_max"], haircut, p["risk_fail_12"], p["risk_hc_12"])
        l2 = _max_pfail(p["level2_max"], haircut, p["risk_fail_12"], p["risk_hc_12"])
        add(f"| {label} | {haircut:.3f} | {l1:.4f} ({l1 * 100:.2f} pp) | {l2:.4f} ({l2 * 100:.2f} pp) |")
    add("")
    l1_a = _max_pfail(p["level1_max"], p["haircut_a"], p["risk_fail_12"], p["risk_hc_12"])
    add(
        f"Draw Gate declară PASS până la {p['max_draw_strong']} ({p['max_draw_strong'] * 100:.0f} pp), "
        f"dar Nivel 1 cere Pdraw <= {l1_a:.4f} ({l1_a * 100:.2f} pp) chiar în cel mai favorabil "
        "regim de haircut."
    )
    add(
        f"Gate-ul este deci cu un factor de ~{p['max_draw_strong'] / l1_a:.1f}x mai permisiv decât "
        "scorul care decide nivelul."
    )
    add("")
    add("## Unde intră haircut-ul (numărătoare)")
    add("")
    add("| Selecție | Haircut în P_adj | Haircut în gate | Haircut în Risk Score |")
    add("| --- | --- | --- | --- |")
    add("| 1X / X2 | da (`F = B - E`) | nu | da (`B36`·E) |")
    add("| 12 | da (`F = B - E`) | da (`P0_Gates_v2!I6 = C10 + E`) | da (`B38`·E) |")
    add("")
    add(
        "Pentru 12 haircut-ul este contabilizat de trei ori pe căi diferite. Nu este o "
        "eroare de implementare — Excel V2 face exact asta — dar este o observație "
        "metodologică documentată în `V3_CHALLENGER_PROPOSAL.md`."
    )
    add("")

    dest = ROOT / "audit" / "risk_coherence_report.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written -> {dest}")


if __name__ == "__main__":
    main()
