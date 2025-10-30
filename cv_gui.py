"""
Enhanced CV Search GUI with Gradio
Professional interface for CV document upload and intelligent Q&A search.
"""

import gradio as gr
import requests
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from cv_search_system import CVSearchSystem
    CV_SEARCH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ CV Search System not available: {e}")
    CV_SEARCH_AVAILABLE = False

# API Configuration
API_URL = "http://localhost:8082"

class CVSearchGUI:
    """Enhanced GUI for CV search and document management."""
    
    def __init__(self):
        self.cv_system = None
        self.initialize_cv_system()
    
    def initialize_cv_system(self):
        """Initialize the CV search system."""
        if not CV_SEARCH_AVAILABLE:
            return False
        
        try:
            self.cv_system = CVSearchSystem()
            self.cv_system.initialize_components()
            return True
        except Exception as e:
            print(f"❌ Failed to initialize CV system: {e}")
            return False
    
    def upload_cv_document(self, file):
        """Upload and process CV document."""
        if not file:
            return "❌ No file selected", ""
        
        try:
            # Copy uploaded file to data/raw/
            cv_dir = Path("data/raw")
            cv_dir.mkdir(parents=True, exist_ok=True)
            
            # Get file name and extension
            file_name = os.path.basename(file.name)
            destination = cv_dir / file_name
            
            # Copy file
            shutil.copy2(file.name, destination)
            
            status_msg = f"📄 File uploaded: {file_name}\n"
            
            # If it's a PDF and CV system is available, process it
            if file_name.lower().endswith('.pdf') and self.cv_system:
                status_msg += "🔧 Processing PDF for vector search...\n"
                
                success = self.cv_system.process_cv_pdf(str(destination))
                
                if success:
                    status_msg += "✅ CV processed successfully! Ready for search.\n"
                    return status_msg, "CV processed and ready for intelligent search!"
                else:
                    status_msg += "⚠️ CV processing failed. File uploaded but search may be limited.\n"
            
            return status_msg, f"File {file_name} uploaded successfully!"
            
        except Exception as e:
            return f"❌ Upload failed: {str(e)}", ""
    
    def search_cv_content(self, query):
        """Search CV content using the intelligent search system."""
        if not query.strip():
            return "Please enter a search query."
        
        if not self.cv_system:
            return "❌ CV Search system not available. Please check installation."
        
        try:
            # Check if CV vectorstore exists
            if not self.cv_system.load_cv_vectorstore():
                return "❌ No CV data found. Please upload and process a CV PDF first."
            
            # Perform search
            result = self.cv_system.search_cv(query.strip())
            
            # Format response
            response = f"🎯 **Question:** {result['query']}\n\n"
            response += f"📋 **Answer:**\n{result['answer']}\n\n"
            
            if result['sources']:
                response += f"📚 **Sources ({len(result['sources'])} chunks):**\n"
                for i, source in enumerate(result['sources'], 1):
                    response += f"{i}. {source['content']}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Search failed: {str(e)}"
    
    def get_document_status(self):
        """Get status of uploaded documents."""
        try:
            # Check API status
            try:
                response = requests.get(f"{API_URL}/health", timeout=5)
                api_status = "🟢 Online" if response.status_code == 200 else "🔴 Offline"
            except:
                api_status = "🔴 Offline"
            
            # Check CV vectorstore
            cv_status = "❌ Not processed"
            if self.cv_system and os.path.exists(self.cv_system.cv_vectorstore_path):
                cv_status = "✅ Ready for search"
            
            # Check uploaded files
            cv_dir = Path("data/raw")
            uploaded_files = []
            if cv_dir.exists():
                uploaded_files = [f.name for f in cv_dir.iterdir() if f.is_file()]
            
            status = f"""
## 📊 System Status

**API Server:** {api_status}
**CV Search System:** {'✅ Available' if self.cv_system else '❌ Not available'}
**CV Vector Store:** {cv_status}

**📁 Uploaded Files:**
{chr(10).join([f"- {file}" for file in uploaded_files]) if uploaded_files else "No files uploaded"}

**💡 Ready to use:** {'Yes - Upload CV and start searching!' if self.cv_system else 'Please check system setup'}
"""
            return status
            
        except Exception as e:
            return f"❌ Error checking status: {str(e)}"

def create_cv_search_interface():
    """Create the main CV search interface."""
    
    gui = CVSearchGUI()
    
    with gr.Blocks(title="CV Intelligence Search", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("# 🎯 CV Intelligence Search System")
        gr.Markdown("Upload your CV and ask intelligent questions about your experience, skills, and qualifications!")
        
        with gr.Tabs():
            # Tab 1: CV Upload
            with gr.TabItem("📄 Upload CV"):
                gr.Markdown("### Upload your CV (PDF format recommended)")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        cv_file = gr.File(
                            label="Select CV File",
                            file_types=[".pdf", ".docx", ".txt"],
                            type="filepath"
                        )
                        upload_btn = gr.Button("🚀 Upload & Process CV", variant="primary")
                    
                    with gr.Column(scale=2):
                        upload_status = gr.Textbox(
                            label="Upload Status",
                            placeholder="Upload status will appear here...",
                            lines=8,
                            interactive=False
                        )
                
                upload_result = gr.Textbox(
                    label="Processing Result",
                    placeholder="Processing results will appear here...",
                    lines=3,
                    interactive=False
                )
                
                upload_btn.click(
                    fn=gui.upload_cv_document,
                    inputs=[cv_file],
                    outputs=[upload_status, upload_result]
                )
            
            # Tab 2: Intelligent Search
            with gr.TabItem("🔍 CV Search"):
                gr.Markdown("### Ask Questions About Your CV")
                gr.Markdown("Examples: *What programming languages do I know?*, *What is my work experience?*, *What projects have I worked on?*")
                
                with gr.Row():
                    search_query = gr.Textbox(
                        label="Ask about your CV",
                        placeholder="What programming languages does the candidate know?",
                        lines=2,
                        scale=4
                    )
                    search_btn = gr.Button("🔍 Search", variant="primary", scale=1)
                
                search_results = gr.Textbox(
                    label="Search Results",
                    placeholder="Search results will appear here...",
                    lines=15,
                    interactive=False
                )
                
                # Example questions
                gr.Markdown("### 🎯 Example Questions")
                example_questions = [
                    "What is the candidate's educational background?",
                    "What programming languages and technologies does he know?", 
                    "What work experience does the candidate have?",
                    "What projects has he worked on?",
                    "What are his key skills and competencies?",
                    "What certifications does he have?"
                ]
                
                for question in example_questions:
                    example_btn = gr.Button(f"💡 {question}", variant="secondary", size="sm")
                    example_btn.click(
                        fn=lambda q=question: (q, gui.search_cv_content(q)),
                        outputs=[search_query, search_results]
                    )
                
                search_btn.click(
                    fn=gui.search_cv_content,
                    inputs=[search_query],
                    outputs=[search_results]
                )
                
                # Enter key support
                search_query.submit(
                    fn=gui.search_cv_content,
                    inputs=[search_query],
                    outputs=[search_results]
                )
            
            # Tab 3: System Status
            with gr.TabItem("📊 System Status"):
                gr.Markdown("### Check system status and uploaded documents")
                
                status_btn = gr.Button("🔄 Refresh Status", variant="secondary")
                status_display = gr.Markdown(
                    value=gui.get_document_status(),
                    label="System Status"
                )
                
                status_btn.click(
                    fn=gui.get_document_status,
                    outputs=[status_display]
                )
            
            # Tab 4: Instructions  
            with gr.TabItem("📖 Instructions"):
                gr.Markdown("""
### 🚀 How to Use CV Intelligence Search

#### Step 1: Upload Your CV
1. Go to the **"Upload CV"** tab
2. Select your CV file (PDF format recommended)
3. Click **"Upload & Process CV"**
4. Wait for processing to complete

#### Step 2: Search Your CV
1. Go to the **"CV Search"** tab  
2. Type your question in the search box
3. Click **"Search"** or press Enter
4. View intelligent answers with source references

#### 🎯 Example Questions You Can Ask

**Education & Qualifications:**
- What is my educational background?
- What degrees do I have?
- What certifications have I earned?

**Skills & Technologies:**
- What programming languages do I know?
- What technologies am I experienced with?
- What are my key technical skills?

**Work Experience:**
- What work experience do I have?
- What companies have I worked for?
- What roles have I held?

**Projects & Achievements:**
- What projects have I worked on?
- What are my key achievements?
- What notable accomplishments do I have?

#### 💡 Tips for Better Results

- **Be specific**: Ask targeted questions about specific aspects
- **Use keywords**: Include relevant terms from your CV
- **Try variations**: Rephrase questions if needed for better results
- **Check sources**: Review the source chunks to verify answers

#### 🔧 Troubleshooting

- If search doesn't work, check the **System Status** tab
- Make sure your CV is uploaded and processed successfully  
- Ensure the API server is running on port 8082
- Try refreshing the page if you encounter issues
                """)
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("🔧 **CV Intelligence Search System** | Powered by LangChain, ChromaDB, and Google Gemini")
    
    return interface

def main():
    """Launch the CV search application."""
    print("🚀 Starting CV Intelligence Search System...")
    print("=" * 50)
    
    # Create and launch interface
    interface = create_cv_search_interface()
    
    print("🌐 Launching Gradio interface...")
    print(f"📱 Access at: http://localhost:7862")
    print("🔧 Make sure FastAPI server is running on port 8082")
    print("=" * 50)
    
    interface.launch(
        server_name="localhost",
        server_port=7862,
        share=False,
        debug=True,
        show_error=True
    )

if __name__ == "__main__":
    main()