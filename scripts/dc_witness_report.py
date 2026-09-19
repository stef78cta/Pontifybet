"""Raport-martor complet pentru un meci: raw → prior → shrinkage → λ → 1X2 → DC.

Rulare:
    .venv\\Scripts\\python.exe scripts/dc_witness_report.py --date 2026-09-19 \
        --match-id 123456 --out audit/witness.md

Fără `--match-id` alege automat meciul cel mai relevant din lot:
`--pick favourite-small-sample` = cel mai clar favorit cu shrinkage activ;
`--pick verified` = un meci VERIFIED, fără shrinkage.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engines.double_chance import compute_double_chance  # noqa: E402
from src.engines.double_chance.inputs import (  # noqa: E402
    derived_1x2_trace,
    league_prior_is_valid,
    match_to_double_chance_inputs,
    needs_early_season_prior,
)


def _pct(value: Any, digits: int = 2) -> str:
    return "—" if value is None else f"{value * 100:.{digits}f}%"


def _num(value: Any, digits: int = 4) -> str:
    return "—" if value is None else f"{value:.{digits}f}"


def _load(date_iso: str) -> tuple[Any, list[dict[str, Any]]]:
    from src.api.client import FootyStatsClient
    from src.pipeline import _league_names_by_season, attach_league_names

    client = FootyStatsClient()
    raw = client.matches_by_date(date_iso)
    return client, attach_league_names(raw, _league_names_by_season(client))


def _context(client: Any, raw: dict[str, Any]) -> dict[str, Any] | None:
    match = client.enrich_match(raw)
    mapping = match_to_double_chance_inputs(match)
    shrink = needs_early_season_prior(
        mapping.get("Input_Meci!B36"), mapping.get("Input_Meci!C36")
    ) and league_prior_is_valid(match)
    trace = derived_1x2_trace(match, apply_shrinkage=shrink)
    result = compute_double_chance(mapping)
    if result.blend.market[0] is None:
        return None
    return {
        "match": match,
        "mapping": mapping,
        "shrink": shrink,
        "trace": trace,
        "result": result,
    }


def _report(ctx: dict[str, Any]) -> str:
    match = ctx["match"]
    mapping = ctx["mapping"]
    trace = ctx["trace"]
    result = ctx["result"]
    blend = result.blend
    home, away = match.home, match.away

    out: list[str] = []
    add = out.append
    add(f"# Raport-martor: {home.name} vs {away.name}")
    add("")
    if ctx.get("note"):
        add(f"> {ctx['note']}")
        add("")
    add(f"- Ligă: {match.competition_name}")
    add(f"- match_id: {match.match_id}")
    add(f"- Kickoff UTC: {match.kickoff_utc}")
    add(f"- Eșantion: `Surse_Date!C9` = {mapping.get('Surse_Date!C9')}")
    add(f"- Prior: `Surse_Date!C10` = {mapping.get('Surse_Date!C10') or 'N/A'}")
    add(f"- Shrinkage aplicat: **{'DA' if ctx['shrink'] else 'NU'}**")
    add("")

    add("## A. Date raw")
    add("")
    add("| Mărime | Gazde | Oaspeți |")
    add("| --- | --- | --- |")
    rows = [
        ("Meciuri jucate (H / A)", home.matches_played_home, away.matches_played_away),
        ("Meciuri jucate (overall)", home.matches_played_overall, away.matches_played_overall),
        ("Goluri marcate (H / A)", home.goals_for_home, away.goals_for_away),
        ("Goluri primite (H / A)", home.goals_against_home, away.goals_against_away),
        ("xG marcate (H / A)", home.xg_for_home, away.xg_for_away),
        ("xG primite (H / A)", home.xg_against_home, away.xg_against_away),
    ]
    for label, left, right in rows:
        add(f"| {label} | {left.numeric_or_none()} | {right.numeric_or_none()} |")
    add(
        f"| Prior ligă (goluri/meci) | {_num(trace.prior_home)} (acasă) | "
        f"{_num(trace.prior_away)} (deplasare) |"
    )
    add(f"| N prior ligă | {trace.n_prior_home} | {trace.n_prior_away} |")
    add("")

    add("## B/C. Parametri înainte și după shrinkage")
    add("")
    add("| Parametru | N curent | N prior | Pondere curent | Pondere prior | Înainte | După | Δ |")
    add("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for rate in trace.rates:
        before, after = rate.observed, rate.shrunk
        delta = None if before is None or after is None else after - before
        add(
            f"| `{rate.name}` | {_num(rate.n_current, 0)} | {_num(rate.n_prior, 0)} | "
            f"{_pct(rate.weight_current, 1)} | {_pct(rate.weight_prior, 1)} | "
            f"{_num(before)} | {_num(after)} | {_num(delta)} |"
        )
    add("")
    add("### λ (goluri așteptate)")
    add("")
    add("| Model | λ gazde înainte | λ gazde după | λ oaspeți înainte | λ oaspeți după |")
    add("| --- | --- | --- | --- | --- |")
    add(
        f"| Scoreline (H/A + xG) | {_num(trace.lambda_scoreline_raw[0])} | "
        f"{_num(trace.lambda_scoreline[0])} | {_num(trace.lambda_scoreline_raw[1])} | "
        f"{_num(trace.lambda_scoreline[1])} |"
    )
    add(
        f"| Strength (overall) | {_num(trace.lambda_strength_raw[0])} | "
        f"{_num(trace.lambda_strength[0])} | {_num(trace.lambda_strength_raw[1])} | "
        f"{_num(trace.lambda_strength[1])} |"
    )
    add("")

    add("## D/E/F. Cele trei componente 1X2")
    add("")
    add("| Componentă | P(1) | P(X) | P(2) | Sumă |")
    add("| --- | --- | --- | --- | --- |")

    def triplet_row(label: str, triplet) -> None:
        if not triplet or triplet[0] is None:
            add(f"| {label} | — | — | — | — |")
            return
        add(
            f"| {label} | {_pct(triplet[0])} | {_pct(triplet[1])} | {_pct(triplet[2])} | "
            f"{_pct(sum(triplet))} |"
        )

    triplet_row("Scoreline ÎNAINTE de shrinkage", trace.scoreline_raw)
    triplet_row("Scoreline (Model_1X2 rândul 6)", blend.scoreline)
    triplet_row("Strength ÎNAINTE de shrinkage", trace.strength_raw)
    triplet_row("Strength (Model_1X2 rândul 7)", blend.strength)
    triplet_row("Piață de-vig (Model_1X2 rândul 8)", blend.market)
    add("")

    add("## G. Blend final")
    add("")
    add(
        f"Ponderi din `Parametri`: scoreline {blend.weight_scoreline}, "
        f"strength {blend.weight_strength}, piață {blend.weight_market}."
    )
    add("")
    add("| Contribuție | P(1) | P(X) | P(2) |")
    add("| --- | --- | --- | --- |")
    for label, values in (
        (f"{blend.weight_scoreline} × scoreline", blend.contribution_scoreline),
        (f"{blend.weight_strength} × strength", blend.contribution_strength),
        (f"{blend.weight_market} × piață", blend.contribution_market),
        ("**Sumă (rândul 9)**", blend.blend_raw),
        ("**Final normalizat (rândul 10)**", blend.final),
    ):
        add(f"| {label} | {_pct(values[0])} | {_pct(values[1])} | {_pct(values[2])} |")
    if all(p is not None for p in blend.final):
        add("")
        add(f"Verificare: P(1)+P(X)+P(2) = {sum(blend.final):.12f}")
    add("")

    add("## H. Șansă Dublă")
    add("")
    add(
        "| Selecție | P_model | P_market | Δ (pp) | Pfail_model | Pfail_market | Pfail_DC | "
        "Haircut | P_adj | Risk Score | Nivel | Verdict |"
    )
    add("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for sel in result.selections:
        delta = (
            "—"
            if sel.p_model is None or sel.p_market is None
            else f"{(sel.p_model - sel.p_market) * 100:+.2f}"
        )
        add(
            f"| {sel.code} | {_pct(sel.p_model)} | {_pct(sel.p_market)} | {delta} | "
            f"{_pct(sel.pfail_model)} | {_pct(sel.pfail_market)} | {_pct(sel.pfail_dc)} | "
            f"{_pct(sel.haircut_total)} | {_pct(sel.p_adj)} | {sel.score} | {sel.level} | "
            f"{sel.verdict} |"
        )
    add("")
    deltas = [
        sel.p_model - sel.p_market
        for sel in result.selections
        if sel.p_model is not None and sel.p_market is not None
    ]
    if len(deltas) == 3:
        add(f"Suma celor trei delte = {sum(deltas) * 100:.2e} pp (zero prin construcție).")
        add("")
    return "\n".join(out) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True)
    parser.add_argument("--match-id", type=int)
    parser.add_argument("--pick", choices=("favourite-small-sample", "verified"))
    parser.add_argument("--out", required=True)
    parser.add_argument("--limit", type=int, default=160)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    client, raw_matches = _load(args.date)
    candidates = raw_matches[: args.limit]

    chosen: dict[str, Any] | None = None
    if args.match_id:
        raw = next(m for m in candidates if int(m.get("id")) == args.match_id)
        chosen = _context(client, raw)
    else:
        best_score = -1.0
        for raw in candidates:
            try:
                ctx = _context(client, raw)
            except Exception:  # noqa: BLE001
                continue
            if ctx is None:
                continue
            wants_shrink = args.pick == "favourite-small-sample"
            if ctx["shrink"] != wants_shrink:
                continue
            market = ctx["result"].blend.market
            if market[0] is None:
                continue
            score = max(market)
            if score > best_score:
                best_score, chosen = score, ctx

    if chosen is None:
        print("niciun meci potrivit")
        return
    chosen["note"] = args.note
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(_report(chosen), encoding="utf-8")
    print(f"{chosen['match'].home.name} vs {chosen['match'].away.name} -> {dest}")


if __name__ == "__main__":
    main()
