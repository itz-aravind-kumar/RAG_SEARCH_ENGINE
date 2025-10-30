from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path
from typing import Optional

from ragchallenge.api.database import get_database
from ragchallenge.api.paraphraser import PARAPHRASER
from ragchallenge.api.llm import LLM
from ragchallenge.api.config import Settings
from ragchallenge.api.interfaces.ragmodelexpanded import QuestionAnsweringWithQueryExpansion

messages = [
    SystemMessage(
        role="system",
        content="""You are an intelligent document assistant powered by RAG (Retrieval-Augmented Generation).
            Your task is to provide accurate, relevant, and context-specific answers based on the documents provided to you.
            
            **Instructions:**
            - Answer questions using ONLY the information from the provided context (retrieved documents).
            - If the context contains sufficient information, provide a clear, detailed, and well-structured answer.
            - If the context is insufficient or the information is not available, respond with: 'I don't have enough information to answer that question based on the provided documents.'
            - Format your responses using markdown for better readability (use headings, bullet points, code blocks, tables, etc. as appropriate).
            - Be concise yet comprehensive - provide all relevant details without unnecessary verbosity.
            - When appropriate, cite or reference specific parts of the documents you're using.
            - If multiple documents contain relevant information, synthesize the information coherently.
            - Do NOT make assumptions or add information that is not present in the context.
            
            Your goal is to help users understand and extract insights from their uploaded documents."""
    ),
    HumanMessage(
        role="user",
        content="""Context from retrieved documents:
            {context}
            ---
            Now, here is the question you need to answer:

            Question: {question}"""
    ),
]

# Create the ChatPromptTemplate object
prompt_template = ChatPromptTemplate.from_messages(
    [(msg.role, msg.content) for msg in messages]
)

# Initialize config for user vectorstores
config = Settings()
embeddings = None

def get_embeddings():
    """Lazy-load embeddings when needed."""
    global embeddings
    if embeddings is None:
        embeddings = HuggingFaceEmbeddings(
            model_name=config.embedding_model,
            model_kwargs={'device': config.embedding_model_device}
        )
    return embeddings

# Lazy-load the default RAG model
RAG_MODEL = None

def get_rag_model():
    """Lazy-load the default RAG model."""
    global RAG_MODEL
    if RAG_MODEL is None:
        database = get_database()
        RAG_MODEL = QuestionAnsweringWithQueryExpansion(
            knowledge_vector_database=database.vector_store,
            prompt_template=prompt_template,
            question_generator=PARAPHRASER,
            model=LLM
        )
        print("✅ Initialized default RAG model")
    return RAG_MODEL


def get_user_rag_model(user_id: Optional[str] = None) -> QuestionAnsweringWithQueryExpansion:
    """
    Get RAG model for specific user or default model.
    
    Args:
        user_id: User ID to load personal vector store, None for default
        
    Returns:
        QuestionAnsweringWithQueryExpansion instance
    """
    if user_id:
        # Load user-specific vector store
        user_vectorstore_path = Path(f"data/user_vectorstores/{user_id}")
        
        if user_vectorstore_path.exists():
            try:
                user_vectorstore = Chroma(
                    persist_directory=str(user_vectorstore_path),
                    embedding_function=get_embeddings()
                )
                
                return QuestionAnsweringWithQueryExpansion(
                    knowledge_vector_database=user_vectorstore,
                    prompt_template=prompt_template,
                    question_generator=PARAPHRASER,
                    model=LLM
                )
            except Exception as e:
                print(f"⚠️  Error loading user vectorstore for {user_id}: {e}")
                # Fallback to default
                return RAG_MODEL
    
    # Return default RAG model
    return get_rag_model()


def get_combined_rag_model(user_id: Optional[str] = None) -> QuestionAnsweringWithQueryExpansion:
    """
    Get RAG model that searches both user documents and default knowledge base.
    
    Args:
        user_id: User ID to include personal vector store
        
    Returns:
        QuestionAnsweringWithQueryExpansion instance with combined search capability
    """
    if user_id:
        user_vectorstore_path = Path(f"data/user_vectorstores/{user_id}")
        
        if user_vectorstore_path.exists():
            try:
                # Create a combined retriever that searches both stores
                user_vectorstore = Chroma(
                    persist_directory=str(user_vectorstore_path),
                    embedding_function=get_embeddings()
                )
                
                # For now, return user-specific model
                # TODO: Implement true combined search across multiple vector stores
                return QuestionAnsweringWithQueryExpansion(
                    knowledge_vector_database=user_vectorstore,
                    prompt_template=prompt_template,
                    question_generator=PARAPHRASER,
                    model=LLM
                )
            except Exception as e:
                print(f"⚠️  Error loading combined vectorstore for {user_id}: {e}")
    
    # Fallback to default
    return get_rag_model()
