from typing import List, Dict, Any, override
from uuid import uuid4
from azure.search.documents.aio import SearchClient
from azure.core.credentials import AzureKeyCredential
import os
import logging
import openai  # For Azure OpenAI embeddings
from autogen_core.memory import Memory, MemoryQueryResult
import json

logger = logging.getLogger("VectorMemory")

class VectorMemory(Memory):
    """
    General-purpose vector memory for storing and retrieving documents using Azure Cognitive Search and OpenAI embeddings.
    Can be used for core knowledge, user info, or any other vector-based memory needs.
    """
    def __init__(self, index_name=None):
        self.endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
        self.key = os.getenv("AZURE_SEARCH_KEY")
        self.index_name = index_name
        self.client = None  # Will be created in __aenter__
        # Azure OpenAI embedding config
        self.openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.openai_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        super().__init__()

    async def __aenter__(self):
        self.client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=AzureKeyCredential(self.key)
        )
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc, tb)
            self.client = None

    async def get_embedding(self, text: str) -> List[float]:
        openai.api_type = "azure"
        openai.api_key = self.openai_api_key
        openai.api_base = self.openai_endpoint
        openai.api_version = "2023-05-15"
        response = openai.embeddings.create(
            input=[text],
            model=self.openai_deployment
        )
        return response.data[0].embedding

    @override
    async def add(self, messages: List[Dict[str, Any]]):
        docs = []
        for msg in messages:
            content = msg.get("content", "")
            embedding = await self.get_embedding(content)
            doc = {
                "id": str(uuid4()),
                "content": content,
                "embedding": embedding,
                "metadata": json.dumps(msg.get("metadata", {}))
            }
            docs.append(doc)
        await self.client.upload_documents(documents=docs)
        logger.info(f"Stored {len(docs)} messages in Azure Vector DB")
    
    @override
    async def query(self, query: str, top_k: int = 5, filter: str = None) -> MemoryQueryResult:
        embedding = await self.get_embedding(query)
        search_kwargs = {
            "search_text": "",
            "vector_queries": [{
                "vector": embedding,
                "fields": "embedding",
                "k": top_k,
                "kind": "vector"
            }],
            "top": top_k
        }
        if filter:
            search_kwargs["filter"] = filter
        results = await self.client.search(**search_kwargs)
        docs = [doc async for doc in results]
        logger.info(f"Retrieved {len(docs)} results from Azure Vector DB")
        # Convert docs to the format expected by MemoryQueryResult
        messages = [
            {
                "content": doc.get("content", ""),
                "metadata": doc.get("metadata", {}),
                "mime_type": "text/plain"
            }
            for doc in docs
        ]
        return MemoryQueryResult(results=messages)

    @override
    async def clear(self):
        # Azure Search does not support bulk delete by default; this is a placeholder
        logger.warning("Clear method is not implemented for Azure Search.")
        pass

    async def update_context(self, context: str):
        pass

    async def close(self):
        pass
