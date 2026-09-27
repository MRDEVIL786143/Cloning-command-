import os
import shlex
import socket
import subprocess
import sys
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "terminal-runner")
socketio = SocketIO(app, cors_allowed_origins="*")

process = None
process_lock = threading.Lock()


def parse_env(raw_env):
    env_map = os.environ.copy()
    if not raw_env:
        return env_map
    for line in raw_env.splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env_map[key.strip()] = value.strip()
    return env_map


def emit_status(status, message=""):
    socketio.emit("status", {"status": status, "message": message})


def stream_output():
    global process
    if process is None:
        return
    try:
        for line in iter(process.stdout.readline, ""):
            if not line:
                break
            socketio.emit("output", {"data": line})
        process.stdout.close()
    except Exception as exc:
        socketio.emit("output", {"data": f"\n[ERROR] Stream reader failed: {exc}\n"})
    finally:
        if process.poll() is not None:
            emit_status("stopped", f"Process exited with code {process.returncode}")
        else:
            emit_status("stopped", "Process ended")


def start_process(script_path, args, working_dir, env_raw):
    global process
    with process_lock:
        if process is not None and process.poll() is None:
            emit_status("error", "A process is already running.")
            return

        cleaned_path = script_path.strip()
        if not cleaned_path:
            emit_status("error", "Please choose a Python file to run.")
            return

        if not os.path.exists(cleaned_path):
            if not os.path.exists(os.path.join(working_dir, cleaned_path)):
                emit_status("error", f"File not found: {cleaned_path}")
                return
            cleaned_path = os.path.join(working_dir, cleaned_path)

        if not cleaned_path.endswith(".py"):
            emit_status("error", "Only Python files can be run from this terminal.")
            return

        cmd = [sys.executable, cleaned_path] + shlex.split(args)
        env = parse_env(env_raw)
        try:
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                env=env,
                shell=False,
            )
        except Exception as exc:
            emit_status("error", f"Failed to start process: {exc}")
            process = None
            return

        emit_status("running", f"Started: {' '.join(cmd)}")
        t = threading.Thread(target=stream_output, daemon=True)
        t.start()


@socketio.on("start")
def handle_start(payload):
    script_path = payload.get("script_path", "")
    args = payload.get("args", "")
    working_dir = payload.get("working_dir") or os.getcwd()
    env_raw = payload.get("env_vars", "")
    start_process(script_path, args, working_dir, env_raw)


@socketio.on("send_input")
def handle_input(data):
    global process
    if process is None or process.stdin is None or process.poll() is not None:
        emit_status("error", "No active process to send input to.")
        return
    text = data.get("text", "")
    if text:
        process.stdin.write(text)
        process.stdin.flush()


@socketio.on("stop")
def handle_stop():
    global process
    if process is None or process.poll() is not None:
        emit_status("stopped", "No running process found.")
        return
    try:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        emit_status("stopped", "Process stopped manually.")
    except Exception as exc:
        emit_status("error", f"Failed to stop process: {exc}")
    finally:
        process = None


@socketio.on("connect")
def handle_connect():
    emit_status("ready", "Cyber terminal connected.")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "5000"))
    socketio.run(app, host=host, port=port, debug=False, use_reloader=False)
