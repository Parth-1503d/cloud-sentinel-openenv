from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
# Keep only the environment import
from src.envs.cloud_audit.environment import CloudAuditEnvironment

# --- 1. Models moved inside to prevent ImportErrors ---
class ResetRequest(BaseModel):
    task_id: str

class StepRequest(BaseModel):
    action_str: str

class EnvironmentResponse(BaseModel):
    observation: str
    reward: float
    done: bool
    info: Dict[str, Any]

# --- 2. Server Logic ---
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
    # Using the local app object directly for maximum reliability
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
