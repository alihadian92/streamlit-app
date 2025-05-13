# magickal_record_app.py
"""Magickal Record – Streamlit Web-App (Enhanced v2)
===================================================
新增ها / New in this version
---------------------------
• **Delete & Edit** capability (Manage page)
• Keeps previous features: SQLite, moon-phase, export, password

Run locally:
    pip install streamlit pandas SQLAlchemy ephem
    streamlit run magickal_record_app.py
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict

import pandas as pd
import streamlit as st
from sqlalchemy import Column, Date, Integer, String, Text, Time, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# ─────────────────────────────────────────────────────────────
# 🔐 OPTIONAL PASSWORD ---------------------------------------
# ─────────────────────────────────────────────────────────────
APP_PASSWORD = st.secrets.get("APP_PASSWORD", "")
if APP_PASSWORD:
    if st.session_state.get("auth_ok") is not True:
        pw = st.text_input("Password", type="password")
        if pw == APP_PASSWORD:
            st.session_state["auth_ok"] = True
        else:
            st.stop()

# ─────────────────────────────────────────────────────────────
# 💾 DATABASE ------------------------------------------------
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
# 🌙 MOON-PHASE UTIL -----------------------------------------
# ─────────────────────────────────────────────────────────────
try:
    import ephem  # type: ignore
except ModuleNotFoundError:
    ephem = None

_PHASES: list[tuple[str, float]] = [
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
        moon = ephem.Moon(d)
        age = moon.moon_phase * 29.53
    else:
        ref = dt.date(2000, 1, 6)
        age = (d - ref).days % 29.53
    return min(_PHASES, key=lambda p: abs(p[1] - age))[0]

# ─────────────────────────────────────────────────────────────
# 📦 DATA HELPERS --------------------------------------------
# ─────────────────────────────────────────────────────────────

def save_entry(data: Dict[str, Any]) -> None:
    with Session() as s:
        s.add(Entry(**data))
        s.commit()


def update_entry(entry_id: int, data: Dict[str, Any]) -> None:
    with Session() as s:
        entry = s.get(Entry, entry_id)
        if entry:
            for k, v in data.items():
                setattr(entry, k, v)
            s.commit()


def delete_entry(entry_id: int) -> None:
    with Session() as s:
        entry = s.get(Entry, entry_id)
        if entry:
            s.delete(entry)
            s.commit()


def load_entries(filters: Dict[str, Any] | None = None) -> pd.DataFrame:
    with Session() as s:
        q = s.query(Entry)
        if filters:
            if (pt := filters.get("practice_type")):
                q = q.filter(Entry.practice_type == pt)
            if (st_date := filters.get("start")):
                q = q.filter(Entry.date >= st_date)
            if (en_date := filters.get("end")):
                q = q.filter(Entry.date <= en_date)
        rows = q.all()
        df = pd.DataFrame([r.__dict__ for r in rows])
        if not df.empty:
            df.drop(columns=["_sa_instance_state"], inplace=True)
        return df

# ─────────────────────────────────────────────────────────────
# 🖊️ PAGES ---------------------------------------------------
# ─────────────────────────────────────────────────────────────

PRACTICES = ["LBRP", "Middle Pillar", "Meditation", "Resh", "Eucharist", "Yoga", "Other"]


def page_new_entry() -> None:
    st.header("📝 New Entry")
    col1, col2 = st.columns(2)

    date = col1.date_input("Date", value=dt.date.today())
    start_time = col1.time_input("Start Time", value=dt.datetime.now().time())
    end_time = col2.time_input("End Time")

    practice_type = col2.selectbox("Practice Type", PRACTICES)

    pre_feeling = st.text_area("Pre-Feeling / Mindset")
    experience_notes = st.text_area("Experience During Practice")
    insights = st.text_area("Post-Practice Insights")
    tags = st.text_input("Tags (comma-separated)")

    if st.button("💾 Save Entry"):
        save_entry({
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "practice_type": practice_type,
            "pre_feeling": pre_feeling,
            "experience_notes": experience_notes,
            "insights": insights,
            "tags": tags,
            "moon_phase": moon_phase_str(date),
        })
        st.success("Saved ✨")
        st.balloons()


def browsing_table(df: pd.DataFrame) -> None:
    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)
    st.download_button("⬇️ Export CSV", df.to_csv(index=False), "magickal_entries.csv")
    daily = df.groupby("date").size().reset_index(name="count").sort_values("date")
    if not daily.empty:
        st.line_chart(daily.set_index("date"))


def page_browse() -> None:
    st.header("📚 Browse Entries")
    ft, sdate, edate = _filter_controls()
    filters: Dict[str, Any] = {}
    if ft != "All":
        filters["practice_type"] = ft
    if sdate:
        filters["start"] = sdate
    if edate:
        filters["end"] = edate
    df = load_entries(filters)
    if df.empty:
        st.info("No entries found.")
    else:
        browsing_table(df)


def _filter_controls():
    with st.expander("Filters", expanded=False):
        c1, c2, c3 = st.columns(3)
        ft = c1.selectbox("Practice Type", ["All"] + PRACTICES)
        sd = c2.date_input("From", value=None)
        ed = c3.date_input("To", value=None)
    return ft, sd, ed


def page_manage() -> None:
    st.header("🛠️ Manage Entries (Edit / Delete)")
    df = load_entries({})
    if df.empty:
        st.info("No entries yet.")
        return

    df_display = df[["id", "date", "practice_type", "tags"]]
    st.dataframe(df_display, use_container_width=True)

    ids = df["id"].tolist()
    sel_id = st.selectbox("Select entry ID", ids)
    entry_row = df[df["id"] == sel_id].iloc[0]

    mode = st.radio("Action", ["Edit", "Delete"], horizontal=True)

    if mode == "Edit":
        _edit_form(sel_id, entry_row)
    else:
        if st.button("❌ Delete this entry", type="secondary"):
            delete_entry(sel_id)
            st.success("Entry deleted.")
            st.experimental_rerun()


def _edit_form(eid: int, row: pd.Series) -> None:
    with st.form(key="edit_form"):
        col1, col2 = st.columns(2)
        date = col1.date_input("Date", value=row.date)
        start_time = col1.time_input("Start Time", row.start_time)
        end_time = col2.time_input("End Time", row.end_time)
        practice_type = col2.selectbox("Practice Type", PRACTICES, index=PRACTICES.index(row.practice_type) if row.practice_type in PRACTICES else len(PRACTICES)-1)
        pre_feeling = st.text_area("Pre-Feeling", row.pre_feeling or "")
        experience_notes = st.text_area("Experience", row.experience_notes or "")
        insights = st.text_area("Insights", row.insights or "")
        tags = st.text_input("Tags", row.tags or "")
        submitted = st.form_submit_button("💾 Save Changes")
    if submitted:
        update_entry(eid, {
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "practice_type": practice_type,
            "pre_feeling": pre_feeling,
            "experience_notes": experience_notes,
            "insights": insights,
            "tags": tags,
            "moon_phase": moon_phase_str(date),
        })
        st.success("Updated!")
        st.experimental_rerun()

# ─────────────────────────────────────────────────────────────
# 🚀 MAIN -----------------------------------------------------
# ─────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config("Magickal Record", page_icon="✨", layout="wide")
    page = st.sidebar.radio("Menu", ["New Entry", "Browse", "Manage"], index=0)
    if page == "New Entry":
        page_new_entry()
    elif page == "Browse":
        page_browse()
    else:
        page_manage()


if __name__ == "__main__":
    main()
