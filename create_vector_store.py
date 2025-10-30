"""
Vector Store Creation Script
Populate the vector store with documents from data/raw/
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from ragchallenge.api.config import settings
from pathlib import Path

def create_vector_store():
    """Create and populate vector store from raw documents."""
    print("🚀 Creating Vector Store...")
    
    try:
        # Initialize embeddings
        print("📊 Loading embeddings model...")
        embeddings = HuggingFaceEmbeddings(
            model_name=settings.embedding_model,
            model_kwargs={'device': settings.embedding_model_device}
        )
        print("✅ Embeddings loaded successfully")
        
        # Initialize text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Load documents from raw directory
        raw_dir = Path("data/raw")
        documents = []
        
        for file_path in raw_dir.glob("*.md"):
            print(f"📖 Processing {file_path.name}...")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split into chunks
            chunks = text_splitter.split_text(content)
            
            # Create documents
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": file_path.name,
                        "chunk": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)
            
            print(f"  ✅ Created {len(chunks)} chunks from {file_path.name}")
        
        print(f"\n📚 Total documents created: {len(documents)}")
        
        # Create vector store
        print("🔧 Creating vector store...")
        vectorstore_path = "data/vectorstore"
        
        # Remove existing vectorstore if it exists
        import shutil
        if os.path.exists(vectorstore_path):
            shutil.rmtree(vectorstore_path)
            print("🗑️  Removed existing vector store")
        
        # Create new vectorstore
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=vectorstore_path
        )
        
        print("✅ Vector store created and populated!")
        
        # Test the vector store
        print("\n🔍 Testing vector store...")
        test_query = "How to initialize git repository?"
        search_results = vectorstore.similarity_search(test_query, k=3)
        
        print(f"📋 Search Results for: '{test_query}'")
        for i, doc in enumerate(search_results, 1):
            print(f"  {i}. {doc.page_content[:100]}...")
            print(f"     Source: {doc.metadata.get('source', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating vector store: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_vector_store()
    if success:
        print("\n🎉 Vector store created successfully!")
    else:
        print("\n❌ Failed to create vector store!")