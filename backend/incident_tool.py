import json
from pathlib import Path


# Find the project's incidents.json file
PROJECT_ROOT = Path(__file__).resolve().parent.parent
INCIDENTS_FILE = PROJECT_ROOT / "data" / "incidents" / "incidents.json"


def load_incidents():
    """Load all incidents from the JSON dataset."""

    if not INCIDENTS_FILE.exists():
        raise FileNotFoundError(
            f"Incident data not found at: {INCIDENTS_FILE}"
        )

    with open(INCIDENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_incident(incident_id):
    """Retrieve one incident by incident ID."""

    incidents = load_incidents()

    for incident in incidents:
        if incident["incident_id"].lower() == incident_id.lower():
            return incident

    return None


def list_incidents():
    """Return a summary of all available incidents."""

    incidents = load_incidents()

    return [
        {
            "incident_id": incident["incident_id"],
            "service": incident["service"],
            "severity": incident["severity"],
            "root_cause": incident["root_cause"],
        }
        for incident in incidents
    ]


if __name__ == "__main__":

    print("========== OPSMIND INCIDENT TOOL ==========\n")

    print("Available incidents:\n")

    for incident in list_incidents():
        print(
            f'{incident["incident_id"]} | '
            f'{incident["service"]} | '
            f'{incident["severity"]}'
        )

    print("\n--------------------------------------------")

    incident_id = input("\nEnter incident ID: ")

    incident = get_incident(incident_id)

    if incident is None:
        print(f"\n❌ Incident {incident_id} not found.")
    else:
        print("\n✅ Incident found!\n")
        print(json.dumps(incident, indent=2))