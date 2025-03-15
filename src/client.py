from openai import OpenAI
import os
from dotenv import load_dotenv

# Load .env from the project root (parent of src/)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
secret_key = os.getenv("OPENAI_API_KEY")

if not secret_key:
    raise ValueError("Not found in .env")

print(f"Client: Loaded with token")  # Verify key

# Initialize OpenAI client matching your working setup
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),  # This is the default and can be omitted
)

# Test the client to catch auth issues early
try:
    test_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Test connection"}],
        max_tokens=10
    )
    print("Client auth test successful:", test_response.choices[0].message.content)
except Exception as e:
    raise ValueError(f"Client auth test failed: {e}")