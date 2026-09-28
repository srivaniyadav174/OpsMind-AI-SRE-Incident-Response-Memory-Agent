import os
import re

from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BANK_ID = os.getenv(
    "HINDSIGHT_BANK_ID",
    "opsmind-incidents",
)

client = None


def get_client():
    global client

    if client is None:
        client = Hindsight(
            base_url="https://api.hindsight.vectorize.io",
            api_key=HINDSIGHT_API_KEY,
        )

    return client


def close_memory_client():
    global client

    if client is not None:
        try:
            client.close()
        except Exception:
            pass
        finally:
            client = None


def extract_incident_id(text: str):
    """
    Extract an incident ID such as INC-001 from memory text.
    """

    match = re.search(r"\bINC-\d+\b", text)

    if match:
        return match.group(0)

    return None


def clean_memory_text(text: str):
    """
    Clean memory text for readable output.
    """

    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_memory_text(memory):
    """
    Extract the actual text from a Hindsight memory object.
    """

    if isinstance(memory, str):
        return memory

    if isinstance(memory, dict):
        return (
            memory.get("text")
            or memory.get("content")
            or memory.get("memory")
            or ""
        )

    text = getattr(memory, "text", None)

    if text:
        return text

    return ""


def normalize_for_comparison(text: str):
    """
    Normalize text for duplicate detection.
    """

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        text.lower(),
    ).strip()


def deduplicate_texts(texts):
    """
    Remove exact duplicate memory statements.
    """

    unique = []
    seen = set()

    for text in texts:

        text = clean_memory_text(text)

        if not text:
            continue

        normalized = normalize_for_comparison(text)

        if normalized in seen:
            continue

        seen.add(normalized)
        unique.append(text)

    return unique


def merge_incident_memories(memories):
    """
    Group Hindsight memories by incident ID.
    """

    grouped = {}

    for memory in memories:

        text = extract_memory_text(memory)
        text = clean_memory_text(text)

        if not text:
            continue

        incident_id = extract_incident_id(text)

        if incident_id is None:
            incident_id = "UNKNOWN"

        grouped.setdefault(
            incident_id,
            [],
        )

        grouped[incident_id].append(text)

    merged = []

    for incident_id, texts in grouped.items():

        unique_texts = deduplicate_texts(texts)

        if not unique_texts:
            continue

        selected = unique_texts[:4]

        merged.append(
            {
                "incident_id": incident_id,
                "memory": " ".join(selected),
            }
        )

    return merged


def recall_similar_incidents(
    current_incident_id: str,
    query: str,
    max_memories: int = 5,
):
    """
    Recall similar historical incidents.

    IMPORTANT:
    This function returns clean TEXT STRINGS because
    sre_agent.py expects a list of strings.
    """

    hindsight_client = get_client()

    memories = hindsight_client.recall(
        bank_id=HINDSIGHT_BANK_ID,
        query=query,
    )

    merged = merge_incident_memories(memories)

    results = []

    for item in merged:

        if item["incident_id"] == current_incident_id:
            continue

        # Convert the structured memory back into a readable
        # string for the existing SRE agent.
        memory_text = (
            f"Historical Incident: "
            f"{item['incident_id']}\n"
            f"{item['memory']}"
        )

        results.append(memory_text)

        if len(results) >= max_memories:
            break

    return results


def format_historical_context(memories):
    """
    Format historical memory strings for the SRE agent.
    """

    if not memories:
        return "No similar historical incidents found."

    sections = []

    for memory in memories:

        if isinstance(memory, str):
            sections.append(memory)

        elif isinstance(memory, dict):

            incident_id = memory.get(
                "incident_id",
                "UNKNOWN",
            )

            memory_text = memory.get(
                "memory",
                "",
            )

            sections.append(
                f"Historical Incident: "
                f"{incident_id}\n"
                f"{memory_text}"
            )

    return "\n\n".join(sections)


if __name__ == "__main__":

    print(
        "========== OPSMIND MEMORY TOOL =========="
    )

    current_incident_id = input(
        "\nEnter current incident ID: "
    ).strip()

    print(
        "\nSearching Hindsight memory..."
    )

    memories = recall_similar_incidents(
        current_incident_id=current_incident_id,
        query=(
            "Find previous incidents involving payment-api, "
            "database connection pool exhaustion, high latency, "
            "HTTP 500 errors, connection utilization, and "
            "successful remediation."
        ),
    )

    print(
        "\n========== HISTORICAL INCIDENTS =========="
    )

    if not memories:

        print(
            "No historical incidents found."
        )

    else:

        for index, memory in enumerate(
            memories,
            start=1,
        ):

            print(
                f"\n[Historical Memory {index}]"
            )

            print(memory)

            print(
                "\n" + "-" * 40
            )

    close_memory_client()

    print(
        "\n✅ Hindsight client closed cleanly."
    )