"""
Enhanced RAG GUI with Beautiful Chat Interface
Premium design with modern UI, typography, and interactive elements.
"""

import gradio as gr
import requests
import json
import uuid
from typing import List, Optional, Tuple
import os
from datetime import datetime

# Configuration
API_URL = "http://localhost:8082"

# Global user session
user_session = {"user_id": str(uuid.uuid4())}

# Custom CSS for beautiful UI
CUSTOM_CSS = """
/* Import beautiful fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global styling */
.gradio-container {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    min-height: 100vh;
}

/* Main container */
.main-container {
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(20px) !important;
    border-radius: 20px !important;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1) !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    margin: 20px !important;
    padding: 30px !important;
}

/* Header styling */
.main-header {
    text-align: center;
    background: linear-gradient(135deg, #667eea, #764ba2);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    margin-bottom: 10px !important;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}

.sub-header {
    text-align: center;
    color: #6b7280 !important;
    font-size: 1.1rem !important;
    font-weight: 400 !important;
    margin-bottom: 30px !important;
}

/* Tab styling */
.tab-nav {
    background: rgba(255, 255, 255, 0.8) !important;
    border-radius: 15px !important;
    padding: 5px !important;
    margin-bottom: 25px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}

.tab-nav button {
    background: transparent !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    transition: all 0.3s ease !important;
    color: #6b7280 !important;
}

.tab-nav button.selected {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

.tab-nav button:hover {
    background: rgba(102, 126, 234, 0.1) !important;
    color: #667eea !important;
}

/* Chat interface styling */
.chat-container {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 20px !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1) !important;
    min-height: 500px !important;
    display: flex !important;
    flex-direction: column !important;
}

.chat-messages {
    flex: 1 !important;
    padding: 20px !important;
    overflow-y: auto !important;
    max-height: 400px !important;
}

.message {
    margin-bottom: 16px !important;
    animation: fadeInUp 0.3s ease !important;
}

.user-message {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    padding: 16px 20px !important;
    border-radius: 20px 20px 5px 20px !important;
    margin-left: 20% !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}

.assistant-message {
    background: rgba(248, 250, 252, 0.9) !important;
    color: #1f2937 !important;
    padding: 16px 20px !important;
    border-radius: 20px 20px 20px 5px !important;
    margin-right: 20% !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
}

.message-content {
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    word-wrap: break-word !important;
}

.message-time {
    font-size: 0.75rem !important;
    color: rgba(255, 255, 255, 0.7) !important;
    margin-top: 8px !important;
    text-align: right !important;
}

.assistant-time {
    color: #9ca3af !important;
    text-align: left !important;
}

/* Input styling */
.chat-input {
    border-top: 1px solid rgba(0, 0, 0, 0.1) !important;
    padding: 20px !important;
    background: rgba(255, 255, 255, 0.95) !important;
    border-radius: 0 0 20px 20px !important;
}

.question-input textarea {
    border: 2px solid rgba(102, 126, 234, 0.2) !important;
    border-radius: 15px !important;
    padding: 16px 20px !important;
    font-size: 1rem !important;
    font-family: 'Inter', sans-serif !important;
    background: rgba(255, 255, 255, 0.9) !important;
    transition: all 0.3s ease !important;
    resize: none !important;
}

.question-input textarea:focus {
    border-color: #667eea !important;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.2) !important;
    outline: none !important;
}

/* Button styling */
.primary-button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 32px !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4) !important;
}

.primary-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
}

.secondary-button {
    background: rgba(255, 255, 255, 0.9) !important;
    border: 2px solid #667eea !important;
    border-radius: 12px !important;
    padding: 10px 24px !important;
    color: #667eea !important;
    font-weight: 500 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}

.secondary-button:hover {
    background: #667eea !important;
    color: white !important;
    transform: translateY(-1px) !important;
}

/* Card styling */
.info-card {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 16px !important;
    padding: 24px !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1) !important;
    margin-bottom: 20px !important;
    transition: all 0.3s ease !important;
}

.info-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.15) !important;
}

.info-card h3 {
    color: #1f2937 !important;
    font-size: 1.2rem !important;
    font-weight: 600 !important;
    margin-bottom: 12px !important;
}

.info-card p {
    color: #6b7280 !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
}

/* Upload area styling */
.upload-area {
    border: 2px dashed rgba(102, 126, 234, 0.3) !important;
    border-radius: 16px !important;
    padding: 40px 20px !important;
    text-align: center !important;
    background: rgba(102, 126, 234, 0.02) !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
}

.upload-area:hover {
    border-color: #667eea !important;
    background: rgba(102, 126, 234, 0.05) !important;
}

/* Status indicators */
.status-success {
    background: linear-gradient(135deg, #10b981, #059669) !important;
    color: white !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3) !important;
}

.status-error {
    background: linear-gradient(135deg, #ef4444, #dc2626) !important;
    color: white !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3) !important;
}

.status-info {
    background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
    color: white !important;
    padding: 12px 20px !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
}

/* Knowledge base selector */
.kb-selector {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    margin-bottom: 20px !important;
}

.kb-option {
    padding: 12px 16px !important;
    border-radius: 8px !important;
    margin: 4px 0 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    border: 2px solid transparent !important;
}

.kb-option:hover {
    background: rgba(102, 126, 234, 0.1) !important;
}

.kb-option.selected {
    background: rgba(102, 126, 234, 0.15) !important;
    border-color: #667eea !important;
}

/* Document list styling */
.document-item {
    background: rgba(255, 255, 255, 0.9) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    margin-bottom: 12px !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    transition: all 0.3s ease !important;
}

.document-item:hover {
    transform: translateX(4px) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
}

.document-name {
    font-weight: 600 !important;
    color: #1f2937 !important;
    font-size: 1rem !important;
    margin-bottom: 8px !important;
}

.document-meta {
    color: #6b7280 !important;
    font-size: 0.85rem !important;
}

/* Animations */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulse {
    0%, 100% {
        opacity: 1;
    }
    50% {
        opacity: 0.5;
    }
}

.loading {
    animation: pulse 2s infinite;
}

/* Responsive design */
@media (max-width: 768px) {
    .main-container {
        margin: 10px !important;
        padding: 20px !important;
    }
    
    .user-message {
        margin-left: 10% !important;
    }
    
    .assistant-message {
        margin-right: 10% !important;
    }
    
    .main-header {
        font-size: 2rem !important;
    }
}

/* Code blocks */
.code-block {
    background: #1f2937 !important;
    color: #f9fafb !important;
    border-radius: 8px !important;
    padding: 16px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.9rem !important;
    overflow-x: auto !important;
    margin: 12px 0 !important;
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: rgba(102, 126, 234, 0.5);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(102, 126, 234, 0.7);
}

/* Typography improvements */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
}

p, span, div {
    font-family: 'Inter', sans-serif !important;
    line-height: 1.6 !important;
}

code {
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(102, 126, 234, 0.1) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.9em !important;
}
"""

def upload_document(file_path: str, user_id: str = None) -> dict:
    """Upload a document to the RAG system."""
    if not file_path:
        return {"error": "No file selected"}
    
    if not user_id:
        user_id = user_session["user_id"]
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            params = {'user_id': user_id}
            response = requests.post(f"{API_URL}/documents/upload", files=files, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Upload failed: {response.text}"}
    except Exception as e:
        return {"error": f"Error uploading file: {str(e)}"}

def upload_multiple_documents(files: List[str], user_id: str = None) -> dict:
    """Upload multiple documents to the RAG system."""
    if not files:
        return {"error": "No files selected"}
    
    if not user_id:
        user_id = user_session["user_id"]
    
    try:
        files_data = []
        for file_path in files:
            if file_path and os.path.exists(file_path):
                files_data.append(('files', open(file_path, 'rb')))
        
        if not files_data:
            return {"error": "No valid files found"}
        
        params = {'user_id': user_id}
        response = requests.post(f"{API_URL}/documents/upload-multiple", files=files_data, params=params)
        
        # Close all opened files
        for _, file_obj in files_data:
            file_obj.close()
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Upload failed: {response.text}"}
    except Exception as e:
        return {"error": f"Error uploading files: {str(e)}"}

def list_user_documents(user_id: str = None) -> dict:
    """List documents in user's knowledge base."""
    if not user_id:
        user_id = user_session["user_id"]
    
    try:
        response = requests.get(f"{API_URL}/documents/list/{user_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to list documents: {response.text}"}
    except Exception as e:
        return {"error": f"Error listing documents: {str(e)}"}

def delete_document(document_name: str, user_id: str = None) -> dict:
    """Delete a document from user's knowledge base."""
    if not user_id:
        user_id = user_session["user_id"]
    
    try:
        response = requests.delete(f"{API_URL}/documents/{user_id}/{document_name}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to delete document: {response.text}"}
    except Exception as e:
        return {"error": f"Error deleting document: {str(e)}"}

def get_vectorstore_info(user_id: str = None) -> dict:
    """Get information about user's vector store."""
    if not user_id:
        user_id = user_session["user_id"]
    
    try:
        response = requests.get(f"{API_URL}/documents/vectorstore/info/{user_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to get vectorstore info: {response.text}"}
    except Exception as e:
        return {"error": f"Error getting vectorstore info: {str(e)}"}

def clear_vectorstore(user_id: str = None) -> dict:
    """Clear all documents from user's vector store."""
    if not user_id:
        user_id = user_session["user_id"]
    
    try:
        response = requests.post(f"{API_URL}/documents/clear/{user_id}")
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to clear vectorstore: {response.text}"}
    except Exception as e:
        return {"error": f"Error clearing vectorstore: {str(e)}"}

def format_chat_message(content: str, is_user: bool = True) -> str:
    """Format a chat message with proper styling."""
    timestamp = datetime.now().strftime("%H:%M")
    
    if is_user:
        return f"""
        <div class="message user-message">
            <div class="message-content">{content}</div>
            <div class="message-time">{timestamp}</div>
        </div>
        """
    else:
        return f"""
        <div class="message assistant-message">
            <div class="message-content">{content}</div>
            <div class="message-time assistant-time">{timestamp}</div>
        </div>
        """

def ask_question_chat(question: str, chat_history: str, knowledge_base_type: str = "personal", user_id: str = None) -> Tuple[str, str, str, str, str]:
    """Ask a question using the RAG system with chat interface."""
    if not question.strip():
        return chat_history, "", "Please enter a question.", "", ""
    
    if not user_id:
        user_id = user_session["user_id"]
    
    # Add user message to chat
    new_chat = chat_history + format_chat_message(question, is_user=True)
    
    try:
        messages = [{"role": "user", "content": question}]
        
        # Prepare request based on knowledge base type
        if knowledge_base_type == "personal":
            params = {"user_id": user_id, "use_combined": False}
        elif knowledge_base_type == "combined":
            params = {"user_id": user_id, "use_combined": True}
        else:  # default
            params = {}
        
        response = requests.post(
            f"{API_URL}/generate-answer",
            json={"messages": messages},
            params=params
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract answer
            answer = ""
            for msg in result.get("messages", []):
                if msg.get("role") == "system":
                    answer = msg.get("content", "")
            
            # Add assistant message to chat
            new_chat += format_chat_message(answer, is_user=False)
            
            # Format additional info
            questions = "\\n".join(result.get("questions", []))
            documents = "\\n---\\n".join(result.get("documents", []))
            kb_type = result.get("knowledge_base_type", knowledge_base_type)
            
            return new_chat, "", questions, documents, f"Knowledge Base: {kb_type}"
        else:
            error_msg = f"API Error: {response.status_code} - {response.text}"
            error_chat = new_chat + format_chat_message(f"❌ {error_msg}", is_user=False)
            return error_chat, "", "", "", ""
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        error_chat = new_chat + format_chat_message(f"❌ {error_msg}", is_user=False)
        return error_chat, "", "", "", ""

# Gradio interface functions
def handle_file_upload(file):
    """Handle single file upload with beautiful formatting."""
    if file is None:
        return "❌ No file selected", ""
    
    result = upload_document(file.name)
    
    if "error" in result:
        return f"""
        <div class="status-error">
            <strong>❌ Upload Failed</strong><br>
            {result['error']}
        </div>
        """, ""
    else:
        # Update global user session
        user_session["user_id"] = result["user_id"]
        
        return f"""
        <div class="status-success">
            <strong>✅ Upload Successful!</strong><br>
            📄 <strong>Document:</strong> {result['document_name']}<br>
            📊 <strong>Chunks Created:</strong> {result['chunks_created']}<br>
            👤 <strong>User ID:</strong> {result['user_id']}
        </div>
        """, get_document_list_display()

def handle_multiple_file_upload(files):
    """Handle multiple file upload with beautiful formatting."""
    if not files:
        return "❌ No files selected", ""
    
    file_paths = [f.name for f in files if f is not None]
    result = upload_multiple_documents(file_paths)
    
    if "error" in result:
        return f"""
        <div class="status-error">
            <strong>❌ Batch Upload Failed</strong><br>
            {result['error']}
        </div>
        """, ""
    else:
        # Update global user session
        user_session["user_id"] = result["user_id"]
        
        return f"""
        <div class="status-success">
            <strong>✅ Batch Upload Complete!</strong><br>
            📈 <strong>Total Files:</strong> {result['total_files']}<br>
            ✅ <strong>Successful:</strong> {result['successful_uploads']}<br>
            ❌ <strong>Failed:</strong> {result['failed_uploads']}<br>
            👤 <strong>User ID:</strong> {result['user_id']}
        </div>
        """, get_document_list_display()

def get_document_list_display():
    """Get beautifully formatted display of user documents."""
    result = list_user_documents()
    
    if "error" in result:
        return f"""
        <div class="status-error">
            <strong>❌ Error Loading Documents</strong><br>
            {result['error']}
        </div>
        """
    
    if not result.get("documents"):
        return """
        <div class="info-card" style="text-align: center; padding: 40px;">
            <h3>📭 No Documents Yet</h3>
            <p>Upload your first document to get started with your personal knowledge base!</p>
        </div>
        """
    
    docs_html = f"""
    <div class="info-card">
        <h3>📚 Your Knowledge Base ({result['total_documents']} documents)</h3>
    </div>
    """
    
    for doc in result["documents"]:
        docs_html += f"""
        <div class="document-item">
            <div class="document-name">📄 {doc['name']}</div>
            <div class="document-meta">
                📊 <strong>{doc['chunks']}</strong> chunks • 
                🔧 Type: <strong>{doc['document_type']}</strong>
            </div>
        </div>
        """
    
    return docs_html

def handle_document_deletion(document_name):
    """Handle document deletion with beautiful formatting."""
    if not document_name.strip():
        return """
        <div class="status-error">
            <strong>❌ Invalid Input</strong><br>
            Please enter a document name to delete.
        </div>
        """, ""
    
    result = delete_document(document_name.strip())
    
    if "error" in result:
        return f"""
        <div class="status-error">
            <strong>❌ Deletion Failed</strong><br>
            {result['error']}
        </div>
        """, get_document_list_display()
    else:
        return f"""
        <div class="status-success">
            <strong>✅ Document Deleted</strong><br>
            🗑️ <strong>Removed:</strong> {result['deleted_chunks']} chunks
        </div>
        """, get_document_list_display()

def handle_vectorstore_clear():
    """Handle clearing the vectorstore with beautiful formatting."""
    result = clear_vectorstore()
    
    if "error" in result:
        return f"""
        <div class="status-error">
            <strong>❌ Clear Failed</strong><br>
            {result['error']}
        </div>
        """, ""
    else:
        return f"""
        <div class="status-success">
            <strong>✅ Knowledge Base Cleared</strong><br>
            All documents have been removed from your knowledge base.
        </div>
        """, get_document_list_display()

def get_vectorstore_info_display():
    """Get vectorstore information with beautiful formatting."""
    result = get_vectorstore_info()
    
    if "error" in result:
        return f"""
        <div class="status-error">
            <strong>❌ Info Unavailable</strong><br>
            {result['error']}
        </div>
        """
    
    return f"""
    <div class="info-card">
        <h3>📊 Vector Store Statistics</h3>
        <p><strong>📚 Total Documents:</strong> {result['total_documents']}</p>
        <p><strong>📊 Total Chunks:</strong> {result['total_chunks']}</p>
        <p><strong>📋 Status:</strong> <span style="color: #10b981; font-weight: 600;">{result['status']}</span></p>
    </div>
    """

# Create the beautiful Gradio interface
def create_interface():
    with gr.Blocks(
        title="🧠 RAG Knowledge Base Manager",
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS
    ) as app:
        
        # Header
        with gr.Row():
            with gr.Column():
                gr.HTML("""
                <div class="main-container">
                    <h1 class="main-header">🧠 RAG Knowledge Base Manager</h1>
                    <p class="sub-header">
                        Upload documents and chat with your personal AI assistant powered by 
                        <strong>Retrieval-Augmented Generation</strong>
                    </p>
                </div>
                """)
        
        with gr.Tabs() as tabs:
            # Chat Interface Tab
            with gr.TabItem("💬 Chat Assistant", elem_classes=["tab-nav"]):
                with gr.Row():
                    with gr.Column(scale=2):
                        # Chat Display
                        chat_display = gr.HTML(
                            value="""
                            <div class="chat-container">
                                <div class="chat-messages">
                                    <div class="message assistant-message">
                                        <div class="message-content">
                                            👋 Hello! I'm your AI assistant. Upload some documents and start asking me questions about them!
                                        </div>
                                        <div class="message-time assistant-time">Ready</div>
                                    </div>
                                </div>
                            </div>
                            """,
                            elem_classes=["chat-container"]
                        )
                        
                        # Chat Input
                        with gr.Row():
                            question_input = gr.Textbox(
                                label="💭 Ask me anything...",
                                placeholder="What would you like to know about your documents?",
                                lines=2,
                                scale=4,
                                elem_classes=["question-input"]
                            )
                            ask_btn = gr.Button(
                                "🚀 Send",
                                variant="primary",
                                size="lg",
                                scale=1,
                                elem_classes=["primary-button"]
                            )
                    
                    with gr.Column(scale=1):
                        # Knowledge Base Selector
                        gr.HTML("<h3 style='margin-bottom: 16px;'>🎯 Knowledge Base</h3>")
                        knowledge_base_choice = gr.Radio(
                            choices=[
                                ("🏠 Personal", "personal"),
                                ("🌐 Combined", "combined"), 
                                ("📚 Default", "default")
                            ],
                            label="Select Source",
                            value="personal",
                            elem_classes=["kb-selector"]
                        )
                        
                        gr.HTML("""
                        <div class="info-card">
                            <h3>💡 Knowledge Base Types</h3>
                            <p><strong>🏠 Personal:</strong> Search only your uploaded documents</p>
                            <p><strong>🌐 Combined:</strong> Search your documents + default knowledge</p>
                            <p><strong>📚 Default:</strong> Search only built-in knowledge base</p>
                        </div>
                        """)
                
                # Query Details (Hidden by default)
                with gr.Accordion("🔍 Query Details", open=False):
                    with gr.Row():
                        with gr.Column():
                            questions_output = gr.Textbox(
                                label="🤖 Generated Queries",
                                lines=3,
                                interactive=False
                            )
                        with gr.Column():
                            documents_output = gr.Textbox(
                                label="📖 Source Documents",
                                lines=3,
                                interactive=False
                            )
                    kb_info_output = gr.Textbox(
                        label="ℹ️ Knowledge Base Info",
                        lines=1,
                        interactive=False
                    )
            
            # Document Upload Tab
            with gr.TabItem("📤 Upload Documents", elem_classes=["tab-nav"]):
                gr.HTML("<h2 style='text-align: center; margin-bottom: 30px;'>📤 Upload Documents to Your Knowledge Base</h2>")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.HTML("""
                        <div class="info-card">
                            <h3>📄 Single Document Upload</h3>
                            <p>Upload one document at a time for processing</p>
                        </div>
                        """)
                        
                        file_upload = gr.File(
                            label="Select Document",
                            file_types=[".pdf", ".docx", ".txt", ".md"],
                            elem_classes=["upload-area"]
                        )
                        upload_btn = gr.Button(
                            "📤 Upload Document",
                            variant="primary",
                            size="lg",
                            elem_classes=["primary-button"]
                        )
                        upload_result = gr.HTML()
                    
                    with gr.Column(scale=1):
                        gr.HTML("""
                        <div class="info-card">
                            <h3>📚 Batch Document Upload</h3>
                            <p>Upload multiple documents simultaneously</p>
                        </div>
                        """)
                        
                        files_upload = gr.File(
                            label="Select Multiple Documents",
                            file_count="multiple",
                            file_types=[".pdf", ".docx", ".txt", ".md"],
                            elem_classes=["upload-area"]
                        )
                        multi_upload_btn = gr.Button(
                            "📚 Upload Multiple",
                            variant="primary",
                            size="lg",
                            elem_classes=["primary-button"]
                        )
                        multi_upload_result = gr.HTML()
            
            # Knowledge Base Management Tab
            with gr.TabItem("📚 Manage Knowledge Base", elem_classes=["tab-nav"]):
                gr.HTML("<h2 style='text-align: center; margin-bottom: 30px;'>📚 Manage Your Knowledge Base</h2>")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        gr.HTML("<h3>📋 Document Library</h3>")
                        doc_list = gr.HTML(value=get_document_list_display())
                        
                        with gr.Row():
                            refresh_btn = gr.Button(
                                "🔄 Refresh",
                                variant="secondary",
                                elem_classes=["secondary-button"]
                            )
                    
                    with gr.Column(scale=1):
                        gr.HTML("""
                        <div class="info-card">
                            <h3>🗑️ Delete Document</h3>
                            <p>Remove a specific document from your knowledge base</p>
                        </div>
                        """)
                        
                        doc_to_delete = gr.Textbox(
                            label="Document Name",
                            placeholder="Enter exact document name...",
                            lines=1
                        )
                        delete_btn = gr.Button(
                            "🗑️ Delete Document",
                            variant="stop",
                            elem_classes=["secondary-button"]
                        )
                        delete_result = gr.HTML()
                        
                        gr.HTML("""
                        <div class="info-card">
                            <h3>📊 Statistics</h3>
                        </div>
                        """)
                        
                        info_btn = gr.Button(
                            "📊 Get Statistics",
                            elem_classes=["secondary-button"]
                        )
                        vectorstore_info = gr.HTML()
                        
                        gr.HTML("""
                        <div class="info-card">
                            <h3>🧹 Reset Knowledge Base</h3>
                            <p style="color: #ef4444; font-weight: 500;">⚠️ This will delete ALL your documents!</p>
                        </div>
                        """)
                        
                        clear_btn = gr.Button(
                            "🧹 Clear All Documents",
                            variant="stop"
                        )
                        clear_result = gr.HTML()
        
        # Event Handlers
        ask_btn.click(
            ask_question_chat,
            inputs=[question_input, chat_display, knowledge_base_choice],
            outputs=[chat_display, question_input, questions_output, documents_output, kb_info_output]
        )
        
        question_input.submit(
            ask_question_chat,
            inputs=[question_input, chat_display, knowledge_base_choice],
            outputs=[chat_display, question_input, questions_output, documents_output, kb_info_output]
        )
        
        upload_btn.click(
            handle_file_upload,
            inputs=[file_upload],
            outputs=[upload_result, doc_list]
        )
        
        multi_upload_btn.click(
            handle_multiple_file_upload,
            inputs=[files_upload],
            outputs=[multi_upload_result, doc_list]
        )
        
        refresh_btn.click(
            get_document_list_display,
            outputs=[doc_list]
        )
        
        delete_btn.click(
            handle_document_deletion,
            inputs=[doc_to_delete],
            outputs=[delete_result, doc_list]
        )
        
        info_btn.click(
            get_vectorstore_info_display,
            outputs=[vectorstore_info]
        )
        
        clear_btn.click(
            handle_vectorstore_clear,
            outputs=[clear_result, doc_list]
        )
        
        # Auto-refresh on load
        app.load(
            get_document_list_display,
            outputs=[doc_list]
        )
    
    return app

if __name__ == "__main__":
    # Display startup info
    print("🚀 Starting Enhanced RAG Knowledge Base Manager")
    print(f"👤 User Session ID: {user_session['user_id']}")
    print(f"🔗 API URL: {API_URL}")
    print("✨ Features: Beautiful UI, Chat Interface, Modern Design")
    
    # Create and launch the interface
    app = create_interface()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=True,
        show_error=True
    )