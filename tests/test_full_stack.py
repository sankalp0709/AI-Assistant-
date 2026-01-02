import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Ensure API key is set to match tests
os.environ["API_KEY"] = os.environ.get("API_KEY", "localtest")

client = TestClient(app)
client.headers.update({"X-API-Key": os.environ["API_KEY"]})

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Assistant Core v3 API" in response.json()["message"]

def test_summarize():
    response = client.post("/api/summarize", json={"text": "This is a test text.", "max_length": 10})
    assert response.status_code == 200
    assert "summary" in response.json()

def test_intent():
    response = client.post("/api/intent", json={"text": "Hello"})
    assert response.status_code == 200
    assert "intent" in response.json()

def test_task():
    response = client.post("/api/task", json={"intent": "note", "original_text": "Test task"})
    assert response.status_code == 200
    assert "task" in response.json()

def test_decision_hub():
    response = client.post("/api/decision_hub", data={
        "input_text": "Test input",
        "platform": "web",
        "device_context": "desktop"
    })
    assert response.status_code == 200
    data = response.json()
    required = ["assistant_message", "action_taken", "next_steps", "confidence_level", "trace_id", "response_version"]
    for k in required:
        assert k in data
    assert data["response_version"] == "v1"

def test_decision_hub_vr():
    response = client.post("/api/decision_hub", data={
        "input_text": "Speak something",
        "platform": "vr",
        "device_context": "vr",
        "voice_input": True
    })
    assert response.status_code == 200
    data = response.json()
    required = ["assistant_message", "action_taken", "next_steps", "confidence_level", "trace_id", "response_version"]
    for k in required:
        assert k in data
    assert data["response_version"] == "v1"

def test_rl_action():
    response = client.post("/api/rl_action", json={"state": {}, "actions": ["action1", "action2"]})
    assert response.status_code == 200
    assert "selected_action" in response.json()

def test_embed():
    response = client.post("/api/embed", json={"texts": ["Hello world"]})
    assert response.status_code == 200
    assert "embeddings" in response.json()

def test_respond():
    response = client.post("/api/respond", json={"query": "Hello", "context": {}})
    assert response.status_code == 200
    assert "response" in response.json()

def test_voice_stt():
    # Stub STT via form param
    response = client.post("/api/voice_stt", data={"request": '{"audio_url": "test"}'})
    assert response.status_code == 200
    assert "text" in response.json()

def test_voice_tts():
    response = client.post("/api/voice_tts", json={"text": "Hello", "voice": "alloy"})
    assert response.status_code == 200
    assert "audio_base64" in response.json()

def test_external_llm():
    response = client.post("/api/external_llm", json={"prompt": "Hello", "model": "uniguru"})
    assert response.status_code == 200
    assert "response" in response.json()

def test_external_app_crm():
    response = client.post("/api/external_app", json={"app": "crm", "action": "update", "params": {}})
    assert response.status_code == 200
    assert "crm_action" in response.json()["result"]

def test_external_app_erp():
    response = client.post("/api/external_app", json={"app": "erp", "action": "process", "params": {}})
    assert response.status_code == 200
    assert "erp_action" in response.json()["result"]

def test_external_app_calendar():
    response = client.post("/api/external_app", json={"app": "calendar", "action": "add", "params": {}})
    assert response.status_code == 200
    assert "calendar_action" in response.json()["result"]

def test_external_app_email():
    response = client.post("/api/external_app", json={"app": "email", "action": "send", "params": {}})
    assert response.status_code == 200
    assert "email_action" in response.json()["result"]

def test_voice_to_intent_flow():
    # Test voice STT then intent
    stt_response = client.post("/api/voice_stt", data={"request": '{"audio_url": "test"}'})
    text = stt_response.json()["text"]
    intent_response = client.post("/api/intent", json={"text": text})
    assert intent_response.status_code == 200

def test_multi_llm_routing():
    models = ["uniguru", "chatgpt", "groq", "gemini", "mistral"]
    for model in models:
        response = client.post("/api/external_llm", json={"prompt": "Hello", "model": model})
        assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__])
