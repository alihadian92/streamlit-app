# magickal_record_app.py
"""Magickal Record – Streamlit Web‑App (v4: Dashboard & Advanced Filters)
=======================================================================
**What's new in v4?**
1. 📊 **Dashboard** page – summary stats & charts for Rituals and Dreams.
2. 🔎 Full‑text **search** + **tag filter** in Browse pages.
3. 📈 Charts:
   • Ritual practice distribution pie‑chart
   • Ritual streak (consecutive days) bar‑chart
   • Dream emotions pie‑chart
4. 💾 **Download backup** – one‑click SQLite export.
5. Minor UI polish (dark/light theme toggle via Streamlit built‑in).

Run locally:
    pip install streamlit pandas SQLAlchemy ephem
    streamlit run magickal_record_app.py
"""
from __future__ import annotations

import datetime as dt
import io
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd
import streamlit as st
from sqlalchemy import Column, Date, Integer, String, Text, Time, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ╭──────────────────────────────────────────────────────────╮
# │ 🔐  OPTIONAL PASSWORD                                   │
# ╰──────────────────────────────────────────────────────────╯
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")
if APP_PASSWORD and st.session_state.get("auth_ok") is not True:
    if st.text_input("Password", type="password") != APP_PASSWORD:
        st.stop()
    st.session_state["auth_ok"] = True

# ╭──────────────────────────────────────────────────────────╮
# │ 💾  DATABASE & MODELS                                   │
# ╰──────────────────────────────────────────────────────────╯
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

# ╭──────────────────────────────────────────────────────────╮
# │ 🌙  MOON‑PHASE (for Rituals)                            │
# ╰──────────────────────────────────────────────────────────╯
try:
    import ephem  # type: ignore
except ModuleNotFoundError:
    ephem = None

_PHASES: list[Tuple[str, float]] = [
    ("New Moon", 0),
    ("Waxing Crescent", 4),
    ("First Quarter", 7),
    ("Waxing Gibbous", 11),
    ("Full Moon", 15),
    ("Waning Gibbous", 18),
    ("Last Quarter", 22),
    ("Waning Crescent", 26),
]


def moon_phase_str(d: dt.date) -> str:
    if ephem is not None:
        age = ephem.Moon(d).moon_phase * 29.53
    else:
        age = ((d - dt.date(2000, 1, 6)).days) % 29.53
    return min(_PHASES, key=lambda p: abs(p[1] - age))[0]

# ╭──────────────────────────────────────────────────────────╮
# │ 🗄️  DATA HELPERS                                        │
# ╰──────────────────────────────────────────────────────────╯

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
        rec = s.get(model, pk)
        if rec:
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

# ╭──────────────────────────────────────────────────────────╮
# │ 🔧  UTIL – STREAKS / TAG SPLIT                          │
# ╰──────────────────────────────────────────────────────────╯

def _calc_streak(dates: list[dt.date]) -> int:
    if not dates:
        return 0
    dates = sorted(set(dates))
    streak = current = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current += 1
            streak = max(streak, current)
        else:
            current = 1
    return streak


def _split_tags(series: pd.Series) -> list[str]:
    tags: list[str] = []
    for t in series.dropna():
        tags.extend([x.strip() for x in t.split(",") if x.strip()])
    return tags

# ╭──────────────────────────────────────────────────────────╮
# │ 🖊️  UI –  RITUAL SECTION                                │
# ╰──────────────────────────────────────────────────────────╯
R_PRACTICES = ["LBRP", "Middle Pillar", "Meditation", "Resh", "Eucharist", "Yoga", "Other"]


def ritual_new():
    st.subheader("📝 New Ritual Entry")
    c1, c2 = st.columns(2)
    date = c1.date_input("Date", value=dt.date.today(), key="r_date")
    stime = c1.time_input("Start", value=dt.datetime.now().time(), key="r_start")
    etime = c2.time_input("End", key="r_end")
    ptype = c2.selectbox("Practice Type", R_PRACTICES, key="r_ptype")
    pre = st.text_area("Pre‑Feeling", key="r_pre")
    exp = st.text_area("Experience Notes", key="r_exp")
    ins = st.text_area("Insights", key="r_ins")
    tags = st.text_input("Tags", key="r_tags")
    if st.button("💾 Save Ritual"):
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
        st.success("Ritual saved ✨")
        st.balloons()


def ritual_browse():
    st.subheader("📚 Browse Rituals")
    col1, col2 = st.columns([2, 1])
    search = col1.text_input("Search text or tags")
    pfilter = col2.selectbox("Practice", ["All"] + R_PRACTICES)
    df = _load(Ritual)

    if pfilter != "All":
        df = df[df.practice_type == pfilter]
    if search:
        df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)]

    if df.empty:
        st.info("No rituals match.")
        return
    _table_with_csv(df, "rituals.csv")


def ritual_manage():
    st.subheader("🛠️ Manage Rituals")
    _manage_generic(Ritual, R_PRACTICES)

# ╭──────────────────────────────────────────────────────────╮
# │ 🖊️  UI –  DREAM SECTION                                 │
# ╰──────────────────────────────────────────────────────────╯
D_EMOTIONS = ["Calm", "Fear", "Joy", "Sadness", "Lucid", "Other"]


def dream_new():
    st.subheader("🌙 New Dream Entry")
    date = st.date_input("Date", value=dt.date.today(), key="d_date")
    dream_txt = st.text_area("Dream narrative", key="d_txt")
    emotions = st.multiselect("Emotions", D_EMOTIONS, key="d_emotions")
    ins = st.text_area("Insights / Interpretation", key="d_ins")
    tags = st.text_input("Tags", key="d_tags")
    if st.button("💾 Save Dream"):
        _save(Dream, {
            "date": date,
            "dream_text": dream_txt,
            "emotions": ", ".join(emotions),
            "insights": ins,
            "tags": tags,
        })
        st.success("Dream saved 🌠")
        st.balloons()


def dream_browse():
    st.subheader("🔍 Browse Dreams")
    col1, col2 = st.columns([2, 1])
    search = col1.text_input("Search text or tags", key="d_search")
    df = _load(Dream)
    if search:
        df = df[df.apply(lambda r: search.lower() in str(r).lower(), axis=1)]
    if df.empty:
        st.info("No dreams match.")
        return
    _table_with_csv(df, "dreams.csv")


def dream_manage():
    st.subheader("🛠️ Manage Dreams")
    _manage_generic(Dream, [])

# ╭──────────────────────────────────────────────────────────╮
# │ 📊  DASHBOARD                                           │
# ╰──────────────────────────────────────────────────────────╯

def dashboard():
    st.title("📊 Dashboard")
    r_df, d_df = _load(Ritual), _load(Dream)

    col1, col2 = st.columns(2)

    # Ritual stats
    with col1:
        st.header("Rituals")
        st.metric("Total rituals", len(r_df))
        if not r_df.empty:
            freq = r_df.practice_type.value_counts()
            st.subheader("By practice type")
            st.pyplot(_pie(freq))
            streak = _calc_streak(list(r_df.date))
            st.metric("Longest streak (days)", streak)

    # Dream stats
    with col2:
        st.header("Dreams")
        st.metric("Total dreams", len(d_df))
        if not d_df.empty:
            emos = pd.Series(_split_tags(d_df.emotions))
            emo_counts = emos.value_counts()
            st.subheader("Emotions")
            st.pyplot(_pie(emo_counts))


# ╭──────────────────────────────────────────────────────────╮
# │ 🔧  SHARED UI PARTS                                      │
# ╰──────────────────────────────────────────────────────────╯
import matplotlib.pyplot as plt


def _pie(series: pd.Series):
    fig, ax = plt.subplots()
    ax.pie(series, labels=series.index, autopct="%1.0f%%")
    return fig


def _table_with_csv(df: pd.DataFrame, fname: str):
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
    st.download_button("⬇️ Export CSV", df.to_csv(index=False), fname)


def _manage_generic(model, ptype_list):
    df = _load(model)
    if df.empty:
        st.info("Nothing to manage yet.")
        return
    st.dataframe(df, use_container_width=True)
    sel_id = st.selectbox("Select ID", df["id"].tolist())
    mode = st.radio("Action", ["Edit", "Delete"], horizontal
