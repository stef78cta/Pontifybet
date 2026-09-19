"""Pontifybet MVP — interfață Streamlit (o singură pagină)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Asigură importurile din rădăcina proiectului
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Streamlit poate păstra module incomplete după reload parțial.
_client_mod = sys.modules.get("src.api.client")
if _client_mod is not None and not hasattr(_client_mod, "FootyStatsClient"):
    sys.modules.pop("src.api.client", None)

_settings_mod = sys.modules.get("config.settings")
if _settings_mod is not None and not hasattr(_settings_mod, "DEV_MODULE_RELOAD"):
    sys.modules.pop("config.settings", None)

_pipeline_mod = sys.modules.get("src.pipeline")
if _pipeline_mod is not None and not hasattr(_pipeline_mod, "run_export"):
    sys.modules.pop("src.pipeline", None)

import streamlit as st

import config.settings as settings

DEFAULT_TIMEZONE = settings.DEFAULT_TIMEZONE
DEV_MODULE_RELOAD = getattr(settings, "DEV_MODULE_RELOAD", False)
ensure_runtime_dirs = settings.ensure_runtime_dirs
from src.api.client import FootyStatsError, current_season_id
from src.api.factory import get_client
import importlib

import src.pipeline as pipeline

if not hasattr(pipeline, "run_export"):
    pipeline = importlib.reload(pipeline)

MODEL_LABELS = pipeline.MODEL_LABELS
cleanup_after_download = pipeline.cleanup_after_download
list_matches_for_filters = pipeline.list_matches_for_filters
sort_listed_matches = pipeline.sort_listed_matches
run_export = getattr(pipeline, "run_export", None)

_orch_mod = sys.modules.get("src.orchestration.snapshot")
if _orch_mod is not None and not hasattr(_orch_mod, "analysis_fingerprint"):
    sys.modules.pop("src.orchestration.snapshot", None)

from src.orchestration.snapshot import analysis_fingerprint
from src.security.auth import verify_password
from src.excel.integrity import IntegrityError
import src.history.backtest as history_backtest
import src.history.excel_ingest as history_ingest
import src.history.results as history_results
import src.history.views as history_views

st.set_page_config(page_title="Pontifybet", page_icon="P", layout="wide")
ensure_runtime_dirs()

SORT_LABELS = {"ora": "Oră de începere", "liga": "Ligă"}
SORT_BY_LABEL = {v: k for k, v in SORT_LABELS.items()}


def _fmt_prob(value: Any) -> str:
    if value is None or value == "":
        return ""
    try:
        return f"{float(value) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(value)


def _fmt_score(value: Any) -> str:
    if value is None or value == "":
        return ""
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return str(value)


def _reload_analysis_modules() -> None:
    """Reîncarcă MatchData + client înainte de generate, ca Streamlit să nu țină clase vechi."""
    import src.api.client as fs_client
    import src.api.factory as fs_factory
    import src.adapters.double_chance as dc_adapter
    import src.adapters.over05 as over05_adapter
    import src.engines.double_chance as dc_pkg
    import src.engines.double_chance.engine as dc_engine
    import src.engines.double_chance.inputs as dc_inputs
    import src.engines.over05 as over05_pkg
    import src.engines.over05.engine as over05_engine
    import src.engines.over05.evaluator as over05_eval
    import src.engines.over05.inputs as over05_inputs
    import src.excel.generator as excel_generator
    import src.models.match_data as match_data
    import src.ui_tables as ui_tables

    importlib.reload(match_data)
    importlib.reload(fs_client)
    importlib.reload(fs_factory)
    importlib.reload(excel_generator)
    importlib.reload(over05_eval)
    importlib.reload(over05_inputs)
    importlib.reload(over05_engine)
    importlib.reload(over05_pkg)
    importlib.reload(over05_adapter)
    importlib.reload(dc_inputs)
    importlib.reload(dc_engine)
    importlib.reload(dc_pkg)
    importlib.reload(dc_adapter)
    importlib.reload(pipeline)
    importlib.reload(ui_tables)


def _editor_key() -> str:
    return f"match_editor_{st.session_state.match_editor_rev}"


def _bump_match_editor() -> None:
    st.session_state.match_editor_rev = int(st.session_state.get("match_editor_rev", 0)) + 1


def _filter_fingerprint(date_iso: str, timezone_name: str, league_ids: list[int]) -> tuple[Any, ...]:
    return (date_iso, timezone_name, tuple(sorted(int(x) for x in league_ids)))


def _rows_from_editor(data: Any) -> list[dict[str, Any]]:
    if data is None:
        return []
    if hasattr(data, "to_dict"):
        return list(data.to_dict("records"))
    if isinstance(data, dict):
        keys = list(data.keys())
        if not keys:
            return []
        first = data[keys[0]]
        n = len(first) if isinstance(first, (list, tuple)) else 0
        return [{k: data[k][i] for k in keys} for i in range(n)]
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    return []


def _apply_editor_to_listed() -> None:
    """Citește bifele din widget înainte de sortare / select-all / generate."""
    data = st.session_state.get(_editor_key())
    rows = _rows_from_editor(data)
    if not rows:
        return
    by_id = {
        str(r.get("match_id")): bool(r.get("selected"))
        for r in rows
        if r.get("match_id") is not None
    }
    for item in st.session_state.listed_matches:
        mid = str(item["match_id"])
        if mid in by_id:
            item["selected"] = by_id[mid]


def _on_sort_change() -> None:
    _apply_editor_to_listed()
    _bump_match_editor()


def _set_all_selected(value: bool) -> None:
    _apply_editor_to_listed()
    for item in st.session_state.listed_matches:
        item["selected"] = value
    _bump_match_editor()


# --- Autentificare ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Pontifybet")
    st.caption("Aplicație privată — acces cu parolă.")
    with st.form("login_form"):
        pwd = st.text_input("Parolă", type="password")
        submitted = st.form_submit_button("Intră")
    if submitted:
        if verify_password(pwd):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Parolă greșită. Verifică APP_PASSWORD din .env sau secrets.toml.")
    st.stop()

if "listed_matches" not in st.session_state:
    st.session_state.listed_matches = []
if "listed_fingerprint" not in st.session_state:
    st.session_state.listed_fingerprint = None
if "match_editor_rev" not in st.session_state:
    st.session_state.match_editor_rev = 0
if "match_sort_label" not in st.session_state:
    st.session_state.match_sort_label = SORT_LABELS["ora"]
if "analysis_snapshot" not in st.session_state:
    st.session_state.analysis_snapshot = None
if "export_result" not in st.session_state:
    st.session_state.export_result = None
if "analysis_fingerprint" not in st.session_state:
    st.session_state.analysis_fingerprint = None

# --- UI principal ---
st.title("Pontifybet")
st.write(
    "Selectează data, ligile și modelele, apasă **Listează meciurile**, "
    "bifează meciurile, apoi **Generează analiza**. "
    "Aplicația completează copii ale șabloanelor Excel — fără a modifica originalele."
)
st.info(
    "Over 0.5 și Șansă Dublă sunt calculate în Python: verdict, nivel, scor și "
    "probabilități oficiale apar în tabelele de mai jos. "
    "Șansă Dublă LIVE derivează 1X2 din goluri/xG (Poisson independent, etichetă "
    "DERIVED), nu din Dixon–Coles/Elo Excel. Cornere rămân calculate în Microsoft Excel."
)
st.caption("Mod date: **LIVE (FootyStats)**")

with st.sidebar:
    st.header("Filtre")
    date_iso = st.date_input("Data meciurilor").isoformat()
    timezone_name = st.selectbox(
        "Fus orar",
        options=[DEFAULT_TIMEZONE, "UTC", "Europe/London"],
        index=0,
    )

    client = get_client()
    league_ids: list[int] = []
    selected_models: list[str] = []
    try:
        leagues = client.list_leagues()
        league_options = {}
        for lg in leagues:
            sid = current_season_id(lg)
            label = lg.get("name") or lg.get("league_name") or str(sid)
            if sid is not None:
                league_options[label] = int(sid)
        if not league_options:
            st.warning(
                "Nu am găsit ligi alese pe cheia ta. Selectează ligile în "
                "[API Settings](https://footystats.org/api/u/api-settings)."
            )
        selected_league_labels = st.multiselect(
            "Ligi",
            options=list(league_options.keys()),
            default=list(league_options.keys())[:2] if league_options else [],
        )
        league_ids = [league_options[x] for x in selected_league_labels]

        model_options = list(MODEL_LABELS.keys())
        selected_models = st.multiselect(
            "Modele",
            options=model_options,
            default=model_options,
            format_func=lambda x: MODEL_LABELS[x],
        )
    except FootyStatsError as exc:
        st.error(exc.user_message)
    finally:
        client.close()

current_fp = _filter_fingerprint(date_iso, timezone_name, league_ids)
if (
    st.session_state.listed_fingerprint is not None
    and st.session_state.listed_fingerprint != current_fp
):
    st.session_state.listed_matches = []
    st.session_state.listed_fingerprint = None
    st.session_state.analysis_snapshot = None
    st.session_state.export_result = None
    st.session_state.analysis_fingerprint = None
    if "last_result" in st.session_state:
        del st.session_state["last_result"]
    _bump_match_editor()

btn_list, btn_gen, _ = st.columns([2.6, 2.6, 1.8])
with btn_list:
    list_clicked = st.button("Listează meciurile")
with btn_gen:
    generate = st.button("Generează analiza", type="primary")

if list_clicked:
    if not league_ids:
        st.warning("Selectează cel puțin o ligă în filtru.")
    else:
        try:
            rows = list_matches_for_filters(
                date_iso=date_iso,
                league_ids=league_ids,
                timezone_name=timezone_name,
            )
            st.session_state.listed_matches = sort_listed_matches(
                rows, SORT_BY_LABEL.get(st.session_state.match_sort_label, "ora")
            )
            st.session_state.listed_fingerprint = current_fp
            _bump_match_editor()
        except FootyStatsError as exc:
            st.error(exc.user_message)

listed_ok = st.session_state.listed_fingerprint == current_fp

if generate:
    _apply_editor_to_listed()
    match_ids = [
        str(r["match_id"])
        for r in st.session_state.listed_matches
        if r.get("selected")
    ]
    if not listed_ok:
        st.error("Listează mai întâi meciurile, apoi bifează cel puțin unul.")
    elif not match_ids:
        st.error("Bifează cel puțin un meci.")
    elif not selected_models:
        st.error("Selectează cel puțin un model.")
    else:
        progress_bar = st.progress(0.0, text="Pornesc…")
        status = st.empty()

        def on_progress(msg: str, pct: float) -> None:
            progress_bar.progress(min(max(pct, 0.0), 1.0), text=msg)
            status.write(msg)

        if DEV_MODULE_RELOAD:
            _reload_analysis_modules()
        result = pipeline.run_analysis(
            date_iso=date_iso,
            league_ids=league_ids,
            match_ids=match_ids,
            model_ids=selected_models,
            timezone_name=timezone_name,
            progress=on_progress,
        )
        st.session_state["last_result"] = result
        st.session_state.analysis_snapshot = result["snapshot"]
        st.session_state.analysis_fingerprint = result["analysis_fingerprint"]
        st.session_state.export_result = None

if listed_ok and not st.session_state.listed_matches:
    st.info("Nu am găsit meciuri pentru data și ligile selectate.")

if listed_ok and st.session_state.listed_matches:
    st.radio(
        "Sortează după",
        options=list(SORT_LABELS.values()),
        horizontal=True,
        key="match_sort_label",
        on_change=_on_sort_change,
    )
    sel1, sel2, _ = st.columns([2.4, 2.4, 2])
    with sel1:
        st.button("Selectează toate", on_click=_set_all_selected, args=(True,))
    with sel2:
        st.button("Debifează toate", on_click=_set_all_selected, args=(False,))

    display_rows = [
        {
            "selected": r["selected"],
            "liga": r["liga"],
            "ora": r["ora"],
            "echipe": r["echipe"],
            "match_id": r["match_id"],
        }
        for r in sort_listed_matches(
            st.session_state.listed_matches,
            SORT_BY_LABEL.get(st.session_state.match_sort_label, "ora"),
        )
    ]
    edited = st.data_editor(
        display_rows,
        column_order=["selected", "liga", "ora", "echipe"],
        column_config={
            "selected": st.column_config.CheckboxColumn("Selectat", required=True),
            "liga": st.column_config.TextColumn("Ligă"),
            "ora": st.column_config.TextColumn("Oră"),
            "echipe": st.column_config.TextColumn("Echipe"),
            "match_id": None,
        },
        disabled=["liga", "ora", "echipe"],
        hide_index=True,
        use_container_width=True,
        num_rows="fixed",
        key=_editor_key(),
    )
    selected_count = sum(1 for r in _rows_from_editor(edited) if r.get("selected"))
    st.caption(f"{len(display_rows)} meciuri listate, {selected_count} bifațe.")
    by_id = {
        str(r.get("match_id")): bool(r.get("selected"))
        for r in _rows_from_editor(edited)
        if r.get("match_id") is not None
    }
    for item in st.session_state.listed_matches:
        mid = str(item["match_id"])
        if mid in by_id:
            item["selected"] = by_id[mid]

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    import src.ui_tables as ui_tables

    importlib.reload(ui_tables)
    st.subheader("Rezumat validare")

    def color_status(val: str) -> str:
        if val == "valid":
            return "valid (verde)"
        if val == "pending":
            return "pending (galben)"
        return "blocat (roșu)"

    result_rows = ui_tables.fill_missing_liga(
        result["rows"],
        st.session_state.get("listed_matches"),
    )
    over05_rows = [r for r in result_rows if r.get("model_id") == "over05"]
    if over05_rows and not any(r.get("recommendation") for r in over05_rows):
        st.warning(
            "Recomandarea Over 0.5 lipsește din acest rezumat. "
            "Apasă din nou **Generează analiza** ca motorul să recaluzeze meciurile."
        )
    if over05_rows:
        st.subheader("Recomandare finală Over 0.5")
        over05_display = ui_tables.over05_summary_rows(
            over05_rows, fmt_prob=_fmt_prob, fmt_score=_fmt_score
        )
        st.dataframe(
            over05_display,
            use_container_width=True,
            hide_index=True,
            column_order=list(over05_display[0].keys()) if over05_display else None,
        )

    dc_rows = [r for r in result_rows if r.get("model_id") == "double_chance"]
    if dc_rows:
        st.subheader("Recomandare finală Șansă Dublă")
        st.caption(
            "1X2 LIVE este DERIVED din goluri/xG (Poisson independent). "
            "Nu este Dixon–Coles sau Elo din workbook; piața rămâne ancora de 25%. "
            "Market Direction / Protected Strength / Draw Gate / P0 final sunt controale "
            "de input, nu verdictul: verdictul final este în coloana Verdict."
        )
        show_all_dc = st.toggle(
            "Afișează toate selecțiile (inclusiv WATCH și NO BET)",
            value=False,
            key="dc_show_all",
            help=(
                "Implicit apar doar selecțiile eligibile pentru clasament (AA=YES) "
                "sau cu P0 final PASS/PRUDENT. Toate cele trei selecții rămân calculate "
                "și exportate în CSV."
            ),
        )
        dc_display = ui_tables.double_chance_summary_rows(
            dc_rows, fmt_prob=_fmt_prob, fmt_score=_fmt_score, show_all=show_all_dc
        )
        st.dataframe(
            dc_display,
            use_container_width=True,
            hide_index=True,
            column_order=list(dc_display[0].keys()) if dc_display else None,
        )

    validation_rows = ui_tables.validation_summary_rows(
        result_rows,
        fmt_prob=_fmt_prob,
        fmt_score=_fmt_score,
        color_status=color_status,
    )
    st.dataframe(validation_rows, use_container_width=True, hide_index=True)

    if result.get("errors"):
        for err in result["errors"]:
            st.error(err)

    current_analysis_fp = analysis_fingerprint(
        date_iso=date_iso,
        timezone_name=timezone_name,
        league_ids=league_ids,
        match_ids=[
            str(r["match_id"])
            for r in st.session_state.listed_matches
            if r.get("selected")
        ],
        model_ids=selected_models,
    )
    snapshot = st.session_state.get("analysis_snapshot")
    export_stale = (
        snapshot is None
        or st.session_state.get("analysis_fingerprint") != current_analysis_fp
    )
    if export_stale and snapshot is not None:
        st.warning(
            "Parametrii s-au schimbat față de ultima analiză. "
            "Apasă din nou **Generează analiza** înainte de export."
        )

    export_clicked = st.button(
        "Pregătește fișierele Excel",
        type="secondary",
        disabled=export_stale or snapshot is None,
    )
    if export_clicked and snapshot is not None and not export_stale:
        export_progress = st.progress(0.0, text="Pornesc export…")
        export_status = st.empty()

        def on_export_progress(msg: str, pct: float) -> None:
            export_progress.progress(min(max(pct, 0.0), 1.0), text=msg)
            export_status.write(msg)

        if run_export is None:
            st.error(
                "Export indisponibil — repornește aplicația Streamlit "
                "(modul pipeline vechi în memorie)."
            )
        else:
            st.session_state.export_result = run_export(
                snapshot,
                progress=on_export_progress,
            )

    export_result = st.session_state.get("export_result")
    if export_result:
        zip_path = Path(export_result["zip_path"])
        if zip_path.exists():
            data = zip_path.read_bytes()
            clicked = st.download_button(
                label="Descarcă fișierele Excel",
                data=data,
                file_name=zip_path.name,
                mime="application/zip",
            )
            st.caption(
                f"Fișiere generate: {len(export_result.get('generated', []))} | "
                "Raport inclus în ZIP."
            )
            if clicked:
                cleanup_after_download(export_result["run_dir"])
                st.session_state.export_result = None

# --- Istoric și rezultate ---
st.divider()
st.subheader("Istoric și rezultate")
st.caption(
    "Predicțiile pre-match sunt memorate imuabil în SQLite (`data/`), separat de "
    "`outputs/`. Rezultatele oficiale vin din FootyStats și nu modifică niciodată "
    "recomandarea înghețată."
)

history_summary = st.session_state.get("history_update_summary")
col_btn, col_pending = st.columns([2.4, 4])
with col_btn:
    update_clicked = st.button("Actualizează rezultate")
with col_pending:
    try:
        st.metric("Predicții fără settlement final", history_results.pending_count())
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Istoricul nu poate fi citit: {exc}")

if update_clicked:
    with st.spinner("Preiau rezultatele oficiale din FootyStats…"):
        try:
            history_summary = history_results.update_results().to_dict()
            st.session_state.history_update_summary = history_summary
        except FootyStatsError as exc:
            st.error(exc.user_message)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Actualizarea rezultatelor a eșuat: {exc}")

if history_summary:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Predicții procesate", history_summary["pending_predictions"])
    m2.metric("Rezultate actualizate", history_summary["results_updated"])
    m3.metric("HIT", history_summary["hit"])
    m4.metric("MISS", history_summary["miss"])
    m5.metric("Rezultat indisponibil", history_summary["result_data_unavailable"])
    for err in history_summary.get("errors", []):
        st.warning(err)

with st.expander("Import verdicte Cornere din Excel recalculat"):
    st.write(
        "Cornere V14 este calculat de Microsoft Excel. Deschide fișierul "
        "`corners_*.xlsx` din export, salvează-l, apoi încarcă-l aici ca "
        "verdictele să fie înghețate în istoric."
    )
    uploaded = st.file_uploader("Workbook Cornere recalculat", type=["xlsx"])
    if uploaded is not None and st.button("Importă verdictele Cornere"):
        tmp_path = Path(settings.DATA_DIR) / "_import_corners.xlsx"
        try:
            tmp_path.write_bytes(uploaded.getbuffer())
            report = history_ingest.ingest_corners_workbook(tmp_path)
            st.success(
                f"Linii citite: {report['lines_read']} | înghețate: {report['frozen']} | "
                f"deja înghețate: {report['already_frozen']} | "
                f"necunoscute: {report['unknown_predictions']}"
            )
        except IntegrityError as exc:
            st.error(exc.message)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Importul a eșuat: {exc}")
        finally:
            tmp_path.unlink(missing_ok=True)

try:
    _, history_leagues = history_views.load_history(limit=1)
except Exception as exc:  # noqa: BLE001
    history_leagues = []
    st.warning(f"Istoricul nu poate fi citit: {exc}")

f1, f2, f3 = st.columns(3)
with f1:
    filter_models = st.multiselect(
        "Model",
        options=list(history_views.MODEL_LABELS.keys()),
        format_func=lambda x: history_views.MODEL_LABELS[x],
        key="history_filter_models",
    )
with f2:
    filter_leagues = st.multiselect("Ligă", options=history_leagues, key="history_filter_leagues")
with f3:
    filter_outcomes = st.multiselect(
        "Outcome", options=["HIT", "MISS"], key="history_filter_outcomes"
    )

try:
    history_rows, _ = history_views.load_history(
        model_keys=filter_models,
        leagues=filter_leagues,
        outcomes=filter_outcomes,
        timezone_name=timezone_name,
    )
except Exception as exc:  # noqa: BLE001
    history_rows = []
    st.warning(f"Istoricul nu poate fi citit: {exc}")

if history_rows:
    st.dataframe(
        history_rows,
        use_container_width=True,
        hide_index=True,
        column_order=list(history_rows[0].keys()),
    )
else:
    st.info("Încă nu există predicții în istoric pentru filtrele alese.")

with st.expander("Backtest (doar măsurare)"):
    try:
        totals = history_backtest.summary()
        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Predicții", totals["predictions"])
        b2.metric("Settled", totals["settled"])
        b3.metric("HIT / MISS", f"{totals['hit']} / {totals['miss']}")
        b4.metric(
            "Hit-rate",
            "—" if totals["hit_rate"] is None else f"{totals['hit_rate'] * 100:.1f}%",
        )
        for title, rows in (
            ("Pe model", history_backtest.by_model()),
            ("Pe Risk Level", history_backtest.by_risk_level()),
            ("Pe ligă", history_backtest.by_league()),
            ("Cornere: pe market/linie", history_backtest.by_corners_line()),
        ):
            st.markdown(f"**{title}**")
            if rows:
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else:
                st.caption("Fără settlement-uri încă.")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Backtest-ul nu poate fi calculat: {exc}")
