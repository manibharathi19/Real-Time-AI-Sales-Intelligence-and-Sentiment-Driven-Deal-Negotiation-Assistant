import streamlit as st
import groq
from config import GROQ_API_KEY

# Initialize Groq client
client = groq.Groq(api_key=GROQ_API_KEY)

def analyze_conversation(text):
    """
    Comprehensive conversation analysis
    """
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an advanced Real Estate Negotiation AI. "
                        "Analyze the following customer statement and provide: "
                        "1. Sentiment (Positive/Neutral/Negative) "
                        "2. Primary Intent "
                        "3. Recommended Negotiation Approach"
                    )
                },
                {"role": "user", "content": text}
            ],
            max_tokens=100
        )
        
        analysis_text = response.choices[0].message.content
        
        # Parse analysis
        sentiment = 'Neutral'
        intent = 'Inquiry'
        
        if 'positive' in analysis_text.lower():
            sentiment = 'Positive'
        elif 'negative' in analysis_text.lower():
            sentiment = 'Negative'
        
        # Extract intent from analysis
        if 'buy' in text.lower():
            intent = 'Purchase Inquiry'
        elif 'price' in text.lower():
            intent = 'Price Negotiation'
        elif 'location' in text.lower():
            intent = 'Location Preference'
        
        return {
            'sentiment': sentiment,
            'intent': intent,
            'full_analysis': analysis_text
        }
    
    except Exception as e:
        st.error(f"Analysis Error: {e}")
        return {
            'sentiment': 'Neutral',
            'intent': 'General Inquiry',
            'full_analysis': 'Unable to process analysis'
        }

def generate_ai_response(customer_text, analysis):
    """
    Generate contextual AI response
    """
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a professional Real Estate Agent. "
                        f"Customer Sentiment: {analysis['sentiment']} "
                        f"Customer Intent: {analysis['intent']} "
                        "Provide a precise, helpful response."
                    )
                },
                {"role": "user", "content": customer_text}
            ],
            max_tokens=150
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        st.error(f"Response Generation Error: {e}")
        return "I'm here to help. Could you tell me more about what you're looking for in a property?"

def generate_summary_with_groq(conversation):
    """
    Sends the entire conversation to Groq for summarization.
    """
    try:
        conversation_text = "\n".join([f"{timestamp}: {text}" for timestamp, text in conversation])
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI summarization assistant. Generate a concise summary of the following conversation in 3-4 sentences."
                    ),
                },
                {"role": "user", "content": conversation_text},
            ],
            max_tokens=150
        )
        
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Summary generation failed: {e}")
        return "Summary generation failed."