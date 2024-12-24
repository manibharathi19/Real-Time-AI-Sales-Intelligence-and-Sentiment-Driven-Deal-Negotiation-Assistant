import streamlit as st
import requests
from textblob import TextBlob  # type: ignore
import speech_recognition as sr

def query_llama_llm(user_input):
    url = "https://api.groq.com/openai/v1/chat/completions"  # Endpoint URL
    headers = {
        "Authorization": "Bearer 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",  
        "Content-Type": "application/json"
    }
    
    # Define the prompt 
    negotiation_prompt = (
        "You are a negotiation coach assistant chatbot. Your goal is to provide insights and "
        "strategies for successful negotiation based on user inputs. "
        "Respond to the user in a helpful and informative manner. And Give the output response in 2 to 3 lines."
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

def speech_to_text(audio_file):
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)  # Read the entire audio file
            text = recognizer.recognize_google(audio)  # Use Google Web Speech API
            return text
    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except sr.RequestError as e:
        return f"Error with the SpeechRecognition API: {e}"

def main():
    st.title("Real-Time AI Sales Intelligence and Sentiment-Driven Deal Negotiation Assistant")
    st.write("### Instructions:")
    st.write("1. Type your negotiation details or questions about sales.")
    st.write("2. Alternatively, upload an audio file for speech-to-text conversion.")
    st.write("3. The assistant will provide insights and analyze the sentiment of your input.")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    menu = st.radio("Select Mode:", ["Speech to Text", "Text to Text"])
    
    user_input = ""
    if menu == "Speech to Text":
        audio_file = st.file_uploader("Upload audio file:", type=["wav", "flac", "mp3"])
        if audio_file and st.button("Convert Speech to Text"):
            user_input = speech_to_text(audio_file)  # Convert audio to text
            st.write(f"**You said:** {user_input}")
    elif menu == "Text to Text":
        user_input = st.text_input("Negotiation coach assistant chatbot:")

    if user_input:
        sentiment, sentiment_score = analyze_sentiment(user_input)
        response = query_llama_llm(user_input)
        
        st.session_state.chat_history.append({
            "user": user_input,
            "assistant": response,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score
        })

        # Display sentiment and response in a concise format
        st.write("### Output:")
        st.markdown(f"**Sentiment:** {sentiment} (Score: {sentiment_score:.2f})")
        st.markdown(f"**Response:** {response}")

    # Text input for next message (continue the conversation)
    user_input = st.text_input("Reply Negotiation coach assistant chatbot:")


    # if st.session_state.chat_history:
    #     st.write("### History:")
    #     for chat in st.session_state.chat_history:
    #         st.markdown(f"**You:** {chat['user']}")
    #         st.markdown(f"**Assistant:** {chat['assistant']} (Sentiment: {chat['sentiment']}, Score: {chat['sentiment_score']:.2f})")
    #         st.write("---")

if __name__ == "__main__":
    main()
