from py_compile import main
from fastapi import FastAPI, HTTPException # type: ignore
from enum import Enum
import uvicorn # type: ignore
from .models import CloudAction, StepResult
from .environment import CloudAuditEnv

class TaskID(str, Enum):
    task_1 = "task_1"
    task_2 = "task_2"
    task_3 = "task_3"

# 1. Initialize the web server
app = FastAPI(title="Cloud Sentinel Environment API")

# 2. Spin up an instance of our simulation
env = CloudAuditEnv()

# ---------------------------------------------------------
# THE ENDPOINTS (The "Doors" the agent can knock on)
# ---------------------------------------------------------

@app.post("/reset", response_model=StepResult)
def reset_environment(task_id: TaskID = TaskID.task_1): # <-- Changed parameter type
    try:
        # We use .value to extract the actual string ("task_1") to send to the environment
        return env.reset(task_id=task_id.value) 
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

@app.get("/state", response_model=StepResult)
def get_current_state():
    """
    Mandatory endpoint for OpenEnv spec compliance. 
    Returns the current state without taking a step.
    """
    try:
        # We'll just return the current observation from our environment
        return env.step(CloudAction(action_str="noop()")) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()