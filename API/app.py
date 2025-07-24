from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def list_routes():
    return {
        "message": "API is live!",
        "routes": {
            "/": "Lists all available routes",
            "/status": "Check service status",
            "/pipeline/run_main_file": "Runs the main pipeline script"
        }
    }

@app.get("/status")
def status_check():
    return {"status": "Service is active and unsecured (no auth)."}

@app.get("/pipeline/run_main_file")
def run_main_file():
    try:
        result = subprocess.run(
            ["python", "../main.py"],
            capture_output=True,
            text=True
        )
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"status": "exception", "error": str(e)}
