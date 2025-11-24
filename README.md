# Mini Agent Platform

A multi-tenant AI agent management system that allows you to create, manage, and execute AI agents with configurable
tools and instructions.

## Features

- **Multi-Tenant Architecture**: Complete data isolation using tenant-based API keys
- **Agent Management**: Full CRUD operations for AI agents with roles and descriptions
- **Tool Management**: Create and assign tools to agents
- **Agent Execution**: Run agents with tasks and track execution history
- **Rate Limiting**: Per-tenant API throttling (e.g.10 requests per 60 seconds)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip
- git
- PostgreSQL

### Setup

1. **Clone the repository**:

```bash
git clone https://github.com/1tamar/MiniAgentPlatform.git
cd MiniAgentPlatform
```

2. **Create a virtual environment**:

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install requirements from inside project dir**:

```bash
pip install -r requirements.txt
```

4. **Run the application**:

```bash
python main.py
```

The server will start at `http://localhost:8000`

---

## API Authentication

The platform uses API key-based authentication. Each API key represents a different tenant.

### Available API Keys

```

API_KEYS = {
    "tenant_a": {
        "name": "tenant_a",
        "request_limit": 10,
        "limit_window": timedelta(hours=1),
        "count_requests": 0,
        "last_reset": datetime.utcnow()
    },
    "tenant_b": {
        "name": "tenant_b",
        "request_limit": 200,
        "limit_window": timedelta(days=1),
        "count_requests": 0,
        "last_reset": datetime.utcnow()
    },
    "tenant_c": {
        "name": "tenant_c",
        "request_limit": 2,
        "limit_window": timedelta(minutes=1),
        "count_requests": 0,
        "last_reset": datetime.utcnow()
    }
}
```

## Include the API key in the `X-API-Key: tenant_a` header for all requests!

---

## API Endpoints

## Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test all endpoints directly from your browser.

### Tools

#### - Create - `POST /tools`

```
Body:
{
  "name": "tool1",
  "description": "Description of tool1"
}
```

#### - Get all - `Get /tools`

#### - GET by agent name `/tools?agent_name=agent_name`

#### - Get by tool id - `Get /tools/{tool_id}`

#### - Get by tool name - `Get /tools/{tool_name}`

#### - Update - `PUT /tools/{tool_id}`

```
Body:
{
  "name": "tool1-updated",
  "description": "New description"
}
```

#### - Delete by id - `DELETE /tools/{tool_id}`

### Agents

#### - Create - `POST /agents`

```
Body:
{
  "name": "agent1",
  "role": "assistant",
  "description": "Agent that does X",
  "tenant_id": 1,
  "tool_ids": [1]
}
```

#### - Get all - `Get /agents`

#### - GET by tool name `/agents?tool_name=tool_name`

#### - Get by agent id - `Get /agents/{agent_id}`

#### - Get by agent name - `Get /agents/{agent_name}`

#### - Update - `PUT /agents/{agent_id}`

```
Body:
{
  "name": "agent1-updated",
  "description": "New description",
  "role":"new role"
}
```

#### - Delete by id - `DELETE /agents/{agent_id}`

#### - Run agent by id - `Post /agents/{agent_id}/run`

**model should be one of the SUPPORTED_MODELS: ["gpt-4o", "gpt-4-turbo", "claude-3-opus"]**

```
Body:
{
  "task": "Please summarise the latest report.",
  "model": "gpt-4o"
}
```

### Executions

#### - Get all - `GET /executions`

#### - Get by agent_id - `GET /executions?agent_id=1`

#### - Get with Pagination - `GET /executions?page=1&page_size=10`

---

## Testing

The project includes a test suite.
To run the tests:

```bash
pytest tests/test_main.py -v
```
