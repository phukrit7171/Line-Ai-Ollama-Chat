import ollama


system_instruct = """
You are a helpful and harmless AI assistant. Please answer the user's questions in a comprehensive and informative way, even if they are open ended, challenging, or strange. 
"""
messages = [{"role": "system", "content": system_instruct}]
model = "qwen2:1.5b-instruct-q2_K"


def generate_response(prompt) -> str:
    messages.append({"role": "user", "content": prompt})
    response = ollama.chat(model=model, messages=messages)
    messages.append({"role": "assistant", "content": response["message"]["content"]})
    return response["message"]["content"]


# print(generate_response("Hi Bro"))
