import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

def assert_keys(data, keys):
    for k in keys:
        if k not in data:
            raise AssertionError(f"Missing key: {k}")

def verify_decision_hub():
    os.environ["API_KEY"] = os.environ.get("API_KEY", "localtest")
    client = TestClient(app)
    client.headers.update({"X-API-Key": os.environ["API_KEY"]})
    r = client.post("/api/decision_hub", data={"input_text": "Schedule meeting", "platform": "web", "device_context": "desktop"})
    if r.status_code != 200:
        raise AssertionError(f"decision_hub status {r.status_code}")
    data = r.json()
    required = ["assistant_message", "action_taken", "next_steps", "confidence_level", "trace_id", "response_version"]
    assert_keys(data, required)
    if data.get("response_version") != "v1":
        raise AssertionError("response_version is not v1")

def main():
    verify_decision_hub()
    print("OK ARL v1 integration verified")

if __name__ == "__main__":
    main()
