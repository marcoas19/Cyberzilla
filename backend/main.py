
from pathlib import Path

from detector import (
    load_events,
    detect_threats,
    save_report
)


def main():

    print("=" * 50)
    print("       CYBERZILLA: ATOMIC DEFENSE")
    print("          THREAT HUNTING SYSTEM")
    print("=" * 50)

    # Locate the sample security logs
    base_dir = Path(__file__).parent

    log_file = (
        base_dir
        / "sample_logs"
        / "auth_events.json"
    )

    print("\n[MOTHRA] Starting security scan...")

    try:
        events = load_events(log_file)

        print(
            f"[MOTHRA] Analyzed {len(events)} events."
        )

        print(
            "\n[GODZILLA] Hunting for suspicious activity..."
        )

        alerts = detect_threats(events)

        if not alerts:

            print(
                "\n[GODZILLA] No threats detected."
            )

        else:

            for alert in alerts:

                print("\n" + "!" * 50)

                print("       THREAT DETECTED!")

                print("!" * 50)

                print(
                    f"Source IP: {alert['source_ip']}"
                )

                print(
                f"Rule: {alert['rule_id']}"
                )

                print(
                f"Threat: {alert['rule_name']}"
                )

                print(
                    f"Severity: {alert['severity']}"
                )

                print(
                    f"Failed attempts: {alert['attempts']}"
                )

                print(
                    f"First seen: {alert['first_seen']}"
                )

                print(
                    f"Last seen: {alert['last_seen']}"
                )

                
                print(
                    f"\nDescription: {alert['description']}"
            )

                print("\n[HUNTER MODE] Evidence collected:")

            for evidence in alert["evidence"]:

                print(
        f"  [{evidence['timestamp']}] "
        f"{evidence['source_ip']} "
        f"-> {evidence['username']} "
        f"({evidence['event_type']})"
    )

                print(
                    "\n[GODZILLA] ATOMIC BREATH READY!"
                )

                print(
                    "[DEFENSE] Simulation only."
                )

                print(
                    "[DEFENSE] No IP addresses were blocked."
                )

        report_path = save_report(alerts)

        print(
            f"\n[REPORT] Saved to: {report_path}"
        )

        print("\n[CYBERZILLA] Scan completed.")

    except (
        FileNotFoundError,
        ValueError,
        KeyError,
        TypeError
    ) as error:

        print(
            f"\n[ERROR] Scan failed: {error}"
        )


if __name__ == "__main__":
    main()
    