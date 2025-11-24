from datetime import datetime

from sqlalchemy import Integer, Column, String, ForeignKey, Table, Text, DateTime
from sqlalchemy.orm import relationship

from database import Base


agent_tools = Table(
    "agent_tools",
    Base.metadata,
    Column("agent_id", Integer, ForeignKey("agent.id"), primary_key=True),
    Column("tool_id", Integer, ForeignKey("tool.id"), primary_key=True),
)


class Agent(Base):
    __tablename__ = "agent"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    tenant_id = Column(String, index=True, nullable=False)
    tools = relationship("Tool", secondary=agent_tools)


class Tool(Base):
    __tablename__ = "tool"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    tenant_id = Column(String, index=True, nullable=False)


class Execution(Base):
    __tablename__ = "execution"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String, index=True, nullable=False)
    agent_id = Column(Integer, ForeignKey("agent.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    model = Column(String, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

