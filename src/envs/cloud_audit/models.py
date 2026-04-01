from pydantic import BaseModel, Field   # pyright: ignore[reportMissingImports]
from typing import Optional, List, Dict, Any

# ---------------------------------------------------------
# 1. THE ACTION SPACE (What the agent says to the server)
# ---------------------------------------------------------
class CloudAction(BaseModel):
    """
    The exact command the agent wants to execute.
    In your inference script, this matches the parsed strings like "click('82')".
    """
    action_str: str = Field(
        ..., 
        description="A valid action string like click('<ID>') or noop()."
    )

# ---------------------------------------------------------
# 2. THE OBSERVATION SPACE (What the server sends to the agent)
# ---------------------------------------------------------
class CloudObservation(BaseModel):
    """
    The 'eyes' of the agent. This matches exactly what your 
    inference.py script expects to receive after every step.
    """
    goal: str = Field(
        ..., 
        description="The current objective, e.g., 'Find the exposed S3 bucket.'"
    )
    url: str = Field(
        default="https://console.cloud-sentinel.ai/dashboard",
        description="The virtual URL the agent is currently 'viewing'."
    )
    # We use a nested list of integers because JSON cannot send raw NumPy arrays.
    # Your inference script will convert this back using np.array()
    screenshot: Optional[List[List[List[int]]]] = Field(
        default=None,
        description="A 3D array representing the RGB image of the dashboard."
    )
    last_action_error: str = Field(
        default="",
        description="Error message if the last command failed. Empty if successful."
    )
    # This metadata dictionary is the secret sauce for your inference script!
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Holds the 'browsergym_obs' data for clickable elements."
    )

# ---------------------------------------------------------
# 3. THE STEP RESULT (The complete package returned every turn)
# ---------------------------------------------------------
class StepResult(BaseModel):
    """
    Every time env.step() is called, it returns this exact structure.
    """
    observation: CloudObservation
    reward: float = Field(default=0.0, description="Score from 0.0 to 1.0")
    done: bool = Field(default=False, description="True if the task is finished or failed.")
    info: Dict[str, Any] = Field(default_factory=dict, description="Extra debugging info.")