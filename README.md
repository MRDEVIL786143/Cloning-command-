# Cyber Terminal Runner

This project creates a cyber-style web terminal that can launch a Python file and stream its output in the browser.

Important:
- This runner is intentionally generic and does not modify the repository's original Python script.
- Do not point it at harmful or unauthorized scripts.
- Use it only for scripts you own or are explicitly authorized to execute.

Files included:
- `app.py` - Flask + Socket.IO backend that starts/stops a Python process and streams output.
- `templates/index.html` - cyber-terminal frontend.
- `static/style.css` - cyber styling.
- `safe_script.py` - sample script for testing the terminal runner.
- `requirements.txt` - Python dependencies for the web UI and terminal.
- `Dockerfile` and `docker-compose.yml` - run the app 24/7 with restart policies.

Run locally:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open:

```text
http://localhost:5000
```

Run with Docker:

```bash
docker compose up --build -d
```

Then open:

```text
http://localhost:5000
```

Use the UI to enter:
- Python file path: for example `./safe_script.py`
- Arguments: for example `--count 5`
- Working directory: `.`

The terminal starts the script, streams output, and allows you to send stdin when needed.
