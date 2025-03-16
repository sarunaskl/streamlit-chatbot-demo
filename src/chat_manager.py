import os
from src.client import client

def get_response(messages, qa_chain=None):
    system_prompt = "Jūs esate naudingas asistentas, kuris visada atsako lietuvių kalba."
    
    if qa_chain:
        user_message = messages[-1]["content"]
        try:
            print(f"Attempting RAG with input: {{'query': '{user_message}'}}")
            response = qa_chain({"query": user_message})
            print("RAG succeeded")
            return response  # LLMChain returns a string directly
        except Exception as e:
            print(f"RAG error: {e}")
            raise
    else:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt}
            ] + [{"role": m["role"], "content": m["content"]} for m in messages],
            stream=True
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        return full_response