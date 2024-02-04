import bentoml
from llama_index.embeddings.base import BaseEmbedding

import os

EMBEDDINGS_URL = "https://sentence-transformers-kwk9-b8418a6d.mt-guc1.bentoml.ai"

class BentoMLEmbeddings(BaseEmbedding):
    url = EMBEDDINGS_URL
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def sync_client(self, query: str):
        response = {}
        with bentoml.SyncHTTPClient(self.url) as client:
            if isinstance(query, list):
                response = client.encode(sentences=query)
            else:
                response = client.encode(sentences=[query])  
        return response
    
    async def async_client(self, query: str):
        response = {}
        async with bentoml.AsyncHTTPClient(self.url) as client:
            if isinstance(query, list):
                response = client.encode(sentences=query)
            else:
                response = client.encode(sentences=[query])  
        return response
    
    async def _aget_query_embedding(self, query: str):
        res = await self.async_client(query)
        return res[0]
    
    def _get_query_embedding(self, query: str):
        return self.sync_client(query)[0]
    
    def _get_text_embedding(self, text):
        if isinstance(text, str):
            return self.sync_client(text)
        else:
            return self.sync_client(text[0].get_text())
    
    def _get_text_embeddings(self, text):
        if isinstance(text, str) or isinstance(text[0], str):
            return self.sync_client(text)
        else:
            return self.sync_client(text[0].get_text())
