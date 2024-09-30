import streamlit as st

# عنوان اپلیکیشن
st.title("Simple Web App")

# ورودی کاربر
name = st.text_input("esme kirit?")

# دکمه برای تایید
if st.button("taiead esme kirit"):
    st.write(f"Hello, {name}! Welcome to our web app.")
gender = st.radio("jense kirit?:", ("Male", "Female", "Other"))
st.write(f"jense kirit?: {gender}")
age = st.slider("sene kirit?", 0, 100)
st.write(f"sene kirit?: {age}")
import matplotlib.pyplot as plt
import numpy as np

chart_data = np.random.randn(50, 3)
st.line_chart(chart_data)

