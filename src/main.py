# Now import everything else
import streamlit as st
from langchain.memory import ConversationBufferMemory
from init import Config as config
import file_processing as processing
import init_resource as resource

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'vectorstore' not in st.session_state:
    # Initialize embeddings
    embeddings = resource.get_embeddings()

    # Initialize vector store
    vectorstore = resource.get_vectorstore(embeddings, persist_directory=config.PERSIST_DIR)
    st.session_state.vectorstore = vectorstore

    # Initialize chat model and memory
    model = resource.get_chat_model()
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )
    st.session_state.memory = memory

    # Create and store the conversation chain
    st.session_state.chain = resource.get_conversation_chain(
        model,
        vectorstore.as_retriever(search_kwargs={"k": config.NUM_CHUNKS}),
        memory
    )

if 'processed_files' not in st.session_state:
    st.session_state.processed_files = set()

# Streamlit UI
st.title("🤖 AI Assistant & Document Chat")
st.markdown("""
This AI assistant can:
- Answer questions about your uploaded documents
- Remember details from your conversation
- Help with general questions
- Maintain context across the chat
""")

# Sidebar for file upload
with st.sidebar:
    st.header("📄 Document Upload")
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["txt", "pdf", "doc", "docx"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    if uploaded_files:
        processing.process_uploaded_files(uploaded_files,  st.session_state.vectorstore)

    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.session_state.memory.clear()
        st.rerun()

# Chat interface
chat_container = st.container()
with chat_container:
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message("assistant" if message["is_assistant"] else "user"):
            st.write(message["content"])
            if message.get("sources"):
                with st.expander("View sources"):
                    for source in message["sources"]:
                        st.markdown(f"""
                        **From**: {source['filename']}
                        **Text**: \n\n{source['text']}
                        ---
                        """)

# User input
if question := st.chat_input("Ask a question about your documents or chat with me"):
    # Add user message to chat
    st.session_state.chat_history.append({"is_assistant": False, "content": question})
    
    # Get response from chain
    try:
        result = st.session_state.chain({"question": question})
        answer = result["answer"]
        sources = []
        
        if result.get("source_documents"):
            for doc in result["source_documents"]:
                sources.append({
                    "filename": doc.metadata.get("filename", "Unknown"),
                    "text": doc.page_content
                })
        
        # Add assistant response to chat
        st.session_state.chat_history.append({
            "is_assistant": True,
            "content": answer,
            "sources": sources if sources else None
        })
        
        # Rerun to update chat display
        st.rerun()
        
    except Exception as e:
        st.error(f"Error: {str(e)}")     



