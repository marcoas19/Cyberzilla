# CYBERZILLA: ATOMIC DEFENSE SYSTEM
# Version 0.5 - Threat Detection API

from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from detector import (
    load_events,
    detect_threats,
)

# Create our API
app = FastAPI(
    title="Cyberzilla: Atomic Defense System",
    description="Threat Detection and Hunting API",
    version="0.5.0",
)

# Project paths
BASE_DIR = Path(__file__).resolve().parent

LOG_FILE = BASE_DIR / "sample_logs" / "auth_events.json"

# Allow our local Vue dashboard to communicate
# with the Python backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# API health check
@app.get("/")
def home():
    return {
        "name": "CYBERZILLA",
        "system": "Atomic Defense System",
        "version": "0.5.0",
        "status": "ONLINE",
    }


# Run the threat detection engine
@app.post("/api/scan")
def scan():
    try:
        # Load our sample authentication events
        events = load_events(LOG_FILE)

        # Analyze events using our detector
        threats = detect_threats(events)

        return {
            "status": "SCAN_COMPLETED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_events": len(events),
            "threats_detected": len(threats),
            "threats": threats,
            "mode": "SAMPLE_LOG_ANALYSIS",
        }

    except Exception as error:
        print(f"[CYBERZILLA API ERROR] {error}")

        raise HTTPException(
            status_code=500,
            detail="Threat detection scan failed.",
        )