from typing import List, Optional

from fastapi import APIRouter, HTTPException

from base_model import ExecutionResponse
from models import Execution
from utils import db_dependency, api_key_dependency

router = APIRouter()


@router.get("", response_model=List[ExecutionResponse])
async def get_executions(db: db_dependency,
                         tenant_id: api_key_dependency,
                         agent_id: Optional[int] = None,
                         page: Optional[int] = None,
                         page_size: Optional[int] = None
                         ):
    query = db.query(Execution).filter(Execution.tenant_id == tenant_id)
    if agent_id:
        query = query.filter(Execution.agent_id == agent_id)
    if page is not None and page_size is not None:
        if page < 1 or page_size < 1:
            raise HTTPException(status_code=400, detail="page and page_size must be positive integers")
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
    elif page is not None or page_size is not None:
        raise HTTPException(
            status_code=400,
            detail="Both page and page_size must be provided together"
        )
    executions = query.all()
    if not executions:
        raise HTTPException(status_code=404, detail="Executions not found")
    return executions
