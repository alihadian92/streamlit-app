"""
Streamlit web app: 7‑Card Tarot Reading – Major Arcana (Thelema Interpretation)
===============================================================================
Author: <your name>
Repository: https://github.com/<your-user>/tarot-seven-card

» Persian interface · Thelema‑based card meanings

Usage
-----
1. Install Python ≥ 3.9 and Streamlit:  `pip install streamlit`  
2. Run locally:                       `streamlit run app.py`  
3. Deploy on Streamlit Community Cloud by connecting the GitHub repo.

Copyright © 2025 — For entertainment purposes only.
"""
from __future__ import annotations

import random
import streamlit as st

# ─── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="فال تاروت ۷ کارتی (تعبیر تلمایی)",
    page_icon="🃏",
    layout="centered",
)

st.title("🃏 فال تاروت – ۷ کارت (تفاسیر مکتب تـِلِما)")
st.caption("برای دریافت فال خود، کارت‌ها را بکشید. تنها کارت‌های ماژور آرکانا استفاده می‌شوند.")

# ─── Major Arcana Data ───────────────────────────────────────────────────────
MAJOR_ARCANA: list[str] = [
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

THELEMA_MEANINGS: dict[str, str] = {
    "۰. دیوانه (The Fool)": "آغازِ سفری نو، پتانسیلِ خالص، ریسک با ایمان به جهان. در تِلِما نماد روح آزاد و عنصر هوا است.",
    "۱. جادوگر (The Magician)": "اراده متمرکز، تجلی، تسلط بر ابزار. به‌کارگیری قدرت خلاق برای تحقق خواسته‌ها.",
    "۲. کاهنه اعظم (The High Priestess)": "راز، سکوت، شهودِ برتر. دریچه‌ای به حکمت نهان و دانش باطنی.",
    "۳. امپرس (The Empress)": "باروری، عشقِ مادرانه، طبیعت. زایش ایده‌ها و فراوانی.",
    "۴. امپراطور (The Emperor)": "ساختار، اقتدار، قانون. قدرتی که نظم می‌آفریند و مسئولیت‌پذیر است.",
    "۵. هیرو فانت (The Hierophant)": "آیین و سنت، مدرس روحانی، شعائر مقدس. تمسک به میراث معنوی.",
    "۶. عاشقان (The Lovers)": "انتخاب آگاهانه، اتحاد دوگانه‌ها، عشق الهی. همسویی قلب و عقل.",
    "۷. ارابه (The Chariot)": "پیروزی اراده، کنترل نیروهای متضاد، پیشرفت قهرمانانه.",
    "۸. قدرت (Strength)": "شجاعت و مهربانی توأمان، تسلط بر خویشتن، نیروی نرم. لیبیدوی مهار شده.",
    "۹. مرتاض (The Hermit)": "انزوا برای کشف حقیقت درونی، مشعل خرد، راهنمایی خویشتن.",
    "۱۰. چرخ سرنوشت (Wheel of Fortune)": "چرخش ادوار، تغییر کارما، پذیرش قانون علت و معلول.",
    "۱۱. عدالت (Justice)": "توازن، انصاف، پیامد اعمال. هماهنگی کائناتی از طریق مسئولیت‌پذیری.",
    "۱۲. مرد معلق (The Hanged Man)": "تسلیم در آگاهی، دید وارونه، قربانی برای روشنگری.",
    "۱۳. مرگ (Death)": "پایان لازم برای تولد دوباره، تحول بنیادین، رها کردن کهنه.",
    "۱۴. اعتدال (Temperance)": "کیمیاگری روح، ادغام متضادها، میانه‌روی و هارمونی.",
    "۱۵. شیطان (The Devil)": "وابستگی و زنجیرهای خودساخته، سایه نفس، آزمون میل زمینی.",
    "۱۶. برج (The Tower)": "فروپاشی ناگهانی ساختار کهنه، رهایی از محدودیت، شهود تکان‌دهنده.",
    "۱۷. ستاره (The Star)": "امید، وحی، شفابخشی. جریان نو شدن و الهام آسمانی.",
    "۱۸. ماه (The Moon)": "توهم، دنیای رؤیا و ناخودآگاه، مواجهه با ترس‌های پنهان.",
    "۱۹. خورشید (The Sun)": "روشنی، موفقیت، انرژی حیاتی و کودکی شاد. افشای حقیقت با شادی.",
    "۲۰. داوری (Judgement)": "بیداری روح، داوری بر گذشته، فراخوان به رسالت بالاتر.",
    "۲۱. جهان (The World)": "تکمیل چرخه، ادغام و وحدت با کل، آگاهی کیهانی.",
}

# ─── Utility: Optional Images ────────────────────────────────────────────────
IMAGE_BASE = "https://raw.githubusercontent.com/<your-user>/tarot-seven-card/main/images"

def get_card_image(card_name: str) -> str | None:
    """Return image URL for a given card name if available in the repo."""
    slug = card_name.split("(")[1].split(")")[0].strip().lower().replace(" ", "-")
    url = f"{IMAGE_BASE}/{slug}.jpg"
    # Return None for now; enable when images are provided
    return None

# ─── Session State ───────────────────────────────────────────────────────────
if "cards" not in st.session_state:
    st.session_state.cards: list[str] = []

# ─── Control Buttons ────────────────────────────────────────────────────────
col_draw, col_reset = st.columns(2)
if col_draw.button("🎴 کارت‌ها را بکش", type="primary"):
    st.session_state.cards = random.sample(MAJOR_ARCANA, 7)
if col_reset.button("🔄 پاک‌کردن", type="secondary"):
    st.session_state.cards = []

# ─── Display Reading ────────────────────────────────────────────────────────
if st.session_state.cards:
    st.subheader("نتیجه فال شما")
    for idx, card in enumerate(st.session_state.cards, start=1):
        st.markdown(f"### {idx}. {card}")
        st.markdown(THELEMA_MEANINGS.get(card, "معنای این کارت موجود نیست."))
        img_url = get_card_image(card)
        if img_url:
            st.image(img_url, use_column_width=True)
        st.divider()

    # ─ Summary Guidance ─
    st.subheader("👁️‍🗨️ جمع‌بندی کلی")
    st.write(
        "این ۷ کارت، داستان مسیر فعلی شما را از ریسک و پتانسیل (کارت نخست) تا نتیجهٔ احتمالی (کارت هفتم) روایت می‌کنند.\n"
        "برای درک عمیق‌تر، به پیوند میان معانی هر کارت توجه کنید و ببینید چگونه مضامین مشترک—مثل تغییر، انتخاب یا امید—در زندگى‌تان پژواک می‌یابند."
    )
else:
    st.info("هنوز کارتی انتخاب نشده است.")

# ─── Footer ─────────────────────────────────────────────────────────────────
st.markdown(
    "---\n"
    "© 2025 با ❤️ توسط شما · [کد منبع](https://github.com/<your-user>/tarot-seven-card) · برای سرگرمی استفاده شود"
)
