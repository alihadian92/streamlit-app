# magickal_record_app.py
"""Magickal Record – **Ultra‑Minimal** Streamlit App
=================================================
This is the *simplest possible* working prototype:
* 1 Python file (this one)
* 1 CSV file for storage (auto‑created: `records.csv`)

Run locally with:
    streamlit run magickal_record_app.py
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st

# ─────────────────────────────────────────────────────────────
# 📁 DATA STORAGE (CSV) ---------------------------------------
# ─────────────────────────────────────────────────────────────
DATA_PATH = Path("records.csv")  # created on first save


def load_entries() -> pd.DataFrame:
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH, parse_dates=["date"])
    return pd.DataFrame(columns=["date", "practice_type", "notes"])


def save_entry(entry: dict) -> None:
    df = load_entries()
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

# ─────────────────────────────────────────────────────────────
# 🖊️ PAGES ----------------------------------------------------
# ─────────────────────────────────────────────────────────────

def page_new_entry() -> None:
    st.header("📝 New Entry")

    date = st.date_input("Date", value=dt.date.today())
    practice_type = st.selectbox("Practice Type", [
        "LBRP",
        "Meditation",
        "Middle Pillar",
        "Other",
    ])
    notes = st.text_area("Notes (what happened, insights, etc.)")

    if st.button("💾 Save Entry"):
        if not notes.strip():
            st.warning("Please write something in notes ✍️")
            return
        save_entry({
            "date": date,
            "practice_type": practice_type,
            "notes": notes,
        })
        st.success("Saved!")
        st.balloons()


def page_browse() -> None:
    st.header("📚 Browse Entries")

    df = load_entries()
    if df.empty:
        st.info("No entries yet. Add one in the *New Entry* tab.")
        return

    st.dataframe(df.sort_values("date", ascending=False), use_container_width=True)

    with st.expander("Practice Type Frequency"):
        st.bar_chart(df["practice_type"].value_counts())

# ─────────────────────────────────────────────────────────────
# 🚀 MAIN -----------------------------------------------------
# ─────────────────────────────────────────────────────────────

def main() -> None:
    st.set_page_config("Magickal Record", page_icon="✨")
    page = st.sidebar.radio("Menu", ["New Entry", "Browse"], index=0)

    if page == "New Entry":
        page_new_entry()
    else:
        page_browse()


if __name__ == "__main__":
    main()
