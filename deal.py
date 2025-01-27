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
from queue import Queue
from threading import Lock

# Load environment variables
load_dotenv()

# Create a queue for real-time conversation
conversation_queue = Queue()
chat_lock = Lock()

def app():
    # Initialize session state for conversation history
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    
    def train_chatbot():
        try:
            embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
            index_name = "documentindex"
            pine = pc(api_key=os.getenv("PINECONE_API_KEY"))
            cloud = os.getenv('PINECONE_CLOUD', 'aws')
            region = os.getenv('PINECONE_REGION', 'us-east-1')
            spec = ServerlessSpec(cloud=cloud, region=region)

            if index_name not in pine.list_indexes().names():
                pine.create_index(name=index_name, dimension=384, metric="cosine", spec=spec)
                while not pine.describe_index(index_name).status['ready']:
                    time.sleep(1)

            vector_store = PineconeVectorStore.from_existing_index(index_name, embeddings)

            # Updated prompt template to handle conversation context
            prompt_template = """
            You are a real estate assistant handling a live conversation. Use the context and conversation history to provide relevant answers.
            
            Previous conversation history: {history}
            Context from documents: {context}
            Current question/statement: {question}
            
            Provide a natural, conversational response that addresses the current query while maintaining context from the conversation history.
            """
            prompt = PromptTemplate(
                template=prompt_template, 
                input_variables=["context", "question", "history"]
            )

            llm = ChatGroq(
                model_name="llama-3.2-1b-preview", 
                api_key=os.getenv("GROQ_API_KEY"), 
                temperature=0.7  # Slightly increased temperature for more natural conversation
            )
            
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(search_kwargs={"k": 10}),
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt},
            )

            st.success("ChatBot is ready for live conversation!")
            st.session_state['qa_chain'] = qa_chain
            
        except Exception as e:
            st.error(f"Error during training: {e}")

    def process_live_input(text_input):
        """Process incoming live speech input"""
        with chat_lock:
            qa_chain = st.session_state.get('qa_chain')
            if not qa_chain:
                return "Chatbot is not initialized yet."
            
            # Format conversation history
            history = "\n".join([
                f"{'Customer' if i%2==0 else 'Assistant'}: {msg}"
                for i, msg in enumerate(st.session_state.conversation_history[-6:])  # Keep last 6 messages for context
            ])
            
            # Prepare the query with conversation history
            result = qa_chain.invoke({
                "question": text_input,
                "history": history
            })
            
            # Update conversation history
            st.session_state.conversation_history.extend([text_input, result['result']])
            
            return result['result']

    def handle_continuous_conversation():
        """Handle continuous conversation from speech input"""
        placeholder = st.empty()
        while True:
            if not conversation_queue.empty():
                incoming_text = conversation_queue.get()
                response = process_live_input(incoming_text)
                
                # Update display
                with placeholder.container():
                    for i, message in enumerate(st.session_state.conversation_history[-10:]):  # Show last 10 messages
                        role = "Customer" if i % 2 == 0 else "Assistant"
                        st.text(f"{role}: {message}")
            
            time.sleep(0.1)  # Prevent excessive CPU usage

    # Initialize chatbot
    train_chatbot()

    # Start continuous conversation handler
    handle_continuous_conversation()

    # Add a way to manually input questions for testing
    st.divider()
    st.subheader("Manual Input (For Testing)")
    user_question = st.text_input("Type your question here:")
    if st.button("Send"):
        if user_question:
            conversation_queue.put(user_question)
        else:
            st.warning("Please enter a question.")

def add_to_conversation(text):
    """External function to add speech input to the conversation queue"""
    conversation_queue.put(text)

if __name__ == "__main__":
    app()