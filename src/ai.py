import ollama
import asyncio
import base64

system_instruct = r"""
Act as my best friends and Speak the same language as your conversation partner. Like to use emojis to express my emotions.
"""
models = [
    'llava-llama3:8b-v1.1-q4_0',
    'llava:13b',
    'bakllava:7b',
    'llava-phi3'
]
model = models[3]

# Store chat histories per user in a dictionary
user_conversations = {}

async def generate_response(user_id: str, prompt :str = "What do you see bro? 🤔", image_data=None) -> str:
    print('user id :',user_id,'prompt :', prompt)
    """Generates a response using Ollama, maintaining separate chat histories per user.

    Args:
        user_id: A unique identifier for the user.
        prompt: The user's message.
        image_data: Optional. Base64 encoded image data.

    Returns:
        The AI's response.
    """
    if '/clear' in prompt.lower():
        clear_chat_history(user_id)
        return 'Chat history cleared.'

    # Get the conversation history for this user, or create a new one
    conversation = user_conversations.get(user_id, [])

    # Add the system instruction to new conversations
    if not conversation:
        conversation.append({"role": "user", "content": system_instruct})
        pass

    # Add the user's message to the conversation
    if image_data:
        
        image_data = base64.b64encode(image_data).decode('utf-8') # convert to base64
        conversation.append({"role": "user", "content": prompt, "images": [image_data]})
    else:
        conversation.append({"role": "user", "content": prompt})

    # Get the AI's response
    response = await asyncio.to_thread(ollama.chat, model=model, messages=conversation)

    # Add the AI's response to the conversation
    conversation.append({"role": "assistant", "content": response["message"]["content"]})

    # Update the conversation history for this user
    user_conversations[user_id] = conversation

    return response["message"]["content"]

def clear_chat_history(user_id: str):
    """Clears the chat history for a specific user.

    Args:
        user_id: The unique identifier for the user.
    """
    if user_id in user_conversations:
        del user_conversations[user_id]
