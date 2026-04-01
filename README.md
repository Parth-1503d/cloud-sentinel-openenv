
-----

````markdown
<div align="center">

# 🛡️ CLOUD-SENTINEL 
**Autonomous Cloud Security Posture Management (CSPM) Environment**

[![System Status: Online](https://img.shields.io/badge/System_Status-Online-brightgreen?style=for-the-badge)](#)
[![Framework: OpenEnv](https://img.shields.io/badge/Framework-OpenEnv-blue?style=for-the-badge)](#)
[![Backend: FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge)](https://fastapi.tiangolo.com/)
[![Deployment: Hugging Face](https://img.shields.io/badge/Deployed_On-Hugging_Face-ffcc66?style=for-the-badge)](https://parth-72-cloud-sentinel.hf.space)

*An interactive, simulated cloud infrastructure designed to evaluate and train Agentic AI models in real-time threat detection and remediation.*

</div>

---

## ⚡ System Overview

**Cloud-Sentinel** transcends static benchmarks. It provides a live, dynamic console environment where AI agents are dropped into an active cloud infrastructure and tasked with securing it. 

Instead of answering multiple-choice questions, agents must navigate the dashboard, interpret system telemetry, cross-reference metadata, and execute precise, coordinate-based actions to neutralize vulnerabilities before they are exploited.

> **Mission Directive:** Train autonomous agents to act as continuous security sentinels for modern cloud environments.

---

## 🏗️ Architecture & Tech Stack

The system is built for hyper-fast execution and strict data compliance, ensuring seamless interaction between the AI models and the simulated environment.

* **Core Engine:** `OpenEnv` framework for standardized agent-environment interaction.
* **Server Infrastructure:** `FastAPI` + `Uvicorn` for high-performance, asynchronous routing.
* **Data Contracts:** Strict `Pydantic` schemas for foolproof state management and observation serialization.
* **Dependency Management:** `uv` for lightning-fast, deterministically locked builds.
* **Deployment:** Fully containerized via `Docker` and hosted on `Hugging Face Spaces`.

---

## 🎯 Threat Scenarios (Evaluation Matrix)

The environment challenges agents across three escalating tiers of security breaches:

### Level 1: Perimeter Defense
* **ID:** `task_1`
* **Objective:** Identify and quarantine an explicitly exposed S3 storage bucket.
* **Agent Skills Required:** Spatial UI navigation, entity recognition, and direct remediation.

### Level 2: Credential Revocation
* **ID:** `task_2`
* **Objective:** Navigate complex IAM routing to revoke a compromised access key.
* **Agent Skills Required:** Multi-stage planning, context switching, and state memory.

### Level 3: Active Breach Tracing
* **ID:** `task_3`
* **Objective:** Trace a malicious actor (IP: 192.168.1.50) through raw system logs, identify the compromised database target, and execute a lockdown.
* **Agent Skills Required:** Unstructured data analysis, cross-referencing, and deductive logic.

---

## 🚀 Deployment & Telemetry

### Local Sandbox Initialization
To spin up the simulated environment on your local machine for manual testing or agent integration:

```bash
# Clone the repository
git clone https://github.com/Parth-1503d/cloud-sentinel-openenv.git
cd Cloud-Sentinel

# Install ultra-fast dependencies
pip install uv
uv sync

# Ignite the server
uvicorn src.envs.cloud_audit.server:app --port 7860
````

*Access the live telemetry and Swagger UI at: `http://127.0.0.1:7860/docs`*

### Autonomous Agent Evaluation

To run a full diagnostic evaluation using an LLM (requires an active OpenAI/HF API key):

```bash
export OPENAI_API_KEY="your-secure-api-key"
python inference.py
```

*The script will output `[START]`, `[STEP]`, and `[END]` telemetry logs as the agent navigates the console.*

-----

## 🌍 Global Deployment

This architecture is rigorously validated and currently deployed as a live Docker container on **Hugging Face Spaces**. It adheres strictly to OpenEnv multi-mode deployment specifications.