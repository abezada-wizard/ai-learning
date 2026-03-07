import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()

conversation_history = []

print("Chat con Claude (escribe 'salir' para terminar)\n")

while True:
    user_input = input("Vos: ")
    
    if user_input.lower() == "salir":
        break
    
    conversation_history.append({
        "role": "user",
        "content": user_input
    })
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system="Eres un asistente experto en AI Engineering. Respuestas cortas y directas.",
        messages=conversation_history
    )
    
    assistant_message = response.content[0].text
    
    conversation_history.append({
        "role": "assistant", 
        "content": assistant_message
    })
    
    print(f"\nClaude: {assistant_message}\n")