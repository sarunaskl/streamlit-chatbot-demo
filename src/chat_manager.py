import os
from src.client import client

def get_response(messages, qa_chain=None):
    if qa_chain:
        user_message = messages[-1]["content"]
        try:
            response = qa_chain.invoke({"query": user_message})
            return response["result"]
        except Exception as e:
            print(f"RAG error: {e}")
            raise
    else:
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Jūs esate naudingas asistentas, kuris visada atsako lietuvių kalba."}
            ] + [{"role": m["role"], "content": m["content"]} for m in messages],
            stream=True
        )
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
        return full_response