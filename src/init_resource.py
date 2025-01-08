import os
import streamlit as st

from init import Config as config
from langchain.chains import ConversationalRetrievalChain
from langchain_aws import ChatBedrock
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

import logging
from init import Config as config

# Cache BedrockChat model
@st.cache_resource(show_spinner=False)
def get_chat_model():
    """Initialize and return the BedrockChat model."""
    logging.info("Initializing BedrockChat model...")
    return ChatBedrock(
        model_id=config.BEDROCK_MODEL,
        model_kwargs={"temperature": config.TEMPERATURE},
        region_name=config.AWS_REGION
    )

# Cache HuggingFace embeddings
@st.cache_resource(show_spinner=False)
def get_embeddings():
    """Initialize and return HuggingFace embeddings."""
    logging.info("Initializing HuggingFace embeddings...")
    return HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

# Cache ChromaDB with persistence
@st.cache_resource(show_spinner=False)
def get_vectorstore(_embeddings, persist_directory, collection_name="documents"):
    """Initialize ChromaDB with persistence and transformer embeddings."""
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # Create or load Chroma vector store
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=_embeddings,
        collection_name=collection_name
    )
    
    return vectorstore

@st.cache_resource(show_spinner=False)
def get_conversation_chain(_model, _retriever, _memory):
    """Create and return a conversation chain."""
    logging.info("Creating conversation chain...")
    
    # Define the prompt template
    template = """You are a helpful AI assistant:
    - Answer questions based on uploaded documents
    - Engage in general conversation
    - Maintain context across the chat

    Current conversation:
    {chat_history}

    Context from documents:
    {context}

    Human: {question}
    Assistant:"""

    PROMPT = ChatPromptTemplate.from_template(template)

    return ConversationalRetrievalChain.from_llm(
        llm=_model,
        retriever=_retriever,
        memory=_memory,
        combine_docs_chain_kwargs={"prompt": PROMPT},
        return_source_documents=True,
        verbose=True
    )

