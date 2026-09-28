from fastapi import FastAPI, HTTPException


# ============================================================
# IMPORT OPSMIND ENGINE
# ============================================================

from opsmind_engine import process_incident


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="OpsMind API",
    description=(
        "AI SRE Incident Response and Memory Agent"
    ),
    version="1.0.0",
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "service": "OpsMind API",
    }


# ============================================================
# ANALYZE INCIDENT
# ============================================================

@app.post("/incidents/{incident_id}/analyze")
def analyze_incident(
    incident_id: str
):

    try:

        result = process_incident(
            incident_id
        )

        return {
            "success": True,
            "data": result,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"OpsMind failed to process "
                f"the incident: {error}"
            ),
        )