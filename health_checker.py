from fastapi import FastAPI, HTTPException
import uvicorn
from subprocess import Popen
import os
import signal

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Health check successful"}


# Variable to store the process
process = None

@app.get("/start")
def start_script():
    global process
    if process and process.poll() is None:  # Check if process is already running
        raise HTTPException(status_code=400, detail="Script is already running.")
    try:
        process = Popen(["python", "main.py"], stdout=None, stderr=None)  # Change stdout/stderr as needed
        return {"message": "Script started successfully.", "pid": process.pid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start script: {str(e)}")

@app.get("/stop")
def stop_script():
    global process
    if not process or process.poll() is not None:  # Check if process is not running
        raise HTTPException(status_code=400, detail="Script is not running.")
    try:
        os.kill(process.pid, signal.SIGTERM)  # Send termination signal
        process.wait()  # Wait for the process to terminate
        process = None
        return {"message": "Script stopped successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop script: {str(e)}")

@app.get("/status")
def script_status():
    global process
    if process and process.poll() is None:  # Check if process is running
        return {"status": "running", "pid": process.pid}
    return {"status": "not running"}


if __name__ == "__main__":
    print("GOING HERE !!")
    uvicorn.run(app, host="0.0.0.0", port=8080)
