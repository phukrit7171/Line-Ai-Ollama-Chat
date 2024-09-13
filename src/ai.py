import ollama

system_instruct = """
You are a helpful and harmless AI assistant. Please answer the user's questions in a comprehensive and informative way, even if they are open ended, challenging, or strange. 
"""
model = "qwen2:1.5b-instruct-q2_K"

# Store chat histories per user in a dictionary
user_conversations = {}

def generate_response(user_id: str, prompt: str) -> str:
    """Generates a response using Ollama, maintaining separate chat histories per user.

    Args:
        user_id: A unique identifier for the user.
        prompt: The user's message.

    Returns:
        The AI's response.
    """
    if prompt == r'/clear':
        clear_chat_history(user_id)
        return 'Chat history cleared.'
    # Get the conversation history for this user, or create a new one
    conversation = user_conversations.get(user_id, [])

    # Add the system instruction to new conversations
    if not conversation:
        conversation.append({"role": "system", "content": system_instruct})

    # Add the user's message to the conversation
    conversation.append({"role": "user", "content": prompt})

    # Get the AI's response
    response = ollama.chat(model=model, messages=conversation)
    
    # Add the AI's response to the conversation
    conversation.append({"role": "assistant", "content": response["message"]["content"]})

    # Update the conversation history for this user
    user_conversations[user_id] = conversation
    # print(user_conversations)


    return response["message"]["content"]

def clear_chat_history(user_id: str):
    """Clears the chat history for a specific user.

    Args:
        user_id: The unique identifier for the user.
    """
    if user_id in user_conversations:
        del user_conversations[user_id]

