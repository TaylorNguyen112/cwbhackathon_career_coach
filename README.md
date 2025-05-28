# Career Coach: Multi-Agent, Streaming, MCP-Integrated AI Platform

A modular, production-ready multi-agent system for career coaching, featuring:
- **MCP tool server integration** (web search, extensible)
- **Shared and semantic memory for agents**
- **Modern web frontend and backend**
- **Extensible, clean codebase for research or production**

---

## Project Structure

```
career_coach/
│
├── requirements.txt      # Python dependencies
├── .env                  # (You must provide) Environment variables for Azure/OpenAI/MCP
│
├── docs/                 # Additional documentation (memory, tools, swarm vs group chat, etc.)
│
└── src/
    ├── api/              # FastAPI backend (main.py)
    ├── frontend/         # React frontend (src/App.js)
    ├── memory/           # Memory modules (short-term, vector/semantic)
    ├── mcp/
    │   └── web-search/   # MCP server for web search (Node.js)
    ├── workflow/         # Agent orchestration, tools, and workflow logic

```
---

## Key Features

### 1. **Multi-Agent Orchestration**
- Modular agent design, easily extensible.
- Agents have both shared (short-term) and semantic (vector) memory.
- Agents can use all tools from MCP servers.

### 2. **MCP Tool Integration**
- MCP server for web search (`src/mcp/web-search/`).
- Tools are fetched at runtime and assigned to agents.
- Easily extensible: add new MCP servers by following the pattern in `src/mcp/`.

### 3. **Modern Web UI**
- React frontend (`src/frontend/src/App.js`) for chat, including CV upload and preview.
- FastAPI backend (`src/api/main.py`) for streaming and CV extraction.

---

## File/Folder Purpose

- **requirements.txt**: Python dependencies (OpenAI, FastAPI, etc.)
- **.env**: (You must provide) API keys and endpoints for Azure/OpenAI/MCP.
- **src/api/main.py**: FastAPI backend, handles chat WebSocket and agent streaming.
- **src/frontend/src/App.js**: React chat UI, connects to backend via WebSocket.
- **src/memory/shortterm_memory.py**: FIFO memory for agent collaboration.
- **src/memory/vector_memory.py**: Vector/semantic memory for knowledge retrieval.
- **src/mcp/web-search/**: Node.js MCP server for web search.
- **src/workflow/agents.py**: Main agent orchestration and workflow logic.

---

## Environment Variables (`.env`)

Create a `.env` file in the root with at least:

```
AZURE_OPENAI_API_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_SEARCH_ENDPOINT=https://your-azure-search-endpoint.search.windows.net/
AZURE_SEARCH_KEY=your-azure-search-key
AZURE_SEARCH_INDEX=your-azure-search-index
```

---

## Step-by-Step: How to Run and Host

### 1. **Install Python Dependencies**
```sh
cd career_coach
pip install -r requirements.txt
```

### 2. **Install Node.js (for MCP servers)**
Make sure you have Node.js and npm installed.

### 3. **Host the MCP Web Search Server**
```sh
cd src/mcp/web-search
npm install
npm start
```

### 4. **Set Up Your .env**
Create a `.env` file in the root as described above.

### 5. **Start the FastAPI Backend**
```sh
cd src
uvicorn api.main:app --reload
```

### 6. **Start the React Frontend**
```sh
cd src/frontend
npm install
npm start
```
The frontend will typically run at [http://localhost:3000](http://localhost:3000).

---

## How It Works

- The frontend (React) sends user messages to the backend (FastAPI) via WebSocket.
- The backend streams each LLM token as soon as it is generated.
- Agents can use all tools from MCP servers.
- Both shared and semantic memory are used for agent context.
- The chat UI updates in real time as the LLM responds.

---

## Memory in Career Coach

- **Shared Message Context:** The running history of the current conversation.
- **Short-Term Memory:** Persistent, structured memory for recent facts and user preferences (`src/memory/shortterm_memory.py`).
- **Semantic Memory:** Vector-based memory for long-term/core knowledge and retrieval (`src/memory/vector_memory.py`).

---

## Extending and Customizing

- Add new agents or tools by extending the agent or MCP server modules.
- Adjust memory or streaming logic in `src/workflow/`.
- Add new MCP servers by following the pattern in `src/mcp/`.

---

## Contributors

- **Ngoc Nguyen** (main author and maintainer)

For further customization, deployment, or questions, please open an issue or contact the maintainers!

