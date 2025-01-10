from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok", "message": "Health check successful"}

if __name__ == "__main__":
    print("GOING HERE !!")
    uvicorn.run(app, host="0.0.0.0", port=8080)
