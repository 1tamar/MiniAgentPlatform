from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ToolBase(BaseModel):
    name: str
    description: str


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ToolResponse(ToolBase):
    id: int
    tenant_id: str

    model_config = ConfigDict(from_attributes=True)


class AgentBase(BaseModel):
    name: str
    role: str
    description: str
    tool_ids: List[int] = []


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    tool_ids: Optional[List[int]] = None


class AgentResponse(BaseModel):
    id: int
    tenant_id: str
    name: str
    role: str
    description: str
    tools: List[ToolResponse]

    model_config = ConfigDict(from_attributes=True)


class AgentRunRequest(BaseModel):
    task: str
    model: str = "gpt-4o"


class AgentRunResponse(BaseModel):
    execution_id: int
    agent_id: int
    agent_name: str
    prompt: str
    model: str
    response: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionResponse(BaseModel):
    id: int
    agent_id: int
    prompt: str
    model: str
    response: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
