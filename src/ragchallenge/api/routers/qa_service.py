
from ragchallenge.api.rag import get_rag_model, get_user_rag_model, get_combined_rag_model
from fastapi import APIRouter, HTTPException, Query
from ragchallenge.api.schemas.messages import ChatResponse, ChatRequest, ChatMessage
from typing import Optional

router = APIRouter(responses={404: {"description": "Not Found"}})


# ---------------------------- Endpoints --------------------------- #


@router.post("/generate-answer", response_model=ChatResponse)
async def generate_answer(
    request: ChatRequest, 
    user_id: Optional[str] = Query(None, description="User ID for personal knowledge base"),
    use_combined: bool = Query(False, description="Search both personal and default knowledge base")
):
    """Generate an answer to a question and append it as the last message. Uses RAG, query expansion, and hypothetical question generation."""
    try:
        # Get the user's question from the last message in the list
        user_message = request.messages[-1].content
        
        # Select appropriate RAG model based on user preferences
        if use_combined and user_id:
            rag_model = get_combined_rag_model(user_id)
        elif user_id:
            rag_model = get_user_rag_model(user_id)
        else:
            rag_model = get_rag_model()
        
        response = rag_model.answer_question(user_message)
        request.messages.append(ChatMessage(role="system", content=response.get("answer")))

        # Return the updated messages list with the generated answer appended
        return ChatResponse(
            messages=request.messages, 
            questions=response.get("question"), 
            documents=response.get("documents"),
            user_id=str(user_id) if user_id is not None else "",
            knowledge_base_type="personal" if user_id and not use_combined else "combined" if use_combined else "default"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-answer-personal", response_model=ChatResponse)
async def generate_answer_personal(request: ChatRequest, user_id: str):
    """Generate an answer using only the user's personal knowledge base."""
    try:
        user_message = request.messages[-1].content
        rag_model = get_user_rag_model(user_id)
        response = rag_model.answer_question(user_message)
        request.messages.append(ChatMessage(role="system", content=response.get("answer")))

        return ChatResponse(
            messages=request.messages, 
            questions=response.get("question"), 
            documents=response.get("documents"),
            user_id=user_id,
            knowledge_base_type="personal"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
