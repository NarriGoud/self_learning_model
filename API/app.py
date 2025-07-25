from fastapi import FastAPI
import subprocess

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "API is running on Render!",
        "routes": {
            "/status": "Check if service is up",
            "/run": "Trigger main pipeline",
            "/hello": "Test route"
        }
    }

@app.get("/status")
def status():
    return {"status": "✅ Service is up!"}

@app.get("/hello")
def hello():
    return {"message": "👋 Hello from the API!"}

@app.get("/run")
def run_main():
    try:
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True)
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"status": "exception", "error": str(e)}
