import asyncio
import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.llm_bridge import llm_bridge

async def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"Checking OPENAI_API_KEY: {'Found' if api_key else 'Missing'}")
    
    if not api_key:
        print("❌ Error: OPENAI_API_KEY is not set in .env file.")
        print("Please edit the .env file and add your OpenAI API Key.")
        return

    print("Attempting to connect to OpenAI...")
    try:
        # Force re-initialization if needed, though script run is fresh
        if not llm_bridge.openai_client:
             from openai import AsyncOpenAI
             llm_bridge.openai_client = AsyncOpenAI(api_key=api_key)

        response = await llm_bridge.call_llm(
            model="chatgpt",
            prompt="Hello, this is a connectivity test. Respond with 'Connection Successful'."
        )
        
        print("\n✅ Response from OpenAI:")
        print(response)
        
        if "Mock" in response:
            print("\n⚠️ Warning: Received a Mock response. This usually means the API call failed internally.")
        else:
            print("\n🎉 Success! OpenAI integration is working.")
            
    except Exception as e:
        print(f"\n❌ Connection Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_openai())
