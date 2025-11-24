from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import models
from database import engine
from routers import tools, agents, executions

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Agent Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools.router, prefix="/tools", tags=["tools"])
app.include_router(agents.router, prefix="/agents", tags=["agents"])
app.include_router(executions.router, prefix="/executions", tags=["executions"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
