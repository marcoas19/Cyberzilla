
import sys
import unittest

from datetime import datetime, timedelta
from pathlib import Path

# Import Cyberzilla's detection engine
backend = Path(__file__).resolve().parents[1] / "backend"

sys.path.insert(0, str(backend))

from detector import detect_threats


class TestCyberzilla(unittest.TestCase):

    def create_events(self, ip, count, interval):

        start = datetime(2026, 9, 24, 10, 0, 0)

        return [
            {
                "timestamp": start + timedelta(
                    seconds=i * interval
                ),
                "source_ip": ip,
                "username": "admin",
                "event_type": "login_failed"
            }
            for i in range(count)
        ]

    def test_detects_suspicious_activity(self):

        events = self.create_events(
            "192.0.2.10", 5, 10
        )

        alerts = detect_threats(events)

        self.assertEqual(len(alerts), 1)

        self.assertEqual(
            alerts[0]["severity"],
            "HIGH"
        )

        self.assertEqual(
            alerts[0]["rule_id"],
            "CZ-001"
        )

        self.assertEqual(
            len(alerts[0]["evidence"]),
            5
        )

        self.assertEqual(
            alerts[0]["response"],
            "NOT_EXECUTED"
        )

    def test_ignores_normal_activity(self):

        events = self.create_events(
            "192.0.2.20", 2, 10
        )

        alerts = detect_threats(events)

        self.assertEqual(len(alerts), 0)

    def test_ignores_attempts_outside_window(self):

        events = self.create_events(
            "192.0.2.30", 5, 70
        )

        alerts = detect_threats(events)

        self.assertEqual(len(alerts), 0)


if __name__ == "__main__":
    unittest.main()