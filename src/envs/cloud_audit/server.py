from fastapi import FastAPI, HTTPException # type: ignore
from .models import CloudAction, StepResult
from .environment import CloudAuditEnv

# 1. Initialize the web server
app = FastAPI(title="Cloud Sentinel Environment API")

# 2. Spin up an instance of our simulation
env = CloudAuditEnv()

# ---------------------------------------------------------
# THE ENDPOINTS (The "Doors" the agent can knock on)
# ---------------------------------------------------------

@app.post("/reset", response_model=StepResult)
def reset_environment():
    """
    The agent calls this to start a new puzzle.
    It returns the fresh observation and sets the score to 0.
    """
    try:
        return env.reset()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/step", response_model=StepResult)
def step_environment(action: CloudAction):
    """
    The agent sends its Action here (e.g., {"action_str": "click('82')"}).
    We pass it to the Brain, and return the new state and reward.
    """
    try:
        return env.step(action)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def health_check():
    """
    A simple check to see if the server is awake. 
    Hugging Face uses this to know your Space deployed successfully.
    """
    return {"status": "Cloud Sentinel Environment is online and ready."}