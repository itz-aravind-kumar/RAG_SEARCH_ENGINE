"""
Simple CV Search GUI
Lightweight version for CV document upload and search without complex imports.
"""

import gradio as gr
import os
import json
from pathlib import Path

class SimpleCVSearchGUI:
    """Simple GUI for CV search and document management."""
    
    def __init__(self):
        self.cv_content = ""
        self.cv_file_name = ""
    
    def upload_cv_document(self, file):
        """Upload and store CV document."""
        if not file:
            return "❌ No file selected", ""
        
        try:
            file_name = os.path.basename(file.name)
            
            # Read file content based on type
            if file_name.lower().endswith('.txt'):
                with open(file.name, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_name.lower().endswith('.pdf'):
                try:
                    import PyPDF2
                    with open(file.name, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        content = ""
                        for page_num, page in enumerate(reader.pages):
                            content += f"\n[Page {page_num + 1}]\n{page.extract_text()}\n"
                except ImportError:
                    return "❌ PyPDF2 not available for PDF processing", ""
            else:
                return "❌ Unsupported file format. Use .txt or .pdf files.", ""
            
            # Store CV content
            self.cv_content = content
            self.cv_file_name = file_name
            
            # Save to data/raw/
            cv_dir = Path("data/raw")
            cv_dir.mkdir(parents=True, exist_ok=True)
            
            # Save content as text file for processing
            text_file_path = cv_dir / f"{Path(file_name).stem}_processed.txt"
            with open(text_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            status_msg = f"""📄 **File Uploaded Successfully**
**File:** {file_name}
**Size:** {len(content)} characters
**Saved to:** {text_file_path}
**Status:** ✅ Ready for search"""
            
            return status_msg, f"✅ {file_name} uploaded and processed successfully!"
            
        except Exception as e:
            return f"❌ Upload failed: {str(e)}", ""
    
    def simple_search_cv(self, query):
        """Simple text-based search of CV content."""
        if not query.strip():
            return "Please enter a search query."
        
        if not self.cv_content:
            return "❌ No CV uploaded. Please upload a CV file first."
        
        try:
            query_lower = query.lower()
            lines = self.cv_content.split('\n')
            
            # Find relevant lines containing query terms
            relevant_lines = []
            query_words = query_lower.split()
            
            for line in lines:
                line_lower = line.lower()
                # Check if any query words are in this line
                if any(word in line_lower for word in query_words):
                    relevant_lines.append(line.strip())
            
            if not relevant_lines:
                return f"❌ No information found for: '{query}'"
            
            # Create sections for better organization
            sections = {}
            current_section = "General"
            
            for line in relevant_lines:
                if line.isupper() or line.endswith(':'):
                    current_section = line.replace(':', '').strip()
                    if current_section not in sections:
                        sections[current_section] = []
                else:
                    if current_section not in sections:
                        sections[current_section] = []
                    if line:  # Skip empty lines
                        sections[current_section].append(line)
            
            # Format response
            response = f"🎯 **Search Results for:** {query}\n\n"
            
            for section, content in sections.items():
                if content:
                    response += f"## 📋 {section}\n"
                    for item in content[:5]:  # Limit to 5 items per section
                        response += f"• {item}\n"
                    response += "\n"
            
            if len(relevant_lines) > 20:
                response += f"\n📊 **Found {len(relevant_lines)} relevant matches** (showing top results)\n"
            
            return response
            
        except Exception as e:
            return f"❌ Search failed: {str(e)}"
    
    def get_cv_summary(self):
        """Get a summary of the uploaded CV."""
        if not self.cv_content:
            return "❌ No CV uploaded yet."
        
        try:
            lines = [line.strip() for line in self.cv_content.split('\n') if line.strip()]
            
            # Extract key information
            name = "Not found"
            email = "Not found"
            phone = "Not found"
            
            for line in lines:
                if 'name:' in line.lower() and name == "Not found":
                    name = line.split(':', 1)[1].strip()
                elif '@' in line and 'email' in line.lower():
                    email = line.split(':', 1)[1].strip() if ':' in line else line.strip()
                elif any(x in line.lower() for x in ['phone', 'mobile', 'tel']):
                    phone = line.split(':', 1)[1].strip() if ':' in line else line.strip()
            
            summary = f"""
## 📊 CV Summary

**📄 File:** {self.cv_file_name}
**👤 Name:** {name}
**📧 Email:** {email}  
**📱 Phone:** {phone}
**📝 Content Length:** {len(self.cv_content)} characters
**📑 Lines:** {len(lines)} lines

**🔍 Ready for Search:** ✅ Yes

### 💡 Try These Searches:
- "What programming languages"
- "education background" 
- "work experience"
- "projects"
- "skills"
- "certifications"
"""
            return summary
            
        except Exception as e:
            return f"❌ Error generating summary: {str(e)}"

def create_simple_cv_interface():
    """Create the simple CV search interface."""
    
    gui = SimpleCVSearchGUI()
    
    with gr.Blocks(title="CV Search System", theme=gr.themes.Soft()) as interface:
        
        gr.Markdown("# 🎯 CV Search System")
        gr.Markdown("Upload your CV and search through its content using simple keyword matching!")
        
        with gr.Tabs():
            # Tab 1: CV Upload
            with gr.TabItem("📄 Upload CV"):
                gr.Markdown("### Upload your CV (PDF or TXT format)")
                
                with gr.Row():
                    with gr.Column():
                        cv_file = gr.File(
                            label="Select CV File",
                            file_types=[".pdf", ".txt"],
                            type="filepath"
                        )
                        upload_btn = gr.Button("🚀 Upload CV", variant="primary")
                    
                with gr.Row():
                    upload_status = gr.Textbox(
                        label="Upload Status",
                        placeholder="Upload status will appear here...",
                        lines=8,
                        interactive=False
                    )
                
                upload_result = gr.Textbox(
                    label="Upload Result",
                    placeholder="Upload results will appear here...",
                    lines=2,
                    interactive=False
                )
                
                upload_btn.click(
                    fn=gui.upload_cv_document,
                    inputs=[cv_file],
                    outputs=[upload_status, upload_result]
                )
            
            # Tab 2: Search CV
            with gr.TabItem("🔍 Search CV"):
                gr.Markdown("### Search Your CV Content")
                
                with gr.Row():
                    search_query = gr.Textbox(
                        label="Enter your search query",
                        placeholder="e.g., programming languages, education, experience...",
                        lines=2
                    )
                    search_btn = gr.Button("🔍 Search", variant="primary")
                
                search_results = gr.Textbox(
                    label="Search Results",
                    placeholder="Search results will appear here...",
                    lines=15,
                    interactive=False
                )
                
                # Quick search buttons
                gr.Markdown("### 🚀 Quick Searches")
                
                with gr.Row():
                    skills_btn = gr.Button("💻 Technical Skills", variant="secondary")
                    education_btn = gr.Button("🎓 Education", variant="secondary")
                    experience_btn = gr.Button("💼 Experience", variant="secondary")
                    projects_btn = gr.Button("🚀 Projects", variant="secondary")
                
                # Button actions
                search_btn.click(
                    fn=gui.simple_search_cv,
                    inputs=[search_query],
                    outputs=[search_results]
                )
                
                search_query.submit(
                    fn=gui.simple_search_cv,
                    inputs=[search_query],
                    outputs=[search_results]
                )
                
                skills_btn.click(
                    fn=lambda: gui.simple_search_cv("technical skills programming languages technologies"),
                    outputs=[search_results]
                )
                
                education_btn.click(
                    fn=lambda: gui.simple_search_cv("education degree university college qualification"),
                    outputs=[search_results]
                )
                
                experience_btn.click(
                    fn=lambda: gui.simple_search_cv("work experience job employment career"),
                    outputs=[search_results]
                )
                
                projects_btn.click(
                    fn=lambda: gui.simple_search_cv("projects applications systems developed built"),
                    outputs=[search_results]
                )
            
            # Tab 3: CV Summary
            with gr.TabItem("📊 CV Summary"):
                gr.Markdown("### View CV Summary and Status")
                
                summary_btn = gr.Button("🔄 Get CV Summary", variant="secondary")
                cv_summary = gr.Markdown(
                    value="Upload a CV to see summary here.",
                    label="CV Summary"
                )
                
                summary_btn.click(
                    fn=gui.get_cv_summary,
                    outputs=[cv_summary]
                )
            
            # Tab 4: Instructions
            with gr.TabItem("📖 How to Use"):
                gr.Markdown("""
### 🚀 How to Use the CV Search System

#### Step 1: Upload Your CV
1. Go to the **"Upload CV"** tab
2. Click **"Select CV File"** and choose your CV (.pdf or .txt)
3. Click **"Upload CV"**
4. Wait for the success message

#### Step 2: Search Your CV
1. Go to the **"Search CV"** tab
2. Type your search query in the text box
3. Click **"Search"** or press Enter
4. Use the quick search buttons for common queries

#### Step 3: View Summary
1. Go to the **"CV Summary"** tab
2. Click **"Get CV Summary"** to see an overview

### 💡 Search Tips

**Good Search Queries:**
- "programming languages" - Find technical skills
- "education degree" - Get educational background  
- "work experience" - View employment history
- "projects applications" - See project details
- "certifications" - Find credentials

**Search Features:**
- ✅ Case-insensitive matching
- ✅ Multiple keyword support
- ✅ Section-organized results
- ✅ Quick search buttons

### 🔧 Supported Formats
- **PDF files** (.pdf) - Extracted using PyPDF2
- **Text files** (.txt) - Direct text processing

### 📞 Example Searches
Try these examples with your CV:
- "What programming languages do I know?"
- "Where did I study?"
- "What companies have I worked for?"
- "What projects have I completed?"
                """)
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("🔧 **CV Search System** | Simple text-based CV search and analysis")
    
    return interface

def main():
    """Launch the simple CV search application."""
    print("🚀 Starting Simple CV Search System...")
    print("=" * 50)
    
    # Create and launch interface
    interface = create_simple_cv_interface()
    
    print("🌐 Launching Gradio interface...")
    print(f"📱 Access at: http://localhost:7863")
    print("=" * 50)
    
    interface.launch(
        server_name="localhost",
        server_port=7863,
        share=True,
        debug=True,
        show_error=True
    )

if __name__ == "__main__":
    main()