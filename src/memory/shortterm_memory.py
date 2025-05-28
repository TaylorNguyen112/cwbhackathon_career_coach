from typing import List, Dict, Any, Optional
from autogen_core.memory import Memory, MemoryQueryResult
from typing import override

class ShortTermMemory(Memory):
    """
    Simple FIFO memory for storing messages with optional capacity, compatible with AutoGen BaseMemory interface.
    """
    def __init__(self, capacity: Optional[int] = None):
        self._memory: List[Dict[str, Any]] = []
        self._capacity = capacity

    @override
    async def add(self, messages: List[Dict[str, Any]]):
        for msg in messages:
            if self._capacity is not None and len(self._memory) >= self._capacity:
                self._memory.pop(0)
            self._memory.append(msg)

    @override
    async def query(self, query: str, top_k: int = 5) -> MemoryQueryResult:
        # For short-term memory, just return the most recent messages (optionally filter by query in the future)
        results = self._memory[-top_k:] if top_k > 0 else self._memory.copy()
        return MemoryQueryResult(messages=results)

    @override
    async def clear(self):
        self._memory = []

    @override
    async def update_context(self, context: str):
        self._memory = [{"role": "system", "content": context}] + self._memory

    def size(self) -> int:
        return len(self._memory)
    
    async def close(self):
        pass