from fastapi import FastAPI, HTTPException
from .models import ResetRequest, StepRequest, EnvironmentResponse
from .environment import CloudAuditEnvironment

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

# The validator requires a main function as an entry point
def main():
    import uvicorn
    # 0.0.0.0 is required for Docker/Hugging Face to be accessible
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
