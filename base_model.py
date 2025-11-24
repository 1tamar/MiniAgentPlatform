# from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ToolBase(BaseModel):
    name: str
    description: str


class ToolUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


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


class AgentRunRequest(BaseModel):
    task: str
    model: str = "gpt-4o"

