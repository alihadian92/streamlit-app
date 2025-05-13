"""
Streamlit web app: 7-Card Tarot Reading (Major Arcana Only)
-----------------------------------------------------------
Author: <your name>
Repository: https://github.com/<your-user>/tarot-seven-card

Setup
^^^^^
1. Install Python ≥ 3.9
2. Install dependencies:

    pip install streamlit

3. Launch locally:

    streamlit run app.py

Deploy
^^^^^^
Push *app.py* to GitHub.  
You can deploy free on [Streamlit Community Cloud](https://streamlit.io/cloud) by connecting the repo.

"""
import random
from pathlib import Path
import streamlit as st

# --- Page Config -------------------------------------------------------------
st.set_page_config(
    page_title="فال تاروت ۷ کارتی (Major Arcana)",
    page_icon="🃏",
    layout="centered"
)

# --- Data --------------------------------------------------------------------
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

# Optional: map each card to a local image in ./images or a remote URL
IMAGE_BASE = "https://raw.githubusercontent.com/<your-user>/tarot-seven-card/main/images"  # edit if you host images

def get_card_image(card_name: str) -> str | None:
    """Return image URL for a given card name if available."""
    # slug = card_name.split("(", 1)[-1].split(")")[0].lower().replace(" ", "_")
    # return f"{IMAGE_BASE}/{slug}.jpg"
    return None  # placeholder – add your own images!

# --- UI ----------------------------------------------------------------------
st.title("🃏 فال تاروت – ۷ کارت (فقط Major Arcana)")
st.caption("برای دریافت فال خود، روی دکمه زیر کلیک کنید.")

if 'cards' not in st.session_state:
    st.session_state.cards = []

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("کارت‌ها را بکش 🎴", type="primary"):
        st.session_state.cards = random.sample(MAJOR_ARCANA, 7)

with col2:
    if st.button("پاک‌کردن", type="secondary"):
        st.session_state.cards = []

# Show cards -----------------------------------------------------------
if st.session_state.cards:
    st.subheader("کارت‌های شما")
    for idx, card in enumerate(st.session_state.cards, start=1):
        st.markdown(f"**{idx}. {card}**")
        img_url = get_card_image(card)
        if img_url:
            st.image(img_url, use_column_width=True)
        st.divider()

else:
    st.info("هنوز کارتی انتخاب نشده است.")

# Footer
st.markdown(
    "----\n"
    "© 2025 با ❤️ توسط شما.  "
    "[کد منبع](https://github.com/<your-user>/tarot-seven-card)  "
    "| برای سرگرمی، نتیجه را جدی نگیرید.  "
)
