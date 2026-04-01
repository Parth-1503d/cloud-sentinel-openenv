import re
from typing import List, Optional
from .models import CloudAction, CloudObservation, StepResult

class CloudAuditEnv:
    def __init__(self):
        self.max_steps = 10
        self.current_step = 0
        self.active_task = "task_1"
        self.current_view = "dashboard" # Tracking "sub-menus"
        
        # All possible elements in our "Cloud Console"
        self.all_elements = {
            "12": {"bbox": [10, 10, 50, 50], "clickable": True, "type": "secure_db"},
            "45": {"bbox": [60, 10, 100, 50], "clickable": True, "type": "settings_menu"},
            "82": {"bbox": [10, 60, 50, 100], "clickable": True, "type": "exposed_s3_bucket"},
            "99": {"bbox": [150, 20, 200, 60], "clickable": True, "type": "revoke_iam_key"}, # Hidden in Settings
            "LOG": {"bbox": [0,0,0,0], "clickable": False, "type": "text_log", "content": "Alert: Unauthorized access from IP 192.168.1.50 detected."}
        }

    def _get_visible_elements(self):
        """Logic to show only certain buttons based on the current 'menu'."""
        if self.current_view == "settings":
            return {"99": self.all_elements["99"], "45": {"type": "back_to_dashboard", "clickable": True}}
        return {k: v for k, v in self.all_elements.items() if k != "99"}

    def reset(self, task_id: str = "task_1") -> StepResult:
        self.current_step = 0
        self.active_task = task_id
        self.current_view = "dashboard"
        
        goals = {
            "task_1": "Find and quarantine the exposed S3 bucket (ID: 82).",
            "task_2": "Revoke the compromised IAM Key. (Hint: Check Settings).",
            "task_3": "Trace the log IP 192.168.1.50 and quarantine the matching DB (ID: 12)."
        }
        
        obs = CloudObservation(
            goal=goals.get(task_id, goals["task_1"]),
            screenshot=[[[0,0,0]]], 
            metadata={"browsergym_obs": {"extra_element_properties": self._get_visible_elements()}},
            last_action_error=""
        )
        return StepResult(observation=obs, reward=0.0, done=False)

    def step(self, action: CloudAction) -> StepResult:
        self.current_step += 1
        reward, done, error = 0.0, False, ""
        action_str = action.action_str.strip()
        match = re.search(r"click\('(\w+)'\)", action_str)
        clicked_id = match.group(1) if match else None

        # --- NAVIGATION LOGIC ---
        if clicked_id == "45":
            self.current_view = "settings"
            error = "Switched to Settings View."
        
        # --- TASK GRADING LOGIC ---
        if self.active_task == "task_1":
            if clicked_id == "82":
                reward, done, error = 1.0, True, "Task 1 Complete: Bucket Secured."
        
        elif self.active_task == "task_2":
            if clicked_id == "99" and self.current_view == "settings":
                reward, done, error = 1.0, True, "Task 2 Complete: Key Revoked."
            elif clicked_id == "99":
                error = "Error: Key not visible in current view."

        elif self.active_task == "task_3":
            if clicked_id == "12":
                reward, done, error = 1.0, True, "Task 3 Complete: Resource 12 Quarantined."

        # --- TIMEOUT CHECK ---
        if self.current_step >= self.max_steps:
            done = True

        obs = CloudObservation(
            goal=f"Current Task: {self.active_task}",
            screenshot=[[[0,0,0]]],
            metadata={"browsergym_obs": {"extra_element_properties": self._get_visible_elements()}},
            last_action_error=error
        )
        return StepResult(observation=obs, reward=reward, done=done)