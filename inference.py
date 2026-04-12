import os
from openai import OpenAI # type: ignore
import re
import base64
import subprocess
import sys
import textwrap
import requests # pyright: ignore[reportMissingModuleSource]
import numpy as np
from io import BytesIO
from PIL import Image # type: ignore
from typing import List, Optional, Dict
try:
    from openai import OpenAI # type: ignore
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
    from openai import OpenAI # type: ignore

# ==========================================
# 1. CONFIGURATION & SECRETS
# ==========================================
# For local testing, we point to our local FastAPI server.
# When deploying, you would change this to your Hugging Face Space URL.
ENV_URL = "http://127.0.0.1:7860"

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

MAX_STEPS = 8
TEMPERATURE = 0.2
FALLBACK_ACTION = "noop()"

ACTION_PATTERN = re.compile(r"click\('\d+'\)|noop\(\)")

# ==========================================
# 2. THE ENVIRONMENT CLIENT (Talks to our Server)
# ==========================================
class CloudEnvClient:
    """A simple client to talk to our FastAPI OpenEnv server."""
    def __init__(self, base_url: str):
        self.base_url = base_url

    def reset(self):
        response = requests.post(f"{self.base_url}/reset")
        response.raise_for_status()
        return response.json()

    def step(self, action_str: str):
        payload = {"action_str": action_str}
        response = requests.post(f"{self.base_url}/step", json=payload)
        response.raise_for_status()
        return response.json()

# ==========================================
# 3. HELPER FUNCTIONS (Adapted from your sample)
# ==========================================
SYSTEM_PROMPT = textwrap.dedent("""
    You are an automated Cloud Security SOC Analyst.
    You control a security dashboard to quarantine exposed infrastructure.
    
    Reply with exactly ONE action string from the following:
    - noop()
    - click('<ID>')
    
    Use single quotes around the ID.
    Only click IDs that correspond to PUBLIC or EXPOSED resources.
    Do not include explanations or additional text.
""").strip()

def extract_screenshot_uri(observation: dict) -> Optional[str]:
    """Converts the JSON screenshot array back into a base64 image."""
    screen_data = observation.get("screenshot")
    if not screen_data:
        return None
    
    screen_array = np.array(screen_data, dtype=np.uint8)
    image = Image.fromarray(screen_array)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    data_uri = base64.b64encode(buffer.read()).decode("utf-8")
    return f"data:image/png;base64,{data_uri}"

def extract_clickable_elements(observation: dict) -> List[Dict[str, str]]:
    """Extracts the element IDs from our metadata dictionary."""
    metadata = observation.get("metadata", {})
    extra_props = metadata.get("browsergym_obs", {}).get("extra_element_properties", {})
    
    clickables = []
    for bid, props in extra_props.items():
        if not props.get("clickable"):
            continue
        # Get the label so the AI knows what the button does!
        label = props.get("type", "unknown")
        clickables.append({"bid": str(bid), "label": label})
        
    clickables.sort(key=lambda item: item["bid"])
    return clickables

def build_user_prompt(step: int, observation: dict, history: List[str]) -> str:
    goal = observation.get("goal", "Unknown")
    error_note = observation.get("last_action_error", "")
    
    clickables = extract_clickable_elements(observation)
    if clickables:
        actions_hint = "\n".join(f"  - ID '{item['bid']}': {item['label']}" for item in clickables)
    else:
        actions_hint = "  (none detected)"
        
    history_str = "\n".join(history[-4:]) if history else "None"

    prompt = textwrap.dedent(f"""
        Step: {step}
        Goal: {goal}
        
        Previous steps:
        {history_str}
        
        Last action error: {error_note}
        
        Available Dashboard Elements:
        {actions_hint}
        
        Reply with exactly one action string (e.g., click('82')).
    """).strip()
    return prompt

def parse_model_action(response_text: str) -> str:
    if not response_text:
        return FALLBACK_ACTION
        
    match = ACTION_PATTERN.search(response_text)
    if match:
         return match.group(0).strip()
    return FALLBACK_ACTION

# ==========================================
# 4. THE MAIN LOOP
# ==========================================
def main():
    # MANDATORY LOG: [START]
    print(f"[START] Task: task_1 | Model: {MODEL_NAME}")
    
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = CloudEnvClient(ENV_URL)
    history = []
    
    try:
        result = env.reset(task_id="task_1")
        observation = result["observation"]
        
        for step_idx in range(1, MAX_STEPS + 1):
            if result.get("done"):
                break
                
            user_prompt = build_user_prompt(step_idx, observation, history)
            user_content = [{"type": "text", "text": user_prompt}]
            
            # (Image logic remains the same...)
            screenshot_uri = extract_screenshot_uri(observation)
            if screenshot_uri:
                user_content.append({"type": "image_url", "image_url": {"url": screenshot_uri}})
                
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_content}]
            )
            response_text = completion.choices[0].message.content or ""
            action_str = parse_model_action(response_text)
            
            result = env.step(action_str)
            observation = result["observation"]
            reward = result.get("reward", 0.0)

            # MANDATORY LOG: [STEP]
            # Format: [STEP] <step_num> | Action: <action> | Reward: <reward>
            print(f"[STEP] {step_idx} | Action: {action_str} | Reward: {reward}")
            history.append(f"Step {step_idx}: {action_str} -> {reward}")

        # MANDATORY LOG: [END]
        # Format: [END] | Final Reward: <total_reward>
        print(f"[END] | Final Reward: {result.get('reward', 0.0)}")
            
    except Exception as e:
        print(f"Error during inference: {e}")

if __name__ == "__main__":
    main()