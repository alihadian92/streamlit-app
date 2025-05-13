"""
Tarot Interpreter · Thelema × Qabalah
====================================
کاربر کارت‌های خود را در دنیای واقعی می‌کِشد و این برنامه فقط **تفسیر** می‌کند.

* تفاسیر کامل به شیوهٔ تِلِما (قائم و معکوس)
* تطبیق هر کارت با مسیرش روی درخت حیات قبالا
* سه الگوی فال (۳، ۵ و ۷ کارت) و امکان افزودن آسان
* جمع‌بندی خودکارِ پیام کلی فال بر اساس کلیدواژه‌های تکرارشونده

Repo: https://github.com/<your-user>/tarot-interpreter  
© 2025 — For entertainment purposes only
"""
from __future__ import annotations

import streamlit as st
from collections import Counter

# ───────────────────────────── CONFIG ─────────────────────────────
st.set_page_config(page_title="مفسر تاروت (تِلِما/قبالا)", page_icon="🃏", layout="centered")

st.title("🃏 مفسر تاروت – معانی تِلِما و قبالا")
st.caption("کارت‌ها را بکشید، سپس برای هر موقعیت کارت و حالت (قائم/معکوس) را برگزینید و روی «تفسیر کن» بزنید.")

# ───────────────────────────── DATA ───────────────────────────────
MAJOR_ARCANA: list[str] = [
    "۰. دیوانه (The Fool)", "۱. جادوگر (The Magician)", "۲. کاهنه اعظم (The High Priestess)",
    "۳. امپرس (The Empress)", "۴. امپراطور (The Emperor)", "۵. هیرو فانت (The Hierophant)",
    "۶. عاشقان (The Lovers)", "۷. ارابه (The Chariot)", "۸. قدرت (Strength)",
    "۹. مرتاض (The Hermit)", "۱۰. چرخ سرنوشت (Wheel of Fortune)", "۱۱. عدالت (Justice)",
    "۱۲. مرد معلق (The Hanged Man)", "۱۳. مرگ (Death)", "۱۴. اعتدال (Temperance)",
    "۱۵. شیطان (The Devil)", "۱۶. برج (The Tower)", "۱۷. ستاره (The Star)",
    "۱۸. ماه (The Moon)", "۱۹. خورشید (The Sun)", "۲۰. داوری (Judgement)", "۲۱. جهان (The World)"
]

# --- Upright meanings --------------------------------------------------------
THELEMA_UPRIGHT: dict[str, str] = {
    "۰. دیوانه (The Fool)": "آغازِ سفر، پتانسیل خالص و رهایی؛ اعتماد به جریان کائنات.",
    "۱. جادوگر (The Magician)": "تجلی اراده؛ تبدیل ایده به واقعیت از راه تمرکز.",
    "۲. کاهنه اعظم (The High Priestess)": "راز و شهود؛ دانش باطنی و الهام پنهان.",
    "۳. امپرس (The Empress)": "باروری و پرورش؛ فراوانی طبیعت و خلاقیت.",
    "۴. امپراطور (The Emperor)": "ساختار و اقتدار؛ رهبری و قانون‌گذاری.",
    "۵. هیرو فانت (The Hierophant)": "سنت و آیین؛ آموزه‌های معنوی و انتقال دانش.",
    "۶. عاشقان (The Lovers)": "اتحاد و انتخاب؛ هماهنگی قلب و عقل.",
    "۷. ارابه (The Chariot)": "پیروزی اراده؛ پیشرفت کنترل‌شده به سوی هدف.",
    "۸. قدرت (Strength)": "نیروی نرم؛ شجاعت همراه با شفقت و مهار غرایز.",
    "۹. مرتاض (The Hermit)": "انزوای خردمندانه؛ جستجوی حقیقت درونی.",
    "۱۰. چرخ سرنوشت (Wheel of Fortune)": "چرخش ادوار؛ تغییر کارمایی و پذیرش سرنوشت.",
    "۱۱. عدالت (Justice)": "توازن و مسئولیت؛ قضاوت منصفانه و هماهنگی کیهانی.",
    "۱۲. مرد معلق (The Hanged Man)": "تسلیم خلاق؛ دید وارونه و قربانی‌کردن کهنه.",
    "۱۳. مرگ (Death)": "دگرگونی بنیادین؛ پایان لازم برای تولد تازه.",
    "۱۴. اعتدال (Temperance)": "کیمیاگری روح؛ آشتی اضداد و جریان متوازن انرژی.",
    "۱۵. شیطان (The Devil)": "آگاهی از سایه؛ وابستگی و آزمون میل زمینی.",
    "۱۶. برج (The Tower)": "فروپاشی ناگهانی؛ آزادی از ساختار محدودکننده.",
    "۱۷. ستاره (The Star)": "امید و الهام؛ آرامش پس از طوفان و شفابخشی.",
    "۱۸. ماه (The Moon)": "قلمروی رؤیا؛ توهم و برخورد با ناخودآگاه.",
    "۱۹. خورشید (The Sun)": "سرور و روشنی؛ موفقیت و وضوح حقیقت.",
    "۲۰. داوری (Judgement)": "بیداری روح؛ فراخوان به رسالت بالاتر.",
    "۲۱. جهان (The World)": "کمال و ادغام؛ پایان چرخه و جشن دستاورد.",
}

# --- Reversed meanings -------------------------------------------------------
# برای کوتاهی، اگر معنای معکوس صریح وارد نشده باشد، توضیح پیش‌فرض با پیشوند اضافه می‌شود.
THELEMA_REVERSED: dict[str, str] = {
    key: (
        {
            "۰. دیوانه (The Fool)": "بی‌احتیاطی، ریسک نسنجیده و بی‌توجهی به پیامدها.",
            "۱. جادوگر (The Magician)": "سوء‌استفاده از قدرت، فریب یا انرژی پراکنده.",
            "۲. کاهنه اعظم (The High Priestess)": "انسداد شهود یا توهم معنوی.",
            "۳. امپرس (The Empress)": "انسداد خلاقیت یا افراط در لذات.",
            "۴. امپراطور (The Emperor)": "استبداد یا مقاومت با تغییر.",
            "۵. هیرو فانت (The Hierophant)": "تعصب یا دگم مذهبی.",
            "۶. عاشقان (The Lovers)": "عدم‌تعهد یا تضاد ارزش‌ها.",
            "۷. ارابه (The Chariot)": "فقدان کنترل یا غرور افراطی.",
            "۸. قدرت (Strength)": "تسلیم در برابر ترس یا سوء‌استفاده از زور.",
            "۹. مرتاض (The Hermit)": "انزوای ناسالم یا گم‌گشتی.",
            "۱۰. چرخ سرنوشت (Wheel of Fortune)": "مقاومت با تغییر یا بدبیاری.",
            "۱۱. عدالت (Justice)": "بی‌انصافی یا اجتناب از پیامد.",
            "۱۲. مرد معلق (The Hanged Man)": "تعلل بی‌ثمر یا قربانی‌گری بیهوده.",
            "۱۳. مرگ (Death)": "مقاومت در برابر دگرگونی یا ترس.",
            "۱۴. اعتدال (Temperance)": "عدم‌تعادل یا افراط.",
            "۱۵. شیطان (The Devil)": "اسارت در وابستگی یا وسوسه.",
            "۱۶. برج (The Tower)": "ویرانی طولانی یا شوک سمی.",
            "۱۷. ستاره (The Star)": "ناامیدی یا کاهش ایمان.",
            "۱۸. ماه (The Moon)": "سردرگمی یا فریب خیالات.",
            "۱۹. خورشید (The Sun)": "شادی سطحی یا غرور کودکانه.",
            "۲۰. داوری (Judgement)": "خودقضاوتی شدید یا سرکوب درونی.",
            "۲۱. جهان (The World)": "دوره ناتمام یا احساس انسداد.",
        }.get(key, "جنبهٔ منفی/معکوس: " + val)
    )
    for key, val in THELEMA_UPRIGHT.items()
}

# --- Qabalah paths ----------------------------------------------------------
KABBALAH_PATHS: dict[str, str] = {
    "۰. دیوانه (The Fool)": "حرف א (Aleph) – مسیر ۱۱ بین כתר و حکمه؛ عنصر هوا.",
    "۱. جادوگر (The Magician)": "ب (Beth) – مسیر ۱۲ بین כתר و بینه.",
    "۲. کاهنه اعظم (The High Priestess)": "ג (Gimel) – مسیر ۱۳ بین כתר و تیفارت.",
    "۳. امپرس (The Empress)": "ד (Daleth) – مسیر ۱۴ بین حکمه و بینه.",
    "۴. امپراطور (The Emperor)": "ה (He) – مسیر ۱۵ بین حکمه و גבורה.",
    "۵. هیرو فانت (The Hierophant)": "ו (Vav) – مسیر ۱۶ بین حکمه و חסד.",
    "۶. عاشقان (The Lovers)": "ז (Zayin) – مسیر ۱۷ بین بینه و تیفارت.",
    "۷. ارابه (The Chariot)": "ח (Cheth) – مسیر ۱۸ بین בינה ו גבורה.",
    "۸. قدرت (Strength)": "ט (Teth) – مسیر ۱۹ بین חסד ו גבורה.",
    "۹. مرتاض (The Hermit)": "י (Yod) – مسیر ۲۰ بین חסד ו תפארת.",
    "۱۰. چرخ سرنوشت (Wheel of Fortune)": "כ (Kaph) – مسیر ۲۱ بین חסد ו נצח.",
    "۱۱. عدالت (Justice)": "ל (Lamed) – مسیر ۲۲ بین גבורה ו תפארת.",
    "۱۲. مرد معلق (The Hanged Man)": "מ (Mem) – مسیر ۲۳ بین גבורה ו הוד؛ عنصر آب.",
    "۱۳. مرگ (Death)": "נ (Nun) – مسیر ۲۴ بین נצח و תפארת.",
    "۱۴. اعتدال (Temperance)": "ס (Samekh) – مسیر ۲۵ بین تפארת ו יסוד.",
    "۱۵. شیطان (The Devil)": "ע (Ayin) – مسیر ۲۶ بین תפארת ו הוד.",
    "۱۶. برج (The Tower)": "פ (Peh) – مسیر ۲۷ بین נצח ו הוד.",
    "۱۷. ستاره (The Star)": "צ (Tzaddi) – مسیر ۲۸ بین נצח ו יסוד.",
    "۱۸. ماه (The Moon)": "ק (Qoph) – مسیر ۲۹ بین נצח ו מלכות.",
    "۱۹. خورشید (The Sun)": "ר (Resh) – مسیر ۳۰ بین הוד ו יסוד.",
    "۲۰. داوری (Judgement)": "ש (Shin) – مسیر ۳۱ بین הוד ו מלכות؛ عنصر آتش.",
    "۲۱. جهان (The World)": "ת (Tav) – مسیر ۳۲ بین יסוד ו מלכות.",
}

# --- Spread templates -------------------------------------------------------
SPREADS = {
    "۳ کارت (گذشته/حال/آینده)": ["گذشته", "حال", "آینده"],
    "۵ کارت (عنصرهای پنتاگرام)": ["روح", "آتش", "آب", "هوا", "زمین"],
    "۷ کارت (مسیر جادویی)": [f"موقعیت {i}" for i in range(1, 8)],
}

# ─────────────────────────── Helper functions ───────────────────────────────

def card_meaning(card: str, reversed_: bool) -> str:
    return (THELEMA_REVERSED if reversed_ else THELEMA_UPRIGHT).get(card, "⸺")


def synthesize_summary(selections: dict[str, tuple[str, bool]]) -> str:
    """Generate a simple narrative + keyword theme summary."""
    clauses, words = [], []
    for pos, (card, rev) in selections.items():
        meaning = card_meaning(card, rev)
        head_clause = meaning.split("؛")[0].split("،")[0]
        clauses.append(f"در *{pos}*, **{card.split('(')[0].strip()}** نمایانگر {head_clause} است")
        words.extend([w for w in head_clause.split() if len(w) > 3])
    top = [w for w, _ in Counter(words).most_common(3)]
    summary = "؛ ".join(clauses) + "."
    if top:
        summary += f"\n\n▪️ تم‌های غالب: {'، '.join(top)}."
    return summary

# ───────────────────────────── STATE ─────────────────────────────────────────
if "chosen" not in st.session_state:
    st.session_state.chosen = {}

# ───────────────────────────── UI – Sidebar ─────────────────────────────────
st.sidebar.header("انتخاب الگو")
spread = st.sidebar.selectbox("الگو:", list(SPREADS.keys()))
positions = SPREADS[spread]

# ───────────────────────────── Card entry form ─────────────────────────────
with st.form("card_form"):
    picks = {}
    for pos in positions:
        c1, c2 = st.columns([3, 1])
        card_pick = c1.selectbox(pos, MAJOR_ARCANA, key=f"card_{pos}")
        is_rev = c2.checkbox("معکوس", key=f"rev_{pos}")
        picks[pos] = (card_pick, is_rev)
    if st.form_submit_button("تفسیر کن 🪄"):
        st.session_state.chosen = picks

# ───────────────────────────── Display result ──────────────────────────────
selections = st.session_state.chosen
if selections:
    st.subheader("🔮 تفسیر کارت‌ها")
    for pos, (card, rev) in selections.items():
        st.markdown(f"### {pos} — {card}{' (معکوس)' if rev else ''}")
        st.write("**معنی تِلِما:**", card_meaning(card, rev))
        st.write("**قبالا:**", KABBALAH_PATHS.get(card, "⸺"))
        st.divider()
    st.subheader("📜 جمع‌بندی نهایی")
    st.write(synthesize_summary(selections))
else:
    st.info("کارت‌ها را انتخاب کنید و تفسیر بگیرید.")

# ───────────────────────────── Footer ───────────────────────────────────────
st.markdown("---\n© 2025 · گیت‌هاب: <your-user>/tarot-interpreter · برای سرگرمی")
