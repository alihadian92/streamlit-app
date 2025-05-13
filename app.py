# magickal_record_app.py

"""Streamlit Magickal Record Web‑App (Thelema)
---------------------------------------------
A minimal MVP for recording daily magical practices.
Dependencies:
    pip install streamlit sqlalchemy pandas ephem
Run with:
    streamlit run magickal_record_app.py
"""

import datetime as dt
from pathlib import Path
import streamlit as st
import pandas as pd
import ephem
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, Text
from sqlalchemy.orm import declarative_base, sessionmaker

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


def init_db():
    Base.metadata.create_all(engine)


def moon_phase_str(date_obj: dt.date) -> str:
    phases = [
        ("New Moon", 0),
        ("Waxing Crescent", 2),
        ("First Quarter", 7),
        ("Waxing Gibbous", 9),
        ("Full Moon", 14),
        ("Waning Gibbous", 16),
        ("Last Quarter", 22),
        ("Waning Crescent", 24),
    ]
    # Using ephem to calculate moon phase (0-29)
    new_moon = ephem.next_new_moon(date_obj)
    days_since_new = (date_obj - ephem.Date(new_moon - 29)).real
    age = int(days_since_new % 29.53058867)
    # Pick closest phase label
    label = min(phases, key=lambda p: abs(p[1] - age))[0]
    return label


def save_entry(data: dict):
    with SessionLocal() as db:
        entry = Entry(**data)
        db.add(entry)
        db.commit()


def load_entries(filters: dict | None = None) -> pd.DataFrame:
    with SessionLocal() as db:
        query = db.query(Entry)
        if filters:
            if filters.get("practice_type"):
                query = query.filter(Entry.practice_type == filters["practice_type"])
            if filters.get("start_date"):
               query = query.filter(Entry.date >= filters["start_date"])
            if filters.get("end_date"):
               query = query.filter(Entry.date <= filters["end_date"])
        rows = query.all()
        return pd.DataFrame([r.__dict__ for r in rows]).drop(columns=["_sa_instance_state"])


def main():
    st.set_page_config("Magickal Record", page_icon="✨", layout="wide")
    init_db()

    st.title("📖 Magickal Record – Thelema")
    menu = st.sidebar.radio("Menu", ["New Entry", "Browse"])

    if menu == "New Entry":
        with st.form("entry_form"):
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
            insights = st.text_area("Post‑Practice Insights / Analysis")
            tags = st.text_input("Tags (comma‑separated)")
            submitted = st.form_submit_button("Save Entry")

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
                "planetary_hour": "",  # TODO: calculate
            }
            save_entry(data)
            st.success("Entry saved ✨")

    elif menu == "Browse":
        st.header("📅 Browse Entries")
        with st.expander("Filters", expanded=False):
            col1, col2, col3 = st.columns(3)
            type_filter = col1.selectbox(
                "Practice Type", ["All", "LBRP", "Middle Pillar", "Meditation", "Resh", "Eucharist", "Yoga", "Other"]
            )
            start_date = col2.date_input("From", value=None)
            end_date = col3.date_input("To", value=None)

        filters = {}
        if type_filter != "All":
            filters["practice_type"] = type_filter
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date

        df = load_entries(filters)
        if df.empty:
            st.info("No entries found.")
            return
        st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

        # Simple daily count chart
        daily_counts = (
            df.groupby("date")
            .size()
            .reset_index(name="count")
            .sort_values("date")
        )
        st.subheader("Entry Frequency")
        st.line_chart(daily_counts.set_index("date"))

if __name__ == "__main__":
    main()
