from celery import Celery
import os
import json

app = Celery(
    "tasks",
    broker="pyamqp://guest@localhost//",
    backend=None  # kita nggak pakai Redis
)

RESULT_DIR = "results"
os.makedirs(RESULT_DIR, exist_ok=True)

@app.task
def add(x, y):
    result = x + y
    key = f"{x}_{y}"
    with open(f"{RESULT_DIR}/{key}.json", "w") as f:
        json.dump({"x": x, "y": y, "result": result}, f)
    return result

@app.task
def get_result_from_file(key: str):
    path = f"{RESULT_DIR}/{key}.json"
    if not os.path.exists(path):
        return "NOT_FOUND"
    with open(path, "r") as f:
        return json.load(f)
