import tempfile
import streamlit as st
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader, UnstructuredCSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Pinecone
from langchain_core.prompts import PromptTemplate
from langchain.schema import Document
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone as pc, ServerlessSpec
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import time
import speech_recognition as sr
import threading
import queue
from datetime import datetime
import pyaudio
import wave
import numpy as np

# Load environment variables
load_dotenv()

class AudioHandler:
    def __init__(self):
        self.chunk = 1024
        self.format = pyaudio.paFloat32
        self.channels = 1
        self.rate = 16000
        self.record_seconds = 5
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.stream = None
        self.is_recording = False

    def start_stream(self):
        self.stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        self.is_recording = True

    def stop_stream(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.is_recording = False
        self.frames = []

    def get_audio_data(self):
        if self.is_recording and self.stream:
            try:
                data = self.stream.read(self.chunk)
                self.frames.append(data)
                return np.frombuffer(data, dtype=np.float32)
            except Exception as e:
                print(f"Error reading audio: {e}")
                return None
        return None

def app():
    st.title("VOICE-ENABLED NEGOTIATION COACH")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'audio_handler' not in st.session_state:
        st.session_state.audio_handler = AudioHandler()
    if 'recognizer' not in st.session_state:
        st.session_state.recognizer = sr.Recognizer()

    def train_chatbot():
        try:
            embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
            index_name = "documentindex"
            pine = pc(api_key=os.getenv("PINECONE_API_KEY"))
            cloud = os.getenv('PINECONE_CLOUD', 'aws')
            region = os.getenv('PINECONE_REGION', 'us-east-1')
            spec = ServerlessSpec(cloud=cloud, region=region)

            if index_name not in pine.list_indexes().names():
                pine.create_index(
                    name=index_name, 
                    dimension=384,  # dimension for all-MiniLM-L6-v2
                    metric="cosine", 
                    spec=spec
                )
                while not pine.describe_index(index_name).status['ready']:
                    time.sleep(1)

            vector_store = PineconeVectorStore.from_existing_index(index_name, embeddings)

            prompt_template = """
            You are a live real estate negotiation assistant processing real-time conversation.
            provide price also details discuss abot reduce 10% of the place of price dont give blindly for 10% negotiate to customer 
            Based on the context and current query, provide immediate, relevant advice.
            
            Context: {context}
            Current Query: {question}
            
            Focus on:
            1. Quick, actionable responses
            2. Clear negotiation strategies
            3. Immediate price analysis
            4. Direct property recommendations
            
            Provide concise, real-time guidance that can be immediately useful in the conversation.
            """
            prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

            llm = ChatGroq(
                model_name="llama-3.2-1b-preview",
                api_key=os.getenv("GROQ_API_KEY"),
                temperature=0.7
            )
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt},
            )

            return qa_chain
            
        except Exception as e:
            st.error(f"Error during initialization: {e}")
            return None

    # Initialize chatbot
    if 'qa_chain' not in st.session_state:
        with st.spinner("Initializing AI Assistant..."):
            st.session_state.qa_chain = train_chatbot()

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(f"{message['content']}")
                st.caption(f"{message['timestamp']}")

    # Live speech processing
    def process_speech():
        try:
            with sr.Microphone() as source:
                st.session_state.recognizer.adjust_for_ambient_noise(source)
                audio = st.session_state.recognizer.listen(source, timeout=5)
                text = st.session_state.recognizer.recognize_google(audio)
                return text
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            st.error(f"Error processing speech: {e}")
            return None

    # Real-time response processing
    def get_ai_response(text):
        try:
            if st.session_state.qa_chain:
                result = st.session_state.qa_chain.invoke(text)
                return result['result']
            return "Assistant not initialized properly."
        except Exception as e:
            return f"Error getting response: {e}"

    # Voice interface
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Speaking"):
            st.session_state.is_speaking = True
            st.success("Listening... Speak your question!")
            
            # Start real-time speech processing
            while st.session_state.is_speaking:
                text = process_speech()
                if text:
                    # Add user message
                    timestamp = datetime.now().strftime("%I:%M %p")
                    st.session_state.messages.append({
                        "role": "user",
                        "content": text,
                        "timestamp": timestamp
                    })
                    
                    # Get and add AI response
                    response = get_ai_response(text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": timestamp
                    })
                    
                    st.experimental_rerun()

    with col2:
        if st.button("Stop Speaking"):
            st.session_state.is_speaking = False
            st.warning("Stopped listening.")

    # Text input as backup
    with st.container():
        if user_input := st.chat_input("Type your message here..."):
            timestamp = datetime.now().strftime("%I:%M %p")
            
            # Add user message
            st.session_state.messages.append({
                "role": "user",
                "content": user_input,
                "timestamp": timestamp
            })
            
            # Get and add AI response
            response = get_ai_response(user_input)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": timestamp
            })
            
            st.experimental_rerun()

if __name__ == "__main__":
    app()