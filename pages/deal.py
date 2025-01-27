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

from torch import embedding_bag

# API Keys

load_dotenv()





def app():
    # Function to train chatbot
    def train_chatbot():
        try:
            embeddings=HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
            # Initialize Pinecone
            index_name = "documentindex"
            pine = pc(api_key=os.getenv("PINECONE_API_KEY"))
            cloud = os.getenv('PINECONE_CLOUD', 'aws')
            region = os.getenv('PINECONE_REGION', 'us-east-1')
            spec = ServerlessSpec(cloud=cloud, region=region)

            if index_name not in pine.list_indexes().names():
                
                pine.create_index(name=index_name, dimension=embedding_bag, metric="cosine", spec=spec)
                while not pine.describe_index(index_name).status['ready']:
                    time.sleep(1)

            # Create vector store
            
            vector_store= PineconeVectorStore.from_existing_index(index_name, embeddings)

            prompt_template = """
            From the given information, answer the user's question. 
            If you don't know the answer, say you don't know. Do not fabricate answers.
            Context: {context}
            Question: {question}
            Only return the appropriate answer and also your negotition with customer.
            """
            prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])

            llm = ChatGroq(model_name="llama-3.2-1b-preview", api_key=os.getenv("GROQ_API_KEY"), temperature=0)
            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(search_kwargs={"k": 10}),
                return_source_documents=True,
                chain_type_kwargs={"prompt": prompt},
            )

            st.success("ChatBot is ready!")
            st.session_state['qa_chain'] = qa_chain
        except Exception as e:
            st.error(f"Error during training: {e}")


    # Handle data upload and chatbot training

    train_chatbot()

    # Question answering interface
    st.divider()
    st.subheader("Ask Your Question")
    user_question = st.text_input("Type your Question Here:")
    if st.button("Answer"):
        if user_question:
            qa_chain = st.session_state['qa_chain']
            if qa_chain:
                result = qa_chain.invoke(user_question)
                st.write(result['result'])
            else:
                st.warning("Please upload data and create the chatbot first.")
        else:
            st.warning("Please enter a question.")
