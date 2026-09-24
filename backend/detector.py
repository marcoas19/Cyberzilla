
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from ipaddress import ip_address
from pathlib import Path


# CYBERZILLA CONFIGURATION
THRESHOLD = 5
TIME_WINDOW = timedelta(seconds=60)


def load_events(file_path):
    """Mothra reads the security event file."""

    with open(file_path, "r", encoding="utf-8") as file:
        events = json.load(file)

    if not isinstance(events, list):
        raise ValueError("Expected a list of events.")

    validated_events = []

    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Invalid event format.")

        # Validate required event fields
        timestamp = datetime.fromisoformat(
            event["timestamp"]
        )

        source_ip = str(
            ip_address(event["source_ip"])
        )

        event_type = event["event_type"]

        if event_type not in (
            "login_failed",
            "login_success"
        ):
            raise ValueError(
                f"Unknown event type: {event_type}"
            )

        validated_events.append({
            "timestamp": timestamp,
            "source_ip": source_ip,
            "username": event["username"],
            "event_type": event_type
        })

    return sorted(
        validated_events,
        key=lambda event: event["timestamp"]
    )



def detect_threats(events):
    """Cyberzilla Hunter Mode: detect and investigate threats."""

    failed_attempts = defaultdict(deque)
    alerts = []
    alerted_ips = set()

    for event in events:

        if event["event_type"] != "login_failed":
            continue

        source_ip = event["source_ip"]
        timestamp = event["timestamp"]

        attempts = failed_attempts[source_ip]

        # Store the complete event as evidence
        attempts.append(event)

        # Remove events outside the detection window
        while attempts and (
            timestamp - attempts[0]["timestamp"] > TIME_WINDOW
        ):
            attempts.popleft()

        # Trigger the detection rule
        if (
            len(attempts) >= THRESHOLD
            and source_ip not in alerted_ips
        ):

            evidence = []

            for attempt in attempts:

                evidence.append({
                    "timestamp": attempt[
                        "timestamp"
                    ].isoformat(),
                    "source_ip": attempt["source_ip"],
                    "username": attempt["username"],
                    "event_type": attempt["event_type"]
                })

            alert = {
                "rule_id": "CZ-001",
                "rule_name": (
                    "Repeated Failed Login Attempts"
                ),
                "source_ip": source_ip,
                "severity": "HIGH",
                "attempts": len(attempts),
                "first_seen": attempts[0][
                    "timestamp"
                ].isoformat(),
                "last_seen": timestamp.isoformat(),
                "description": (
                    f"{len(attempts)} failed login attempts "
                    f"detected within 60 seconds from "
                    f"{source_ip}."
                ),
                "evidence": evidence,
                "status": "DETECTED",
                "response": "NOT_EXECUTED"
            }

            alerts.append(alert)

            alerted_ips.add(source_ip)

    return alerts


def save_report(alerts):
    """Save the detection results as JSON."""

    reports_dir = Path(__file__).parent / "reports"

    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    report_path = reports_dir / "alerts.json"

    with open(
        report_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            alerts,
            file,
            indent=4
        )

    return report_path
