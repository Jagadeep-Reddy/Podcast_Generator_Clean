import os
from dotenv import load_dotenv
import sys

# Force reload of environment
os.environ.pop("GROQ_API_KEY", None)
load_dotenv(override=True)

key = os.getenv("GROQ_API_KEY")

print(f"Python Executable: {sys.executable}")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Environment File Exists: {os.path.exists('.env')}")

if key:
    print(f"Key found: '{key}'")
    print(f"Key length: {len(key)}")
    print(f"Key starts with 'gsk_': {key.startswith('gsk_')}")
    
    # Check for hidden characters
    print(f"Key repr: {repr(key)}")
    
    from groq import Groq
    try:
        client = Groq(api_key=key.strip()) # Try stripping just in case
        print("Attempting API call...")
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        print("SUCCESS: API call worked with stripped key.")
    except Exception as e:
        print(f"ERROR: API call failed: {e}")

else:
    print("ERROR: GROQ_API_KEY not found in environment.")
