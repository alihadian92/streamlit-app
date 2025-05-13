# magickal_record_app.py
"""Magickal Record – Streamlit Web‑App (Enhanced v1)
===================================================
Features added compared to the ultra‑minimal prototype:
• SQLite database (no more CSV race‑conditions)
• Rich fields (start/end time, feelings, insights, tags…)
• Moon‑phase auto‑fill (uses `ephem` if installed → graceful fallback)
• Browse page with filters + daily‑count chart + export CSV
• Basic app‑level password (optional; see `APP_PASSWORD` secrets)

Run locally:
    pip install streamlit pandas SQLAlchemy ephem
    streamlit run magickal_record_app.py
"""
from __future__ import annotations

import datetime as dt
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from sqlalchemy import Column, Date, Integer, String, Text, Time, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ─────────────────────────────────────────────────────────────
# 🔐 OPTIONAL SIMPLE PASSWORD --------------------------------
# ─────────────────────────────────────────────────────────────
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")  # add in Streamlit Cloud Secrets
if APP_PASSWORD:
    passwd_ok = st.text_input("Password", type="password")
    if passwd_ok != APP_PASSWORD:
        st.stop()

# ─────────────────────────────────────────────────────────────
# 💾 DATABASE (SQLite) ---------------------------------------
# ─────────────────────────────────────────────────────────────
DB_PATH = Path("magickal_record.db")
engine = create_engine(f"sqlite:///{DB_PATH}", future=True, echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Entry(Base):
    __tablename__ = "entries"
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


Base.metadata.create_all(engine)

# ─────────────────────────────────────────────────────────────
# 🌙 MOON‑PHASE UTILS ----------------------------------------
# ─────────────────────────────────────────────────────────────
try:
    import ephem  # type: ignore
except ModuleNotFoundError:
    ephem = None  # fallback later

_PHASES: list[tuple[str, float]] = [
    ("New Moon", 0),
    ("Waxing Crescent", 3.5),
    ("First Quarter", 7),
    ("Waxing Gibbous", 11),
    ("Full Moon", 14.5),
    ("Waning Gibbous", 18),
    ("Last Quarter", 22),
    ("Waning Crescent", 26),
]


def moon_phase_str(date_obj: dt.date) -> str:
    """Return nearest named moon phase for given date."""
    if ephem is not None:
        moon = ephem.Moon(date_obj)
        age = moon.moon_phase * 29.53  # 0‑29.53 days
    else:
        # fallback: average lunation 29.53 days since a reference new moon
        ref_new = dt.date(2000, 1, 6)  # known new moon
        age = (date_obj - ref_new).days % 29.53
    return min(_PHASES, key=lambda p: abs(p[1] - age))[0]

# ─────────────────────────────────────────────────────────────
# 📦 DATA HELPERS --------------------------------------------
# ─────────────────────────────────────────────────────────────

def save_entry(data: dict[str, Any]) -> None:
    with Session() as sess:
        sess.add(Entry(**data))
        sess.commit()


def load_entries(filters: dict[str, Any] | None = None) -> pd.DataFrame:
    with Session() as sess:
        query = sess.query(Entry)
        if filters:
            if pt := filters.get("practice_type"):
                query = query.filter(Entry.practice_type == pt)
            if s := filters.get("start"):
                query = query.filter(Entry.date >= s)
            if e := filters.get("end"):
                query = query.filter(Entry.date <= e)
        records = query.all()
        df = pd.DataFrame([r.__dict__ for r in records])
        if not df.empty:
            df.drop(columns=["_sa_instance_state"], inplace=True)
        return df

# ─────────────────────────────────────────────────────────────
# 🖊️ UI PAGES ------------------------------------------------
# ─────────────────────────────────────────────────────────────

def page_new_entry() -> None:
    st.header("📝 New Entry")
    col1, col2 = st.columns(2)

    date = col1.date_input("Date", value=dt.date.today())
    start_time = col1.time_input("Start Time", value=dt.datetime.now().time())
    end_time = col2.time_input("End Time")

    practice_type = col2.selectbox(
        "Practice Type",
        ["LBRP", "Middle Pillar", "Meditation", "Resh", "Eucharist", "Yoga", "Other"],
    )

    pre_feeling = st.text_area("Pre‑Feeling / Mindset")
    experience_notes = st.text_area("Experience During Practice")
    insights = st.text_area("Post‑Practice Insights")
    tags = st.text_input("Tags (comma‑separated)")

    if st.button("💾 Save Entry"):
        data = {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "practice_type": practice_type,
            "pre_feeling": pre_feeling,
            "experience_notes": experience_notes,
            "insights": insights,
            "tags": tags,
            "moon_phase": moon_phase_str(date),
        }
        save_entry(data)
        st.success("Saved ✨")
        st.balloons()


def page_browse() -> None:
    st.header("📚 Browse Entries")

    with st.expander("Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        ft = col1.selectbox(
            "Practice Type",
            ["All", "LBRP", "Middle Pillar", "Meditation", "Resh", "Eucharist", "Yoga", "Other"],
        )
        sdate = col2.date_input("From", value=None)
        edate = col3.date_input("To", value=None)

    filters: dict[str, Any] = {}
    if ft != "All":
        filters["practice_type"] = ft
    if sdate:
        filters["start"] = sdate
    if edate:
        filters["end"] = edate

    df = load_entries(filters)
    if df.empty:
        st.info("No entries found.")
        return

    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

    st.download_button("⬇️ Export CSV", df.to_csv(index=False), file_name="magickal_entries.csv")

    daily = df.groupby("date").size().reset_index(name="count").sort_values("date")
    st.subheader("Entry Count by Day")
    st.line_chart(daily.set_index("date"))

# ─────────────────────────────────────────────────────────────
# 🚀 MAIN -----------------------------------------------------
# ─────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config("Magickal Record", page_icon="✨", layout="wide")
    page = st.sidebar.radio("Menu", ["New Entry", "Browse"], index=0)
    if page == "New Entry":
        page_new_entry()
    else:
        page_browse()


if __name__ == "__main__":
    main()
