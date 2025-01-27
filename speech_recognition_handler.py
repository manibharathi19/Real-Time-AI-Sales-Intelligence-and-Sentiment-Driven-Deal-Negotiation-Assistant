# speech_recognition_handler.py
import speech_recognition as sr
from datetime import datetime
import streamlit as st
from typing import Tuple

# Initialize recognizer
r = sr.Recognizer()

def listen_and_convert() -> Tuple[str, str]:
    """
    Captures audio from the microphone and transcribes it using Google Speech Recognition.
    """
    with sr.Microphone() as source:
        st.info("Listening for speech...")
        audio = r.listen(source)

        try:
            # Use Wit.ai as an alternative to Google Speech Recognition
            text = r.recognize_wit(audio, key="HTIEDSIZCFOFESXSRDC7FJ66WAJK5A72")
            st.success(f"Recognized text: {text}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return timestamp, text
        except sr.UnknownValueError:
            st.error("Could not understand the audio.")
            return None, None
        except sr.RequestError as e:
            st.error(f"Wit.ai Speech Recognition error: {e}")
            return None, None
