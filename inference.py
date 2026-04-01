import os
import re
import base64
import textwrap
import requests # pyright: ignore[reportMissingModuleSource]
import numpy as np
from io import BytesIO
from PIL import Image # type: ignore
from typing import List, Optional, Dict
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
    print("Initializing Cloud-Sentinel Agent...")
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    env = CloudEnvClient(ENV_URL)
    
    history: List[str] = []
    
    try:
        # 1. Start the simulation
        result = env.reset()
        observation = result["observation"]
        print(f"Episode Goal: {observation['goal']}")
        
        for step in range(1, MAX_STEPS + 1):
            if result.get("done"):
                print("Environment signaled DONE. Stopping early.")
                break
                
            # 2. Format the data for the LLM
            user_prompt = build_user_prompt(step, observation, history)
            user_content = [{"type": "text", "text": user_prompt}]
            
            screenshot_uri = extract_screenshot_uri(observation)
            if screenshot_uri:
                user_content.append({
                    "type": "image_url",
                    "image_url": {"url": screenshot_uri}
                })
                
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ]
            
            # 3. Ask the LLM what to do
            try:
                completion = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    temperature=TEMPERATURE
                )
                response_text = completion.choices[0].message.content or ""
            except Exception as exc:
                print(f"Model request failed: {exc}")
                response_text = FALLBACK_ACTION
                
            # 4. Clean up the response and send to Server
            action_str = parse_model_action(response_text)
            print(f"\nStep {step}: Model suggested -> {action_str}")
            
            result = env.step(action_str)
            observation = result["observation"]
            reward = result.get("reward", 0.0)
            
            # 5. Log the results
            error_flag = " [ERROR]" if observation.get("last_action_error") else ""
            history_line = f"Step {step}: {action_str} -> reward {reward:+.2f}{error_flag}"
            history.append(history_line)
            
            print(f"  Reward: {reward:+.2f} | Done: {result['done']}")
            if observation.get("last_action_error"):
                print(f"  Server Error Message: {observation['last_action_error']}")
                
        if result.get("done"):
            print("\n Episode Complete! Mission Accomplished.")
        else:
            print(f"\n Reached max steps ({MAX_STEPS}). Mission Failed.")
            
    except requests.exceptions.ConnectionError:
        print("\n[CRITICAL ERROR] Could not connect to the environment.")
        print("Did you forget to start the FastAPI server in another terminal?")

if __name__ == "__main__":
    main()