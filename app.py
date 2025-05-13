"""
Streamlit web app: Tarot Interpreter – Thelema / Qabalah
========================================================
*Offline draw, online interpretation*  
این نسخه، علاوه بر نمایش تکیِ هر کارت، یک **جمع‌بندی هوشمند** از فال ارائه می‌دهد که مضامین کلیدی و پیامِ کلی را استخراج می‌کند.

Author  : <your name>  
Repo    : https://github.com/<your-user>/tarot-interpreter

2025 — For entertainment purposes only.
"""
from __future__ import annotations

import streamlit as st
from collections import Counter

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="مفسر تاروت (تِلِما/قبالا)",
    page_icon="🃏",
    layout="centered",
)

st.title("🃏 مفسر تاروت – معانی تِلِما و قبالا")
st.caption(
    "ابتدا کارت‌های خود را بکشید؛ سپس برای هر موقعیت کارت و وضعیت آن (قائم/معکوس) را انتخاب کنید و بر دکمهٔ «تفسیر کن» بزنید."
)

# ─── CARD DATA ──────────────────────────────────────────────────────────────
# (lists and dictionaries unchanged – truncated for brevity in this snippet)
MAJOR_ARCANA = [
    "۰. دیوانه (The Fool)", "۱. جادوگر (The Magician)", "۲. کاهنه اعظم (The High Priestess)",
    "۳. امپرس (The Empress)", "۴. امپراطور (The Emperor)", "۵. هیرو فانت (The Hierophant)",
    "۶. عاشقان (The Lovers)", "۷. ارابه (The Chariot)", "۸. قدرت (Strength)",
    "۹. مرتاض (The Hermit)", "۱۰. چرخ سرنوشت (Wheel of Fortune)", "۱۱. عدالت (Justice)",
    "۱۲. مرد معلق (The Hanged Man)", "۱۳. مرگ (Death)", "۱۴. اعتدال (Temperance)",
    "۱۵. شیطان (The Devil)", "۱۶. برج (The Tower)", "۱۷. ستاره (The Star)",
    "۱۸. ماه (The Moon)", "۱۹. خورشید (The Sun)", "۲۰. داوری (Judgement)", "۲۱. جهان (The World)"
]

# **** FULL dictionaries (UPRIGHT / REVERSED / KABBALAH) kept from prior version ****
# → They remain exactly the same; omitted here for brevity ←

# ─── SPREAD TEMPLATES ────────────────────────────────────────────────────────
SPREADS = {
    "۳ کارت (گذشته/حال/آینده)": ["گذشته", "حال", "آینده"],
    "۵ کارت (عنصرهای پنتاگرام)": ["روح", "آتش", "آب", "هوا", "زمین"],
    "۷ کارت (عبور جادویی تِلِما)": [f"موقعیت {i}" for i in range(1, 8)],
}

# ─── Helper Functions ────────────────────────────────────────────────────────

def card_meaning(card: str, reversed_: bool) -> str:
    """Return Thelema meaning respecting upright/reversed."""
    return (THELEMA_REVERSED if reversed_ else THELEMA_UPRIGHT).get(card, "—")


def synthesize_summary(selected: dict[str, tuple[str, bool]]) -> str:
    """Create an overall narrative summarizing the spread.

    Strategy (simple heuristic):
    1. Collect first clause (before first '؛' or '،') of each card meaning.
    2. Detect most frequent key words (e.g., تغییر، اراده، عشق، ...).
    3. Compose a paragraph mentioning dominant themes and trajectory.
    """
    first_clauses: list[str] = []
    keywords: list[str] = []

    for pos, (card, rev) in selected.items():
        meaning = card_meaning(card, rev)
        clause = meaning.split("؛")[0].split("،")[0]
        first_clauses.append(f"در موقعیت {pos}، کارت **{card.split('(')[0].strip()}** نشان‌دهندهٔ {clause} است")
        # crude keyword extraction – pick final noun-ish word of clause
        if clause:
            keywords.extend(clause.split()[-2:])

    # Determine top 3 keywords (heuristic, ignoring short tokens)
    keywords = [w for w in keywords if len(w) > 3]
    top_kw = [w for w, _ in Counter(keywords).most_common(3)]

    paragraph = "؛ ".join(first_clauses) + "."
    if top_kw:
        paragraph += f"\n\n▪️ تم‌های غالب این فال عبارت‌اند از: {'، '.join(top_kw)}."
    return paragraph

# ─── STATE INIT ──────────────────────────────────────────────────────────────
if "chosen_cards" not in st.session_state:
    st.session_state.chosen_cards: dict[str, tuple[str, bool]] = {}

# ─── SIDEBAR – SPREAD SELECTION ─────────────────────────────────────────────
st.sidebar.header("نوع فال را برگزینید")
spread_name = st.sidebar.selectbox("الگو:", list(SPREADS.keys()))
positions = SPREADS[spread_name]

st.sidebar.info("برای هر موقعیت، کارت و وضعیت معکوس بودن را مشخص کنید.")

# ─── FORM FOR CARD INPUT ────────────────────────────────────────────────────
with st.form(key="card_input_form"):
    selected: dict[str, tuple[str, bool]] = {}
    for pos in positions:
        cols = st.columns([3, 1])
        card = cols[0].selectbox(f"{pos}:", MAJOR_ARCANA, key=f"card_{pos}")
        rev = cols[1].checkbox("معکوس؟", key=f"rev_{pos}")
        selected[pos] = (card, rev)
    submitted = st.form_submit_button("تفسیر کن 🪄")

if submitted:
    st.session_state.chosen_cards = selected

# ─── DISPLAY INTERPRETATION ─────────────────────────────────────────────────
if st.session_state.chosen_cards:
    st.subheader("🔮 تفسیر کارت‌ها")
    for pos, (card, rev) in st.session_state.chosen_cards.items():
        st.markdown(f"### {pos} – {card}{' (معکوس)' if rev else ''}")

        th_mean = card_meaning(card, rev)
        qabalah = KABBALAH_PATHS.get(card, "—")

        with st.expander("معانی تِلِما"):
            st.write(th_mean)
        with st.expander("ارتباط قبالا / درخت حیات"):
            st.write(qabalah)
        st.divider()

    # 🪄 Overall synthesis
    st.subheader("📜 جمع‌بندی نهایی فال")
    summary_text = synthesize_summary(st.session_state.chosen_cards)
    st.write(summary_text)
    st.success("🎉 تفسیر و جمع‌بندی کامل شد.")
else:
    st.info("کارت‌ها را انتخاب کنید و دکمهٔ تفسیر را بزنید.")

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown(
    "---\n"
    "© 2025 با ❤️ توسط شما · [کد منبع](https://github.com/<your-user>/tarot-interpreter) · برای سرگرمی استفاده شود"
)
