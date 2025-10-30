"""
Enhanced RAG Application Startup Script
Starts both the API server and enhanced GUI with document upload functionality.
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_api_server():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Start the API server
    api_process = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=project_dir
    )
    
    return api_process

def start_enhanced_gui():
    """Start the enhanced Gradio GUI."""
    print("🖥️ Starting Enhanced GUI...")
    
    # Change to project directory
    project_dir = Path(__file__).parent
    
    # Start the enhanced GUI
    gui_process = subprocess.Popen(
        [sys.executable, "src/ragchallenge/gui/enhanced_main.py"],
        cwd=project_dir
    )
    
    return gui_process

def main():
    """Main startup function."""
    print("=" * 60)
    print("🧠 RAG Knowledge Base Manager - Enhanced Version")
    print("=" * 60)
    print()
    
    # Start API server
    api_process = start_api_server()
    
    # Wait for API to start
    print("⏳ Waiting for API server to start...")
    time.sleep(5)
    
    # Start GUI
    gui_process = start_enhanced_gui()
    
    print()
    print("✅ Application started successfully!")
    print()
    print("📍 Access Points:")
    print("   🔗 API Server: http://localhost:8081")
    print("   🔗 API Docs: http://localhost:8081/docs")
    print("   🖥️ Enhanced GUI: http://localhost:7862")
    print()
    print("🆕 New Features:")
    print("   📤 Document Upload (PDF, DOCX, TXT, MD)")
    print("   📚 Personal Knowledge Base Management")
    print("   🗑️ Document Deletion")
    print("   🔄 Multiple Knowledge Base Options")
    print("   📊 Vector Store Information")
    print()
    print("💡 Usage Tips:")
    print("   1. Upload your documents in the 'Document Upload' tab")
    print("   2. Manage your knowledge base in the 'Knowledge Base' tab")
    print("   3. Ask questions about your documents in the 'Ask Questions' tab")
    print("   4. Choose 'personal' to search only your documents")
    print("   5. Choose 'combined' to search both your docs and default knowledge")
    print()
    print("Press Ctrl+C to stop the application")
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("⚠️ API server stopped unexpectedly")
                break
                
            if gui_process.poll() is not None:
                print("⚠️ GUI stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\\n🛑 Shutting down application...")
        
        # Terminate processes
        api_process.terminate()
        gui_process.terminate()
        
        # Wait for clean shutdown
        api_process.wait()
        gui_process.wait()
        
        print("✅ Application shut down successfully")

if __name__ == "__main__":
    main()