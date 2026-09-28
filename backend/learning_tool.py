import os

from dotenv import load_dotenv
from hindsight_client import Hindsight


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

HINDSIGHT_API_KEY = os.getenv(
    "HINDSIGHT_API_KEY"
)

BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "opsmind-incidents"
)

if not HINDSIGHT_API_KEY:
    raise ValueError(
        "HINDSIGHT_API_KEY is missing from .env"
    )


# ============================================================
# HINDSIGHT CLIENT
# ============================================================

client = Hindsight(
    base_url="https://api.hindsight.vectorize.io",
    api_key=HINDSIGHT_API_KEY,
)


def close_learning_client():
    """
    Close the Hindsight client used by the learning tool.
    """

    try:
        client.close()
    except Exception:
        pass


# ============================================================
# STORE INCIDENT OUTCOME
# ============================================================

def retain_incident_outcome(
    incident_id,
    service,
    diagnosis,
    actions_taken,
    outcome,
    successful=True
):
    """
    Store the result of an incident investigation in Hindsight.
    """

    if isinstance(actions_taken, list):

        actions_text = "\n".join(
            f"- {action}"
            for action in actions_taken
        )

    else:

        actions_text = str(
            actions_taken
        )

    learning_record = f"""
OpsMind Incident Learning Record

Incident ID: {incident_id}

Service: {service}

AI Diagnosis:
{diagnosis}

Actions Taken:
{actions_text}

Outcome:
{outcome}

Resolution Successful:
{successful}

Learning:
Future incidents involving similar symptoms should consider
this previous experience when determining investigation and
remediation steps.
"""

    client.retain(
        bank_id=BANK_ID,
        content=learning_record,
        context="OpsMind SRE incident learning",
        metadata={
            "incident_id": str(
                incident_id
            ),
            "service": str(
                service
            ),
            "type": "incident_outcome",
            "successful": str(
                successful
            ).lower(),
        },
    )

    return True


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========== OPSMIND LEARNING TOOL ==========\n"
    )

    print(
        "Storing simulated incident outcome...\n"
    )

    try:

        retain_incident_outcome(
            incident_id="INC-006",

            service="payment-api",

            diagnosis=(
                "Database connection pool exhaustion"
            ),

            actions_taken=[
                "Inspected database connection pool",
                "Simulated increasing pool capacity",
                "Simulated restarting payment-api",
            ],

            outcome=(
                "API latency returned toward normal levels "
                "and HTTP 500 errors decreased."
            ),

            successful=True,
        )

        print(
            "✅ Incident outcome stored in Hindsight."
        )

        print(
            "\nOpsMind has learned from this incident."
        )

    except Exception as error:

        print(
            "\n❌ Failed to store incident outcome."
        )

        print(
            f"Error: {error}"
        )

    finally:

        close_learning_client()

        print(
            "\n✅ Hindsight client closed cleanly."
        )