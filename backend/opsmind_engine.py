import json

from agent.sre_agent import diagnose_incident
from incident_tool import get_incident

from learning_tool import (
    retain_incident_outcome,
    close_learning_client,
)

from memory_tool import close_memory_client


# ============================================================
# OPSMIND INCIDENT WORKFLOW
# ============================================================

def process_incident(incident_id):
    """
    Run the complete OpsMind incident workflow:

    1. Investigate incident
    2. Generate AI diagnosis
    3. Retrieve runbook
    4. Simulate remediation
    5. Store outcome in Hindsight
    """

    # --------------------------------------------------------
    # 1. Get incident
    # --------------------------------------------------------

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
        "        OPSMIND INCIDENT WORKFLOW"
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

    # --------------------------------------------------------
    # 2. AI diagnosis
    # --------------------------------------------------------

    print(
        "\n[1/4] Investigating incident..."
    )

    diagnosis = diagnose_incident(
        incident_id
    )

    print(
        "✅ AI diagnosis generated."
    )

    print(
        f"\nLikely Root Cause:\n"
        f"{diagnosis.get('likely_root_cause')}"
    )

    print(
        f"\nConfidence:\n"
        f"{diagnosis.get('confidence')}"
    )

    # --------------------------------------------------------
    # 3. Display recommended actions
    # --------------------------------------------------------

    print(
        "\n[2/4] Recommended Actions"
    )

    actions = diagnosis.get(
        "recommended_actions",
        []
    )

    for index, action in enumerate(
        actions,
        start=1
    ):

        print(
            f"{index}. {action}"
        )

    # --------------------------------------------------------
    # 4. Display runbook
    # --------------------------------------------------------

    print(
        "\n[3/4] Runbook"
    )

    runbook = diagnosis.get(
        "runbook",
        {}
    )

    print(
        f"Title: {runbook.get('title')}"
    )

    procedure = runbook.get(
        "procedure",
        []
    )

    for step in procedure:

        print(
            f"{step['step']}. "
            f"{step['action']}"
        )

    # --------------------------------------------------------
    # 5. Simulate resolution
    # --------------------------------------------------------

    print(
        "\n[4/4] Simulating Resolution..."
    )

    simulated_actions = [
        step["action"]
        for step in procedure
    ]

    print(
        "\n⚠️ No real production systems are changed."
    )

    print(
        "All remediation actions are simulated."
    )

    for action in simulated_actions:

        print(
            f"   ✓ Simulated: {action}"
        )

    # --------------------------------------------------------
    # 6. Simulated outcome
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 7. Store learning in Hindsight
    # --------------------------------------------------------

    print(
        "\nStoring incident learning in Hindsight..."
    )

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

    # --------------------------------------------------------
    # 8. Close Hindsight clients
    # --------------------------------------------------------

    close_memory_client()

    close_learning_client()

    print(
        "✅ Hindsight clients closed cleanly."
    )

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

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

        "diagnosis": diagnosis,

        "actions": simulated_actions,

        "outcome": outcome,

        "learned": True,
    }


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    incident_id = input(
        "Enter incident ID: "
    ).strip()

    try:

        result = process_incident(
            incident_id
        )

        print(
            "\n========== FINAL RESULT ==========\n"
        )

        print(
            json.dumps(
                result,
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