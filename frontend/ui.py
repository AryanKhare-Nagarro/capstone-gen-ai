import streamlit as st
import requests
import os
import time

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Multimodal RAG", page_icon="📚", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .upload-box { 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border: 1px solid #ddd;
    }
    .query-box { 
        padding: 20px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #ddd;
    }
    .result-box { 
        border-left: 4px solid #0066cc; 
        padding: 15px; 
        border-radius: 5px; 
        margin-top: 15px;
        border: 1px solid #ddd;
    }
    .success-box { 
        padding: 10px; 
        border-radius: 5px; 
        color: #155724; 
        border: 1px solid #c3e6cb;
        background-color: #f8fff9;
    }
    .error-box { 
        padding: 10px; 
        border-radius: 5px; 
        color: #721c24; 
        border: 1px solid #f5c6cb;
        background-color: #fff8f8;
    }
    </style>
""", unsafe_allow_html=True)

def upload_file(file):
    """Upload file to API"""
    files = {"file": (file.name, file, file.type)}
    try:
        response = requests.post(f"{API_BASE_URL}/upload/", files=files)
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def query_documents(query):
    """Query documents through API"""
    try:
        response = requests.post(f"{API_BASE_URL}/query/", json={"query": query})
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)

def main():
    st.title("📚 Multimodal RAG Application")
    st.markdown("Process PDFs and SQLite databases with AI-powered queries")
    
    # Initialize session state
    if "file_processed" not in st.session_state:
        st.session_state.file_processed = False
    if "processing_message" not in st.session_state:
        st.session_state.processing_message = ""
    if "query_history" not in st.session_state:
        st.session_state.query_history = []

    # File Upload Section
    st.markdown('<div class="upload-box">', unsafe_allow_html=True)
    st.subheader("📁 Upload Document")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF or SQLite database file",
        type=["pdf", "db"],
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        if st.button("📤 Process File", use_container_width=True):
            with st.spinner("Processing your file..."):
                result, error = upload_file(uploaded_file)
                if result:
                    st.session_state.file_processed = True
                    st.session_state.processing_message = f"✅ {result['message']} ({result['data_items_count']} items)"
                    st.markdown(f'<div class="success-box">{st.session_state.processing_message}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Error: {error}</div>', unsafe_allow_html=True)
    
    if st.session_state.processing_message and st.session_state.file_processed:
        st.markdown(f'<div class="success-box">{st.session_state.processing_message}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Query Section
    st.markdown('<div class="query-box">', unsafe_allow_html=True)
    st.subheader("💬 Ask Questions")
    
    # Check if file is processed
    if not st.session_state.file_processed:
        st.info("👆 Please upload and process a file first")
    else:
        # Query input
        query = st.text_input("Enter your question:", placeholder="e.g., What is the transformer architecture?")
        
        col1, col2 = st.columns(2)
        with col1:
            submit_button = st.button("🔍 Ask", use_container_width=True, type="primary")
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.session_state.query_history = []
            st.experimental_rerun()
        
        if submit_button and query:
            with st.spinner("Thinking..."):
                result, error = query_documents(query)
                if result:
                    # Add to history
                    st.session_state.query_history.append({
                        "query": query,
                        "answer": result["answer"],
                        "timestamp": time.strftime("%H:%M:%S")
                    })
                    st.markdown("**🤖 Answer:**")
                    st.markdown(f'<div class="result-box">{result["answer"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="error-box">❌ Error: {error}</div>', unsafe_allow_html=True)
        
        # Display query history
        if st.session_state.query_history:
            st.subheader("📝 History")
            for i, item in enumerate(reversed(st.session_state.query_history[-5:])):  # Show last 5
                with st.expander(f"Q: {item['query'][:50]}{'...' if len(item['query']) > 50 else ''}"):
                    st.markdown(f"**⏰ {item['timestamp']}**")
                    st.markdown(f"**🤖 Answer:** {item['answer']}")

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; font-size: 12px;">
            Multimodal RAG Application - Process PDFs and databases with AI
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/health/")
        if response.status_code == 200:
            main()
        else:
            st.error(" Backend API is not responding. Please start the API server.")
            st.info("Run in terminal: `uvicorn api:app --reload`")
    except requests.exceptions.ConnectionError:
        st.error(" Cannot connect to backend API. Please start the API server.")
        st.info("Run in terminal: `uvicorn api:app --reload`")