from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
secret_key = os.getenv("GITHUB_TOKEN")

if not secret_key:
    raise ValueError("GITHUB_TOKEN not found in .env")

client = OpenAI(
    api_key=secret_key,
    base_url="https://models.inference.ai.azure.com"
)

try:
    test_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Test connection"}],
        max_tokens=10
    )
    print("Client auth test successful:", test_response.choices[0].message.content)
except Exception as e:
    raise ValueError(f"Client auth test failed: {e}")