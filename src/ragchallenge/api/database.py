from ragchallenge.api.interfaces.database import DocumentStore
from ragchallenge.api.config import settings

# ---------------------------- Load Database --------------------------- #

# Lazy load database to avoid startup issues
DATABASE = None

def get_database():
    """Lazy-load the database when needed."""
    global DATABASE
    if DATABASE is None:
        DATABASE = DocumentStore(
            model_name=settings.embedding_model,
            persist_directory="data/vectorstore",  # Use the populated vectorstore
            device=settings.embedding_model_device
        )
        print(f"📊 Loaded vector database with {len(DATABASE.vector_store.get()['ids'])} documents")
    return DATABASE
