# Mini Agent Platform

A multi-tenant AI agent management system that allows you to create, manage, and execute AI agents with configurable
tools and instructions.

## Features

- **Multi-Tenant Architecture**: Complete data isolation using tenant-based API keys
- **Agent Management**: Full CRUD operations for AI agents with roles and descriptions
- **Tool Management**: Create and assign tools to agents
- **Agent Execution**: Run agents with tasks and track execution history
- **Rate Limiting**: Per-tenant API throttling (e.g.10 requests per 60 seconds)
- 
---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip

### Setup

1. **Clone project**

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
pip install -r requiremants.txt
```

4. **Run the application**:

```bash
python main.py
```

The server will start at `http://localhost:8000`

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
        "request_limit": 5,
        "limit_window": timedelta(minutes=1),
        "count_requests": 0,
        "last_reset": datetime.utcnow()
    }
}
```
Include the API key in the `X-API-Key` header for all requests:

---


## API Endpoints
## Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to test all endpoints directly from your browser.
### Tools

#### - Create - `POST /tools`
#### - Get all - `Get /tools`
#### - GET by agent name `/tools?agent_name=agent_name`
#### - Get by tool id - `Get /tools/{tool_id}`
#### - Get by tool name - `Get /tools/{tool_name}`
#### - Update - `PUT /tools/{tool_id}`
#### - Delete by id - `DELETE /tools/{tool_id}`



### Agents
#### - Create - `POST /agents`
#### - Get all - `Get /agents`
#### - GET by tool name `/agents?tool_name=tool_name`
#### - Get by agent id - `Get /agents/{agent_id}`
#### - Get by agent name - `Get /agents/{agent_name}`
#### - Update - `PUT /agents/{agent_id}`
#### - Delete by id - `DELETE /agents/{agent_id}`
#### - Run agent by id - `Post /agents/{agent_id}/run`


### Executions
#### - Get all - `GET /executions`
#### - Get by agent_id - `GET /executions?agent_id=1`
#### - Get with Pagination - `GET /executions?page=1&page_size=10`

---

### Database Schema

```
┌─────────────┐
│   Tool      │
├─────────────┤
│ id          │
│ tenant_id   │
│ name        │
│ description │
└─────────────┘
       │
       │ 
       │
┌──────────────┐      ┌─────────────────────┐
│   Agents     │──────│  Executions         │
├──────────────┤      ├─────────────────────┤
│ id           │      │ id                  │
│ tenant_id    │      │ tenant_id           │
│ name         │      │ agent_id            │
│ role         │      │ prompt              │
│ description  │      │ model               │
└──────────────┘      │ response            │
                      │ timestamp           │
                      └─────────────────────┘
```

---

## Testing

### Test Coverage

- **Authentication**: API key validation and tenant isolation
- **Tool CRUD**: Create, read, update, delete operations
- **Agent CRUD**: Full agent management with tool associations
- **Tenant Isolation**: Ensures complete data separation between tenants
- **Agent Execution**: Running agents with tasks and tracking history
- **Rate Limiting**: Per-tenant throttling enforcement
- **Pagination**: Handling large result sets
- **Filtering**: Query operations with filters

Run the comprehensive test suite:

```bash
pytest test_main.py -v
```
