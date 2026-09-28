import os
import re

from dotenv import load_dotenv
from hindsight_client import Hindsight


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")

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


def close_memory_client():
    """
    Close the Hindsight client used by the memory tool.
    """

    try:
        client.close()
    except Exception:
        pass


# ============================================================
# EXTRACT INCIDENT ID
# ============================================================

def extract_incident_id(memory_text):
    """
    Extract an incident ID such as INC-001 from memory text.
    """

    if not memory_text:
        return None

    match = re.search(
        r"\bINC-\d+\b",
        memory_text.upper()
    )

    if match:
        return match.group(0)

    return None


# ============================================================
# CLEAN MEMORY TEXT
# ============================================================

def clean_memory_text(text):
    """
    Remove Hindsight-generated date suffixes and
    normalize whitespace.
    """

    if not text:
        return ""

    text = re.sub(
        r"\s*\|\s*When:\s*\d{4}-\d{2}-\d{2}",
        "",
        text,
        flags=re.IGNORECASE
    )

    return " ".join(text.split())


# ============================================================
# MERGE MEMORIES FOR ONE INCIDENT
# ============================================================

def merge_incident_memories(memories):
    """
    Combine multiple Hindsight memories belonging to
    the same incident into one historical record.
    """

    grouped = {}

    for memory in memories:

        incident_id = extract_incident_id(memory)

        if not incident_id:
            incident_id = "UNKNOWN"

        if incident_id not in grouped:
            grouped[incident_id] = []

        cleaned = clean_memory_text(memory)

        if cleaned and cleaned not in grouped[incident_id]:
            grouped[incident_id].append(cleaned)

    merged = []

    for incident_id, texts in grouped.items():

        combined_text = " ".join(texts)

        if incident_id != "UNKNOWN":

            combined_text = (
                f"Historical Incident: {incident_id}\n"
                f"{combined_text}"
            )

        merged.append(combined_text)

    return merged


# ============================================================
# RECALL SIMILAR INCIDENTS
# ============================================================

def recall_similar_incidents(
    query,
    current_incident_id=None,
    max_memories=5
):
    """
    Search Hindsight for relevant historical incidents.

    Features:
    - Excludes current incident
    - Groups memories by incident ID
    - Removes duplicate memory text
    - Returns clean historical context
    """

    result = client.recall(
        bank_id=BANK_ID,
        query=query,
    )

    raw_memories = []

    current_id = (
        current_incident_id.upper()
        if current_incident_id
        else None
    )

    for memory in result.results:

        text = getattr(
            memory,
            "text",
            ""
        )

        if not text:
            continue

        incident_id = extract_incident_id(text)

        # ----------------------------------------------------
        # Exclude current incident
        # ----------------------------------------------------

        if (
            current_id
            and incident_id == current_id
        ):
            continue

        raw_memories.append(text)

    # --------------------------------------------------------
    # Group related memories
    # --------------------------------------------------------

    merged_memories = merge_incident_memories(
        raw_memories
    )

    return merged_memories[:max_memories]


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========== OPSMIND MEMORY TOOL ==========\n"
    )

    current_incident_id = input(
        "Enter current incident ID: "
    ).strip()

    query = """
    Payment API is experiencing high latency and HTTP 500
    errors. Database connection utilization is very high.
    Requests are waiting for database connections.

    Find previous incidents with similar symptoms and
    useful remediation experience.
    """

    print(
        "\nSearching Hindsight memory...\n"
    )

    try:

        memories = recall_similar_incidents(
            query=query,
            current_incident_id=current_incident_id,
            max_memories=5,
        )

        if not memories:

            print(
                "No relevant historical incidents found."
            )

        else:

            print(
                "========== HISTORICAL INCIDENTS ==========\n"
            )

            for index, memory in enumerate(
                memories,
                start=1
            ):

                print(
                    f"[Historical Memory {index}]"
                )

                print(memory)

                print(
                    "\n----------------------------------------\n"
                )

    except Exception as error:

        print(
            f"❌ Memory search failed: {error}"
        )

    finally:

        close_memory_client()

        print(
            "✅ Hindsight client closed cleanly."
        )