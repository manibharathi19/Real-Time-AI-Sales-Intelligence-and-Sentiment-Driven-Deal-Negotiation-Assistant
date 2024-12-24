import pyaudio
import wave
import keyboard
import faster_whisper
import torch.cuda
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import stream
import requests
from transformers import pipeline

# Set environment variables
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
elevenlabs_client = ElevenLabs(api_key="sk_5441a78ec19cb8391850566ba198addcf395b6ea2141407b")  # Replace with your ElevenLabs API key

# System prompt for Groq API
groq_system_prompt = {
    "role": "system",
    "content": (
        "Your name is Sophiya , and you are an advanced AI-powered Negotiation Coach. "
        "You are assisting customers with real-time sentiment and intent analysis to negotiate prices "
        "or discuss queries about products. "
        "You analyze live speech streams and text to detect sentiment changes in tone, language, and context. "
        "You provide concise insights about the speaker's emotional state and intent, such as: "
        "'Positive and Engaged', 'Neutral with Doubt', or 'Negative and Frustrated'. "
        "Based on the sentiment and intent, respond with effective negotiation strategies and product recommendations. "
        "Maintain a professional tone and aim to maximize customer satisfaction while protecting profitability. "
        "Available products: Mango - 1kg - 100rs, Apple - 1kg - 150rs, Orange - 1kg - 200rs. "
        "Steps to follow in every interaction: "
        "1. Monitor sentiment and intent (e.g., polite, frustrated, firm, or casual). "
        "2. Provide feedback explaining the product's value or available options. "
        "3. Suggest strategic offers like combo discounts, minor price reductions, or value-add options. "
        "4. Adapt responses dynamically to maintain customer engagement and ensure a positive experience."
    )
}

# Initialize Whisper model
model = faster_whisper.WhisperModel(model_size_or_path="tiny.en", device='cuda' if torch.cuda.is_available() else 'cpu')
answer, history = "", []

# Load sentiment analysis model
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased")

# Function to call Groq API
def call_groq_api(messages):
    api_key = "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"  # Replace with your Groq API key
    api_url = "https://api.groq.com/openai/v1/chat/completions"  # Replace with the actual Groq API endpoint

    payload = {
        "model": "llama3-8b-8192",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            return response_data["choices"][0]["message"]["content"]
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return "I'm having trouble connecting to my brain right now. Try again later!"
    except Exception as e:
        print(f"Exception occurred: {e}")
        return "Oops, something went wrong!"

# Function to analyze sentiment
def analyze_sentiment(text):
    result = sentiment_analyzer(text)
    sentiment = result[0]["label"]  # Example: 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    return sentiment

# Function to deduce intent
def detect_intent(user_text):
    if "discount" in user_text.lower():
        return "Wants a discount"
    elif "combo" in user_text.lower():
        return "Interested in combos"
    else:
        return "General inquiry"

# Function to process response
def generate_response_with_analysis(messages, user_text):
    sentiment = analyze_sentiment(user_text)
    intent = detect_intent(user_text)

    print(f"Detected Sentiment: {sentiment}")
    print(f"Detected Intent: {intent}")

    additional_context = {
        "role": "assistant",
        "content": f"Customer sentiment: {sentiment}. Detected intent: {intent}."
    }
    messages.append(additional_context)

    response = call_groq_api(messages)
    print(response, flush=True)
    return response

while True:
    print("\n\nTap space when you're ready. ", end="", flush=True)
    keyboard.wait('space')
    while keyboard.is_pressed('space'): pass

    print("I'm all ears. Tap space when you're done.\n Products: \n 1.Mango-100rs \n 2.Apple-150rs \n 3.Orange-200rs")

    audio, frames = pyaudio.PyAudio(), []
    py_stream = audio.open(rate=16000, format=pyaudio.paInt16, channels=1, input=True, frames_per_buffer=512)
    while not keyboard.is_pressed('space'):
        frames.append(py_stream.read(512))
    py_stream.stop_stream(), py_stream.close(), audio.terminate()

    with wave.open("voice_record.wav", 'wb') as wf:
        wf.setparams((1, audio.get_sample_size(pyaudio.paInt16), 16000, 0, 'NONE', 'NONE'))
        wf.writeframes(b''.join(frames))

    transcription_result = model.transcribe("voice_record.wav", language="en")[0]
    user_text = " ".join(seg.text for seg in transcription_result)
    print(f'>>>{user_text}\n<<< ', end="", flush=True)
    history.append({'role': 'user', 'content': user_text})

    assistant_response = generate_response_with_analysis([groq_system_prompt] + history[-10:], user_text)

    stream(
        elevenlabs_client.generate(
            text=assistant_response,
            voice="Nicole",
            model="eleven_monolingual_v1",
            stream=True
        )
    )

    history.append({'role': 'assistant', 'content': assistant_response})
