import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
from ipaddress import ip_address
from pathlib import Path


# ============================================================
# CYBERZILLA CONFIGURATION
# ============================================================

THRESHOLD = 5
TIME_WINDOW = timedelta(seconds=60)


def load_events(file_path):
    """Mothra reads and validates the security event file."""

    with open(file_path, "r", encoding="utf-8") as file:
        events = json.load(file)

    if not isinstance(events, list):
        raise ValueError("Expected a list of events.")

    validated_events = []

    for event in events:
        if not isinstance(event, dict):
            raise ValueError("Invalid event format.")

        # Validate required fields
        timestamp = datetime.fromisoformat(
            event["timestamp"]
        )

        source_ip = str(
            ip_address(event["source_ip"])
        )

        username = event["username"]
        event_type = event["event_type"]

        if not isinstance(username, str):
            raise ValueError(
                "Username must be a string."
            )

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
            "username": username,
            "event_type": event_type
        })

    return sorted(
        validated_events,
        key=lambda event: event["timestamp"]
    )


def serialize_event(event):
    """Convert an internal event into JSON-safe evidence."""

    return {
        "timestamp": event["timestamp"].isoformat(),
        "source_ip": event["source_ip"],
        "username": event["username"],
        "event_type": event["event_type"]
    }


def remove_old_events(events, current_time):
    """Remove events that fall outside the detection window."""

    while events and (
        current_time - events[0]["timestamp"] > TIME_WINDOW
    ):
        events.popleft()


def detect_threats(events):
    """
    Cyberzilla Hunter Mode.

    CZ-001:
        Detect repeated failed login attempts from one IP.

    CZ-002:
        Detect a successful login after repeated failures
        from the same IP against the same username.
    """

    # Used by CZ-001:
    # source_ip -> recent failed events
    failures_by_ip = defaultdict(deque)

    # Used by CZ-002:
    # (source_ip, username) -> recent failed events
    failures_by_account = defaultdict(deque)

    alerts = []

    # Prevent duplicate alerts for the same activity
    alerted_ips = set()
    alerted_success_sequences = set()

    for event in events:

        source_ip = event["source_ip"]
        username = event["username"]
        timestamp = event["timestamp"]
        event_type = event["event_type"]

        account_key = (
            source_ip,
            username
        )

        # ====================================================
        # FAILED LOGIN
        # ====================================================

        if event_type == "login_failed":

            # ----------------------------
            # Track failures by IP
            # for CZ-001
            # ----------------------------

            ip_attempts = failures_by_ip[source_ip]

            ip_attempts.append(event)

            remove_old_events(
                ip_attempts,
                timestamp
            )

            # ----------------------------
            # Track failures by IP + user
            # for CZ-002
            # ----------------------------

            account_attempts = (
                failures_by_account[account_key]
            )

            account_attempts.append(event)

            remove_old_events(
                account_attempts,
                timestamp
            )

            # =================================================
            # CZ-001
            # Repeated Failed Login Attempts
            # =================================================

            if (
                len(ip_attempts) >= THRESHOLD
                and source_ip not in alerted_ips
            ):

                evidence = [
                    serialize_event(attempt)
                    for attempt in ip_attempts
                ]

                alert = {
                    "rule_id": "CZ-001",
                    "rule_name": (
                        "Repeated Failed Login Attempts"
                    ),
                    "source_ip": source_ip,
                    "severity": "HIGH",
                    "attempts": len(ip_attempts),
                    "first_seen": (
                        ip_attempts[0][
                            "timestamp"
                        ].isoformat()
                    ),
                    "last_seen": (
                        timestamp.isoformat()
                    ),
                    "description": (
                        f"{len(ip_attempts)} failed login "
                        f"attempts detected within 60 "
                        f"seconds from {source_ip}."
                    ),
                    "evidence": evidence,
                    "status": "DETECTED",
                    "response": "NOT_EXECUTED"
                }

                alerts.append(alert)

                alerted_ips.add(source_ip)

        # ====================================================
        # SUCCESSFUL LOGIN
        # ====================================================

        elif event_type == "login_success":

            account_attempts = (
                failures_by_account[account_key]
            )

            # Remove failures that are too old
            remove_old_events(
                account_attempts,
                timestamp
            )

            # =================================================
            # CZ-002
            # Successful Login After Repeated Failures
            # =================================================

            if (
                len(account_attempts) >= THRESHOLD
                and account_key
                not in alerted_success_sequences
            ):

                evidence = [
                    serialize_event(attempt)
                    for attempt in account_attempts
                ]

                # Include the successful login itself
                evidence.append(
                    serialize_event(event)
                )

                alert = {
                    "rule_id": "CZ-002",
                    "rule_name": (
                        "Successful Login After "
                        "Repeated Failures"
                    ),
                    "source_ip": source_ip,
                    "username": username,
                    "severity": "HIGH",
                    "attempts": len(
                        account_attempts
                    ),
                    "first_seen": (
                        account_attempts[0][
                            "timestamp"
                        ].isoformat()
                    ),
                    "last_seen": (
                        timestamp.isoformat()
                    ),
                    "description": (
                        f"Successful login for "
                        f"'{username}' from {source_ip} "
                        f"after {len(account_attempts)} "
                        f"failed attempts within "
                        f"60 seconds."
                    ),
                    "evidence": evidence,
                    "status": "DETECTED",
                    "response": "NOT_EXECUTED"
                }

                alerts.append(alert)

                alerted_success_sequences.add(
                    account_key
                )

            # A successful login ends this sequence.
            account_attempts.clear()

    return alerts


def save_report(alerts):
    """Save the detection results as JSON."""

    reports_dir = (
        Path(__file__).parent / "reports"
    )

    reports_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    report_path = (
        reports_dir / "alerts.json"
    )

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