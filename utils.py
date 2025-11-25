from datetime import datetime, timedelta
from typing import Annotated

import redis
from fastapi import Header, Depends, HTTPException
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Agent

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)
REDIS_KEY = "rate_limit"

API_KEYS = {
    "tenant_a": {
        "request_limit": 10,
        "limit_window": timedelta(hours=1)
    },
    "tenant_b": {
        "request_limit": 200,
        "limit_window": timedelta(days=1)
    },
    "tenant_c": {
        "request_limit": 2,
        "limit_window": timedelta(minutes=1)
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
    return tenant_id_header


db_dependency = Annotated[Session, Depends(get_db)]
api_key_dependency = Annotated[str, Depends(verify_api_key)]


def check_tenant_limit(tenant_id):
    tenant = API_KEYS.get(tenant_id)
    now = datetime.utcnow()

    count = redis_client.get(f"{REDIS_KEY}:{tenant_id}:count")
    count = int(count) if count else 0
    last_reset = redis_client.get(f"{REDIS_KEY}:{tenant_id}:last_reset")
    if last_reset:
        last_reset = datetime.fromisoformat(last_reset)

    else:
        last_reset = now
        redis_client.set(f"{REDIS_KEY}:{tenant_id}:last_reset", now.isoformat())

    time_diff = now - last_reset
    if time_diff >= tenant["limit_window"]:
        redis_client.set(f"{REDIS_KEY}:{tenant_id}:count", 0)
        redis_client.set(f"{REDIS_KEY}:{tenant_id}:last_reset", now.isoformat())
        count = 0

    if count >= tenant["request_limit"]:
        return False

    redis_client.incr(f"{REDIS_KEY}:{tenant_id}:count")
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
