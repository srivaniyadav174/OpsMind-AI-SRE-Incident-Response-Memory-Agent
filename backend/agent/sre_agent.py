import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"

sys.path.insert(0, str(BACKEND_DIR))


# ============================================================
# IMPORT BACKEND TOOLS
# ============================================================

from evidence_tool import get_evidence
from incident_tool import get_incident
from memory_tool import recall_similar_incidents
from runbook_tool import get_runbook


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(
    PROJECT_ROOT / ".env"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing from .env"
    )


# ============================================================
# GROQ CLIENT
# ============================================================

groq_client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# AI SRE DIAGNOSIS
# ============================================================

def diagnose_incident(incident_id):

    # --------------------------------------------------------
    # 1. Get incident information
    # --------------------------------------------------------

    incident = get_incident(
        incident_id
    )

    if incident is None:
        raise ValueError(
            f"Incident {incident_id} not found."
        )

    current_incident_id = (
        incident["incident_id"].upper()
    )

    # --------------------------------------------------------
    # 2. Get current evidence
    # --------------------------------------------------------

    evidence = get_evidence(
        current_incident_id
    )

    logs = evidence["logs"]

    metrics = evidence["metrics"]

    if not logs and not metrics:
        raise ValueError(
            f"No current evidence found for "
            f"{current_incident_id}."
        )

    # --------------------------------------------------------
    # 3. Search Hindsight memory
    # --------------------------------------------------------

    memory_query = f"""
Find previous SRE incidents similar to this CURRENT incident.

CURRENT INCIDENT ID:
{current_incident_id}

Service:
{incident["service"]}

Severity:
{incident["severity"]}

Symptoms:
{json.dumps(incident["symptoms"], indent=2)}

Current metrics:
{json.dumps(metrics, indent=2)}

Look for historical incidents involving similar:

- symptoms
- service behavior
- performance problems
- errors
- resource saturation
- remediation experience
- previous outcomes

IMPORTANT:

The current incident is {current_incident_id}.

Do NOT treat {current_incident_id} as a historical incident.

Prefer historical incidents with a DIFFERENT incident ID.

Historical incidents are supporting context only.
Current logs and metrics are the primary evidence.
"""

    memories = recall_similar_incidents(
        query=memory_query,
        current_incident_id=current_incident_id,
    )

    if memories:

        historical_memory = "\n\n".join(
            memories
        )

    else:

        historical_memory = (
            "No relevant historical incidents found."
        )

    # --------------------------------------------------------
    # 4. Prepare SAFE investigation data
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # Do NOT send root_cause, resolution, or outcome
    # from the current incident to the AI.
    #
    # Otherwise the AI would already know the answer.
    # --------------------------------------------------------

    investigation_data = {
        "incident_id":
            current_incident_id,

        "service":
            incident["service"],

        "severity":
            incident["severity"],

        "symptoms":
            incident["symptoms"],
    }

    # --------------------------------------------------------
    # 5. AI SYSTEM PROMPT
    # --------------------------------------------------------

    system_prompt = f"""
You are OpsMind, an AI Site Reliability Engineering agent.

Your job is to investigate the CURRENT incident using:

1. Current incident information
2. Current logs
3. Current metrics
4. Historical SRE memories from Hindsight

============================================================
IMPORTANT RULES
============================================================

- Diagnose the CURRENT incident from current evidence.
- Current logs and metrics are the PRIMARY evidence.
- Historical incidents are supporting context only.
- Do not assume a historical incident has the same root cause.
- Do not blindly copy historical remediation.
- Historical evidence can support a hypothesis but cannot
  prove the current root cause by itself.
- Every claim about the current incident must be supported
  by current logs or metrics.
- Clearly distinguish current evidence from historical
  evidence.
- Do not invent logs, metrics, incidents, or observations.
- Do not invent an incident ID.
- Recommend safe investigative or simulated remediation
  actions.
- Do not claim that you actually changed a production system.

============================================================
CURRENT INCIDENT
============================================================

The current incident ID is:

{current_incident_id}

============================================================
CRITICAL MEMORY RULE
============================================================

The current incident is:

{current_incident_id}

NEVER describe {current_incident_id} as a historical incident.

A historical incident MUST have a DIFFERENT incident ID.

For example:

Current incident:
{current_incident_id}

Valid historical incident:
INC-001

Invalid historical incident:
{current_incident_id}

If Hindsight memory does not clearly identify an incident ID,
treat it only as general historical context.

DO NOT invent an incident ID for any memory.

============================================================
HISTORICAL MEMORY RULE
============================================================

Historical memories can contain:

- previous root causes
- previous resolutions
- previous outcomes
- lessons learned

Use these memories only as supporting context.

Do NOT claim that a historical resolution definitely fixes
the current incident.

Use cautious language when describing historical evidence.

Prefer phrases such as:

- "supports the hypothesis"
- "is consistent with"
- "suggests"
- "provides useful historical context"

Avoid phrases such as:

- "proves"
- "confirms"
- "guarantees"

unless the current evidence independently establishes
the claim.

============================================================
RECOMMENDED ACTION RULES
============================================================

Recommended actions must be:

- relevant to the diagnosed problem
- safe
- specific
- useful to an SRE
- suitable for simulation in this demo

Do not claim that production changes were actually performed.

Never include empty strings in recommended_actions.

============================================================
CONFIDENCE RULE
============================================================

Always return exactly one of:

High
Medium
Low

Use:

High:
Current logs and metrics strongly support the diagnosis.

Medium:
Evidence supports the diagnosis but additional investigation
would be useful.

Low:
Evidence is incomplete or multiple root causes remain possible.

============================================================
OUTPUT FORMAT
============================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
  "likely_root_cause": "string",

  "reasoning": "string",

  "evidence": [
    "current evidence item",
    "current evidence item"
  ],

  "historical_context": "string",

  "recommended_actions": [
    "action",
    "action"
  ],

  "confidence": "High | Medium | Low"
}}

IMPORTANT:

- Do not include Markdown.
- Do not include ```json.
- Do not include explanations outside the JSON.
- Do not include empty recommended actions.
- Always include confidence.
"""


    # --------------------------------------------------------
    # 6. USER PROMPT
    # --------------------------------------------------------

    user_prompt = f"""
============================================================
CURRENT INCIDENT
============================================================

{json.dumps(
    investigation_data,
    indent=2
)}

============================================================
CURRENT LOGS
============================================================

{json.dumps(
    logs,
    indent=2
)}

============================================================
CURRENT METRICS
============================================================

{json.dumps(
    metrics,
    indent=2
)}

============================================================
HISTORICAL HINDSIGHT MEMORY
============================================================

{historical_memory}

============================================================
TASK
============================================================

Analyze the CURRENT incident.

Use current logs and metrics as the primary evidence.

Use Hindsight only as historical context.

Do not identify the current incident
({current_incident_id}) as historical.

Do not claim historical evidence proves the current diagnosis.

Return ONLY the required JSON object.
"""


    # --------------------------------------------------------
    # 7. CALL GROQ
    # --------------------------------------------------------

    try:

        response = groq_client.chat.completions.create(

            model="openai/gpt-oss-20b",

            temperature=0.2,

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },

                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

    except Exception as error:

        raise RuntimeError(
            f"Groq diagnosis request failed: {error}"
        )


    # --------------------------------------------------------
    # 8. GET AI RESPONSE
    # --------------------------------------------------------

    response_text = (
        response
        .choices[0]
        .message
        .content
    )

    if not response_text:

        raise ValueError(
            "Groq returned an empty diagnosis."
        )


    # --------------------------------------------------------
    # 9. PARSE AI RESPONSE
    # --------------------------------------------------------

    try:

        diagnosis = json.loads(
            response_text
        )

    except json.JSONDecodeError as error:

        raise ValueError(
            "Groq returned invalid JSON.\n"
            f"Raw response:\n{response_text}\n"
            f"JSON error: {error}"
        )


    # --------------------------------------------------------
    # 10. NORMALIZE AI OUTPUT
    # --------------------------------------------------------

    # --------------------------------------------------------
    # 10A. Normalize likely root cause
    # --------------------------------------------------------

    root_cause = diagnosis.get(
        "likely_root_cause",
        ""
    )

    if not isinstance(
        root_cause,
        str
    ):

        root_cause = str(
            root_cause
        )

    diagnosis[
        "likely_root_cause"
    ] = root_cause.strip()


    # --------------------------------------------------------
    # 10B. Normalize reasoning
    # --------------------------------------------------------

    reasoning = diagnosis.get(
        "reasoning",
        ""
    )

    if not isinstance(
        reasoning,
        str
    ):

        reasoning = str(
            reasoning
        )

    diagnosis[
        "reasoning"
    ] = reasoning.strip()


    # --------------------------------------------------------
    # 10C. Normalize evidence
    # --------------------------------------------------------

    evidence_items = diagnosis.get(
        "evidence",
        []
    )

    if not isinstance(
        evidence_items,
        list
    ):

        evidence_items = []

    diagnosis[
        "evidence"
    ] = [
        str(item).strip()
        for item in evidence_items
        if str(item).strip()
    ]


    # --------------------------------------------------------
    # 10D. Normalize historical context
    # --------------------------------------------------------

    historical_context = diagnosis.get(
        "historical_context",
        ""
    )

    if not isinstance(
        historical_context,
        str
    ):

        historical_context = str(
            historical_context
        )

    diagnosis[
        "historical_context"
    ] = historical_context.strip()


    # --------------------------------------------------------
    # 10E. Normalize recommended actions
    # --------------------------------------------------------

    recommended_actions = diagnosis.get(
        "recommended_actions",
        []
    )

    if not isinstance(
        recommended_actions,
        list
    ):

        recommended_actions = []

    cleaned_actions = []

    for action in recommended_actions:

        if not isinstance(
            action,
            str
        ):
            continue

        action = action.strip()

        if not action:
            continue

        cleaned_actions.append(
            action
        )

    diagnosis[
        "recommended_actions"
    ] = cleaned_actions


    # --------------------------------------------------------
    # 10F. Normalize confidence
    # --------------------------------------------------------

    confidence = diagnosis.get(
        "confidence"
    )

    if isinstance(
        confidence,
        str
    ):

        confidence = confidence.strip().capitalize()

    else:

        confidence = None


    if confidence not in [
        "High",
        "Medium",
        "Low"
    ]:

        # Conservative fallback if the model
        # does not provide a valid confidence.
        confidence = "Medium"


    diagnosis[
        "confidence"
    ] = confidence


    # --------------------------------------------------------
    # 11. SAFETY CHECK
    # --------------------------------------------------------

    historical_context = diagnosis.get(
        "historical_context",
        ""
    )

    # --------------------------------------------------------
    # Detect the current incident ID in historical context.
    #
    # Case-insensitive replacement prevents the current
    # incident from being presented as historical.
    # --------------------------------------------------------

    if historical_context:

        pattern = re.compile(
            re.escape(
                current_incident_id
            ),
            re.IGNORECASE
        )

        if pattern.search(
            historical_context
        ):

            historical_context = pattern.sub(
                "[CURRENT INCIDENT]",
                historical_context
            )

            diagnosis[
                "historical_context"
            ] = historical_context


    # --------------------------------------------------------
    # 12. FIND MATCHING RUNBOOK
    # --------------------------------------------------------

    root_cause = diagnosis.get(
        "likely_root_cause",
        ""
    )

    runbook = get_runbook(
        root_cause
    )


    # --------------------------------------------------------
    # 13. ATTACH RUNBOOK
    # --------------------------------------------------------

    if runbook:

        diagnosis["runbook"] = {

            "title":
                runbook["title"],

            "procedure":
                runbook["procedure"],

            "verification":
                runbook["verification"],

            "simulation_only":
                True,
        }

    else:

        diagnosis["runbook"] = {

            "title":
                "No matching runbook found",

            "procedure":
                [],

            "verification":
                [],

            "simulation_only":
                True,
        }


    # --------------------------------------------------------
    # 14. RETURN FINAL DIAGNOSIS
    # --------------------------------------------------------

    return diagnosis


# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

if __name__ == "__main__":

    print(
        "========== OPSMIND AI SRE AGENT ==========\n"
    )

    incident_id = input(
        "Enter incident ID: "
    ).strip()

    try:

        diagnosis = diagnose_incident(
            incident_id
        )

        print(
            "\n========== AI DIAGNOSIS ==========\n"
        )

        print(
            json.dumps(
                diagnosis,
                indent=2
            )
        )

    except Exception as error:

        print(
            "\n❌ OpsMind encountered an error:"
        )

        print(
            error
        )