import httpx
import asyncio
import sys
import os

# Ensure we can import app code if needed, but we'll try to hit the running server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def verify_integration():
    print("Wait for server to start...")
    # Simple wait or retry logic could be added here, but for now we assume server is running
    # or we might want to start it here. But usually it's better to run server in separate process.
    
    url = "http://localhost:8000/api/decision_hub"
    
    # Payload for a simple meeting task
    payload = {
        "input_text": "Schedule a meeting with Bob tomorrow at 10am",
        "platform": "web",
        "device_context": "desktop"
    }
    
    # We need to simulate form data as the endpoint expects Form(...)
    # Using httpx to send form data
    
    headers = {
        "X-API-Key": "your_api_key_here"
    }

    print(f"Sending request to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload, headers=headers, timeout=30.0)
            
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("\nResponse Body:")
            import json
            print(json.dumps(data, indent=2))
            
            # Verify keys exist
            required_keys = ["assistant_message", "action_taken", "next_steps", "confidence_level", "trace_id"]
            missing = [k for k in required_keys if k not in data]
            
            if not missing:
                print("\n✅ Verification SUCCESS: All required keys present.")
                return True
            else:
                print(f"\n❌ Verification FAILED: Missing keys: {missing}")
                return False
        else:
            print(f"❌ Verification FAILED: Server returned {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Verification FAILED: Connection error: {str(e)}")
        print("Make sure the server is running on localhost:8000")
        return False

if __name__ == "__main__":
    asyncio.run(verify_integration())
