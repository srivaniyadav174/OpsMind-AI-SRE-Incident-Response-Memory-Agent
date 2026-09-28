import json
import re
from pathlib import Path


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RUNBOOKS_FILE = (
    PROJECT_ROOT
    / "data"
    / "runbooks"
    / "runbooks.json"
)


# ============================================================
# LOAD RUNBOOKS
# ============================================================

def load_runbooks():
    if not RUNBOOKS_FILE.exists():
        raise FileNotFoundError(
            f"Runbook data not found at: {RUNBOOKS_FILE}"
        )

    with open(
        RUNBOOKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):
    """
    Normalize text so that AI-generated root-cause
    descriptions can be matched with runbook names.
    """

    if not text:
        return ""

    text = text.lower()

    # Remove punctuation
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    # Normalize whitespace
    text = " ".join(
        text.split()
    )

    return text


# ============================================================
# FIND MATCHING RUNBOOK
# ============================================================

def get_runbook(incident_type):

    runbooks = load_runbooks()

    if not incident_type:
        return None

    normalized_incident_type = normalize_text(
        incident_type
    )

    # --------------------------------------------------------
    # 1. Exact normalized match
    # --------------------------------------------------------

    for runbook in runbooks:

        normalized_runbook_type = normalize_text(
            runbook["incident_type"]
        )

        if (
            normalized_incident_type
            == normalized_runbook_type
        ):
            return runbook

    # --------------------------------------------------------
    # 2. Runbook name contained in AI diagnosis
    # --------------------------------------------------------

    for runbook in runbooks:

        normalized_runbook_type = normalize_text(
            runbook["incident_type"]
        )

        if (
            normalized_runbook_type
            in normalized_incident_type
        ):
            return runbook

    # --------------------------------------------------------
    # 3. Important keyword matching
    # --------------------------------------------------------

    keyword_groups = {
        "database connection pool exhaustion": [
            "database",
            "connection",
            "pool",
            "exhaustion",
        ],

        "memory leak": [
            "memory",
            "leak",
        ],

        "cpu saturation": [
            "cpu",
            "saturation",
        ],
    }

    for runbook in runbooks:

        runbook_type = normalize_text(
            runbook["incident_type"]
        )

        keywords = keyword_groups.get(
            runbook_type,
            []
        )

        if keywords:

            if all(
                keyword in normalized_incident_type
                for keyword in keywords
            ):
                return runbook

    return None


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========== OPSMIND RUNBOOK TOOL ==========\n"
    )

    incident_type = input(
        "Enter incident type: "
    ).strip()

    runbook = get_runbook(
        incident_type
    )

    if runbook is None:

        print(
            "\n❌ Runbook not found."
        )

    else:

        print(
            "\n✅ Runbook found!\n"
        )

        print(
            f"Incident Type: "
            f"{runbook['incident_type']}"
        )

        print(
            f"Title: "
            f"{runbook['title']}\n"
        )

        print(
            "----- PROCEDURE -----"
        )

        for step in runbook["procedure"]:

            print(
                f"{step['step']}. "
                f"{step['action']}"
            )

        print(
            "\n----- VERIFICATION -----"
        )

        for check in runbook["verification"]:

            print(
                f"- {check}"
            )

        print(
            "\n⚠️ All actions are simulated "
            "for the OpsMind demo."
        )