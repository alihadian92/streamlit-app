import streamlit as st
from google.cloud import texttospeech
import os

# تنظیم کلید API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "AIzaSyBaKDrDQ55nFvS4JSYWZEf0kTZUn9wMmWQ"

# ایجاد کلاینت Google Text-to-Speech
client = texttospeech.TextToSpeechClient()

def synthesize_text(text):
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config)

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
    return "output.mp3"

st.title("Text-to-Speech Web App")

# گرفتن ورودی از کاربر
text = st.text_area("Enter text for voice-over")

if st.button("Convert"):
    if text:
        output = synthesize_text(text)
        st.audio(output, format="audio/mp3")
    else:
        st.warning("Please enter some text.")
