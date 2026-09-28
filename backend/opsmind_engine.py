import json

from backend.agent.sre_agent import diagnose_incident
from backend.incident_tool import get_incident

from backend.learning_tool import (
    retain_incident_outcome,
    close_learning_client,
)

from backend.memory_tool import close_memory_client


# ============================================================
# ANALYZE INCIDENT
# ============================================================

def analyze_incident(incident_id):
    """
    Investigate an incident using current evidence,
    AI reasoning, and Hindsight memory.

    IMPORTANT:
    This function does NOT resolve the incident.
    It only generates the diagnosis and runbook.
    """

    incident = get_incident(
        incident_id
    )

    if incident is None:
        raise ValueError(
            f"Incident {incident_id} not found."
        )

    print(
        "\n========================================"
    )
    print(
        "        OPSMIND INCIDENT ANALYSIS"
    )
    print(
        "========================================\n"
    )

    print(
        f"Incident : {incident['incident_id']}"
    )

    print(
        f"Service  : {incident['service']}"
    )

    print(
        f"Severity : {incident['severity']}"
    )

    print(
        "\n[1/2] Investigating incident..."
    )

    diagnosis = diagnose_incident(
        incident_id
    )

    print(
        "✅ AI diagnosis generated."
    )

    print(
        f"\nLikely Root Cause:"
    )

    print(
        diagnosis.get(
            "likely_root_cause"
        )
    )

    print(
        f"\nConfidence:"
    )

    print(
        diagnosis.get(
            "confidence"
        )
    )

    print(
        "\n[2/2] Analysis complete."
    )

    print(
        "\n⚠️ No remediation has been executed."
    )

    print(
        "Human approval is required before resolution."
    )

    return {
        "incident_id": incident["incident_id"],
        "service": incident["service"],
        "severity": incident["severity"],
        "diagnosis": diagnosis,
        "awaiting_approval": True,
    }


# ============================================================
# RESOLVE INCIDENT
# ============================================================

def resolve_incident(
    incident_id,
    diagnosis,
):
    """
    Simulate the runbook remediation and store
    the resulting incident learning in Hindsight.

    No real production systems are changed.
    """

    incident = get_incident(
        incident_id
    )

    if incident is None:
        raise ValueError(
            f"Incident {incident_id} not found."
        )

    if not diagnosis:
        raise ValueError(
            "Diagnosis is required before resolution."
        )

    print(
        "\n========================================"
    )

    print(
        "        OPSMIND INCIDENT RESOLUTION"
    )

    print(
        "========================================\n"
    )

    print(
        f"Incident : {incident['incident_id']}"
    )

    print(
        f"Service  : {incident['service']}"
    )

    print(
        f"Diagnosis:"
    )

    print(
        diagnosis.get(
            "likely_root_cause",
            "Unknown"
        )
    )

    # ========================================================
    # RUNBOOK
    # ========================================================

    runbook = diagnosis.get(
        "runbook",
        {}
    )

    procedure = runbook.get(
        "procedure",
        []
    )

    if not procedure:
        raise ValueError(
            "No runbook procedure available."
        )

    print(
        "\n[1/3] Runbook:"
    )

    print(
        f"Title: {runbook.get('title')}"
    )

    for step in procedure:

        print(
            f"{step['step']}. "
            f"{step['action']}"
        )

    # ========================================================
    # SIMULATED ACTIONS
    # ========================================================

    print(
        "\n[2/3] Simulating Resolution..."
    )

    print(
        "\n⚠️ No real production systems are changed."
    )

    print(
        "All remediation actions are simulated."
    )

    simulated_actions = []

    for step in procedure:

        action = step["action"]

        simulated_actions.append(
            action
        )

        print(
            f"   ✓ Simulated: {action}"
        )

    # ========================================================
    # SIMULATED OUTCOME
    # ========================================================

    outcome = (
        "Simulated remediation completed successfully. "
        "Expected service metrics returned toward normal "
        "levels."
    )

    print(
        "\nSimulated Outcome:"
    )

    print(
        outcome
    )

    # ========================================================
    # HINDSIGHT LEARNING
    # ========================================================

    print(
        "\n[3/3] Storing incident learning in Hindsight..."
    )

    try:

        retain_incident_outcome(
            incident_id=incident["incident_id"],
            service=incident["service"],
            diagnosis=diagnosis.get(
                "likely_root_cause",
                "Unknown"
            ),
            actions_taken=simulated_actions,
            outcome=outcome,
            successful=True,
        )

        print(
            "✅ Incident learning stored."
        )

    finally:

        close_memory_client()
        close_learning_client()

        print(
            "✅ Hindsight clients closed cleanly."
        )

    print(
        "\n========================================"
    )

    print(
        "       OPSMIND LEARNING COMPLETE"
    )

    print(
        "========================================\n"
    )

    return {
        "incident_id": incident["incident_id"],
        "actions": simulated_actions,
        "outcome": outcome,
        "learned": True,
    }


# ============================================================
# DIRECT CLI TEST
# ============================================================

if __name__ == "__main__":

    incident_id = input(
        "Enter incident ID: "
    ).strip()

    try:

        # ----------------------------------------------------
        # ANALYZE
        # ----------------------------------------------------

        analysis = analyze_incident(
            incident_id
        )

        print(
            "\n========== ANALYSIS RESULT ==========\n"
        )

        print(
            json.dumps(
                analysis,
                indent=2
            )
        )

        # ----------------------------------------------------
        # HUMAN APPROVAL
        # ----------------------------------------------------

        approval = input(
            "\nApprove simulated resolution? (yes/no): "
        ).strip().lower()

        if approval not in (
            "yes",
            "y",
        ):

            print(
                "\nResolution cancelled."
            )

        else:

            # ------------------------------------------------
            # RESOLVE
            # ------------------------------------------------

            resolution = resolve_incident(
                incident_id,
                analysis["diagnosis"],
            )

            print(
                "\n========== RESOLUTION RESULT ==========\n"
            )

            print(
                json.dumps(
                    resolution,
                    indent=2
                )
            )

    except Exception as error:

        print(
            "\n❌ OpsMind workflow failed:"
        )

        print(
            error
        )