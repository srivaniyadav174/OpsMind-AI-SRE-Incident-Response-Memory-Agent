# OpsMind — AI SRE Incident Response & Memory Agent

> An AI-powered SRE incident response agent that combines current incident evidence with persistent organizational memory to diagnose incidents, recommend safe remediation, and continuously learn from past resolutions.

## Overview

**OpsMind** is an AI Site Reliability Engineering (SRE) agent designed to help engineers investigate and respond to production-style incidents faster.

Traditional incident response often requires engineers to manually search through logs, metrics, runbooks, and previous incident reports. OpsMind brings these sources together into a single investigation workflow.

The key capability is **persistent organizational memory using Hindsight**.

Instead of treating every incident as completely new, OpsMind can:

1. Inspect the current incident.
2. Analyze logs and telemetry.
3. Recall similar historical incidents from Hindsight.
4. Use previous remediation outcomes as operational context.
5. Generate an evidence-based diagnosis.
6. Recommend a structured remediation runbook.
7. Require human approval before remediation.
8. Simulate the remediation safely.
9. Retain the incident outcome as organizational memory.

This creates a continuous incident-response learning loop.

---

## Why OpsMind?

When a similar failure happens again, engineers should not have to rediscover the solution from scratch.

```text
Previous Incident
       |
       v
Database connection pool exhaustion
       |
       v
Increase connection pool capacity
       |
       v
Restart payment-api
       |
       v
Incident resolved
       |
       v
Hindsight RETAIN
       |
       v
Future Incident
       |
       v
Recall previous operational experience
```

OpsMind turns individual incident resolutions into reusable **organizational knowledge**.

---

## Key Features

### 1. AI Incident Investigation

OpsMind analyzes:

* Application logs
* Service metrics
* Incident symptoms
* Historical incident memory

The AI produces a structured diagnosis containing:

* Likely root cause
* Reasoning
* Evidence
* Historical context
* Recommended actions
* Confidence
* Remediation runbook

### 2. Hindsight Organizational Memory

Hindsight provides persistent memory for incident experiences.

OpsMind recalls relevant historical incidents during investigation and retains newly resolved incidents after remediation.

Stored operational knowledge includes:

* Incident characteristics
* Root cause
* Remediation actions
* Resolution outcome
* Historical context

This allows future investigations to benefit from previous operational experience.

### 3. Evidence-Based Diagnosis

OpsMind combines current telemetry with historical memory instead of relying only on an LLM response.

Example:

```text
Current Evidence
    |
    +-- Latency: 6.1 seconds
    +-- HTTP 500 error rate: 26%
    +-- DB connection utilization: 97%
    +-- Connection acquisition delays
    +-- Requests waiting for DB connections
    |
    v
Historical Memory
    |
    +-- INC-007
    +-- INC-006
    +-- INC-001
    |
    v
AI Diagnosis
    |
    +-- Database connection pool exhaustion
```

### 4. Automated Runbook Generation

Once the likely cause is identified, OpsMind attaches an appropriate runbook.

Example:

1. Inspect database connection pool configuration.
2. Check active connections and long-running queries.
3. Simulate increasing connection pool capacity.
4. Simulate restarting the affected service.
5. Monitor connection utilization and API error rate.

### 5. Human-in-the-Loop Safety

OpsMind does **not** automatically modify production systems.

```text
AI Investigation
       |
       v
Diagnosis
       |
       v
Recommended Runbook
       |
       v
Human Approval
       |
       v
Simulated Remediation
```

All remediation actions in the prototype are simulated.

### 6. Continuous Learning

After remediation, OpsMind retains the incident experience in Hindsight.

```text
Incident
   |
   v
Investigation
   |
   v
Diagnosis
   |
   v
Human Approval
   |
   v
Remediation
   |
   v
Outcome
   |
   v
Hindsight RETAIN
   |
   v
Future Incident
```

---

## System Architecture

```text
                    +----------------------+
                    |      SRE / User      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |  OpsMind Dashboard   |
                    |      Frontend        |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |     FastAPI API      |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |   OpsMind SRE Agent  |
                    +----------+-----------+
                               |
                +--------------+--------------+
                |                             |
                v                             v
       +----------------+             +------------------+
       | Current        |             | Hindsight        |
       | Evidence       |             | Memory           |
       | Logs + Metrics |             | Historical Data  |
       +--------+-------+             +--------+---------+
                |                              |
                +--------------+---------------+
                               |
                               v
                    +----------------------+
                    |   LLM Reasoning      |
                    |      via Groq         |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Diagnosis + Evidence |
                    | + Historical Context |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |       Runbook        |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Human Approval Gate  |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Simulated Remediation|
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    | Hindsight RETAIN     |
                    | Organizational       |
                    | Learning             |
                    +----------------------+
```

---

## Technology Stack

| Layer           | Technology                 |
| --------------- | -------------------------- |
| Frontend        | HTML, CSS, JavaScript      |
| Backend         | Python, FastAPI            |
| AI / LLM        | Groq API                   |
| Memory          | Hindsight                  |
| Data            | JSON                       |
| API Server      | Uvicorn                    |
| Environment     | Python virtual environment |
| Version Control | Git / GitHub               |

---

## Project Structure

```text
opsmind-ai-sre/
|
+-- backend/
|   +-- agent/
|   |   +-- sre_agent.py
|   |
|   +-- api/
|   |   +-- main.py
|   |
|   +-- incident_tool.py
|   +-- evidence_tool.py
|   +-- memory_tool.py
|   +-- learning_tool.py
|   +-- runbook_tool.py
|   +-- opsmind_engine.py
|
+-- data/
|   +-- incidents/
|   |   +-- incidents.json
|   |
|   +-- logs/
|   |   +-- logs.json
|   |
|   +-- metrics/
|   |   +-- metrics.json
|   |
|   +-- runbooks/
|       +-- runbooks.json
|
+-- frontend/
|   +-- index.html
|   +-- app.js
|   +-- style.css
|
+-- .env.example
+-- .gitignore
+-- README.md
+-- requirements.txt
```

---

## API Endpoints

### Health Check

```http
GET /health
```

Returns the API health status.

### List Incidents

```http
GET /incidents
```

Returns available incidents.

### Get Incident

```http
GET /incidents/{incident_id}
```

Returns information about a selected incident.

### Analyze Incident

```http
POST /incidents/{incident_id}/analyze
```

Runs the OpsMind investigation workflow.

The response contains:

* Diagnosis
* Evidence
* Historical memory
* Recommended actions
* Runbook
* Confidence
* Human approval state

### Resolve Incident

```http
POST /incidents/{incident_id}/resolve
```

Runs the simulated remediation workflow after human approval and retains the resulting incident experience in Hindsight.

---

## Example: INC-008

INC-008 represents a critical `payment-api` incident.

### Current Telemetry

```text
Latency:                    6.1 seconds
HTTP 500 error rate:       26%
DB connection utilization: 97%
```

### Current Log Signals

```text
Database connection acquisition taking longer than 2s
Payment API requests waiting for database connection
Payment API returned HTTP 500
Database connection utilization: 97%
Payment API response latency exceeded 5 seconds
```

### Hindsight Memory

OpsMind recalls historical incidents including:

```text
INC-007
INC-006
INC-001
```

These incidents provide historical operational context related to database connection failures.

### AI Diagnosis

```text
Database connection pool exhaustion
causing connection contention and timeouts
```

### Learned Remediation

```text
Increase database connection pool capacity
and restart the affected service.
```

### Safety

The remediation is simulated and requires human approval.

### Learning

After simulated resolution:

```text
MEMORY RETAINED
```

The incident experience becomes available to future investigations.

---

## Safety Design

OpsMind is intentionally designed with a safe remediation model for the prototype.

### No Uncontrolled Production Actions

All remediation actions are simulated.

### Human Approval

The AI cannot independently approve its own remediation.

### Evidence-Based Reasoning

The agent prioritizes current telemetry and uses historical memory as supporting context.

### Memory Separation

The current incident's stored root cause and resolution are not directly supplied to the investigation reasoning process.

This allows the system to demonstrate diagnosis from evidence and historical experience rather than simply reading the answer.

---

## Running Locally

### 1. Clone the Repository

```bash
git clone https://github.com/srivaniyadav174/OpsMind-AI-SRE-Incident-Response-Memory-Agent.git
cd OpsMind-AI-SRE-Incident-Response-Memory-Agent
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

### 3. Activate the Environment on Windows

```cmd
.venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file based on `.env.example`.

```env
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BANK_ID=opsmind-incidents
GROQ_API_KEY=your_groq_api_key
```

**Never commit `.env` or API keys to GitHub.**

### 6. Start the API

```bash
uvicorn backend.api.main:app --reload
```

### 7. Open the Dashboard

```text
http://127.0.0.1:8000/
```

---

## Demo Flow

For a demonstration:

```text
1. Select an incident
       |
       v
2. Inspect telemetry
       |
       v
3. Click "Analyze Incident"
       |
       v
4. AI investigates current evidence
       |
       v
5. Hindsight recalls historical incidents
       |
       v
6. Diagnosis is generated
       |
       v
7. Historical remediation context is shown
       |
       v
8. Runbook is generated
       |
       v
9. Human approves remediation
       |
       v
10. Remediation is simulated
       |
       v
11. Outcome is retained in Hindsight
```

---

## Project Goal

OpsMind demonstrates how AI agents can move beyond one-time reasoning toward **persistent operational learning**.

The central idea is:

> **Investigate → Remember → Diagnose → Recommend → Approve → Resolve → Learn**

By combining AI reasoning with persistent organizational memory, OpsMind provides a prototype for an SRE assistant that can accumulate incident-response knowledge over time.

---



**Focus Areas:**

* AI Agents
* Site Reliability Engineering
* Incident Response
* Persistent Agent Memory
* Observability
* Human-in-the-Loop Automation
* Operational Knowledge Management

---

## Current Prototype Scope

OpsMind is a prototype using simulated incident telemetry and simulated remediation actions.

The prototype demonstrates the complete memory-driven incident-response workflow without making changes to real production infrastructure.
