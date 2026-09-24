
# CYBERZILLA: Atomic Defense System

Cyberzilla is a cybersecurity portfolio project built with
Python, FastAPI, and Vue.js.

It analyzes sample authentication logs to identify suspicious
activity and displays detection results in an interactive
dashboard.

## Current Features

- Python-based authentication log analysis
- Detection of repeated failed login attempts
- FastAPI endpoint for running scans
- Vue.js security dashboard
- Threat severity and supporting event data
- Animated cyber-kaiju mascots
- Simulated defensive response

## Tech Stack

- Python
- FastAPI
- Vue.js
- Vite

## Detection Example

Rule: CZ-001 — Repeated Failed Login Attempts

The detector identifies five failed login attempts from the
same source IP within a 60-second window.

The project uses synthetic authentication events for
demonstration and testing.

## Project Structure

- `backend/` — Python detection engine and API
- `frontend/` — Vue.js dashboard
- `tests/` — Detection tests

## Project Status

Active development.

The dashboard currently runs locally with a Python API.
Defensive actions are simulated; Cyberzilla does not block
real IP addresses or modify firewall rules.

## Author

Marco Aguilar

Cybersecurity student | BYU