"""Pontifybet MVP — interfață Streamlit (o singură pagină)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Asigură importurile din rădăcina proiectului
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Streamlit poate păstra un src.api.client incomplet după un ImportError anterior.
_client_mod = sys.modules.get("src.api.client")
if _client_mod is not None and not hasattr(_client_mod, "FootyStatsClient"):
    sys.modules.pop("src.api.client", None)

import streamlit as st

from config.settings import DEFAULT_TIMEZONE, ensure_runtime_dirs
from src.api.client import FootyStatsError, current_season_id
from src.api.factory import get_client
import importlib

import src.pipeline as pipeline

from src.pipeline import MODEL_LABELS, cleanup_after_download, list_matches_for_filters, sort_listed_matches
from src.security.auth import verify_password

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
    import src.adapters.over05 as over05_adapter
    import src.engines.over05 as over05_pkg
    import src.engines.over05.engine as over05_engine
    import src.engines.over05.evaluator as over05_eval
    import src.engines.over05.inputs as over05_inputs
    import src.excel.generator as excel_generator
    import src.models.match_data as match_data

    importlib.reload(match_data)
    importlib.reload(fs_client)
    importlib.reload(fs_factory)
    importlib.reload(excel_generator)
    importlib.reload(over05_eval)
    importlib.reload(over05_inputs)
    importlib.reload(over05_engine)
    importlib.reload(over05_pkg)
    importlib.reload(over05_adapter)
    importlib.reload(pipeline)


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

# --- UI principal ---
st.title("Pontifybet")
st.write(
    "Selectează data, ligile și modelele, apasă **Listează meciurile**, "
    "bifează meciurile, apoi **Generează analiza**. "
    "Aplicația completează copii ale șabloanelor Excel — fără a modifica originalele."
)
st.info(
    "Over 0.5 este calculat în Python (V4 / selector v9): P0, Over 0.5, "
    "Confidence, Risk Score, G0 model, nivel și recomandare. "
    "Șansă Dublă și Cornere rămân calculate în Microsoft Excel, la deschiderea fișierului."
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
    st.subheader("Rezumat validare")

    def color_status(val: str) -> str:
        if val == "valid":
            return "valid (verde)"
        if val == "pending":
            return "pending (galben)"
        return "blocat (roșu)"

    over05_rows = [r for r in result["rows"] if r.get("model_id") == "over05"]
    if over05_rows and not any(r.get("recommendation") for r in over05_rows):
        st.warning(
            "Recomandarea Over 0.5 lipsește din acest rezumat. "
            "Apasă din nou **Generează analiza** ca motorul să recaluzeze meciurile."
        )
    if over05_rows:
        st.subheader("Recomandare finală Over 0.5")
        st.dataframe(
            [
                {
                    "Echipe": r["echipe"],
                    "Recomandare": r.get("recommendation") or "—",
                    "Nivel": r.get("risk_level") if r.get("risk_level") is not None else "—",
                    "G0 model": r.get("model_g0") or "—",
                    "Over 0.5": _fmt_prob(r.get("p_over")) or "—",
                    "P0": _fmt_prob(r.get("p0_recalibrated")) or "—",
                    "Confidence": _fmt_score(r.get("confidence")) or "—",
                    "Risk Score": _fmt_score(r.get("risk_score")) or "—",
                }
                for r in over05_rows
            ],
            use_container_width=True,
            hide_index=True,
        )

    validation_rows = []
    for r in result["rows"]:
        validation_rows.append(
            {
                "Echipe": r["echipe"],
                "Model": r["model"],
                "Recomandare (HK)": r.get("recommendation") or "",
                "Nivel (HH)": r.get("risk_level") if r.get("risk_level") is not None else "",
                "G0 model (HG)": r.get("model_g0") or "",
                "Over 0.5 (GP)": _fmt_prob(r.get("p_over")),
                "P0 (GL)": _fmt_prob(r.get("p0_recalibrated")),
                "Confidence (GT)": _fmt_score(r.get("confidence")),
                "Risk Score (HE)": _fmt_score(r.get("risk_score")),
                "Ligă": r["liga"],
                "Oră București": r["ora_bucuresti"],
                "Data Status": color_status(r["data_status"]),
                "G0 validare": r["g0"],
                "Motiv blocare": r["motiv"],
            }
        )
    st.dataframe(validation_rows, use_container_width=True, hide_index=True)

    if result.get("errors"):
        for err in result["errors"]:
            st.error(err)

    zip_path = Path(result["zip_path"])
    if zip_path.exists():
        data = zip_path.read_bytes()
        clicked = st.download_button(
            label="Descarcă fișierele Excel",
            data=data,
            file_name=zip_path.name,
            mime="application/zip",
        )
        st.caption(
            f"Fișiere generate: {len(result.get('generated', []))} | Raport inclus în ZIP."
        )
        if clicked:
            cleanup_after_download(result["run_dir"])
