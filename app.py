"""
Streamlit web app: Tarot Interpreter – Thelema/Kabbalah
======================================================
Use this tool to *interpret* cards you physically drew, rather than drawing
randomly in-app.  Multiple spread types + upright/reversed meanings.

Author: <your name>
Repository: https://github.com/<your-user>/tarot-interpreter

Setup
-----
1. Install Python ≥ 3.9 + Streamlit  
   `pip install streamlit`  
2. Run: `streamlit run app.py`  
3. Deploy on Streamlit Community Cloud.

Data scope: **Major Arcana only** for brevity, but structure allows expansion
to all 78 cards later.
"""
from __future__ import annotations

import streamlit as st

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="مفسر تاروت (تِلِما/قبالا)",
    page_icon="🃏",
    layout="centered",
)

st.title("🃏 مفسر تاروت – معانی تِلِما و قبالا")
st.caption(
    "ابتدا در دنیای واقعی کارت‌ها را بکشید، سپس کارت‌ها و وضعیت آن‌ها (قائم یا معکوس) را اینجا انتخاب کنید تا تفسیر را ببینید."
)

# ─── CARD DATA ───────────────────────────────────────────────────────────────
MAJOR_ARCANA = [
    "۰. دیوانه (The Fool)",
    "۱. جادوگر (The Magician)",
    "۲. کاهنه اعظم (The High Priestess)",
    "۳. امپرس (The Empress)",
    "۴. امپراطور (The Emperor)",
    "۵. هیرو فانت (The Hierophant)",
    "۶. عاشقان (The Lovers)",
    "۷. ارابه (The Chariot)",
    "۸. قدرت (Strength)",
    "۹. مرتاض (The Hermit)",
    "۱۰. چرخ سرنوشت (Wheel of Fortune)",
    "۱۱. عدالت (Justice)",
    "۱۲. مرد معلق (The Hanged Man)",
    "۱۳. مرگ (Death)",
    "۱۴. اعتدال (Temperance)",
    "۱۵. شیطان (The Devil)",
    "۱۶. برج (The Tower)",
    "۱۷. ستاره (The Star)",
    "۱۸. ماه (The Moon)",
    "۱۹. خورشید (The Sun)",
    "۲۰. داوری (Judgement)",
    "۲۱. جهان (The World)",
]

THELEMA_UPRIGHT: dict[str, str] = {
    "۰. دیوانه (The Fool)": "پتانسیل و رهایی: شروع مسیری نو با اعتماد به جریان کائنات.",
    "۱. جادوگر (The Magician)": "تجلی اراده: تمرکز نیروهای چهار عنصر برای خلق واقعیت.",
    # … (تا بقیه کارت‌ها – همان محتواى نسخه قبلى) …
}

THELEMA_REVERSED: dict[str, str] = {
    "۰. دیوانه (The Fool)": "بی احتیاطی، حواس‌پرتی، پریدن بدون نگاه کردن.",
    "۱. جادوگر (The Magician)": "سوء‌استفاده از قدرت، فریب یا اراده‌ی پراکنده.",
    # … تکمیل بقیه کارت‌ها در آینده …
}

KABBALAH_PATHS: dict[str, str] = {
    "۰. دیوانه (The Fool)": "مسیر الف بین כתר و حکمه – انرژی نیروی حیات.",
    # … مسیرهای درخت حیات برای کارت‌ها …
}

# ─── SPREAD TEMPLATES ────────────────────────────────────────────────────────
SPREADS: dict[str, list[str]] = {
    "۳ کارت (گذشته/حال/آینده)": ["گذشته", "حال", "آینده"],
    "۵ کارت (عنصرهای پنتاگرام)": ["روح", "آتش", "آب", "هوا", "زمین"],
    "۷ کارت (عبور جادویی تِلِما)": [f"کارت {i}" for i in range(1, 8)],
}

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
        th_mean = (
            THELEMA_REVERSED.get(card) if rev else THELEMA_UPRIGHT.get(card)
        ) or "—"
        qabalah = KABBALAH_PATHS.get(card, "—")

        with st.expander("معانی تِلِما"):
            st.write(th_mean)
        with st.expander("ارتباط قبالا/درخت حیات"):
            st.write(qabalah)
        st.divider()

    st.success("پایان تفسیر.")
else:
    st.info("کارت‌ها را انتخاب کنید و دکمهٔ تفسیر را بزنید.")

# ─── FOOTER ─────────────────────────────────────────────────────────────────
st.markdown(
    "---\n"
    "© 2025 با ❤️ توسط شما · [کد منبع](https://github.com/<your-user>/tarot-interpreter) · برای سرگرمی استفاده شود"
)
