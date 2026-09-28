import json
from pathlib import Path


INCIDENTS_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "incidents"
    / "incidents.json"
)


def load_incidents():
    with open(INCIDENTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_incident(incident_id: str):
    incidents = load_incidents()

    for incident in incidents:
        if incident["incident_id"] == incident_id:
            return incident

    return None


def list_incidents():
    incidents = load_incidents()

    return [
        {
            "incident_id": incident["incident_id"],
            "service": incident["service"],
            "severity": incident["severity"],
        }
        for incident in incidents
    ]