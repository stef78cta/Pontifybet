"""Ramuri Cornere V14 neacoperite de cele trei exemple REPLAY.

Toate fixture-urile sunt SINTETICE (vezi `tests/corners_synthetic.py`): nu sunt date
FootyStats și nu sunt observații reale. Valorile așteptate sunt citite din
rezultatul formulelor originale — nicio constantă de model nu este rescrisă aici.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from src.engines.corners import CornersCapacityError
from src.engines.corners.inputs import (
    MAX_HISTORY_ROWS,
    MAX_MATCHES,
    CornersBatchInput,
)
from tests.corners_synthetic import (
    AWAY,
    CUTOFF,
    HOME,
    KICKOFF,
    LEAGUE,
    OTHERS,
    PRIOR_SEASON,
    SEASON,
    event,
    match_input,
    oos_record,
    round_robin,
    run,
    run_batch,
    run_with_cells,
    source,
)


# --- LIVE, cutoff și metadate -------------------------------------------------


def test_cutoff_excludes_events_from_the_cutoff_day_onwards():
    """`Match_Date < INT(Cutoff_UTC)`: ziua cutoff-ului nu intră, ziua anterioară da."""
    base = round_robin(count=40)
    cutoff_day = CUTOFF.date()
    on_cutoff_day = event(
        900,
        match_date=cutoff_day,
        home=HOME,
        away=OTHERS[0],
        home_corners=9,
        away_corners=9,
    )
    day_before = event(
        901,
        match_date=cutoff_day - timedelta(days=1),
        home=HOME,
        away=OTHERS[1],
        home_corners=9,
        away_corners=9,
    )

    without = run(base)
    with_cutoff_day = run(base + [on_cutoff_day])
    with_day_before = run(base + [day_before])

    assert with_cutoff_day.motor["N_H_Season"] == without.motor["N_H_Season"]
    assert with_day_before.motor["N_H_Season"] == without.motor["N_H_Season"] + 1


def test_cutoff_after_kickoff_is_not_released_not_level_five():
    """Metadate invalide: NOT RELEASED, fără Risk Level 5 automat."""
    result = run(
        round_robin(count=40),
        matches=(match_input(cutoff_utc=KICKOFF + timedelta(hours=1)),),
    )
    assert result.release == "NOT RELEASED"
    assert result.reason == "Verifica ID, echipe, mod si cutoff < kickoff"
    for item in result.lines:
        assert item.verdict == "NOT RELEASED"
        assert item.risk_level is None
        assert item.risk_level != 5
        assert not item.eligible


def test_unknown_mode_is_not_released():
    result = run(round_robin(count=40), matches=(match_input(mode="SIMULARE"),))
    assert result.release == "NOT RELEASED"
    assert all(item.verdict == "NOT RELEASED" for item in result.lines)


def test_duplicate_match_identity_invalidates_metadata():
    """Două rânduri `Input_Meci` cu aceeași identitate → `Metadata_Valid` INVALID."""
    twin = match_input(match_id="SYN2")
    results = run_batch(round_robin(count=40), (match_input(), twin))
    for result in results.values():
        assert result.motor["Metadata_Valid"] == "INVALID"
        assert result.release == "NOT RELEASED"


def test_replay_mode_is_excluded_from_top_live_but_keeps_all_lines():
    result = run(round_robin(count=40), matches=(match_input(mode="REPLAY"),))
    assert len(result.lines) == 14
    assert all(not item.live_eligible_best for item in result.lines)
    eligible = [item for item in result.lines if item.eligible]
    assert eligible, "REPLAY rămâne evaluat, doar exclus din clasamentul LIVE"
    assert all(item.rank_live is None for item in result.lines)


# --- Date lipsă versus zero ---------------------------------------------------


def test_zero_corners_are_observations_not_missing_data():
    """0 cornere este o observație validă: intră în N și scade media."""
    base = round_robin(count=40)
    zeros = [
        event(
            950 + offset,
            match_date=date(2026, 4, offset + 1),
            home=HOME,
            away=OTHERS[offset % 2],
            home_corners=0,
            away_corners=0,
        )
        for offset in range(4)
    ]
    without = run(base)
    with_zeros = run(base + zeros)

    assert with_zeros.motor["N_H_Season"] == without.motor["N_H_Season"] + 4
    assert with_zeros.motor["Mean_Total_History"] < without.motor["Mean_Total_History"]
    assert with_zeros.g0 == "PASS"


def test_missing_corner_sentinel_marks_the_row_as_problem():
    """Sentinela -1 nu devine zero: rândul este raportat ca problemă de sursă."""
    base = round_robin(count=40)
    broken = event(
        970,
        match_date=date(2026, 4, 10),
        home=HOME,
        away=OTHERS[0],
        home_corners=-1,
        away_corners=5,
    )
    result = run(base + [broken])
    assert result.motor["Source_Problems"] > 0
    assert result.release == "NOT RELEASED"
    assert result.reason == "Istoric invalid sau conflict: verifica randurile native"


# --- Duplicate și conflicte ---------------------------------------------------


def test_identical_duplicate_rows_are_deduplicated_not_counted_twice():
    """`Row_State=DUPLICATE` scoate rândul din calcul, fără să-l declare problemă.

    Doar conflictele (aceeași cheie canonică, cornere diferite) intră în
    `Problem_Rows`; o repetare identică este eliminată silențios prin `Use_Row=0`.
    """
    base = round_robin(count=40)
    original = base[0]
    duplicate = event(
        980,
        match_date=original.match_date,
        home=original.home,
        away=original.away,
        home_corners=original.home_corners,
        away_corners=original.away_corners,
    )
    without = run(base)
    with_duplicate = run(base + [duplicate])
    assert with_duplicate.motor["Source_Problems"] == 0
    assert with_duplicate.release == "READY"
    assert with_duplicate.motor["N_H_Season"] == without.motor["N_H_Season"]
    assert with_duplicate.motor["N_Dispersion"] == without.motor["N_Dispersion"]


def test_conflicting_duplicate_rows_are_reported_as_problem():
    base = round_robin(count=40)
    original = base[0]
    conflicting = event(
        981,
        match_date=original.match_date,
        home=original.home,
        away=original.away,
        home_corners=original.home_corners + 7,
        away_corners=original.away_corners + 7,
    )
    result = run(base + [conflicting])
    assert result.motor["Source_Problems"] > 0
    assert result.reason == "Istoric invalid sau conflict: verifica randurile native"


# --- Small sample și prior ----------------------------------------------------


def test_small_sample_alone_is_not_a_hard_fail_label():
    """Eticheta SMALL SAMPLE nu blochează: sursa rămâne închisă și lotul eliberat."""
    result = run(round_robin(count=12))
    assert result.motor["Prior_Active"] == "YES"
    assert result.release == "READY"
    current_rows = [row for row in result.core if row.get("Role") == "CURRENT"]
    assert all(row.get("Source_State") == "CLOSED" for row in current_rows)
    assert any(row.get("Data_Status") == "SMALL SAMPLE" for row in current_rows)


def test_small_sample_without_valid_prior_has_no_effective_average():
    """Fără prior valid, mediile efective lipsesc: G0 FAIL pe insuficiență, nu pe etichetă."""
    result = run(round_robin(count=12))
    assert result.motor["Core_Effective_Count"] < 12
    assert result.g0 == "FAIL"
    assert result.reason == "Core / sample / prior insuficient"


def test_small_sample_with_valid_prior_uses_shrinkage_and_confidence_cap():
    """Cu prior permis și derivat, mediile efective se completează prin shrinkage."""
    current = round_robin(count=12, first_date=date(2025, 9, 1))
    prior = round_robin(count=60, season=PRIOR_SEASON, first_date=date(2024, 8, 1))
    result = run(
        current + prior,
        matches=(match_input(prior_season=PRIOR_SEASON, prior_allowed="YES"),),
        sources=(
            source(rows=len(current)),
            source(season=PRIOR_SEASON, rows=len(prior)),
        ),
    )
    prior_rows = [row for row in result.core if row.get("Role") == "PRIOR"]
    assert any(row.get("Source_State") == "CLOSED" for row in prior_rows)
    assert all(row.get("Data_Status") == "DERIVED" for row in prior_rows)
    assert result.motor["Core_Effective_Count"] == 12
    assert result.motor["Prior_Active"] == "YES"
    assert result.g0 == "PASS"
    # Cap-ul de Confidence se aplică atunci când priorul este activ.
    assert result.motor["Confidence_Base"] <= 100
    full_sample = run(round_robin(count=60))
    assert result.motor["Confidence_Base"] <= full_sample.motor["Confidence_Base"]


def test_prior_not_allowed_blocks_the_blend_even_with_prior_history():
    """`Prior_Allowed=NO` opreşte amestecul chiar dacă sezonul anterior este închis."""
    current = round_robin(count=12, first_date=date(2025, 9, 1))
    prior = round_robin(count=60, season=PRIOR_SEASON, first_date=date(2024, 8, 1))
    result = run(
        current + prior,
        matches=(match_input(prior_season=PRIOR_SEASON, prior_allowed="NO"),),
        sources=(
            source(rows=len(current)),
            source(season=PRIOR_SEASON, rows=len(prior)),
        ),
    )
    assert result.motor["Core_Effective_Count"] < 12
    assert result.g0 == "FAIL"
    assert result.reason == "Core / sample / prior insuficient"


# --- Ferestre recente cu egalități de dată ------------------------------------


def test_recent_window_keeps_every_event_sharing_the_threshold_date():
    """Fereastra recentă este construită prin prag de dată, deci include egalitățile."""
    base = round_robin(count=40)
    tie_day = date(2026, 3, 1)
    ties = [
        event(
            990 + offset,
            match_date=tie_day,
            home=HOME,
            away=OTHERS[offset % 2],
            home_corners=7,
            away_corners=7,
        )
        for offset in range(3)
    ]
    with_ties = run(base + ties)
    recent = [
        row
        for row in with_ties.core
        if row.get("Side") == "H" and row.get("Role") == "CURRENT" and row.get("Recent_From")
    ]
    assert recent
    # `N` din fereastra recentă poate depăși ținta exact pentru că pragul de dată
    # nu rupe egalitățile.
    assert any(row["N"] >= row["Target_N"] for row in recent)


# --- Soft lipsă și context invalid -------------------------------------------


def test_soft_inputs_absent_are_counted_not_zeroed():
    result = run(round_robin(count=40))
    assert result.motor["Soft_Missing"] == 10
    with_soft = run(
        round_robin(count=40),
        matches=(
            match_input(
                context={
                    "Shots_H": 14,
                    "Shots_A": 11,
                    "Blocked_H": 3,
                    "Blocked_A": 2,
                    "Crosses_H": 18,
                    "Crosses_A": 12,
                    "Possession_H": 55,
                    "Possession_A": 45,
                    "Field_Tilt_H": 6,
                    "Field_Tilt_A": 4,
                }
            ),
        ),
    )
    assert with_soft.motor["Soft_Missing"] == 0
    assert with_soft.motor["Confidence_Base"] >= result.motor["Confidence_Base"]


def test_context_out_of_domain_is_invalid_and_fails_g0():
    """Scorurile contextuale semnate au domeniul lor: ±2, nu 0–10."""
    result = run(
        round_robin(count=40),
        matches=(match_input(context={"Absences_H": 5}),),
    )
    assert result.motor["Context_Valid"] == "INVALID"
    assert result.g0 == "FAIL"
    assert result.reason == "Context invalid"


def test_signed_context_inside_its_own_domain_stays_valid():
    result = run(
        round_robin(count=40),
        matches=(
            match_input(
                context={
                    "Absences_H": -2,
                    "Absences_A": 2,
                    "Stakes_H": -1,
                    "Stakes_A": 1,
                    "Attack_H": 7,
                    "Chasing_A": 0,
                }
            ),
        ),
    )
    assert result.motor["Context_Valid"] == "VALID"
    assert result.g0 == "PASS"


# --- Dispersie, distribuție și praguri ---------------------------------------


def test_low_dispersion_takes_the_poisson_branch():
    result = run(round_robin(count=60, variation=0))
    assert result.distribution_kind == "POISSON"
    assert result.motor["NB_Size"] == 9999


def test_high_dispersion_takes_the_negative_binomial_branch():
    result = run(round_robin(count=60, variation=5))
    assert result.distribution_kind == "NEGATIVE BINOMIAL"
    size = result.motor["NB_Size"]
    mean = result.motor["Mean_Total_History"]
    dispersion = result.motor["D"]
    assert size > 0
    # Parametrul NB derivă din media istorică, nu din Mu.
    assert size == pytest.approx(mean / (dispersion - 1), rel=1e-12)
    assert size != pytest.approx(result.motor["Mu"] / (dispersion - 1), rel=1e-6)


def test_pmf_and_cdf_are_a_consistent_distribution():
    result = run(round_robin(count=60, variation=5))
    pmf = [result.distribution[f"PMF_{k}"] for k in range(19)]
    cdf = [result.distribution[f"CDF_{k}"] for k in range(19)]
    assert all(value >= 0 for value in pmf)
    running = 0.0
    for index, value in enumerate(pmf):
        running += value
        assert cdf[index] == pytest.approx(running, abs=1e-12)
    assert cdf[-1] <= 1.0 + 1e-12


def test_risk_score_uses_failure_gate_and_confidence_base():
    """Risk Score combină Failure_Gate și Confidence Base, exact ca în Excel."""
    result = run(round_robin(count=60, variation=3))
    confidence_base = result.motor["Confidence_Base"]
    for item in result.lines:
        if item.risk_score is None:
            continue
        # Failure_Gate mai mare la aceeași Confidence Base împinge scorul în sus.
        assert item.failure_gate is not None
    ordered = sorted(
        (item for item in result.lines if item.risk_score is not None),
        key=lambda item: item.failure_gate,
    )
    assert [item.risk_score for item in ordered] == sorted(
        item.risk_score for item in ordered
    )
    assert 0 <= confidence_base <= 100


def test_risk_level_raw_follows_the_score_bands():
    result = run(round_robin(count=60, variation=3))
    for item in result.lines:
        score = item.risk_score
        if score is None:
            continue
        expected = 1 if score <= 20 else 2 if score <= 40 else 3 if score <= 60 else 4 if score <= 80 else 5
        assert item.risk_level_raw == expected


def test_p_final_is_capped_by_the_failure_gate():
    result = run(round_robin(count=60, variation=3))
    for item in result.lines:
        if item.p_final is None:
            continue
        assert item.p_final == pytest.approx(
            min(item.p_calibrated, 1 - item.failure_gate), abs=1e-12
        )


# --- PASS / PENALTY / WATCH și gate-uri --------------------------------------


def test_tail_gate_states_are_pass_penalty_watch_or_oos_pending():
    result = run(round_robin(count=60, variation=5))
    states = {item.tail_gate for item in result.lines}
    assert states <= {"PASS", "PENALTY", "WATCH", "OOS PENDING", "INVALID", "NOT RELEASED"}
    for item in result.lines:
        if item.tail_gate == "WATCH":
            assert item.risk_level == 5
            assert item.verdict == "NO BET"
            assert item.reason == "Failure peste limita"
        if item.tail_gate == "PENALTY" and item.risk_level_raw is not None:
            assert item.risk_level >= item.risk_level_raw


def test_watch_verdict_can_keep_risk_level_two():
    """Un verdict WATCH nu impune nivel 5: pragul de P sau Confidence l-a oprit."""
    result = run(round_robin(count=60, variation=1))
    watch = [item for item in result.lines if item.verdict == "WATCH"]
    assert watch
    assert any(item.risk_level == 2 for item in watch)
    assert all(
        item.reason in {"P finala sub prag", "Confidence sub prag"} for item in watch
    )


def test_defensive_gate_pending_when_candidate_lacks_validated_calibration():
    """Candidat DEFENSIV fără calibrare validată → OOS PENDING, nu PASS și nu NO BET."""
    result = run(round_robin(count=60, variation=0))
    candidates = [item for item in result.lines if item.defensive_candidate == "CANDIDATE"]
    for item in candidates:
        assert item.defensive_gate in {"PASS", "OOS PENDING"}
        if item.defensive_gate == "OOS PENDING":
            assert item.verdict != "NO BET"
            assert item.oos_status == "OOS PENDING"


def test_oos_pending_does_not_force_no_bet():
    result = run(round_robin(count=60, variation=1))
    pending = [item for item in result.lines if item.oos_status == "OOS PENDING"]
    assert pending
    assert any(item.verdict in {"PRUDENT", "MODERAT", "RIDICAT", "WATCH"} for item in pending)


def test_pilot_band_skips_the_oos_pending_tail_state():
    """Banda pilot O3,5 evaluează direct pragurile; restul liniilor trec prin OOS PENDING.

    Formula `Tail_Gate` a primului rând conține `IF(NOT(TRUE),"OOS PENDING",…)`,
    deci ramura este inaccesibilă exact pe banda pilot. Păstrăm comportamentul
    formulei originale.
    """
    result = run(round_robin(count=60, variation=0))
    pilot = next(item for item in result.lines if item.line.label == "O3,5")
    others = [item for item in result.lines if item.line.label != "O3,5"]
    assert pilot.tail_gate != "OOS PENDING"
    assert any(item.tail_gate == "OOS PENDING" for item in others)


def test_tail_pass_is_not_an_oos_validation():
    """Tail PASS pe banda pilot nu promovează linia la VALIDATED."""
    result = run(round_robin(count=60, variation=0))
    pilot = next(item for item in result.lines if item.line.label == "O3,5")
    assert pilot.tail_gate == "PASS"
    assert pilot.oos_status == "OOS PENDING"
    assert pilot.builder in {"CONDITIONAL", "YES", "NO"}


def test_builder_reflects_the_tail_gate_not_the_verdict():
    result = run(round_robin(count=60, variation=1))
    for item in result.lines:
        if not item.eligible:
            assert item.builder == "NO"
        elif item.tail_gate == "PASS":
            assert item.builder == "YES"
        elif item.tail_gate == "OOS PENDING":
            assert item.builder == "CONDITIONAL"


# --- Surse și stări de sourcing ----------------------------------------------


def test_access_blocked_is_a_model_state_with_its_own_reason():
    result = run(
        round_robin(count=40),
        matches=(
            match_input(
                sourcing_decision="ACCESS BLOCKED",
                evidence_or_attempts='[{"endpoint": "league-matches"}]',
            ),
        ),
    )
    assert result.release == "NOT RELEASED"
    assert result.reason == "Acces blocat: reia sursele"
    assert all(item.verdict == "NOT RELEASED" for item in result.lines)


def test_not_available_with_evidence_is_released_but_fails_g0():
    result = run(
        round_robin(count=40),
        matches=(
            match_input(
                sourcing_decision="NOT AVAILABLE",
                evidence_or_attempts="sezon fără export",
            ),
        ),
    )
    assert result.release == "READY"
    assert result.g0 == "FAIL"
    assert result.reason == "NOT AVAILABLE"


def test_not_available_without_evidence_is_not_released():
    result = run(
        round_robin(count=40),
        matches=(match_input(sourcing_decision="NOT AVAILABLE"),),
    )
    assert result.release == "NOT RELEASED"


# --- Registrul OOS ------------------------------------------------------------


def _oos_cells(count: int) -> list[str]:
    return [f"OOS_Predictii!{col}{6 + offset}" for offset in range(count) for col in "TU"]


def test_complete_oos_record_is_valid_and_scored():
    """Un rând OOS complet trece `Record_Valid` și primește `Win` după linie."""
    extras = run_with_cells(
        round_robin(count=40),
        cells=_oos_cells(1),
        oos_records=(oos_record(fixture_id="OOS-1", line="O3,5", total_corners=9),),
    )
    assert extras["OOS_Predictii!T6"] == 1
    # O3,5 câștigă dacă totalul depășește k=3.
    assert extras["OOS_Predictii!U6"] == 1


def test_under_line_oos_record_is_scored_on_the_other_side():
    extras = run_with_cells(
        round_robin(count=40),
        cells=_oos_cells(2),
        oos_records=(
            oos_record(fixture_id="OOS-2", line="U10,5", total_corners=9),
            oos_record(fixture_id="OOS-3", line="U10,5", total_corners=14),
        ),
    )
    assert extras["OOS_Predictii!T6"] == 1
    assert extras["OOS_Predictii!U6"] == 1
    assert extras["OOS_Predictii!T7"] == 1
    assert extras["OOS_Predictii!U7"] == 0


def test_duplicate_oos_records_are_both_invalid():
    """Unicitatea `Fixture_ID` + `Line` este o condiție de validitate a înregistrării."""
    extras = run_with_cells(
        round_robin(count=40),
        cells=_oos_cells(2),
        oos_records=(
            oos_record(fixture_id="OOS-4", line="O4,5"),
            oos_record(fixture_id="OOS-4", line="O4,5"),
        ),
    )
    assert extras["OOS_Predictii!T6"] == 0
    assert extras["OOS_Predictii!T7"] == 0


@pytest.mark.parametrize(
    "override",
    [
        {"prior_active": "YES"},
        {"native_core_count": 11},
        {"candidate_tail": "PENALTY"},
        {"mode": "REPLAY"},
        {"p_final": 0.85},
        {"candidate_confidence": 88.0},
        {"risk_score": 25.0},
        {"dispersion": 1.5},
        {"settled": datetime(2026, 4, 21, 17, 0)},
        {"training_end": datetime(2026, 4, 20, 12, 0)},
        {"line": "O9,5"},
    ],
)
def test_oos_record_rejected_when_a_single_condition_fails(override):
    extras = run_with_cells(
        round_robin(count=40),
        cells=_oos_cells(1),
        oos_records=(oos_record(fixture_id="OOS-5", **override),),
    )
    assert extras["OOS_Predictii!T6"] == 0
    assert extras["OOS_Predictii!U6"] == 0


def test_oos_records_alone_do_not_promote_a_line_to_validated():
    """Rândurile OOS nu promovează singure o linie.

    `OOS_N` se numără doar în fereastra de review a liniei (`Training_End_UTC` și
    `Review_UTC` din `Calibrare_Linii`, plus `Scope_League` și `Model_Signature`).
    Șablonul livrat nu are o fereastră aprobată, deci nicio linie nu poate fi
    validată din istoricul aplicației.
    """
    records = tuple(
        oos_record(fixture_id=f"OOS-P{index}", line="O3,5", total_corners=9)
        for index in range(12)
    )
    extras = run_with_cells(
        round_robin(count=40),
        cells=[
            "Calibrare_Linii!I6",
            "Calibrare_Linii!J6",
            "Calibrare_Linii!M6",
            "Calibrare_Linii!S6",
            "Calibrare_Linii!T6",
            "Calibrare_Linii!U6",
            "OOS_Predictii!T6",
        ],
        oos_records=records,
    )
    assert extras["OOS_Predictii!T6"] == 1, "rândurile sunt valide ca înregistrări"
    assert extras["Calibrare_Linii!U6"] == "VALID", "parametrii liniei rămân valizi"
    # Fără fereastră de review numerică, promovarea nu poate fi numărată.
    assert not isinstance(extras["Calibrare_Linii!I6"], (int, float))
    assert extras["Calibrare_Linii!M6"] == 0
    assert extras["Calibrare_Linii!S6"] == "PENDING"
    assert extras["Calibrare_Linii!T6"] == "PENDING"

    result = run(round_robin(count=40), oos_records=records)
    pilot = next(item for item in result.lines if item.line.label == "O3,5")
    assert pilot.oos_status == "OOS PENDING"
    assert pilot.defensive_gate != "PASS"


# --- Ranking ------------------------------------------------------------------


def test_rank_in_match_orders_by_level_then_probability_then_confidence():
    result = run(round_robin(count=60, variation=1))
    ranked = sorted(
        (item for item in result.lines if item.rank_in_match),
        key=lambda item: item.rank_in_match,
    )
    keys = [
        (item.risk_level, -item.p_final, -item.confidence_final, item.line.offset)
        for item in ranked
    ]
    assert keys == sorted(keys)


def test_top_live_keeps_one_line_per_match_and_at_most_ten():
    from src.engines.corners.engine import TOP_LIVE_LIMIT, rank_top_live

    matches = tuple(
        match_input(match_id=f"SYN{index}", kickoff_utc=KICKOFF + timedelta(hours=index))
        for index in range(1, 4)
    )
    results = run_batch(round_robin(count=60, variation=1), matches)
    ordered = rank_top_live(list(results.values()))
    owners = [
        match_id
        for match_id, result in results.items()
        for item in result.lines
        if item in ordered
    ]
    assert len(owners) == len(set(owners))
    assert len(ordered) <= TOP_LIVE_LIMIT


# --- Limitele fizice ale șablonului ------------------------------------------


def test_capacity_error_names_the_limit_instead_of_truncating():
    history = round_robin(count=MAX_HISTORY_ROWS + 5)
    batch = CornersBatchInput(
        matches=(match_input(),),
        history=tuple(history),
        sources=(source(rows=len(history)),),
    )
    with pytest.raises(CornersCapacityError) as exc:
        batch.validate_capacity()
    assert exc.value.limit == MAX_HISTORY_ROWS
    assert exc.value.requested == MAX_HISTORY_ROWS + 5


def test_match_capacity_error_reports_the_slot_limit():
    matches = tuple(
        match_input(match_id=f"SYN{index}", kickoff_utc=KICKOFF + timedelta(minutes=index))
        for index in range(MAX_MATCHES + 2)
    )
    batch = CornersBatchInput(matches=matches, history=(), sources=())
    with pytest.raises(CornersCapacityError) as exc:
        batch.validate_capacity()
    assert exc.value.limit == MAX_MATCHES
