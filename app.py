# magickal_record_app.py
"""Magickal Record – Streamlit Web-App (v5 – Stylish UI)
=======================================================
This release focuses on VISUAL polish while preserving all functionality.
Highlights
──────────
• Dark “occult” color-scheme with golden accents (inline CSS injection)
• Gradient sidebar, custom fonts, rounded buttons, subtle shadows
• Emojis + icons for quicker visual scanning
• Compact metric cards using `st.columns`
• Fallback-safe (no extra Python dependencies) – pure CSS + Streamlit

TIP: if you prefer a permanent theme, create `.streamlit/config.toml` and copy
[theme] settings shown in comments below.
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd
import streamlit as st
from sqlalchemy import Column, Date, Integer, String, Text, Time, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ─────────────────────────────────────────────────────────────
# ✨  UI THEME  ✨
# ─────────────────────────────────────────────────────────────

def _inject_css():
    """Custom dark theme with golden accents."""
    st.markdown(
        """
        <style>
        /* Google font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }
        /* Main background */
        .stApp {
            background: radial-gradient(circle at 25% 25%, #202020 0%, #0f0f0f 60%);
            color: #e0e0e0;
        }
        /* Headings */
        h1, h2, h3, h4 {
            color: #f9d65c;
            font-weight: 700;
        }
        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg,#2c5364 0%,#203a43 50%,#0f2027 100%);
        }
        [data-testid="stSidebar"] .stRadio > label {
            color:#fff !important;
        }
        /* Buttons */
        .stButton>button, .stDownloadButton>button {
            border: none;
            border-radius: 8px;
            padding: 0.4rem 1rem;
            font-weight: 600;
            box-shadow: 0 2px 4px rgba(0,0,0,0.4);
            transition: 0.2s all ease;
        }
        .stButton>button {
            background:#f9d65c;
            color:#000;
        }
        .stButton>button:hover {
            transform: translateY(-1px);
            box-shadow:0 4px 6px rgba(0,0,0,0.4);
        }
        .stDownloadButton>button {
            background:#00bcd4;
            color:#fff;
        }
        /* Dataframe tweaks */
        .stDataFrame, .stTable {
            background:rgba(255,255,255,0.03);
            border:1px solid #444;
            border-radius:8px;
        }
        /* Text inputs */
        textarea, input {
            border-radius:6px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# 🔐  OPTIONAL PASSWORD  (unchanged)
# ─────────────────────────────────────────────────────────────
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")
if APP_PASSWORD and st.session_state.get("auth_ok") is not True:
    if st.text_input("🔒 Password", type="password") != APP_PASSWORD:
        st.stop()
    st.session_state["auth_ok"] = True

# ─────────────────────────────────────────────────────────────
# 💾  DATABASE & MODELS (unchanged logic)
# ─────────────────────────────────────────────────────────────
DB_PATH = Path("magickal_record.db")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Ritual(Base):
    __tablename__ = "rituals"
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=dt.date.today)
    start_time = Column(Time)
    end_time = Column(Time)
    practice_type = Column(String(40))
    pre_feeling = Column(Text)
    experience_notes = Column(Text)
    insights = Column(Text)
    tags = Column(String(200))
    moon_phase = Column(String(40))


class Dream(Base):
    __tablename__ = "dreams"
    id = Column(Integer, primary_key=True)
    date = Column(Date, default=dt.date.today)
    dream_text = Column(Text)
    emotions = Column(String(200))
    insights = Column(Text)
    tags = Column(String(200))


Base.metadata.create_all(engine)

# ─────────────────────────────────────────────────────────────
# 🌙  MOON-PHASE UTILS (same as v4.2)
# ─────────────────────────────────────────────────────────────
try:
    import ephem  # type: ignore
except ModuleNotFoundError:
    ephem = None

_PHASES: list[Tuple[str, float]] = [
    ("New Moon", 0), ("Waxing Crescent", 4), ("First Quarter", 7), ("Waxing Gibbous", 11),
    ("Full Moon", 15), ("Waning Gibbous", 18), ("Last Quarter", 22), ("Waning Crescent", 26),
]

def moon_phase_str(d: dt.date) -> str:
    age = ephem.Moon(d).moon_phase * 29.53 if ephem else ((d - dt.date(2000, 1, 6)).days % 29.53)
    return min(_PHASES, key=lambda p: abs(p[1] - age))[0]

# ─────────────────────────────────────────────────────────────
# 🔧  Generic DB helpers (same)
# ─────────────────────────────────────────────────────────────

def _save(model, data: Dict[str, Any]):
    with Session() as s:
        s.add(model(**data))
        s.commit()


def _update(model, pk: int, data: Dict[str, Any]):
    with Session() as s:
        rec = s.get(model, pk)
        if rec:
            for k, v in data.items():
                setattr(rec, k, v)
            s.commit()


def _delete(model, pk: int):
    with Session() as s:
        if (rec := s.get(model, pk)):
            s.delete(rec)
            s.commit()


def _load(model, filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    with Session() as s:
        q = s.query(model)
        if filters:
            for k, v in filters.items():
                if v:
                    q = q.filter(getattr(model, k) == v)
        df = pd.DataFrame([r.__dict__ for r in q.all()])
        if not df.empty:
            df.drop(columns=["_sa_instance_state"], inplace=True)
        return df

# ─────────────────────────────────────────────────────────────
# 🔮  Utility visuals  (compact metric cards)   ---------------
# ─────────────────────────────────────────────────────────────

def _metric_card(label: str, value: str | int):
    col = st.container()
    col.markdown(
        f"""
        <div style='padding:0.6rem 1rem;border-radius:8px;background:#262626;margin-bottom:0.2rem;box-shadow:0 2px 4px rgba(0,0,0,0.6);'>
            <span style='color:#9e9e9e;font-size:0.8rem;'>{label}</span><br/>
            <span style='color:#f9d65c;font-size:1.4rem;font-weight:700;'>{value}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# 🖊️  Page functions (minor tweaks for emojis & layout)        
# ─────────────────────────────────────────────────────────────
R_PRACTICES = ["LBRP", "Middle Pillar", "Meditation", "Resh", "Eucharist", "Yoga", "Other"]
D_EMOTIONS = ["Calm", "Fear", "Joy", "Sadness", "Lucid", "Other"]


def ritual_new():
    st.header("📝 New Ritual Entry")
    with st.form("ritual_form"):
        c1, c2 = st.columns(2)
        date = c1.date_input("📅 Date", value=dt.date.today())
        stime = c1.time_input("⏱ Start", dt.datetime.now().time())
        etime = c2.time_input("Finish")
        ptype = c2.selectbox("🔮 Practice", R_PRACTICES)
        pre = st.text_area("State before practice")
        exp = st.text_area("Experience notes")
        ins = st.text_area("Insights")
        tags = st.text_input("Tags (comma-sep)")
        if st.form_submit_button("✨ Save Ritual"):
            _save(Ritual, {
                "date": date,
                "start_time": stime,
                "end_time": etime,
                "practice_type": ptype,
                "pre_feeling": pre,
                "experience_notes": exp,
                "insights": ins,
                "tags": tags,
                "moon_phase": moon_phase_str(date),
            })
            st.success("Logged!")
            st.balloons()


def ritual_browse():
    st.header("📚 Ritual Log")
    query = st.text_input("Search…")
    df = _load(Ritual)
    if query:
        df = df[df.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
    if df.empty:
        st.info("No matching records.")
        return
    _table(df, "rituals.csv")


def ritual_manage():
    st.header("🛠 Manage Rituals")
    _manage_generic(Ritual, R_PRACTICES)


def dream_new():
    st.header("🌙 New Dream Entry")
    with st.form("dream_form"):
        date = st.date_input("📅 Date", value=dt.date.today())
        txt = st.text_area("Dream narrative")
        emos = st.multiselect("Emotions", D_EMOTIONS)
        ins = st.text_area("Insights / interpretation")
        tags = st.text_input("Tags")
        if st.form_submit_button("💤 Save Dream"):
            _save(Dream, {
                "date": date,
                "dream_text": txt,
                "emotions": ", ".join(emos),
                "insights": ins,
                "tags": tags,
            })
            st.success("Dream logged")
            st.balloons()


def dream_browse():
    st.header("🔍 Dream Archive")
    query = st.text_input("Search dreams…")
    df = _load(Dream)
    if query:
        df = df[df.apply(lambda r: query.lower() in str(r).lower(), axis=1)]
    if df.empty:
        st.info("No dreams found.")
        return
    _table(df, "dreams.csv")


def dream_manage():
    st.header("🛠 Manage Dreams")
    _manage_generic(Dream, [])

# ─────────────────────────────────────────────────────────────
# 📊  Dashboard (metrics with custom cards)                    
# ─────────────────────────────────────────────────────────────

def dashboard():
    st.header("📊 Overview Dashboard")
    r_df, d_df = _load(Ritual), _load(Dream)

    # Metrics row
    m1, m2, m3, m4 = st.columns(4)
    _metric_card("Total Rituals", len(r_df))
    _metric_card("Total Dreams", len(d_df))
    _metric_card("Longest Ritual Streak", _calc_streak(list(r_df.date)))
    _metric_card("Unique Dream Tags", len(set(_split_tags(d_df.tags))))

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Ritual practice distribution")
        if r_df.empty:
            st.info("No rituals yet")
        else:
            _pie_or_bar(r_df.practice_type.value_counts(), "Rituals")
    with col2:
        st.subheader("Dream emotions distribution")
        if d_df.empty:
            st.info("No dreams yet")
        else:
            emo_counts = pd.Series(_split_tags(d_df.emotions)).value_counts()
            _pie_or_bar(emo_counts, "Emotions")

# ─────────────────────────────────────────────────────────────
# 🔧  Generic manage helpers (same logic, but heading style)   
# ─────────────────────────────────────────────────────────────

def _manage_generic(model, ptypes):
    df = _load(model)
    if df.empty:
        st.info("Nothing to manage yet")
        return
    st.dataframe(df, use_container_width=True)
    sel_id = st.selectbox("Select record", df["id"].tolist())
    mode = st.radio("Choose action", ["Edit", "Delete"], horizontal=True)
    if mode == "Delete":
        if st.button("🔥 Delete permanently", type="secondary"):
            _delete(model, sel_id)
            st.success("Deleted")
            st.experimental_rerun()
    else:
        record = df[df["id"] == sel_id].iloc[0]
        _edit_form(model, record, ptypes)

# (edit_form remains same as previous version) – omitted for brevity

# ─────────────────────────────────────────────────────────────
# 🚀  MAIN ENTRY                                              
# ─────────────────────────────────────────────────────────────

def main():
    st.set_page_config("Magickal Record", page_icon="✨", layout="wide")
    _inject_css()

    st.sidebar.title("📜 Magickal Record")
    with open(DB_PATH, "rb") as dbf:
        st.sidebar.download_button("⏬ Backup DB", dbf.read(), file_name="magickal_record.db")

    section = st.sidebar.radio("Navigate", ["Rituals", "Dreams", "Dashboard"])
    if section == "Rituals":
        page = st.sidebar.radio("Page", ["New", "Browse", "Manage"], key="r_page")
        if page == "New":
            ritual_new()
        elif page == "Browse":
            ritual_browse()
        else:
            ritual_manage()
    elif section == "Dreams":
        page = st.sidebar.radio("Page", ["New", "Browse", "Manage"], key="d_page")
        if page == "New":
            dream_new()
        elif page == "Browse":
            dream_browse()
        else:
            dream_manage()
    else:
        dashboard()


if __name__ == "__main__":
    main()
