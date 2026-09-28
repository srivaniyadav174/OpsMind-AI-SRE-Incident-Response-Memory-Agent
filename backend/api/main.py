from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.incident_tool import (
    get_incident,
    list_incidents,
)

from backend.opsmind_engine import (
    analyze_incident,
    resolve_incident,
)


# ========================================
# PATHS
# ========================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"


# ========================================
# REQUEST MODELS
# ========================================

class ResolveRequest(BaseModel):
    diagnosis: dict


# ========================================
# FASTAPI APPLICATION
# ========================================

app = FastAPI(
    title="OpsMind API",
    description="AI SRE Incident Response and Memory Agent",
    version="1.0.0",
)


# ========================================
# FRONTEND
# ========================================

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )


# ========================================
# HEALTH CHECK
# ========================================

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OpsMind API",
    }


# ========================================
# INCIDENT LIST
# ========================================

@app.get("/incidents")
def get_all_incidents():

    incidents = list_incidents()

    return {
        "success": True,
        "count": len(incidents),
        "incidents": incidents,
    }


# ========================================
# SINGLE INCIDENT
# ========================================

@app.get("/incidents/{incident_id}")
def get_single_incident(
    incident_id: str,
):

    incident = get_incident(
        incident_id
    )

    if incident is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Incident "
                f"{incident_id} "
                f"not found."
            ),
        )

    return {
        "success": True,

        "incident": {
            "incident_id":
                incident["incident_id"],

            "service":
                incident["service"],

            "severity":
                incident["severity"],

            "symptoms":
                incident["symptoms"],

            "metrics":
                incident["metrics"],
        },
    }


# ========================================
# ANALYZE INCIDENT
# ========================================

@app.post(
    "/incidents/{incident_id}/analyze"
)
def analyze_incident_endpoint(
    incident_id: str,
):

    try:

        result = analyze_incident(
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
                "OpsMind failed to "
                f"analyze the incident: "
                f"{error}"
            ),
        )


# ========================================
# RESOLVE INCIDENT
# ========================================

@app.post(
    "/incidents/{incident_id}/resolve"
)
def resolve_incident_endpoint(
    incident_id: str,
    request: ResolveRequest,
):

    try:

        result = resolve_incident(
            incident_id,
            request.diagnosis,
        )

        return {
            "success": True,
            "data": result,
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "OpsMind failed to "
                f"resolve the incident: "
                f"{error}"
            ),
        )