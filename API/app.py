from fastapi import FastAPI, Request, Depends, Security, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from datetime import datetime
import subprocess
import logging
import os
import os
from dotenv import load_dotenv

load_dotenv()  # Loads variables from .env into environment


# -----------------------
# Configuration
# -----------------------
LOG_FILE = "../logs/api_logs.log"
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = "access-token"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# -----------------------
# Logging Setup
# -----------------------
# Get the root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO) # Set overall logging level

# Create a formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s - %(message)s")

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)
root_logger.addHandler(file_handler)

# Stream handler (for console output)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
root_logger.addHandler(stream_handler)

# Specific loggers for Uvicorn access and error logs
# This ensures Uvicorn's own request/error logs are captured by our handlers
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.propagate = False # Prevent double logging if root also catches
uvicorn_access_logger.addHandler(file_handler)
uvicorn_access_logger.addHandler(stream_handler)

uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.propagate = False
uvicorn_error_logger.addHandler(file_handler)
uvicorn_error_logger.addHandler(stream_handler)


logger = logging.getLogger(__name__) # Logger for your application specific messages

# -----------------------
# FastAPI Setup
# -----------------------
app = FastAPI()

# -----------------------
# API Key Validation
# -----------------------
def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        logger.info("API Key validated successfully.")
        return api_key_header
    logger.warning(f"Invalid or missing API Key attempt from: {api_key_header}")
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN,
        detail="Invalid or missing API Key",
    )

# -----------------------
# Utility to run scripts
# -----------------------
def run_script(script_path):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    logger.info(f"{timestamp} Attempting to run script: {script_path}")
    try:
        # Use shell=True for simple commands if they are executable, but generally avoid for security
        # For Python scripts, it's better to explicitly call 'python'
        result = subprocess.run(["python", script_path], capture_output=True, text=True, check=False)

        output_stdout = result.stdout.strip()
        output_stderr = result.stderr.strip()

        # Log stdout line by line with timestamp
        if output_stdout:
            stdout_lines = output_stdout.splitlines()
            for line in stdout_lines:
                logger.info(f"{timestamp} Script OUT: {script_path} - {line}")

        # Log stderr line by line with timestamp
        if output_stderr:
            stderr_lines = output_stderr.splitlines()
            for line in stderr_lines:
                logger.error(f"{timestamp} Script ERR: {script_path} - {line}")

        if result.returncode == 0:
            logger.info(f"{timestamp} Script SUCCESS: {script_path} executed successfully.")
            return {
                "status": "success",
                "output_stdout": output_stdout,
                "output_stderr": output_stderr,
                "return_code": result.returncode
            }
        else:
            logger.error(f"{timestamp} Script FAILED: {script_path} exited with code {result.returncode}. STDOUT: {output_stdout}. STDERR: {output_stderr}")
            return {
                "status": "failed",
                "message": f"Script exited with non-zero code {result.returncode}",
                "output_stdout": output_stdout,
                "output_stderr": output_stderr,
                "return_code": result.returncode
            }
    except FileNotFoundError:
        logger.error(f"{timestamp} Script ERROR: Python interpreter or script '{script_path}' not found.")
        return {"status": "error", "message": f"Script or Python interpreter not found: {script_path}"}
    except Exception as e:
        logger.error(f"{timestamp} Script ERROR: An unexpected error occurred while running {script_path}: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}

# -----------------------
# Root Route - List All
# -----------------------
@app.get("/", dependencies=[Depends(get_api_key)])
def root():
    logger.info("Received request for root route (list all routes).")
    routes = [route.path for route in app.routes]
    logger.info("Successfully listed all routes.")
    return {"message": "Available routes", "routes": routes}

# -----------------------
# Run Entire Pipeline
# -----------------------
@app.get("/pipeline/run_main_file", dependencies=[Depends(get_api_key)])
def run_main_file():
    logger.info("Received request to run finviz_stock_news_scraper.")
    return run_script("../main.py")

# -----------------------
# Individual Scripts
# -----------------------
@app.get("/scrape/finviz_stock_news", dependencies=[Depends(get_api_key)])
def run_finviz_stock_news():
    logger.info("Received request to run finviz_stock_news_scraper.")
    return run_script("scrapers/finviz_stock_news_scraper.py")

@app.get("/scrape/finviz_market_news", dependencies=[Depends(get_api_key)])
def run_finviz_market_news():
    logger.info("Received request to run finviz_market_news_scraper.")
    return run_script("scrapers/finviz_market_news_scraper.py")

@app.get("/scrape/tradingview_news", dependencies=[Depends(get_api_key)])
def run_tradingview_news():
    logger.info("Received request to run tradingview_news_scraper.")
    return run_script("scrapers/tradingview_news_scraper.py")

@app.get("/merge/finviz_tradingview", dependencies=[Depends(get_api_key)])
def merge_finviz_tradingview():
    logger.info("Received request to run finviz_tradingview_csv_merger.")
    return run_script("mergers/finviz_tradingview_csv_merger.py")

@app.get("/sentiment/finviz_stock_news", dependencies=[Depends(get_api_key)])
def sentiment_finviz_stock():
    logger.info("Received request to run finviz_stocknews_sentiment.")
    return run_script("sentiments/finviz_stocknews_sentiment.py")

@app.get("/sentiment/finviz_tradingview", dependencies=[Depends(get_api_key)])
def sentiment_finviz_tradingview():
    logger.info("Received request to run finviz_tradingview_sentiment.")
    return run_script("sentiments/finviz_tradingview_sentiment.py")

# -----------------------
# Logging Routes
# -----------------------
@app.get("/logs", dependencies=[Depends(get_api_key)])
def get_logs():
    logger.info("Received request to fetch full logs.")
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                content = f.read()
            logger.info("Logs fetched successfully.")
            return JSONResponse(content={"logs": content})
        except Exception as e:
            logger.error(f"Error reading log file: {str(e)}", exc_info=True)
            return JSONResponse(content={"message": f"Error reading log file: {str(e)}"}, status_code=500)
    else:
        logger.warning("Attempted to fetch logs but log file not found.")
        return JSONResponse(content={"logs": "Log file not found."}, status_code=404)

@app.get("/logs/tail", dependencies=[Depends(get_api_key)])
def tail_logs(lines: int = 50):
    logger.info(f"Received request to tail logs (last {lines} lines).")
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                log_lines = f.readlines()[-lines:]
            logger.info("Tail logs fetched successfully.")
            return {"last_logs": "".join(log_lines)}
        except Exception as e:
            logger.error(f"Error tailing log file: {str(e)}", exc_info=True)
            return JSONResponse(content={"message": f"Error tailing log file: {str(e)}"}, status_code=500)
    else:
        logger.warning("Attempted to tail logs but log file not found.")
        return {"last_logs": "Log file not found."}

@app.get("/logs/download", dependencies=[Depends(get_api_key)])
def download_logs():
    logger.info("Received request to download log file.")
    if os.path.exists(LOG_FILE):
        logger.info("Log file prepared for download.")
        return FileResponse(LOG_FILE, filename="api_logs.log")
    else:
        logger.warning("Attempted to download logs but log file not found.")
        return JSONResponse(content={"message": "Log file not found."}, status_code=404)