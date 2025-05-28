from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import asyncio
import json
import os
from workflow.config import llm_config
from workflow.agents import create_agents as orig_create_agents
from workflow.agent_selectors import human_in_the_loop_selector
from autogen_agentchat.teams import SelectorGroupChat
from autogen_core.model_context import BufferedChatCompletionContext
from memory.vector_memory import VectorMemory
import queue
import shutil
import uuid
from autogen_agentchat.agents import UserProxyAgent

# For file parsing
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import docx
except ImportError:
    docx = None

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Helper: Patch agent message sending to stream events to WebSocket
async def stream_agent_event(event, websocket):
    # event: dict with keys like 'agent', 'type', 'content', 'tool', 'handoff'
    await websocket.send_text(json.dumps(event))

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    session_id = websocket.query_params.get("session_id")
    await websocket.accept()

    # Patch print to also send to WebSocket as a system message
    import builtins
    orig_print = builtins.print
    async def ws_print(*args, **kwargs):
        msg = " ".join(str(a) for a in args)
        event = {
            "agent": "system",
            "type": "system",
            "content": msg,
            "tool": None,
            "handoff": False
        }
        await stream_agent_event(event, websocket)
        builtins.print = orig_print
        try:
            orig_print(*args, **kwargs)
        finally:
            builtins.print = print_patch
    def print_patch(*args, **kwargs):
        import asyncio
        loop = asyncio.get_event_loop()
        loop.create_task(ws_print(*args, **kwargs))
    builtins.print = print_patch

    try:
        async with VectorMemory(index_name=os.getenv("AZURE_SEARCH_INDEX_PROFILE")) as user_vector_memory:
            agent_config = llm_config("agent")
            tool_config = llm_config("tool")
            model_context = BufferedChatCompletionContext(buffer_size=10)
            user_message_queue = queue.Queue()
            async def websocket_input_func(prompt=None, *args, **kwargs):
                print("WAITING FOR USER INPUT")
                import asyncio
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, user_message_queue.get)
            agents, user_agent = await create_agents_with_patched_user(agent_config, tool_config, websocket_input_func)
            group_agents = agents + [user_agent]
            # Patch ProfilerAgent to auto-retrieve CV from vector memory on first turn
            for agent in group_agents:
                if getattr(agent, "name", None) == "ProfilerAgent":
                    orig_on_message = getattr(agent, "on_message", None)
                    agent._cv_checked = False
                    async def patched_on_message(self, msg, *args, **kwargs):
                        if not self._cv_checked:
                            self._cv_checked = True
                            # Query vector memory for CV/resume
                            result = await user_vector_memory.query("resume OR curriculum OR cv", top_k=1)
                            if result and getattr(result, "results", None):
                                cv_text = result.results[0]["content"]
                                analysis = f"I found your uploaded CV. Here is my analysis:\n\n[CV Preview]\n{cv_text[:500]}...\n\n(For a full analysis, please ask specific questions or provide more details.)"
                                event = {
                                    "agent": self.name,
                                    "type": "message",
                                    "content": analysis,
                                    "tool": None,
                                    "handoff": False
                                }
                                print("HOOK CALLED", event)
                                await stream_agent_event(event, websocket)
                                return
                        if orig_on_message:
                            return await orig_on_message(msg)
                    import types
                    agent.on_message = types.MethodType(patched_on_message, agent)
            groupchat = SelectorGroupChat(
                participants=group_agents,
                model_client=agent_config,
                max_turns=30,
                selector_func=human_in_the_loop_selector,
                model_context=model_context
            )
            import asyncio
            groupchat_task = asyncio.create_task(groupchat.run())
            try:
                while True:
                    data = await websocket.receive_text()
                    user_message = json.loads(data)
                    text = user_message.get("content", "")
                    user_message_queue.put(text)
            except WebSocketDisconnect:
                pass
            except Exception as e:
                await websocket.close(code=1011, reason=str(e))
            finally:
                groupchat_task.cancel()
                try:
                    await groupchat_task
                except Exception:
                    pass
    finally:
        builtins.print = orig_print

# --- PATCHED USERPROXYAGENT TO FORCE CUSTOM INPUT FUNC ---
class PatchedUserProxyAgent(UserProxyAgent):
    def __init__(self, *args, input_func=None, **kwargs):
        super().__init__(*args, **kwargs)
        if input_func:
            self.input_func = input_func
    # Optionally, override methods to guarantee input_func is used

async def create_agents_with_patched_user(agent_config, tool_config, input_func):
    agents, user_agent = await orig_create_agents(agent_config, tool_config)
    # Replace user_agent with patched version
    patched_user_agent = PatchedUserProxyAgent("user_proxy", input_func=input_func)
    return agents, patched_user_agent 