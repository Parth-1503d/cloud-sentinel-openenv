from fastapi import FastAPI, HTTPException
# Changed to absolute imports to prevent ImportError
from src.envs.cloud_audit.models import ResetRequest, StepRequest, EnvironmentResponse
from src.envs.cloud_audit.environment import CloudAuditEnvironment

app = FastAPI(title="Cloud-Sentinel API")

# Global instance of the environment
env = CloudAuditEnvironment()

@app.post("/reset", response_model=EnvironmentResponse)
async def reset(request: ResetRequest):
    """Initializes the environment for a specific task."""
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
    """Executes an action within the current environment."""
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
    """Basic health check for the validator."""
    return {"status": "healthy", "environment": "Cloud-Sentinel"}

def main():
    import uvicorn
    # Starting the app using the full module path string
    uvicorn.run("src.envs.cloud_audit.server:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()
