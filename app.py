# magickal_record_app.py
"""Streamlit Magickal Record Web‑App (Thelema)
------------------------------------------------
MVP for recording daily magical practices.
Run locally with:
    streamlit run magickal_record_app.py
Deploy on Streamlit Cloud (connect to GitHub).
"""

from __future__ import annotations
import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import Column, Date, Integer, String, Text, Time, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ─────────────────────────────────────────────────────────────
# 💾 DATABASE -------------------------------------------------
# ─────────────────────────────────────────────────────────────
DB_PATH = Path(__file__).with_name("magickal_record.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Entry(Base):
    __tablename__ = "entries"

    id = Column(Integer, primary_key=True)
    date = Column(Date, default=dt.date.today)
    start_time = Column(Time)
    end_time = Column(Time)
    practice_type = Column(String(50))
    pre_feeling = Column(Text)
    experience_notes = Column(Text)
    insights = Column(Text)
    tags = Column(String(200))
    moon_phase = Column(String(50))
    planetary_hour = Column(String(50))


Base.metadata.create_all(engine)

# ─────────────────────────────────────────────────────────────
# 🌙 ASTRONOMY UTILS  -----------------------------------------
# ─────────────────────────────────────────────────────────────
try:
    import ephem  # noqa: WPS433  (external import for astronomy)
except ModuleNotFoundError:
    ephem = None  # fallback to naïve calculation


def _moon_phase_simple(date_obj: dt.date) -> int:
    """Very rough moon‑age in days (0‑29) if **ephem** is unavailable."""
    known_new_moon = dt.date(2001, 1, 1)  # near new‑moon reference
    days_since = (date_obj - known_new_moon).days
    return days_since % 30  # 0‑29 approx.


def moon_phase_str(date_obj: dt.date) -> str:
    phases = [
        ("New Moon", 0),
        ("Waxing Crescent", 4),
        ("First Quarter", 7),
        ("Waxing Gibbous", 11),
        ("Full Moon", 15),
        ("Waning Gibbous", 18),
        ("Last Quarter", 22),
        ("Waning Crescent", 26),
    ]

    if ephem is not None:
        moon = ephem.Moon(date_obj)
        age = int(moon.moon_phase * 29.53)  # moon_phase→0‑1 fraction
    else:
        age = _moon_phase_simple(date_obj)

    label = min(phases, key=lambda p: abs(p[1] - age))[0]
    return label


# TODO: planetary‑hour calc (placeholder)
planetary_hour_placeholder = "☉"

# ─────────────────────────────────────────────────────────────
# 🚀 STREAMLIT APP -------------------------------------------
# ─────────────────────────────────────────────────────────────

def save_entry(data: dict) -> None:
    """Persist a single entry to the SQLite DB."""
    with SessionLocal() as db:
        db.add(Entry(**data))
        db.commit()


def load_entries(filters: dict | None = None) -> pd.DataFrame:
    """Return a DataFrame of entries filtered by optional criteria."""
    with SessionLocal() as db:
        query = db.query(Entry)
        if filters:
            if practice := filters.get("practice_type"):
                query = query.filter(Entry.practice_type == practice)
            if start := filters.get("start_date"):
                query = query.filter(Entry.date >= start)
            if end := filters.get("end_date"):
                query = query.filter(Entry.date <= end)
        rows = query.all()
        df = pd.DataFrame([r.__dict__ for r in rows])
        if not df.empty:
            df.drop(columns=["_sa_instance_state"], inplace=True)
        return df


def render_new_entry() -> None:
    st.header("📝 New Entry")

    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date", value=dt.date.today())
        start_time = col1.time_input("Start Time", value=dt.datetime.now().time())
        end_time = col2.time_input("End Time")

        practice_type = col2.selectbox(
            "Practice Type",
            [
                "LBRP",
                "Middle Pillar",
                "Meditation",
                "Resh",
                "Eucharist",
                "Yoga",
                "Other",
            ],
        )

        pre_feeling = st.text_area("Pre‑Feeling / Mindset")
        experience_notes = st.text_area("Experience During Practice")
        insights = st.text_area("Post‑Practice Insights / Analysis")
        tags = st.text_input("Tags (comma‑separated)")

        submitted = st.form_submit_button("💾 Save Entry")

    if submitted:
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
            "planetary_hour": planetary_hour_placeholder,
        }
        save_entry(data)
        st.success("Entry saved ✨")
        st.balloons()


def render_browse() -> None:
    st.header("📚 Browse Entries")

    with st.expander("Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        type_filter = col1.selectbox(
            "Practice Type",
            ["All", "LBRP", "Middle Pillar", "Meditation", "Resh", "Eucharist", "Yoga", "Other"],
        )
        start_date = col2.date_input("From", value=None)
        end_date = col3.date_input("To", value=None)

    filters: dict[str, str | dt.date] = {}
    if type_filter != "All":
        filters["practice_type"] = type_filter
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date

    df = load_entries(filters)
    if df.empty:
        st.info("No entries found with current filters.")
        return

    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

    # Entry count chart
    daily_counts = (
        df.groupby("date").size().reset_index(name="count").sort_values("date")
    )
    st.subheader("Entry Frequency")
    st.line_chart(daily_counts.set_index("date"))


def main():
    st.set_page_config("Magickal Record", page_icon="✨", layout="wide")

    sidebar_choice = st.sidebar.radio("Menu", ["New Entry", "Browse"], index=0)

    if sidebar_choice == "New Entry":
        render_new_entry()
    else:
        render_browse()


if __name__ == "__main__":
    main()
