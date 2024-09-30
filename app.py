import streamlit as st

# عنوان اپلیکیشن
st.title("Simple Web App")

# ورودی کاربر
name = st.text_input("Enter your name:")

# دکمه برای تایید
if st.button("Submit"):
    st.write(f"Hello, {name}! Welcome to our web app.")
gender = st.radio("Select your gender:", ("Male", "Female", "Other"))
st.write(f"You selected: {gender}")
age = st.slider("Select your age:", 0, 100)
st.write(f"Your age is: {age}")
import matplotlib.pyplot as plt
import numpy as np

chart_data = np.random.randn(50, 3)
st.line_chart(chart_data)

