import requests
import streamlit as st

def text_to_speech(text):
    api_key = "AIzaSyBaKDrDQ55nFvS4JSYWZEf0kTZUn9wMmWQ"
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "input": {"text": text},
        "voice": {"languageCode": "en-US", "ssmlGender": "NEUTRAL"},
        "audioConfig": {"audioEncoding": "MP3"}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        audio_content = response.json()['audioContent']
        with open("output.mp3", "wb") as f:
            f.write(audio_content.encode('latin1'))
        return "output.mp3"
    else:
        st.error("Error: " + str(response.status_code))

# Streamlit app interface
st.title("Text-to-Speech Web App")
text = st.text_area("Enter text for voice-over")
if st.button("Convert"):
    if text:
        output = text_to_speech(text)
        st.audio(output, format="audio/mp3")
    else:
        st.warning("Please enter some text.")
