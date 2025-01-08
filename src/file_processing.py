import streamlit as st
from PyPDF2 import PdfReader
from io import BytesIO
from docx import Document

import text_exctraction as gettext
from init import Config as config
import logging
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Constants
CHUNK_SIZE = config.CHUNK_SIZE
CHUNK_OVERLAP = config.CHUNK_OVERLAP

def read_pdf(file: BytesIO) -> str:
    """Reads text from a PDF file."""
    try:
        pdf_reader = PdfReader(file)
        return "\n".join(page.extract_text() or "" for page in pdf_reader.pages).strip()
    except Exception as e:
        st.warning(f"PDF parsing failed. Using OCR as fallback. Error: {e}")
        return gettext.extract_text_from_pdf(file.read())

def read_docx(file: BytesIO) -> str:
    """Reads text from a DOCX file."""
    try:
        doc = Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()
    except Exception as e:
        st.warning(f"Failed to parse DOCX file. Error: {e}")
        return ""

    
def handle_empty_content(file, file_type):
    """Handle empty or unreadable files by attempting OCR."""
    try:
        if file_type == "application/pdf":
            return gettext.extract_text_from_pdf(file.read())
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(BytesIO(file.read()))
            return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()
        else:
            return file.read().decode().strip()
    except Exception as e:
        logging.error(f"Error handling empty content: {e}")
        return "" 
        

def read_generic_file(file: BytesIO, file_type: str) -> str:
    """Reads text from a generic file."""
    try:
        return file.read().decode()
    except Exception as e:
        st.warning(f"Failed to read {file_type} file. Error: {e}")
        return ""
    
# Function to preprocess the content
def preprocess_content(content):
    """Preprocess text to remove excessive whitespace and artifacts."""
    # Normalize whitespace and remove artifacts
    return " ".join(content.split())


# Dynamic chunk size calculation
def get_dynamic_chunk_size(content_length, min_chunk_size=500, max_chunk_size=2000, num_chunks=10):
    """Dynamically adjust chunk size based on content length."""
    return max(min_chunk_size, min(content_length // num_chunks, max_chunk_size))
    

def process_uploaded_files(uploaded_files: list, vectorstore):
    """Processes uploaded files."""
    for file in uploaded_files:
        if file.name in st.session_state.get("processed_files", set()):
            st.info(f"{file.name} already processed.")
            continue

        with st.spinner(f"Processing {file.name}..."):
            try:
                file.seek(0)  # Reset file pointer before reading
                
                # Read file content based on type
                if file.type == "application/pdf":
                    content = read_pdf(BytesIO(file.read()))
                elif ".docx" in file.name:
                    content = read_docx(BytesIO(file.read()))
                else:
                    content = read_generic_file(BytesIO(file.read()), file.type)

                # Fallback to OCR if content is empty
                if not content.strip():
                    st.warning(f"No readable content in {file.name}. Trying OCR fallback.")
                    file.seek(0)
                    content = gettext.extract_text_from_pdf(file.read())

                # Check if fallback also failed
                if not content.strip():
                    st.warning(f"OCR fallback failed for {file.name}. Skipping file.")
                    continue

                # Split text into chunks
                try:
                    preprocessed_content = preprocess_content(content)
                    # Dynamically adjust chunk size based on document length
                    chunk_size = get_dynamic_chunk_size(len(preprocessed_content))
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=chunk_size,
                        chunk_overlap=CHUNK_OVERLAP,
                        separators=["\n\n", "\n", " ", ""]
                    )

                    chunks = text_splitter.split_text(content)
                    if not chunks:
                        st.warning(f"Text splitting failed for {file.name}. Skipping file.")
                        continue

                    # Add to vectorstore
                    vectorstore.add_texts(
                        texts=chunks,
                        metadatas=[{"filename": file.name, "type": file.type}] * len(chunks)
                    )

                    # Mark file as processed
                    st.session_state.processed_files.add(file.name)
                    st.success(f"Text from {file.name} was successfully split into {len(chunks)} chunks!")
                except Exception as e:
                    st.error(f"Error during text splitting for {file.name}: {e}")   

            except Exception as e:
                st.error(f"Error processing {file.name}: {e}")