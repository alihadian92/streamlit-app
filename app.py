# magickal_record_app.py
"""Magickal Record – Streamlit Web-App (v4.1 hot-fix)
====================================================
• Fixes SyntaxError in `_manage_generic` (missing parenthesis)
• Restores edit form helper & main navigation footer
• Adds quick SQLite backup button in sidebar
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sqlalchemy import Column, Date, Integer, String, Text, Time, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ╭─────────────────────────────────────────────────╮
# │ 🔐  OPTIONAL PASSWORD                          │
# ╰─────────────────────────────────────────────────╯
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")
if APP_PASSWORD and st.session_state.get("auth_ok") is not True:
    if st.text_input("Password", type="password") != APP_PASSWORD:
        st.stop()
    st.session_state["auth_ok"] = True

# ╭─────────────────────────────────────────────────╮
# │ 💾  DATABASE                                   │
# ╰─────────────────────────────────────────────────╯
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

# ╭─────────────────────────────────────────────────╮
# │ 🌙  MOON-PHASE                                  │
# ╰─────────────────────────────────────────────────╯
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
    age = ephem.Moon(d).moon_phase * 29.53 if ephem else ((d - dt.date(2000, 1, 6)).days % 29.53)
    return min(_PHASES, key=lambda p: abs(p[1] - age))[0]

# ╭─────────────────────────────────────────────────╮
# │ ✨  DATA HELPERS                                │
# ╰─────────────────────────────────────────────────╯

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

# ╭─────────────────────────────────────────────────╮
# │ 🔧  UTILITIES                                  │
# ╰─────────────────────────────────────────────────╯

def _calc_streak(dates: list[dt.date]) -> int:
    dates = sorted(set(dates))
    streak = cur = 0
    prev: dt.date | None = None
    for d in dates:
        if prev and (d - prev).days == 1:
            cur += 1
        else:
            cur = 1
        streak = max(streak, cur)
        prev = d
    return streak


def _split_tags(series: pd.Series) -> list[str]:
    tags: list[str] = []
    for t in series.dropna():
        tags.extend([x.strip() for x in t.split(",") if x.strip()])
    return tags

# ╭─────────────────────────────────────────────────╮
# │ 🖊️  RITUAL PAGES                               │
# ╰─────────────────────────────────────────────────╯
R_PRACTICES = ["LBRP", "Middle Pillar", "Meditation", "Resh", "Eucharist", "Yoga", "Other"]


def ritual_new():
    st.subheader("📝 New Ritual Entry")
    c1, c2 = st.columns(2)
    date = c1.date_input("Date", value=dt.date.today())
    stime = c1.time_input("Start", dt.datetime.now().time())
    etime = c2.time_input("End")
    ptype = c2.selectbox("Practice", R_PRACTICES)
    pre = st.text_area("Pre-Feeling")
    exp = st.text_area("Experience")
    ins = st.text_area("Insights")
    tags = st.text_input("Tags")
    if st.button("Save"):
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
        st.success("Saved")
        st.balloons()


def ritual_browse():
    st.subheader("📚 Browse Rituals")
    stext = st.text_input("Search")
    df = _load(Ritual)
    if stext:
        df = df[df.apply(lambda r: stext.lower() in str(r).lower(), axis=1)]
    if df.empty:
        st.info("No results")
        return
    _table(df, "rituals.csv")


def ritual_manage():
    st.subheader("🛠️ Manage Rituals")
    _manage_generic(Ritual, R_PRACTICES)

# ╭─────────────────────────────────────────────────╮
# │ 🖊️  DREAM PAGES                                │
# ╰─────────────────────────────────────────────────╯
D_EMOTIONS = ["Calm", "Fear", "Joy", "Sadness", "Lucid", "Other"]


def dream_new():
    st.subheader("🌙 New Dream Entry")
    date = st.date_input("Date", value=dt.date.today())
    txt = st.text_area("Dream narrative")
    emos = st.multiselect("Emotions", D_EMOTIONS)
    ins = st.text_area("Insights")
    tags = st.text_input("Tags")
    if st.button("Save Dream"):
        _save(Dream, {
            "date": date,
            "dream_text": txt,
            "emotions": ", ".join(emos),
            "insights": ins,
            "tags": tags,
        })
        st.success("Saved dream")
        st.balloons()


def dream_browse():
    st.subheader("🔍 Browse Dreams")
    stext = st.text_input("Search dreams")
    df = _load(Dream)
    if stext:
        df = df[df.apply(lambda r: stext.lower() in str(r).lower(), axis=1)]
    if df.empty:
        st.info("No dreams")
        return
    _table(df, "dreams.csv")


def dream_manage():
    st.subheader("🛠️ Manage Dreams")
    _manage_generic(Dream, [])

# ╭─────────────────────────────────────────────────╮
# │ 📊  DASHBOARD                                   │
# ╰─────────────────────────────────────────────────╯

def dashboard():
    st.title("📊 Dashboard")
    r_df, d_df = _load(Ritual), _load(Dream)
    col1, col2 = st.columns(2)
    with col1:
        st.header("Rituals")
        st.metric("Total", len(r_df))
        if not r_df.empty:
            st.pyplot(_pie(r_df.practice_type.value_counts()))
            st.metric("Longest streak", _calc_streak(list(r_df.date)))
    with col2:
        st.header("Dreams")
        st.metric("Total", len(d_df))
        if not d_df.empty:
            emo_counts = pd.Series(_split_tags(d_df.emotions)).value_counts()
            st.pyplot(_pie(emo_counts))

# ╭─────────────────────────────────────────────────╮
# │ 🔧  SHARED COMPONENTS                           │
# ╰─────────────────────────────────────────────────╯

def _pie(series: pd.Series):
    fig, ax = plt.subplots()
    ax.pie(series, labels=series.index, autopct="%1.0f%%")
    return fig


def _table(df: pd.DataFrame, fname: str):
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
    st.download_button("Export CSV", df.to_csv(index=False), file_name=fname)


def _manage_generic(model, ptypes):
    df = _load(model)
    if df.empty:
        st.info("No records yet")
        return
    st.dataframe(df, use_container_width=True)
    sel_id = st.selectbox("Select ID", df["id"].tolist())
    mode = st.radio("Action", ["Edit", "Delete"], horizontal=True)
    if mode == "Delete":
        if st.button("Delete", type="secondary"):
            _delete(model, sel_id)
            st.success("Deleted")
            st.experimental_rerun()
    else:
        record = df[df["id"] == sel_id].iloc[0]
        _edit_form(model, record, ptypes)


def _edit_form(model, row: pd.Series, ptypes):
    with st.form("edit_form"):
        if model is Ritual:
            c1, c2 = st.columns(2)
            date = c1.date_input("Date", value=row.date)
            stime = c1.time_input("Start", row.start_time)
            etime = c2.time_input("End", row.end_time)
            ptype = c2.selectbox("Practice", ptypes, index=ptypes.index(row.practice_type))
            pre = st.text_area("Pre", row.pre_feeling or "")
            exp = st.text_area("Experience", row.experience_notes or "")
            ins = st.text_area("Insights", row.insights or "")
            tags = st.text_input("Tags", row.tags or "")
            if st.form_submit_button("Save"):
                _update(model, row.id, {
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
                st.success("Updated")
                st.experimental_rerun()
        else:  # Dream
            date = st.date_input("Date", value=row.date)
            txt = st.text_area("Dream", row.dream_text or "")
            emo = st.text_input("Emotions", row.emotions or "")
            ins = st.text_area("Insights", row.insights or "")
            tags = st.text_input("Tags", row.tags or "")
            if st.form_submit_button("Save"):
                _update(model, row.id, {
                    "date": date,
                    "dream_text": txt,
                    "emotions": emo,
                    "insights": ins,
                    "tags": tags,
                })
                st.success("Updated")
                st.experimental_rerun()

# ╭─────────────────────────────────────────────────╮
# │ 🚀  MAIN                                        │
# ╰─────────────────────────────────────────────────╯

def main():
    st.set_page_config("Magickal Record", page_icon="✨", layout="wide")
    st.sidebar.title("Magickal Record")
    # Backup button
    with open(DB_PATH, "rb") as dbf:
        st.sidebar.download_button("⏬ Backup DB", dbf.read(), file_name="magickal_record.db")

    section = st.sidebar.radio("Section", ["Rituals", "Dreams", "Dashboard"])
    if section == "Rituals":
        page = st.sidebar.radio("Page", ["New", "Browse", "Manage"])
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
