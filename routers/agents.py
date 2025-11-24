from datetime import datetime
from typing import Optional

from fastapi import HTTPException, APIRouter
from sqlalchemy.orm import joinedload

from base_model import AgentBase, AgentUpdate, AgentRunRequest
from models import Agent, Tool, Execution
from utils import generate_prompt, mock_llm_call, check_tenant_limit, db_dependency, api_key_dependency, \
    SUPPORTED_MODELS

router = APIRouter()


@router.get("")
async def get_agents(db: db_dependency,
                     tenant_id: api_key_dependency,
                     tool_name: Optional[str] = None,
                     name: Optional[str] = None):
    result = db.query(Agent) \
        .options(joinedload(Agent.tools)) \
        .filter(Agent.tenant_id == tenant_id)
    if tool_name:
        result = result.join(Agent.tools).filter(Tool.name == tool_name)
    if name:
        result = result.filter(Agent.name == name)
    agents = result.all()
    if not agents:
        return HTTPException(status_code=404, detail="Agents not found")
    return agents


@router.get("/{agent_id}")
async def get_agent_by_id(agent_id: int, db: db_dependency, tenant_id: api_key_dependency):
    result = db.query(Agent) \
        .options(joinedload(Agent.tools)) \
        .filter(Agent.id == agent_id, Agent.tenant_id == tenant_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Agent not found.")
    return result


@router.delete("/{agent_id}")
async def delete_agent_by_id(agent_id: int, db: db_dependency, tenant_id: api_key_dependency):
    agent = db.query(Agent).filter(Agent.tenant_id == tenant_id, Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    db.delete(agent)
    db.commit()
    return {"detail": f"Deleted agent: {agent_id}"}


@router.put("/{agent_id}")
async def update_agent_by_id(agent_id: int,
                             agent_update: AgentUpdate,
                             db: db_dependency,
                             tenant_id: api_key_dependency):
    agent = db.query(Agent).filter(Agent.tenant_id == tenant_id, Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent_update.name:
        agent.name = agent_update.name
    if agent_update.role:
        agent.role = agent_update.role
    if agent_update.description:
        agent.description = agent_update.description
    if agent_update.tool_ids:
        tools = db.query(Tool).filter(Tool.id.in_(agent_update.tool_ids), Tool.tenant_id == tenant_id).all()
        if len(tools) != len(agent_update.tool_ids):
            raise HTTPException(status_code=400, detail="One or more tools not found")
        agent.tools = tools
    db.commit()
    db.refresh(agent)
    return agent


@router.post("")
async def create_agent(agent: AgentBase, db: db_dependency, tenant_id: api_key_dependency):
    tools = db.query(Tool).filter(Tool.id.in_(agent.tool_ids), Tool.tenant_id == tenant_id).all()
    if len(tools) != len(agent.tool_ids):
        raise HTTPException(status_code=400, detail="One or more tools not found")

    db_agent = Agent(
        tenant_id=tenant_id,
        name=agent.name,
        description=agent.description,
        role=agent.role,
        tools=tools
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


@router.post("{agent_id}/run")
async def create_agent(agent_id: int, request: AgentRunRequest, db: db_dependency, tenant_id: api_key_dependency):
    if not check_tenant_limit(tenant_id):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    agent = db.query(Agent) \
        .options(joinedload(Agent.tools)) \
        .filter(Agent.id == agent_id, Agent.tenant_id == tenant_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    prompt = generate_prompt(agent, request.task)
    if request.model not in SUPPORTED_MODELS:
        raise HTTPException(status_code=400, detail="Request model not supported")
    mock_response = mock_llm_call(prompt, request.model)
    db_execution = Execution(
        tenant_id=tenant_id,
        agent_id=agent_id,
        prompt=prompt,
        model=request.model,
        response=mock_response,
        timestamp=datetime.utcnow()
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution
