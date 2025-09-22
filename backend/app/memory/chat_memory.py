from langchain.memory.chat_message_histories.in_memory import ChatMessageHistory
from typing import Dict, Optional, Any, Tuple
import uuid
from datetime import datetime, timedelta, timezone
from ..config import settings
import threading

def singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance

@singleton
class ChatMemory:
    def __init__(self):
        self.store : Dict[str, Dict[str, Any]] = {}
        self._start_clean_schedule()
    
    def create_memory(self) -> Tuple[str, timedelta]:
        session_id = str(uuid.uuid4())
        while session_id in self.store.keys():
            session_id = str(uuid.uuid4())
        expires = datetime.now(timezone.utc) + timedelta(seconds=settings.MEMORY_CONFIG['ttl'])
        self.store[session_id] = {
            'buffer': ChatMessageHistory(),
            'summary': '',
            'expires_at': expires
        }
        return session_id, expires

    def get_memory(self, session_id: str) -> Optional[Dict[str, Any]]:
        if session_id not in self.store.keys():
            return None
        history = self.store[session_id]
        if history['expires_at'] < datetime.now(timezone.utc):
            self.delete_memory(session_id)
            return None
        return history
    
    def save_memory(self, session_id: str, user_input: str, ai_response: str, summary: str) -> None:
        if session_id not in self.store.keys():
            return
        self.store[session_id]['buffer'].add_user_message(user_input)
        self.store[session_id]['buffer'].add_ai_message(ai_response)
        self.store[session_id]['summary'] = summary
        self.store[session_id]['expires_at'] = datetime.now(timezone.utc) + timedelta(seconds=settings.MEMORY_CONFIG['ttl'])

    def clear_memory(self, session_id: str):
        if session_id in self.store.keys():
            self.store[session_id]['buffer'].clear()
            self.store[session_id]['summary'] = ''
    
    def delete_memory(self, session_id: str):
        self.store.pop(session_id, None)
    
    def clean(self):
        expired_sessions = [
            session_id 
            for session_id, history in self.store.items()
            if history['expires_at'] < datetime.now(timezone.utc)
        ]
        for session_id in expired_sessions:
            self.delete_memory(session_id)
    
    def exists(self, session_id: str) -> bool:
        if session_id not in self.store.keys():
            return False
        history = self.store[session_id]
        if history['expires_at'] < datetime.now(timezone.utc):
            return False
        return True

    def refresh(self, session_id: str) -> Optional[datetime]:
        if session_id in self.store.keys():
            self.store[session_id]['expires_at'] = datetime.now(timezone.utc) + timedelta(seconds=settings.MEMORY_CONFIG['ttl'])
            return self.store[session_id]['expires_at']
        
    def _start_clean_schedule(self):
        def run():
            while True:
                self.clean()
                threading.Event().wait(3600)
        t = threading.Thread(target=run, daemon=True)
        t.start()