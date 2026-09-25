from datetime import datetime, timedelta

from backend.detector import detect_threats


def event(
    timestamp,
    source_ip="192.0.2.10",
    username="admin",
    event_type="login_failed"
):
    return {
        "timestamp": timestamp,
        "source_ip": source_ip,
        "username": username,
        "event_type": event_type
    }


def test_cz001_repeated_failed_logins():
    start = datetime(2026, 9, 24, 10, 0, 0)

    events = [
        event(start + timedelta(seconds=0)),
        event(start + timedelta(seconds=10)),
        event(start + timedelta(seconds=20)),
        event(start + timedelta(seconds=30)),
        event(start + timedelta(seconds=40)),
    ]

    alerts = detect_threats(events)

    assert len(alerts) == 1

    alert = alerts[0]

    assert alert["rule_id"] == "CZ-001"
    assert alert["severity"] == "HIGH"
    assert alert["source_ip"] == "192.0.2.10"
    assert alert["attempts"] == 5
    assert len(alert["evidence"]) == 5


def test_cz002_success_after_failures():
    start = datetime(2026, 9, 24, 10, 0, 0)

    events = [
        event(start + timedelta(seconds=0)),
        event(start + timedelta(seconds=10)),
        event(start + timedelta(seconds=20)),
        event(start + timedelta(seconds=30)),
        event(start + timedelta(seconds=40)),
        event(
            start + timedelta(seconds=50),
            event_type="login_success"
        ),
    ]

    alerts = detect_threats(events)

    rule_ids = [
        alert["rule_id"]
        for alert in alerts
    ]

    assert "CZ-001" in rule_ids
    assert "CZ-002" in rule_ids

    cz002 = next(
        alert
        for alert in alerts
        if alert["rule_id"] == "CZ-002"
    )

    assert cz002["username"] == "admin"
    assert cz002["attempts"] == 5
    assert len(cz002["evidence"]) == 6

    assert (
        cz002["evidence"][-1]["event_type"]
        == "login_success"
    )


def test_normal_login_does_not_trigger_alert():
    events = [
        event(
            datetime(2026, 9, 24, 10, 0, 0),
            source_ip="198.51.100.25",
            username="marco",
            event_type="login_success"
        )
    ]

    alerts = detect_threats(events)

    assert alerts == []


def test_failures_outside_time_window_do_not_trigger():
    start = datetime(2026, 9, 24, 10, 0, 0)

    events = [
        event(start + timedelta(seconds=0)),
        event(start + timedelta(seconds=20)),
        event(start + timedelta(seconds=40)),
        event(start + timedelta(seconds=80)),
        event(start + timedelta(seconds=100)),
    ]

    alerts = detect_threats(events)

    assert alerts == []


def test_different_users_do_not_trigger_cz002():
    start = datetime(2026, 9, 24, 10, 0, 0)

    events = [
        event(
            start + timedelta(seconds=0),
            username="admin"
        ),
        event(
            start + timedelta(seconds=10),
            username="root"
        ),
        event(
            start + timedelta(seconds=20),
            username="guest"
        ),
        event(
            start + timedelta(seconds=30),
            username="test"
        ),
        event(
            start + timedelta(seconds=40),
            username="service"
        ),
        event(
            start + timedelta(seconds=50),
            username="admin",
            event_type="login_success"
        ),
    ]

    alerts = detect_threats(events)

    rule_ids = [
        alert["rule_id"]
        for alert in alerts
    ]

    assert "CZ-002" not in rule_ids