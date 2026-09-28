import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

LOGS_FILE = PROJECT_ROOT / "data" / "logs" / "logs.json"
METRICS_FILE = PROJECT_ROOT / "data" / "metrics" / "metrics.json"


def load_json(file_path):
    """Load JSON data from a file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Data file not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_logs(incident_id):
    """Retrieve logs for an incident."""

    logs = load_json(LOGS_FILE)

    return logs.get(incident_id.upper(), [])


def get_metrics(incident_id):
    """Retrieve metrics for an incident."""

    metrics = load_json(METRICS_FILE)

    return metrics.get(incident_id.upper(), {})


def get_evidence(incident_id):
    """Return logs and metrics for an incident."""

    return {
        "incident_id": incident_id.upper(),
        "logs": get_logs(incident_id),
        "metrics": get_metrics(incident_id),
    }


if __name__ == "__main__":

    print("========== OPSMIND EVIDENCE TOOL ==========\n")

    incident_id = input("Enter incident ID: ")

    evidence = get_evidence(incident_id)

    if not evidence["logs"] and not evidence["metrics"]:
        print(f"\n❌ No evidence found for {incident_id}")
    else:
        print("\n✅ Evidence found!\n")

        print("----- LOGS -----")

        for log in evidence["logs"]:
            print(log)

        print("\n----- METRICS -----")

        for name, value in evidence["metrics"].items():
            print(f"{name}: {value}")