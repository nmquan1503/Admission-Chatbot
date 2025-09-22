from fastapi import APIRouter, Request, Response, HTTPException
from pydantic import BaseModel
from ..chatbot.chatbot import Chatbot
from ..memory.chat_memory import ChatMemory
import atexit

router = APIRouter()
chatbot = Chatbot()
memory = ChatMemory()

class ChatRequest(BaseModel):
    user_input: str

class ChatResponse(BaseModel):
    ai_response: str

@router.post('/', response_model=ChatResponse)
def chat(request: Request, payload: ChatRequest, response: Response):
    session_id = request.cookies.get('chat_session_id')
    if not memory.exists(session_id):
        raise HTTPException(status_code=401, detail='Invalid session')
    ai_response = chatbot.chat(
        session_id=session_id,
        user_input=payload.user_input
    )
    if not ai_response:
        raise HTTPException(status_code=500, detail='Chatbot failed to generate response')
    history = memory.get_memory(session_id)
    expires = history['expires_at']
    response.set_cookie(
        key='chat_session_id',
        value=session_id,
        httponly=True,
        expires=expires
    )
    return ChatResponse(ai_response=ai_response)
    
atexit.register(chatbot.close)