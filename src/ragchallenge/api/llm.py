from langchain_google_genai import ChatGoogleGenerativeAI
from ragchallenge.api.config import settings
import os

# ---------------------------- Load Model ---------------------------

# Set the Google API key
os.environ["GOOGLE_API_KEY"] = settings.google_api_key

# Parameters for generation (you can adjust these as needed)
generation_params = {
    "temperature": 0.7,
    "max_output_tokens": 2048,
    "top_p": 0.9,
}

# Try to initialize Gemini LLM
print("🔄 Initializing Gemini LLM...")

# Create a simple mock LLM for testing that matches LangChain interface
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import LLMResult, Generation
from typing import List, Any, Optional

class MockLLM(BaseLanguageModel):
    # Implement required abstract methods
    def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, **kwargs: Any) -> LLMResult:
        # Extract content from messages to understand context
        context = ""
        user_question = ""
        
        for message in messages:
            if hasattr(message, 'content'):
                content = message.content
                if "context" in content.lower() and len(content) > 100:
                    # Extract context from RAG
                    context = content
                elif len(content) < 500:  # Assume shorter messages are questions
                    user_question = content
        
        if not user_question and messages:
            user_question = messages[-1].content if hasattr(messages[-1], 'content') else "Unknown question"
        
        # Create a generic mock response based on context
        if context:
            mock_response = f"""Based on the retrieved document context, here's the answer to your question: "{user_question}"

**Answer:**
The RAG system has successfully retrieved relevant information from your uploaded documents. 

**Context Summary:**
{context[:500]}{'...' if len(context) > 500 else ''}

**Note:** This is a mock response. For AI-powered answers using Google Gemini, please ensure your Google API key is properly configured in the `.env` file.

To get full AI-generated responses:
1. Set `GOOGLE_API_KEY` in your `.env` file
2. Restart the application
3. The system will automatically use Google Gemini for intelligent responses

The RAG pipeline is working correctly - documents are being retrieved based on your query."""
        else:
            mock_response = f"""I received your question: "{user_question}"

However, I don't have sufficient context from the documents to provide a detailed answer. This could mean:

1. No documents have been uploaded yet
2. The uploaded documents don't contain information related to your query
3. The query expansion didn't find relevant chunks

**Note:** This is a mock LLM response. For better results:
- Ensure documents are uploaded via the `/documents/upload` endpoint
- Verify your Google API key is configured for Gemini integration
- Try rephrasing your question to match document content

The system is ready to process your documents once they are uploaded."""
        
        generation = Generation(text=mock_response)
        return LLMResult(generations=[[generation]])
    
    def invoke(self, input_data, config=None, **kwargs):
        if isinstance(input_data, str):
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=input_data)]
        elif isinstance(input_data, list):
            messages = input_data
        elif isinstance(input_data, dict):
            # Handle prompt template format
            content = str(input_data)
            from langchain_core.messages import HumanMessage
            messages = [HumanMessage(content=content)]
        else:
            messages = [input_data]
        
        result = self._generate(messages, **kwargs)
        return AIMessage(content=result.generations[0][0].text)
    
    @property
    def _llm_type(self) -> str:
        return "mock_llm"
    
    # Implement required abstract methods
    def generate_prompt(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any) -> LLMResult:
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=prompts[0])]
        return self._generate(messages, stop, **kwargs)
    
    def predict(self, text: str, *, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        from langchain_core.messages import HumanMessage
        result = self._generate([HumanMessage(content=text)], stop, **kwargs)
        return result.generations[0][0].text
    
    def predict_messages(self, messages: List[BaseMessage], *, stop: Optional[List[str]] = None, **kwargs: Any) -> BaseMessage:
        result = self._generate(messages, stop, **kwargs)
        return AIMessage(content=result.generations[0][0].text)
    
    # Async methods (simple implementations)
    async def agenerate_prompt(self, prompts: List[str], stop: Optional[List[str]] = None, **kwargs: Any) -> LLMResult:
        return self.generate_prompt(prompts, stop, **kwargs)
    
    async def apredict(self, text: str, *, stop: Optional[List[str]] = None, **kwargs: Any) -> str:
        return self.predict(text, stop=stop, **kwargs)
    
    async def apredict_messages(self, messages: List[BaseMessage], *, stop: Optional[List[str]] = None, **kwargs: Any) -> BaseMessage:
        return self.predict_messages(messages, stop=stop, **kwargs)

# Try to create the Google Gemini LLM, fallback to mock if it fails
try:
    LLM = ChatGoogleGenerativeAI(
        model=settings.chat_model,
        google_api_key=settings.google_api_key,
        **generation_params,
    )
    print(f"✅ Successfully initialized Gemini LLM: {settings.chat_model}")
except Exception as e:
    print(f"❌ Warning: Could not initialize Gemini LLM: {e}")
    print("🔄 Falling back to mock LLM...")
    LLM = MockLLM()
    print(f"✅ Mock LLM initialized as fallback")
