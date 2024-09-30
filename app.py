import streamlit as st

# عنوان اپلیکیشن
st.title("Simple Web App")

# ورودی کاربر
esme kirito bego = st.text_input("Enter your name:")

# دکمه برای تایید
if st.button("taieade kirito bokon"):
    st.write(f"Fuck YOU, {name}! Welcome to our kossher.")
gender = st.radio("Select your gender:", ("Male", "Female", "Other"))
st.write(f"You selected: {gender}")
age = st.slider("Select your age:", 0, 100)
st.write(f"Your age is: {age}")
import matplotlib.pyplot as plt
import numpy as np

chart_data = np.random.randn(50, 3)
st.line_chart(chart_data)

