import sys
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Force the current directory into the path so Python can find 'environment'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now import directly from the local file
try:
    from environment import CloudAuditEnvironment
except ImportError:
    # Fallback for different build environments
    from src.envs.cloud_audit.environment import CloudAuditEnvironment

# --- Models ---
class ResetRequest(BaseModel):
    task_id: str

class StepRequest(BaseModel):
    action_str: str

class EnvironmentResponse(BaseModel):
    observation: str
    reward: float
    done: bool
    info: Dict[str, Any]

# --- Server Logic ---
app = FastAPI(title="Cloud-Sentinel API")
env = CloudAuditEnvironment()

@app.post("/reset", response_model=EnvironmentResponse)
async def reset(request: ResetRequest):
    try:
        observation = env.reset(task_id=request.task_id)
        return EnvironmentResponse(
            observation=observation,
            reward=0.0,
            done=False,
            info={"status": "initialized", "task_id": request.task_id}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step", response_model=EnvironmentResponse)
async def step(request: StepRequest):
    try:
        observation, reward, done, info = env.step(request.action_str)
        return EnvironmentResponse(
            observation=observation,
            reward=reward,
            done=done,
            info=info
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "environment": "Cloud-Sentinel"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
