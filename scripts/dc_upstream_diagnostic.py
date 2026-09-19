"""Diagnostic upstream Șansă Dublă: model vs piață, prior/shrinkage, scoreline vs strength.

Rulare:
    .venv\\Scripts\\python.exe scripts/dc_upstream_diagnostic.py [--date YYYY-MM-DD] [--mock]

Produce în `audit/`:
    model_vs_market_diagnostic.csv   – un rând pe selecție, cu lanțul upstream complet
    risk_score_decomposition.csv     – componentele scorului, fără recalibrare
    upstream_summary.md              – statistici agregate și pe segmente

Scriptul este strict read-only față de logica de producție: apelează exact
`derived_1x2_trace`, `match_to_double_chance_inputs` și `compute_double_chance`.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
from datetime import date
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engines.double_chance import compute_double_chance  # noqa: E402
from src.engines.double_chance.inputs import (  # noqa: E402
    derived_1x2_trace,
    league_prior_is_valid,
    match_to_double_chance_inputs,
    needs_early_season_prior,
)

AUDIT = ROOT / "audit"
# Fiecare șansă dublă este suma a două rezultate din tripletul (1, X, 2).
DC_COMPONENTS: dict[str, tuple[int, int]] = {"1X": (0, 1), "X2": (1, 2), "12": (0, 2)}


def _pair(triplet: tuple[Any, ...], code: str) -> float | None:
    left, right = DC_COMPONENTS[code]
    a, b = triplet[left], triplet[right]
    if a is None or b is None:
        return None
    return a + b


def _top1(triplet: tuple[Any, ...] | None) -> float | None:
    if not triplet:
        return None
    values = [p for p in triplet if p is not None]
    return max(values) if values else None


def _num(value: Any) -> str:
    return "" if value is None else f"{value:.10g}" if isinstance(value, float) else str(value)


def _load_matches(args: argparse.Namespace) -> list[Any]:
    if args.mock:
        from src.api.mock import MockFootyStatsClient

        client = MockFootyStatsClient()
        raw = client.matches_by_date(args.date)
    else:
        from src.api.client import FootyStatsClient
        from src.pipeline import _league_names_by_season, attach_league_names

        client = FootyStatsClient()
        raw = client.matches_by_date(args.date)
        # todays-matches trimite doar competition_id; fără numele ligii, Input_Meci!B5
        # rămâne gol și fixture-ul devine CRITICAL MISSING. Pipeline-ul face la fel.
        raw = attach_league_names(raw, _league_names_by_season(client))
    out = []
    for item in raw[: args.limit]:
        try:
            out.append(client.enrich_match(item))
        except Exception as exc:  # noqa: BLE001 - un meci stricat nu oprește auditul
            print(f"  skip {item.get('id')}: {type(exc).__name__}: {exc}")
    return out


def _rows_for_match(match: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    mapping = match_to_double_chance_inputs(match)
    sample_home = mapping.get("Input_Meci!B36")
    sample_away = mapping.get("Input_Meci!C36")
    shrink = needs_early_season_prior(sample_home, sample_away) and league_prior_is_valid(match)
    trace = derived_1x2_trace(match, apply_shrinkage=shrink)
    result = compute_double_chance(mapping)
    blend = result.blend

    representative = trace.rate("scoreline.home_attack")
    label = f"{match.home.name} vs {match.away.name}"
    market_rows: list[dict[str, Any]] = []
    risk_rows: list[dict[str, Any]] = []

    for sel in result.selections:
        p_model = sel.p_model
        p_market = sel.p_market
        delta = None if p_model is None or p_market is None else (p_model - p_market) * 100
        market_rows.append(
            {
                "match_id": match.match_id,
                "match": label,
                "liga": match.competition_name,
                "selection": sel.code,
                "data_status": sel.release,
                "sample_status": mapping.get("Surse_Date!C9"),
                "prior_status": mapping.get("Surse_Date!C10"),
                "shrinkage_applied": "DA" if shrink else "NU",
                "p_model": p_model,
                "p_market": p_market,
                "delta_model_market_pp": delta,
                "p_scoreline": _pair(blend.scoreline, sel.code),
                "p_strength": _pair(blend.strength, sel.code),
                "p_market_component": _pair(blend.market, sel.code),
                "p_scoreline_raw": _pair(trace.scoreline_raw, sel.code)
                if trace.scoreline_raw
                else None,
                "p_strength_raw": _pair(trace.strength_raw, sel.code)
                if trace.strength_raw
                else None,
                "n_current_home": trace.n_current_home,
                "n_current_away": trace.n_current_away,
                "n_prior_home": trace.n_prior_home,
                "n_prior_away": trace.n_prior_away,
                "weight_current": representative.weight_current if representative else None,
                "weight_prior": representative.weight_prior if representative else None,
                "haircut_total": sel.haircut_total,
                "p_adj": sel.p_adj,
                "scoreline_strength_gap": blend.scoreline_strength_max_gap,
                "model_top1": _top1(blend.final),
                "market_top1": _top1(blend.market),
                "scoreline_top1": _top1(blend.scoreline),
                "strength_top1": _top1(blend.strength),
                "scoreline_raw_top1": _top1(trace.scoreline_raw),
                "strength_raw_top1": _top1(trace.strength_raw),
                "pdraw_model": blend.final[1],
                "pdraw_market": blend.market[1],
                "lambda_home_scoreline": trace.lambda_scoreline[0],
                "lambda_away_scoreline": trace.lambda_scoreline[1],
                "lambda_home_scoreline_raw": trace.lambda_scoreline_raw[0],
                "lambda_away_scoreline_raw": trace.lambda_scoreline_raw[1],
            }
        )
        risk_rows.append(
            {
                "match_id": match.match_id,
                "match": label,
                "selection": sel.code,
                "pfail_model": sel.pfail_model,
                "pfail_market": sel.pfail_market,
                "pfail_dc": sel.pfail_dc,
                "haircut_base": sel.haircut_base,
                "haircut_early": sel.haircut_early,
                "haircut_total": sel.haircut_total,
                "risk_failure_component": sel.risk.failure_component,
                "risk_haircut_component": sel.risk.haircut_component,
                "prudent_gate_surcharge": sel.risk.market_direction_surcharge
                + sel.risk.protected_strength_surcharge,
                "draw_watch_surcharge": sel.risk.draw_gate_surcharge,
                "gate_fail_surcharge": sel.risk.gate_fail_surcharge,
                "away_favorite_surcharge": sel.risk.away_favorite_surcharge,
                "fragility_status": sel.fragility_gate,
                "fragility_level_surcharge": sel.fragility_level_surcharge,
                "risk_score_before_cap": sel.risk.score_before_cap,
                "risk_score_final": sel.score,
                "risk_level": sel.level,
                "market_direction": sel.market_direction,
                "protected_strength": sel.protected_strength,
                "draw_gate": sel.draw_gate,
                "p0_final": sel.p0_final,
                "verdict": sel.verdict,
                "pdraw_model_raw": sel.draw.model_raw if sel.draw else None,
                "pdraw_model_after_haircut": sel.draw.model_plus_haircut if sel.draw else None,
                "pdraw_market": sel.draw.market if sel.draw else None,
                "pdraw_adjusted": sel.draw.adjusted if sel.draw else None,
            }
        )
    return market_rows, risk_rows


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(rows[0].keys())
        for row in rows:
            writer.writerow([_num(v) for v in row.values()])


def _describe(values: Iterable[float]) -> dict[str, Any]:
    data = [v for v in values if v is not None]
    if not data:
        return {"n": 0}
    return {
        "n": len(data),
        "mean": statistics.fmean(data),
        "median": statistics.median(data),
        "min": min(data),
        "max": max(data),
        "stdev": statistics.pstdev(data) if len(data) > 1 else 0.0,
        "pct_below": 100 * sum(1 for v in data if v < -0.005) / len(data),
        "pct_above": 100 * sum(1 for v in data if v > 0.005) / len(data),
        "pct_equal": 100 * sum(1 for v in data if abs(v) <= 0.005) / len(data),
    }


def _fmt(stats: dict[str, Any]) -> str:
    if not stats.get("n"):
        return "| – | – | – | – | – | – | – | – | – |"
    return (
        f"| {stats['n']} | {stats['mean']:.2f} | {stats['median']:.2f} | {stats['min']:.2f} | "
        f"{stats['max']:.2f} | {stats['stdev']:.2f} | {stats['pct_below']:.1f}% | "
        f"{stats['pct_above']:.1f}% | {stats['pct_equal']:.1f}% |"
    )


def _summary(rows: list[dict[str, Any]], source: str, when: str) -> str:
    deltas = [r["delta_model_market_pp"] for r in rows]
    lines = [
        "# Diagnostic upstream: model vs piață",
        "",
        f"Sursă date: **{source}**, data {when}. {len(rows)} selecții "
        f"({len({r['match_id'] for r in rows})} meciuri).",
        "",
        "Delta este `P_model - P_market`, în puncte procentuale.",
        "",
        "## Identitatea de sumă (verificare de sanitate)",
        "",
        "Pentru orice meci, fiecare rezultat (1, X, 2) apare în exact două șanse duble,",
        "deci `P(1X) + P(X2) + P(12) = 2` atât pentru model, cât și pentru piață —",
        "ambele distribuții fiind normalizate la 1 în `Model_1X2`.",
        "Prin urmare **suma celor trei delte ale unui meci este 0 prin construcție**.",
        "",
    ]

    by_match: dict[Any, list[float]] = {}
    for row in rows:
        if row["delta_model_market_pp"] is not None:
            by_match.setdefault(row["match_id"], []).append(row["delta_model_market_pp"])
    complete = {k: v for k, v in by_match.items() if len(v) == 3}
    worst = max((abs(sum(v)) for v in complete.values()), default=0.0)
    lines += [
        f"Meciuri cu toate cele trei selecții: {len(complete)}. "
        f"Cea mai mare abatere de la suma zero: {worst:.2e} pp.",
        "",
        "Consecință: o afirmație de tip „toate selecțiile au P_model < P_market” nu poate",
        "descrie un lot complet; descrie un subset filtrat (de regulă selecțiile cu",
        "probabilitate mare). Semnalul real nu este o deplasare în jos, ci o **compresie**.",
        "",
        "## Statistici delta (pp)",
        "",
        "| Segment | n | medie | mediană | min | max | abatere std | % model<piață | % model>piață | % egal |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        f"| TOTAL {_fmt(_describe(deltas))}",
    ]

    def segment(name: str, predicate) -> None:
        subset = [r["delta_model_market_pp"] for r in rows if predicate(r)]
        lines.append(f"| {name} {_fmt(_describe(subset))}")

    segment("VERIFIED", lambda r: r["sample_status"] == "VERIFIED")
    segment("SMALL SAMPLE", lambda r: r["sample_status"] == "SMALL SAMPLE")
    segment("shrinkage DA", lambda r: r["shrinkage_applied"] == "DA")
    segment("shrinkage NU", lambda r: r["shrinkage_applied"] == "NU")
    for code in ("1X", "X2", "12"):
        segment(code, lambda r, c=code: r["selection"] == c)
    lines.append("")

    lines += [
        "## Segmentare pe bandă de probabilitate a pieței",
        "",
        "Dacă bias-ul ar fi o deplasare uniformă în jos, delta ar fi negativă în toate benzile.",
        "Dacă este compresie, delta este negativă sus și pozitivă jos.",
        "",
        "| Bandă P_market | n | medie | mediană | min | max | abatere std | % model<piață | % model>piață | % egal |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    bands = [(0.0, 0.5), (0.5, 0.65), (0.65, 0.75), (0.75, 0.85), (0.85, 1.01)]
    for low, high in bands:
        subset = [
            r["delta_model_market_pp"]
            for r in rows
            if r["p_market"] is not None and low <= r["p_market"] < high
        ]
        lines.append(f"| [{low:.2f}, {high:.2f}) {_fmt(_describe(subset))}")
    lines.append("")

    lines += [
        "## Măsura compresiei",
        "",
        "`top1` = cea mai mare dintre P(1), P(X), P(2); excesul peste 1/3 arată cât de",
        "departe de uniform este distribuția. Raportul component/piață măsoară ce fracțiune",
        "din semnalul de diferențiere al pieței păstrează fiecare etapă.",
        "",
        "| Componentă | top1 mediu | exces peste 1/3 | raport vs piață |",
        "| --- | --- | --- | --- |",
    ]

    def excess(field: str, subset: list[dict[str, Any]] | None = None) -> float | None:
        data = [r[field] for r in (subset if subset is not None else rows) if r.get(field) is not None]
        return statistics.fmean(d - 1 / 3 for d in data) if data else None

    market_excess = excess("market_top1")
    for label, field in (
        ("Piață de-vig (rândul 8)", "market_top1"),
        ("Scoreline ÎNAINTE de shrinkage", "scoreline_raw_top1"),
        ("Scoreline DUPĂ shrinkage (rândul 6)", "scoreline_top1"),
        ("Strength ÎNAINTE de shrinkage", "strength_raw_top1"),
        ("Strength DUPĂ shrinkage (rândul 7)", "strength_top1"),
        ("Blend final (rândul 10)", "model_top1"),
    ):
        data = [r[field] for r in rows if r.get(field) is not None]
        if not data or market_excess is None:
            continue
        exc = statistics.fmean(d - 1 / 3 for d in data)
        lines.append(
            f"| {label} | {statistics.fmean(data):.4f} | {exc:.4f} | {exc / market_excess:.3f} |"
        )
    lines.append("")

    verified = [r for r in rows if r["shrinkage_applied"] == "NU"]
    shrunk = [r for r in rows if r["shrinkage_applied"] == "DA"]
    lines += [
        "### Compresie separată: cu și fără shrinkage",
        "",
        "| Segment | n | raport scoreline brut | raport scoreline final | raport blend final |",
        "| --- | --- | --- | --- | --- |",
    ]
    for label, subset in (("Fără shrinkage (VERIFIED)", verified), ("Cu shrinkage", shrunk)):
        mkt = excess("market_top1", subset)
        if not subset or mkt is None:
            continue
        parts = []
        for field in ("scoreline_raw_top1", "scoreline_top1", "model_top1"):
            exc = excess(field, subset)
            parts.append("–" if exc is None else f"{exc / mkt:.3f}")
        lines.append(f"| {label} | {len(subset)} | " + " | ".join(parts) + " |")
    lines.append("")

    weights = [r["weight_prior"] for r in shrunk if r.get("weight_prior") is not None]
    if weights:
        n_cur = [r["n_current_home"] for r in shrunk if r.get("n_current_home") is not None]
        n_pri = [r["n_prior_home"] for r in shrunk if r.get("n_prior_home") is not None]
        lines += [
            "## Cât din estimare vine din datele echipei și cât din priorul de ligă",
            "",
            f"Pe cele {len(weights)} selecții cu shrinkage activ:",
            "",
            f"- pondere prior, medie = **{statistics.fmean(weights) * 100:.1f}%**, "
            f"mediană = {statistics.median(weights) * 100:.1f}%, "
            f"max = {max(weights) * 100:.1f}%",
            f"- pondere date proprii, medie = **{(1 - statistics.fmean(weights)) * 100:.1f}%**",
            f"- N_current (gazde), medie = {statistics.fmean(n_cur):.1f}" if n_cur else "",
            f"- N_prior (ligă), medie = {statistics.fmean(n_pri):.1f}" if n_pri else "",
            "",
        ]

    draws = [
        (r["pdraw_model"], r["pdraw_market"])
        for r in rows
        if r.get("pdraw_model") is not None and r.get("pdraw_market") is not None
    ]
    if draws:
        lines += [
            "## Probabilitatea de egal: model vs piață",
            "",
            f"- P(X) model, medie = {statistics.fmean(d for d, _ in draws):.4f}",
            f"- P(X) piață, medie = {statistics.fmean(k for _, k in draws):.4f}",
            f"- diferență medie = {statistics.fmean(d - k for d, k in draws) * 100:.2f} pp",
            "",
        ]

    gaps = [r["scoreline_strength_gap"] for r in rows if r["scoreline_strength_gap"] is not None]
    if gaps:
        lines += [
            "## Distanța dintre scoreline și strength",
            "",
            "Diferența absolută maximă între cele două distribuții, per meci.",
            "Două modele cu adevărat independente ar diverge substanțial.",
            "",
            f"- medie = {statistics.fmean(gaps):.4f}",
            f"- mediană = {statistics.median(gaps):.4f}",
            f"- max = {max(gaps):.4f}",
            "",
        ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--limit", type=int, default=60)
    args = parser.parse_args()

    matches = _load_matches(args)
    print(f"{len(matches)} meciuri incarcate")

    market_rows: list[dict[str, Any]] = []
    risk_rows: list[dict[str, Any]] = []
    for match in matches:
        try:
            m_rows, r_rows = _rows_for_match(match)
        except Exception as exc:  # noqa: BLE001
            print(f"  eroare {match.match_id}: {type(exc).__name__}: {exc}")
            continue
        market_rows.extend(m_rows)
        risk_rows.extend(r_rows)

    _write_csv(AUDIT / "model_vs_market_diagnostic.csv", market_rows)
    _write_csv(AUDIT / "risk_score_decomposition.csv", risk_rows)
    usable = [r for r in market_rows if r["delta_model_market_pp"] is not None]
    source = "MOCK" if args.mock else "FootyStats LIVE"
    (AUDIT / "upstream_summary.md").write_text(
        _summary(usable, source, args.date), encoding="utf-8"
    )
    print(f"{len(market_rows)} selectii -> audit/model_vs_market_diagnostic.csv")
    print(f"{len(risk_rows)} selectii -> audit/risk_score_decomposition.csv")
    print(f"{len(usable)} selectii cu delta -> audit/upstream_summary.md")


if __name__ == "__main__":
    main()
