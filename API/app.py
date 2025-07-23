from fastapi import FastAPI, Header, HTTPException
import subprocess
import os

app = FastAPI()

def verify_api_key(x_api_key: str = Header(...)):
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not set in environment.")
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/")
def health_check():
    return {"message": "API is live and running on Render."}

@app.get("/status")
def status_check(x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
    return {"status": "Service is active and secured."}

@app.get("/pipeline/run_main_file")
def run_main_file(x_api_key: str = Header(...)):
    verify_api_key(x_api_key)
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
