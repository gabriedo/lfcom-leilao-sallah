import os
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

class OpenAIClient:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenAIClient, cls).__new__(cls)
            cls._instance.client = OpenAI(api_key=OPENAI_API_KEY)
            cls._instance.model = OPENAI_MODEL
        return cls._instance
    
    @property
    def client(self):
        return self._instance.client
    
    @property
    def model(self):
        return self._instance.model

# Instância global do cliente OpenAI
openai_client = OpenAIClient() 