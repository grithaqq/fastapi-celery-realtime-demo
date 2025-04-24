from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.tasks import add, get_result_from_file, RESULT_DIR
import asyncio
import os
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients = []

@app.get("/result/{key}")
def fetch_result(key: str):
    path = f"{RESULT_DIR}/{key}.json"
    if not os.path.exists(path):
        return {"status": "NOT_FOUND"}
    with open(path, "r") as f:
        data = json.load(f)
    return {"status": "SUCCESS", "result": data}

@app.post("/add")
def add_task(x: int, y: int):
    key = f"{x}_{y}"
    add.delay(x, y)
    return {"lookup_key": key}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(0.5)
            for filename in os.listdir(RESULT_DIR):
                if filename.endswith(".json"):
                    with open(os.path.join(RESULT_DIR, filename)) as f:
                        data = json.load(f)
                        await websocket.send_json({"type": "result", "payload": data["result"]})
                    os.remove(os.path.join(RESULT_DIR, filename))  # kirim sekali lalu hapus
    except Exception:
        connected_clients.remove(websocket)