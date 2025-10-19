"""
AI Chat UI - Streamlit Interface for RAG System
Supports natural language queries and document uploads (PDF, Word, Excel, etc.)
"""
import streamlit as st
import httpx
import os
from typing import List, Dict, Any
import io

# Import Talentys theme
try:
    from config.talentys_theme import get_company_info
    COMPANY_INFO = get_company_info()
except:
    COMPANY_INFO = {
        "name": "Talentys",
        "tagline": "Data Engineering & Analytics Excellence",
        "website": "https://talentys.eu",
        "email": "support@talentys.eu",
        "logo_local": "static/img/talentys-logo.png"
    }

# Configuration
RAG_API_URL = os.getenv("RAG_API_URL", "http://rag-api:8002")
TIMEOUT = 120.0

# Get version from environment variable (set in docker-compose.yml)
PLATFORM_VERSION = os.getenv("PLATFORM_VERSION", "v1.1.0")

# Page configuration
st.set_page_config(
    page_title="AI Data Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Sidebar logo en haut */
    [data-testid="stSidebarNav"] {
        padding-top: 2rem;
        background-image: url('static/img/talentys-logo.png');
        background-repeat: no-repeat;
        background-position: center 1rem;
        background-size: 60px;
    }
    
    .sidebar-logo {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-logo img {
        width: 80px;
        height: auto;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .source-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .score-badge {
        background-color: #1f77b4;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 0.3rem;
        font-size: 0.8rem;
    }
    .upload-section {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "uploaded_files_count" not in st.session_state:
    st.session_state.uploaded_files_count = 0

# Header
st.markdown('<div class="main-header">🤖 AI Data Assistant</div>', unsafe_allow_html=True)
st.markdown("Ask questions about your data or upload documents to expand the knowledge base")

# Sidebar
with st.sidebar:
    # Logo Talentys monochrome centré en haut de la sidebar
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("static/img/talentys-logo-mono.png", width=80)
    st.markdown("---")
    
    st.header("⚙️ Configuration")
    
    # Model selection
    available_models = ["llama3.1", "mistral", "phi3", "codellama"]
    selected_model = st.selectbox(
        "LLM Model",
        available_models,
        help="Choose the language model for generating answers"
    )
    
    # Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Lower = more focused, Higher = more creative"
    )
    
    # Top K
    top_k = st.slider(
        "Top K Documents",
        min_value=1,
        max_value=20,
        value=5,
        help="Number of context documents to retrieve"
    )
    
    st.divider()
    
    # ============================================
    # DOCUMENT UPLOAD SECTION (NEW)
    # ============================================
    st.header("📤 Upload Documents")
    
    st.markdown("""
    <div class="upload-section">
    <strong>Enrich your knowledge base!</strong><br>
    Upload documents to make AI answers more accurate.
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader with multiple file types
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=["pdf", "docx", "doc", "txt", "xlsx", "xls", "csv", "json", "md"],
        accept_multiple_files=True,
        help="Supported: PDF, Word, Excel, Text, CSV, JSON, Markdown"
    )
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) selected**")
        
        # Show file details
        with st.expander("📋 View selected files"):
            for file in uploaded_files:
                file_size_mb = file.size / (1024 * 1024)
                st.write(f"- **{file.name}** ({file_size_mb:.2f} MB)")
        
        # Metadata for uploaded documents
        st.subheader("Document Metadata (Optional)")
        doc_source = st.text_input(
            "Source/Category",
            placeholder="e.g., 'product-docs', 'internal-policy', 'customer-feedback'",
            help="Tag to identify where this document came from"
        )
        
        doc_tags = st.text_input(
            "Tags (comma-separated)",
            placeholder="e.g., 'sales, q4-2024, confidential'",
            help="Additional tags for filtering and organization"
        )
        
        # Upload button
        if st.button("🚀 Upload & Ingest Documents", type="primary", use_container_width=True):
            with st.spinner("Processing and ingesting documents..."):
                try:
                    success_count = 0
                    error_count = 0
                    
                    for file in uploaded_files:
                        try:
                            # Read file content
                            file_bytes = file.read()
                            
                            # Prepare multipart form data
                            files = {
                                'file': (file.name, io.BytesIO(file_bytes), file.type)
                            }
                            
                            # Prepare metadata
                            data = {
                                'source': doc_source if doc_source else file.name,
                                'tags': doc_tags if doc_tags else ''
                            }
                            
                            # Upload to RAG API
                            response = httpx.post(
                                f"{RAG_API_URL}/upload/document",
                                files=files,
                                data=data,
                                timeout=TIMEOUT
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                success_count += 1
                                
                                # Show detailed success message
                                chunks = result.get('chunks', 0)
                                s3_status = result.get('storage_status', 'unknown')
                                s3_path = result.get('s3_path', 'N/A')
                                
                                st.success(f"✅ **{file.name}**")
                                st.info(f"   📊 Ingested {chunks} chunks | 💾 Storage: {s3_status}")
                                if s3_path and s3_path != 'N/A':
                                    st.caption(f"   📍 S3: `{s3_path}`")
                            else:
                                error_count += 1
                                st.error(f"❌ {file.name}: {response.text}")
                        
                        except Exception as e:
                            error_count += 1
                            st.error(f"❌ {file.name}: {str(e)}")
                    
                    # Summary
                    if success_count > 0:
                        st.success(f"🎉 Successfully uploaded {success_count} document(s)!")
                        st.session_state.uploaded_files_count += success_count
                        st.balloons()
                    
                    if error_count > 0:
                        st.warning(f"⚠️ {error_count} document(s) failed to upload")
                
                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")
    
    # Show total uploaded documents
    if st.session_state.uploaded_files_count > 0:
        st.info(f"📚 Total documents uploaded this session: {st.session_state.uploaded_files_count}")
    
    # View uploaded documents in S3
    with st.expander("📂 View Stored Documents (S3)"):
        if st.button("🔄 Refresh Document List"):
            try:
                response = httpx.get(f"{RAG_API_URL}/documents/list?max_results=50", timeout=30.0)
                if response.status_code == 200:
                    result = response.json()
                    docs = result.get("documents", [])
                    
                    if docs:
                        st.success(f"Found {len(docs)} document(s) in S3 bucket: **{result.get('bucket')}**")
                        
                        for doc in docs:
                            with st.container():
                                col1, col2, col3 = st.columns([3, 1, 1])
                                with col1:
                                    st.write(f"📄 `{doc['object_name']}`")
                                with col2:
                                    st.write(f"{doc['size_mb']} MB")
                                with col3:
                                    st.caption(doc['last_modified'][:10] if doc.get('last_modified') else 'N/A')
                    else:
                        st.info("No documents found in S3 bucket")
                else:
                    st.error(f"Failed to fetch documents: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    st.divider()
    
    # ============================================
    # DATA INGESTION FROM DATABASES
    # ============================================
    st.header("📥 Ingest from Database")
    
    # PostgreSQL ingestion
    with st.expander("🐘 PostgreSQL", expanded=False):
        pg_table = st.text_input("Table name", key="pg_table")
        pg_text_col = st.text_input("Text column", key="pg_text_col")
        pg_metadata_cols = st.text_input(
            "Metadata columns (comma-separated)",
            key="pg_metadata_cols",
            help="e.g., customer_id,name,created_at"
        )
        
        if st.button("Ingest PostgreSQL", key="btn_pg"):
            if pg_table and pg_text_col:
                with st.spinner("Ingesting from PostgreSQL..."):
                    try:
                        metadata_cols = [col.strip() for col in pg_metadata_cols.split(",")] if pg_metadata_cols else []
                        
                        response = httpx.post(
                            f"{RAG_API_URL}/ingest/postgres",
                            json={
                                "table": pg_table,
                                "text_column": pg_text_col,
                                "metadata_columns": metadata_cols
                            },
                            timeout=TIMEOUT
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Failed: {str(e)}")
            else:
                st.warning("Please provide table name and text column")
    
    # Dremio ingestion
    with st.expander("🚀 Dremio", expanded=False):
        dremio_query = st.text_area(
            "SQL Query",
            key="dremio_query",
            placeholder='SELECT * FROM "PostgreSQL"."public"."customers"',
            height=100
        )
        dremio_text_col = st.text_input("Text column", key="dremio_text_col")
        
        if st.button("Ingest Dremio", key="btn_dremio"):
            if dremio_query and dremio_text_col:
                with st.spinner("Ingesting from Dremio..."):
                    try:
                        response = httpx.post(
                            f"{RAG_API_URL}/ingest/dremio",
                            json={
                                "sql_query": dremio_query,
                                "text_column": dremio_text_col
                            },
                            timeout=TIMEOUT
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ {result['message']}")
                        else:
                            st.error(f"❌ Error: {response.text}")
                    except Exception as e:
                        st.error(f"❌ Failed: {str(e)}")
            else:
                st.warning("Please provide SQL query and text column")
    
    st.divider()
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display sources if available
        if message["role"] == "assistant" and "sources" in message:
            with st.expander(f"📚 View {len(message['sources'])} source(s)"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"""
                    <div class="source-card">
                        <strong>Source {i}</strong> 
                        <span class="score-badge">Score: {source['score']:.2f}</span>
                        <p>{source['text'][:300]}{'...' if len(source['text']) > 300 else ''}</p>
                        <small><strong>Metadata:</strong> {source.get('metadata', {})}</small>
                    </div>
                    """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask a question about your data..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Query RAG API
                response = httpx.post(
                    f"{RAG_API_URL}/query",
                    json={
                        "question": prompt,
                        "top_k": top_k,
                        "model": selected_model,
                        "temperature": temperature
                    },
                    timeout=TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    answer = result["answer"]
                    sources = result.get("sources", [])
                    
                    # Display answer
                    st.markdown(answer)
                    
                    # Display sources
                    if sources:
                        with st.expander(f"📚 View {len(sources)} source(s)"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"""
                                <div class="source-card">
                                    <strong>Source {i}</strong> 
                                    <span class="score-badge">Score: {source['score']:.2f}</span>
                                    <p>{source['text'][:300]}{'...' if len(source['text']) > 300 else ''}</p>
                                    <small><strong>Metadata:</strong> {source.get('metadata', {})}</small>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                else:
                    error_msg = f"Error querying RAG API: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
            
            except httpx.TimeoutException:
                error_msg = "⏱️ Request timed out. Try reducing Top K or using a smaller model."
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg
                })

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"**📊 Talentys Data Platform {PLATFORM_VERSION} (AI-Ready)**")
with col2:
    st.markdown(f"**🤖 Model:** {selected_model}")
with col3:
    st.markdown(f"**📚 Messages:** {len(st.session_state.messages)}")
