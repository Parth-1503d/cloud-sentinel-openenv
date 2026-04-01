# Cloud-Sentinel-v1 (OpenEnv Hackathon)

## Environment Description & Motivation
Cloud-Sentinel is a multimodal OpenEnv simulation that trains agents to perform Cloud Infrastructure Audits. In the real world, cloud misconfigurations (like exposed S3 buckets) cause billions in damages. This environment simulates a SOC (Security Operations Center) dashboard, requiring the agent to identify vulnerable components using both visual (screenshot) and DOM-like metadata, and securely quarantine them.

## Action & Observation Spaces
* **Action Space:** String-based commands executed via the agent (e.g., `click('<BID>')` or `noop()`).
* **Observation Space:** Multimodal. Includes a generated UI screenshot, current URL, task goal, and nested `browsergym_obs` metadata containing clickable bounding boxes.

## Tasks
1. **Identify Public S3 Bucket (Easy):** Find and click the single exposed bucket.
2. **Quarantine Exposed IAM Role (Medium):** Locate a compromised identity.
3. **Trace Multi-Step Breach (Hard):** Correlate an IP address to a specific compromised resource.

## Usage
Run the FastAPI server locally:
`uvicorn src.envs.cloud_audit.server:app --port 7860`