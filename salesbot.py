import streamlit as st
import requests
from textblob import TextBlob  # type: ignore
import speech_recognition as sr
import csv
import json  # Import the json library

# Load CRM data from a separate JSON file
def load_crm_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load CRM data
CRM_DATA = load_crm_data('crm_data.json')  # Ensure this file is in the same directory

def query_llama_llm(user_input, customer_context):
    url = "https://api.groq.com/openai/v1/chat/completions"  # Endpoint URL
    headers = {
        "Authorization": "Bearer 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",  
        "Content-Type": "application/json"
    }
    
    # Define the prompt with CRM context integration
    negotiation_prompt = (
        f"Your name is Sophiya, an advanced AI-powered Real Estate business Negotiation Coach. "
        f"You are assisting a customer named {customer_context['name']} who prefers {customer_context['preferences']}. "
        f"The customer has previously purchased {', '.join(customer_context['purchase_history'])}. "
        f"During the last interaction, the customer showed interest in '{customer_context['last_interaction']}'. "
        "Analyze the language, sentiment, and tone to provide tailored recommendations and strategies negotiate prices "
        "or discuss queries about products. "
        "Based on the sentiment and intent, respond with effective negotiation strategies and product recommendations. "
        "Maintain a professional tone and aim to maximize customer satisfaction while protecting profitability. "
        "You're in India right now, so give prices in rupees."
    )

    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": negotiation_prompt},
            {"role": "user", "content": user_input}
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.json().get("choices")[0]["message"]["content"]  
    else:
        return "Error in API call: " + response.text


def analyze_sentiment(user_input):
    analysis = TextBlob(user_input)
    polarity = analysis.sentiment.polarity
    if polarity > 0:
        sentiment = "Positive"
    elif polarity < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
    return sentiment, polarity

def live_speech_to_text():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    with microphone as source:
        st.write("**Listening...**")
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source, duration=2)  # Increased duration
        audio = recognizer.listen(source, timeout=10)  # Set a longer timeout
        st.write("**Processing...**")

    attempts = 3
    for i in range(attempts):
        try:
            text = recognizer.recognize_google(audio, language="en-US")  # Specify language
            st.write("**Transcription Successful!**")
            return text
        except sr.UnknownValueError:
            st.write(f"Attempt {i + 1}: Sorry, could not understand the audio. Please try again.")
            if i < attempts - 1:
                with microphone as source:
                    st.write("**Listening again...**")
                    recognizer.adjust_for_ambient_noise(source, duration=2)  # Increased duration
                    audio = recognizer.listen(source, timeout=10)  # Set a longer timeout
                    st.write("**Processing...**")
        except sr.RequestError as e:
            st.write(f"Error with the SpeechRecognition API: {e}")
            return "Error with the SpeechRecognition API."

    return "Sorry, failed to transcribe audio after multiple attempts."

def log_to_csv(file_name, data):
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def main():
    st.set_page_config(page_title="Real Estate Negotiation Coach", layout="wide", initial_sidebar_state="expanded")
    st.title("🤖 Real-Time AI-Powered Sales Intelligence Tool")
    
    st.write("### Instructions:")
    st.markdown("""
    - Type your negotiation details or questions about Real Estate sales.
    - Alternatively, speak into your microphone for live speech-to-text conversion.
    - The assistant will provide insights and analyze the sentiment of your input.
    """)

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    customer_name = st.text_input("Enter Customer Name:", "")
    
    # Define default context values
    default_context = {
        "name": customer_name,
        "preferences": "Not specified",
        "purchase_history": [],
        "last_interaction": "None"
    }

    # Get the context from CRM data or use default
    customer_context = CRM_DATA.get(customer_name.lower(), default_context)

    menu = st.radio("Select Mode:", ["Live Speech to Text", "Text to Text"], index=0)
    
    user_input = ""
    if menu == "Live Speech to Text":
        if st.button("Start Listening", key="listen_button"):
            user_input = live_speech_to_text()  # Convert live speech to text
            st.write(f"**You said:** {user_input}")
    elif menu == "Text to Text":
        user_input = st.text_input("Negotiation coach assistant chatbot:")

    sentiment, sentiment_score = None, None  # Initialize before usage

    if user_input:
        sentiment, sentiment_score = analyze_sentiment(user_input)
        response = query_llama_llm(user_input, customer_context)  # Ensure both args are passed

        st.session_state.chat_history.append({
            "user": user_input,
            "assistant": response,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score
        })

        # Display sentiment and response in a concise format
        st.write("### Output:")
        output_container = st.container()
        with output_container:
            with output_container:
                st.markdown(f"<div style='background-color: #090979; padding: 10px; border-radius: 5px; border: 2px solid #2414ff;'>"
                    f"<strong style='font-weight: bold; color: #0066ff;'>Sentiment:</strong> <strong>{sentiment} (Score: {sentiment_score:.2f})</strong></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color: #090979; padding: 10px; border-radius: 5px; border: 2px solid #2414ff;'>"
                    f"<strong style='font-weight: bold; color: #0066ff;'>Response:</strong> <strong>{response}</strong></div>", unsafe_allow_html=True)


        # Log to CSV only if sentiment is valid
        if sentiment is not None and sentiment_score is not None:
            log_to_csv("sales_data1.csv", [customer_context['name'], user_input, sentiment, sentiment_score, response])

    # Text input for next message (continue the conversation)
    next_user_input = st.text_input("Reply Negotiation coach assistant chatbot:")
    if next_user_input:
        sentiment, sentiment_score = analyze_sentiment(next_user_input)
        response = query_llama_llm(next_user_input, customer_context)  # Ensure both args are passed

        # Log to CSV for the next input
        log_to_csv("sales_data1.csv", [customer_context['name'], next_user_input, sentiment, sentiment_score, response])

if __name__ == "__main__":
    main()
