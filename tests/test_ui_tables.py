from src.excel.generator import write_over05_results_csv
from src.ui_tables import over05_summary_rows, validation_summary_rows


def _fmt_prob(value):
    if value is None or value == "":
        return ""
    return f"{float(value) * 100:.2f}%"


def _fmt_score(value):
    if value is None or value == "":
        return ""
    return f"{float(value):.2f}"


SAMPLE = {
    "model_id": "over05",
    "ora_bucuresti": "16:00",
    "liga": "Premier League",
    "echipe": "Arsenal vs Chelsea",
    "model": "Over 0.5",
    "recommendation": "WATCH / NO BET",
    "risk_level": 2,
    "model_g0": "PASS",
    "p_over": 0.92,
    "p0_recalibrated": 0.81,
    "confidence": 59.19,
    "risk_score": 7.87,
    "data_status": "valid",
    "g0": "OK",
    "motiv": "",
    "match_id": "90001",
}


def test_over05_table_starts_with_kickoff_and_league():
    rows = over05_summary_rows([SAMPLE], fmt_prob=_fmt_prob, fmt_score=_fmt_score)
    assert list(rows[0].keys())[:3] == ["Oră de începere", "Ligă", "Echipe"]
    assert rows[0]["Oră de începere"] == "16:00"
    assert rows[0]["Ligă"] == "Premier League"


def test_validation_table_starts_with_kickoff_and_league():
    rows = validation_summary_rows(
        [SAMPLE],
        fmt_prob=_fmt_prob,
        fmt_score=_fmt_score,
        color_status=lambda v: v,
    )
    keys = list(rows[0].keys())
    assert keys[:3] == ["Oră de începere", "Ligă", "Echipe"]
    assert "Oră București" not in keys
    assert keys.count("Ligă") == 1


def test_over05_csv_starts_with_ora_and_liga(tmp_path):
    path = write_over05_results_csv(tmp_path, [SAMPLE])
    header = path.read_text(encoding="utf-8").splitlines()[0]
    assert header.startswith("ora,liga,match_id,echipe,")


def test_fill_missing_liga_uses_listing_when_analysis_row_is_blank():
    from src.ui_tables import fill_missing_liga

    rows = fill_missing_liga(
        [{"match_id": "1", "liga": "", "echipe": "A vs B"}],
        [{"match_id": "1", "liga": "Romania Liga I"}],
    )
    assert rows[0]["liga"] == "Romania Liga I"
