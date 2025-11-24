from typing import Optional

from fastapi import APIRouter, HTTPException

from base_model import ToolBase, ToolUpdate
from models import Tool, agent_tools, Agent
from utils import db_dependency, api_key_dependency

router = APIRouter()


@router.get("")
async def get_tools(db: db_dependency,
                    tenant_id: api_key_dependency,
                    agent_name: Optional[str] = None,
                    name: Optional[str] = None):
    query = db.query(Tool).filter(Tool.tenant_id == tenant_id)
    if agent_name:
        query = query.join(agent_tools).join(Agent).filter(Agent.name == agent_name)
    if name:
        query = query.filter(Tool.name == name)
    tools = query.all()
    if not tools:
        raise HTTPException(status_code=404, detail="Tools not found")
    return tools


@router.get("/{tool_id}")
async def get_tool_by_id(tool_id: int, db: db_dependency, tenant_id: api_key_dependency):
    tool = db.query(Tool).filter(Tool.tenant_id == tenant_id, Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.delete("/{tool_id}")
async def delete_tool_by_id(tool_id: int, db: db_dependency, tenant_id: api_key_dependency):
    tool = db.query(Tool).filter(Tool.tenant_id == tenant_id, Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    agents_using_tool = db.query(Agent).join(agent_tools).filter(agent_tools.c.tool_id == tool.id).all()
    if agents_using_tool:
        raise HTTPException(status_code=400, detail="Cannot delete tool, it is used by agent.")
    db.delete(tool)
    db.commit()
    return {"detail": f"Deleted tool {tool_id}"}


@router.put("/{tool_id}")
async def update_tool_by_id(tool_id: int, tool_update: ToolUpdate, db: db_dependency, tenant_id: api_key_dependency):
    tool = db.query(Tool).filter(Tool.tenant_id == tenant_id, Tool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    if tool_update.name:
        tool.name = tool_update.name
    if tool_update.description:
        tool.description = tool_update.description
    db.commit()
    db.refresh(tool)
    return tool


@router.post("")
async def create_tool(tool: ToolBase, db: db_dependency, tenant_id: api_key_dependency):
    db_tool = Tool(
        name=tool.name,
        description=tool.description,
        tenant_id=tenant_id
    )
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool
