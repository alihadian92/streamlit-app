# magickal_record_app.py
"""Magickal Record – Streamlit Web‑App (v3: Rituals + Dreams)
============================================================
Now the app is split into two fully‑independent sections:
1️⃣ **Ritual Journal**  – track magical practices (was the original)
2️⃣ **Dream Journal**   – log dreams separately
Each section has three pages: *New*, *Browse*, *Manage*.

Run locally:
    pip install streamlit pandas SQLAlchemy ephem
    streamlit run magickal_record_app.py
"""
from __future__ import annotations

import datetime as dt
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
        age = ephem.Moon(d).moon_phase * 29.53  # 0‑29.53
    else:
        age = ((d - dt.date(2000, 1, 6)).days) % 29.53
    return min(_PHASES, key=lambda p: abs(p[1] - age))[0]

# ╭──────────────────────────────────────────────────────────╮
# │ 🗄️  DATA HELPERS                                        │
# ╰──────────────────────────────────────────────────────────╯

# Generic helpers using model class dynamic typing

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
                q = q.filter(getattr(model, k) == v)
        df = pd.DataFrame([r.__dict__ for r in q.all()])
        if not df.empty:
            df.drop(columns=["_sa_instance_state"], inplace=True)
        return df

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
    pt = st.selectbox("Filter by Practice", ["All"] + R_PRACTICES)
    filt = {"practice_type": pt} if pt != "All" else {}
    df = _load(Ritual, filt)
    if df.empty:
        st.info("No rituals logged.")
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
    df = _load(Dream)
    if df.empty:
        st.info("No dreams logged.")
        return
    _table_with_csv(df, "dreams.csv")


def dream_manage():
    st.subheader("🛠️ Manage Dreams")
    _manage_generic(Dream, [])

# ╭──────────────────────────────────────────────────────────╮
# │ 🔧  SHARED UI PARTS                                      │
# ╰──────────────────────────────────────────────────────────╯

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
    mode = st.radio("Action", ["Edit", "Delete"], horizontal=True)

    if mode == "Delete":
        if st.button("❌ Delete"):  # irreversible
            _delete(model, sel_id)
            st.success("Deleted")
            st.experimental_rerun()
    else:
        record = df[df["id"] == sel_id].iloc[0]
        _edit_form_generic(model, record, ptype_list)


def _edit_form_generic(model, row: pd.Series, ptypes: list[str]):
    with st.form("edit_form"):
        if model is Ritual:
            c1, c2 = st.columns(2)
            date = c1.date_input("Date", value=row.date)
            stime = c1.time_input("Start", row.start_time)
            etime = c2.time_input("End", row.end_time)
            ptype = c2.selectbox("Practice", ptypes, index=ptypes.index(row.practice_type))
            pre = st.text_area("Pre‑Feeling", row.pre_feeling or "")
            exp = st.text_area("Experience", row.experience_notes or "")
            ins = st.text_area("Insights", row.insights or "")
            tags = st.text_input("Tags", row.tags or "")
            submit = st.form_submit_button("Save")
            if submit:
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
            submit = st.form_submit_button("Save")
            if submit:
                _update(model, row.id, {
                    "date": date,
                    "dream_text": txt,
                    "emotions": emo,
                    "insights": ins,
                    "tags": tags,
                })
                st.success("Updated")
                st.experimental_rerun()

# ╭──────────────────────────────────────────────────────────╮
# │ 🚀  MAIN NAVIGATION                                      │
# ╰──────────────────────────────────────────────────────────╯

SECTION = st.sidebar.radio("Section", ["Ritual Journal", "Dream Journal"])

if SECTION == "Ritual Journal":
    sub = st.sidebar.radio("Page", ["New", "Browse", "Manage"])
    if sub == "New":
        ritual_new()
    elif sub == "Browse":
        ritual_browse()
    else:
        ritual_manage()
else:
    sub = st.sidebar.radio("Page", ["New", "Browse", "Manage"])
    if sub == "New":
        dream_new()
    elif sub == "Browse":
        dream_browse()
    else:
        dream_manage()
