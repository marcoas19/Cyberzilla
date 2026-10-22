# TaTo · Your first scan

[← Back to the project](../README.md)

You do not need to know FastAPI or Vue to follow this guide. Start with the [README's setup commands](../README.md#quick-start), then use this page to understand what you are seeing.

## Five words you will see

| Term | Plain explanation |
| --- | --- |
| Event | One record, such as a failed login |
| Source IP | The address recorded as the origin of that event; it does not identify a person by itself |
| Rule | A condition the program checks, such as five failures within a minute |
| Finding / alert | A rule match that deserves review |
| Evidence | The original event details supporting that finding |

## Why two terminals?

**Terminal one runs the backend:** Python reads the sample records and evaluates the detection rules. FastAPI makes those results available over HTTP on port 8000.

**Terminal two runs the frontend:** Vite serves the Vue dashboard, normally on port 5173. The dashboard sends scan requests through Vite's `/api` proxy to FastAPI.

Closing either terminal stops that part of the application. Running the frontend alone does not run the detector.

## Walk through the bundled sample

1. Start both services using the README.
2. Open the address printed by Vite.
3. Select **Start scan**.
4. Expect **seven analyzed events and two findings** from the bundled file.
5. Expand **View full API result**.
6. Find `CZ-001`: five failures came from the same IP in 40 seconds.
7. Find `CZ-002`: that same user and IP then had a successful login at 50 seconds.
8. Inspect each finding's `evidence`. The successful login appears in CZ-002's evidence.
9. Select **Export JSON** to download the returned result.
10. Select **Simulate response** to see the visual demonstration. No security action is executed.

The two findings overlap. TaTo is showing two patterns in one sequence, not counting two attackers.

> The dashboard's scenario buttons and JSON editor do not control the checked-in backend. It always loads the sample file. This is a known integration gap during the TaTo migration.

## Try a normal login

This experiment changes a local sample file. Make a backup first, then restore it afterward.

1. Open `backend/sample_logs/auth_events.json` in your editor.
2. Save a copy outside the repository so you can restore the original contents.
3. Replace the file contents with this array:

```json
[
  {
    "timestamp": "2026-09-24T10:00:00",
    "source_ip": "192.0.2.20",
    "username": "demo-user",
    "event_type": "login_success"
  }
]
```

4. Save the file. The API reloads the dataset on each scan; restarting it is unnecessary for this data change.
5. Select **Start scan** again. Expect **one event and zero findings**.
6. Restore the original file from your backup. Scan again to return to seven events and two findings.

For this file format, every event needs `timestamp`, `source_ip`, `username`, and `event_type`. Supported types are `login_failed` and `login_success`. Use consistent timestamps, either all with timezone information or all without it. The loader sorts them before detection.

## What should an analyst ask?

A rule match is the start of an investigation. Useful questions include:

- Was the user having password problems at that time?
- Does the source address belong to an expected device, a shared network, or the local computer?
- Was the successful login expected by the account owner?
- Are there other records that support or contradict the finding?

The project does not answer these automatically. A successful login after failures can be legitimate.

## Troubleshooting

| What you see | What to check |
| --- | --- |
| `python` is not recognized | Install Python and reopen PowerShell; confirm `python --version` works |
| `npm` is not recognized | Install a Node version supported by `frontend/package.json` and reopen PowerShell |
| PowerShell blocks `npm.ps1` | Try `npm.cmd ci` and `npm.cmd run dev` instead of changing execution policy |
| `Could not import module api` | Run Uvicorn from the `backend` directory using `api:app` |
| `ModuleNotFoundError` for FastAPI | Install requirements with the same `.venv` Python used to start Uvicorn |
| Port 8000 is in use | Check for a backend you already started; use its terminal or stop it before starting another |
| Dashboard cannot reach the API | Keep the backend running on port 8000; use `npm run dev` so the Vite development proxy is active |
| Vite uses a different frontend port | Open the address Vite prints; the development proxy still handles `/api` |
| Normal scenario still returns findings | This backend ignores submitted JSON. Use the file-based experiment above |
| Scan returns HTTP 500 | Check the backend terminal and restore the original sample if you changed its format |
| `/api/windows/scan` returns 404 | Windows collection is absent from this repository version; this is not an administrator-permission error |
| Interface or download says Cyberzilla | Those application labels still belong to the earlier implementation |

`npm run preview` is not equivalent to `npm run dev`: the checked-in proxy is configured for the development server. Use the development command for this guide.

## Stop and restart later

Press **Ctrl+C** in both terminals. Your installed dependencies remain available.

Next time, open a terminal in `backend` and run:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
```

Open a second terminal in `frontend` and run:

```powershell
npm run dev
```

You only need to reinstall dependencies when they change or when setting up a new environment.
