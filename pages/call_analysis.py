import streamlit as st
import pandas as pd
import plotly.express as px
import pathlib
import time
import uuid
from speech_recognition_handler import listen_and_convert
from text_analysis_handler import analyze_conversation, generate_ai_response, generate_summary_with_groq
import groq
from config import GROQ_API_KEY

def app():
    st.title("Real Estate AI Negotiation Assistant")
    client = groq.Groq(api_key=GROQ_API_KEY)

    # Initialize session state
    if 'conversations' not in st.session_state:
        st.session_state.update({
            'conversations': [],
            'session_id': str(uuid.uuid4()),
            'listening_mode': False
        })

    # User inputs and UI setup
    username = st.text_input("Enter your name:", key="call_username")
    if not username:
        st.warning("Please enter your name to proceed.")
        return

    # UI Components
    conversation_display = st.empty()
    visualization_area = st.empty()
    col1, col2 = st.columns(2)
    
    with col1:
        start_listening = st.button("Start Conversation")
    with col2:
        stop_listening = st.button("End Conversation")

    def update_conversation_display():
        conversation_display.text_area(
            "Transcripts", 
            "\n".join([f"{conv['speaker']}: {conv['text']}" for conv in st.session_state.conversations]), 
            height=300
        )

    def create_interactive_visualization():
        if len(st.session_state.conversations) < 2:
            return
        
        df = pd.DataFrame(st.session_state.conversations)
        
        sentiment_fig = px.pie(
            df[df['speaker'] == 'Customer'], 
            names='sentiment', 
            title='Customer Sentiment Distribution',
            color='sentiment',
            color_discrete_map={'Positive': 'green', 'Neutral': 'blue', 'Negative': 'red'}
        )
        
        intent_fig = px.bar(
            df[df['speaker'] == 'Customer'], 
            x='intent', 
            title='Customer Intent Analysis',
            color='intent'
        )
        
        col1, col2 = visualization_area.columns(2)
        with col1:
            st.plotly_chart(sentiment_fig, use_container_width=True)
        with col2:
            st.plotly_chart(intent_fig, use_container_width=True)

    def analyze_conversation_performance():
        customer_conversations = [conv for conv in st.session_state.conversations if conv['speaker'] == 'Customer']
        
        sentiment_map = {'Positive': 1, 'Neutral': 0, 'Negative': -1}
        sentiment_scores = [sentiment_map.get(conv['sentiment'], 0) for conv in customer_conversations]
        
        return {
            'engagement_score': len(customer_conversations),
            'sentiment_positivity': (sum(score > 0 for score in sentiment_scores) / len(sentiment_scores)) * 100 if sentiment_scores else 0,
            'conversion_potential': calculate_conversion_potential(customer_conversations)
        }

    def calculate_conversion_potential(conversations):
        intent_conversion_weights = {
            'Purchase Inquiry': 0.7,
            'Price Negotiation': 0.5,
            'Location Preference': 0.3,
            'General Inquiry': 0.2
        }
        
        conversion_scores = [intent_conversion_weights.get(conv['intent'], 0.1) for conv in conversations]
        return (sum(conversion_scores) / len(conversion_scores) * 100) if conversion_scores else 0

    def save_conversation_details(username, session_id, conversations, summary, metrics):
        transcribe_dir = pathlib.Path(r"C:\Users\HP\Desktop\sai_deal_code\Customers_Transcribe")
        transcribe_dir.mkdir(parents=True, exist_ok=True)
        
        pd.DataFrame(conversations).to_excel(transcribe_dir / f"{username}_transcript.xlsx", index=False)
        pd.DataFrame([metrics]).to_excel(transcribe_dir / f"{username}_metrics.xlsx", index=False)
        
        with open(transcribe_dir / f"{username}_post_call_summary.txt", 'w') as f:
            f.write(summary)

    def negotiate_conversation():
        st.info("Real Estate Negotiation Mode - Start Speaking")
        
        while st.session_state.get('listening_mode', False):
            try:
                timestamp, customer_text = listen_and_convert()
                
                if customer_text and customer_text.strip():
                    conversation_analysis = analyze_conversation(customer_text)
                    ai_response = generate_ai_response(customer_text, conversation_analysis)
                    
                    # Quickly append conversations
                    st.session_state.conversations.extend([
                        {
                            'timestamp': timestamp,
                            'speaker': 'Customer',
                            'text': customer_text,
                            'sentiment': conversation_analysis['sentiment'],
                            'intent': conversation_analysis['intent']
                        },
                        {
                            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                            'speaker': 'AI',
                            'text': ai_response,
                            'sentiment': 'Neutral',
                            'intent': 'Response'
                        }
                    ])
                    
                    update_conversation_display()
                    create_interactive_visualization()
                
                time.sleep(0.1)  # Reduced sleep time for faster recognition
            
            except Exception as e:
                st.error(f"Negotiation Error: {e}")
                break

    # Conversation Control
    if start_listening:
        st.session_state.listening_mode = True
        negotiate_conversation()

    if stop_listening:
        st.session_state.listening_mode = False
        
        if st.session_state.conversations:
            conversation_summary = generate_summary_with_groq(
                [(conv['timestamp'], conv['text']) for conv in st.session_state.conversations]
            )
            
            performance_metrics = analyze_conversation_performance()
            
            save_conversation_details(
                username, 
                st.session_state.session_id, 
                st.session_state.conversations, 
                conversation_summary, 
                performance_metrics
            )
            
            st.success("Conversation Analysis Complete")
            st.subheader("Conversation Summary")
            st.write(conversation_summary)
            
            st.subheader("Performance Metrics")
            performance_display = st.columns(3)
            with performance_display[0]:
                st.metric("Engagement Score", f"{performance_metrics['engagement_score']:.2f}")
            with performance_display[1]:
                st.metric("Sentiment Positivity", f"{performance_metrics['sentiment_positivity']:.2f}%")
            with performance_display[2]:
                st.metric("Conversion Potential", f"{performance_metrics['conversion_potential']:.2f}%")
            
            st.session_state.conversations = []

if __name__ == "__main__":
    app()