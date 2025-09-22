from fastapi import APIRouter, Request, Response, HTTPException
from pydantic import BaseModel
from ..memory.chat_memory import ChatMemory
from ..config import settings

router = APIRouter()
memory = ChatMemory()

@router.get('/')
def get_session(request: Request, response: Response):
    session_id = request.cookies.get('chat_session_id')
    if session_id:
        expires = memory.refresh(session_id)
        if expires:
            response.set_cookie(
                key='chat_session_id',
                value=session_id,
                httponly=True,
                expires=expires
            )
            return
        else:
            response.delete_cookie('chat_session_id')
            raise HTTPException(status_code=401, detail='Invalid session')
    new_session_id, expires = memory.create_memory()
    response.set_cookie(
        key='chat_session_id',
        value=new_session_id,
        httponly=True,
        expires=expires
    )
    return
