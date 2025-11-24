from typing import List

from fastapi import APIRouter, HTTPException

from models import Execution
from utils import db_dependency, api_key_dependency

router = APIRouter()


@router.get("")
async def get_executions(db: db_dependency,
                         tenant_id: api_key_dependency,
                         agent_id: int = None,
                         page: int = 1,
                         page_size: int = 10
                         ):
    query = db.query(Execution).filter(Execution.tenant_id == tenant_id)
    if agent_id:
        query = query.filter(Execution.agent_id == agent_id)
    offset = (page - 1) * page_size
    query = query.order_by(Execution.timestamp).offset(offset).limit(page_size).all()
    if not query:
        raise HTTPException(status_code=404, detail="Executions not found")
    return query
