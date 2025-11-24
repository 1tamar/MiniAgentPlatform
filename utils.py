from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Agent

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

SUPPORTED_MODELS = ["gpt-4o", "gpt-4-turbo", "claude-3-opus"]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_api_key(tenant_id_header: str = Header(..., alias="x-api-key")):
    tenant_id = API_KEYS.get(tenant_id_header)
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return tenant_id.get("name")


db_dependency = Annotated[Session, Depends(get_db)]
api_key_dependency = Annotated[str, Depends(verify_api_key)]


def check_tenant_limit(tenant_id):
    tenant = API_KEYS.get(tenant_id)
    now = datetime.utcnow()
    if now - tenant.get("last_reset") > tenant.get("limit_window"):
        tenant["count_requests"] = 0
        tenant["last_reset"] = now
        return True
    tenant["count_requests"] += 1
    if tenant.get("count_requests") >= tenant.get("request_limit"):
        return False
    return True


def generate_prompt(agent: Agent, task: str):
    prompt_msg = f"""    You are {agent.name}, {agent.role}.
    Description: {agent.description}
    Available tools: {agent.tools or "No tools available"}
    Task: {task}
    Please complete the task using the information and tools available to you.
    """
    return prompt_msg


def mock_llm_call(prompt: str, model: str):
    mock_res = prompt.split("\n")[0].strip()
    return f"[mock-response from {model}]: {mock_res}"
