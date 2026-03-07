import anthropic
from dotenv import load_dotenv
import json

load_dotenv()

client = anthropic.Anthropic()

# Definimos una herramienta falsa de búsqueda (sin API real por ahora)
def search_web(query: str) -> str:
    # Simulamos resultados - después conectamos búsqueda real
    return f"Resultados simulados para '{query}': El mercado de AI Engineers en LATAM creció 40% en 2025, salario promedio $95K/año."

# Le decimos al modelo qué herramientas tiene disponibles
tools = [
    {
        "name": "search_web",
        "description": "Busca información actualizada en internet sobre cualquier tema",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "La búsqueda a realizar"
                }
            },
            "required": ["query"]
        }
    }
]

def run_agent(user_message: str):
    print(f"\nUsuario: {user_message}")
    
    messages = [{"role": "user", "content": user_message}]
    
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        tools=tools,
        system=f"Hoy es {__import__('datetime').date.today()}. Cuando busques información, usa siempre el año actual.",
        messages=messages
    )
    
    # El modelo decide si usar la herramienta o no
    if response.stop_reason == "tool_use":
        tool_call = next(b for b in response.content if b.type == "tool_use")
        print(f"\n→ El modelo decidió buscar: '{tool_call.input['query']}'")
        
        # Ejecutamos la herramienta
        result = search_web(tool_call.input["query"])
        print(f"→ Resultado obtenido, procesando...\n")
        
        # Le devolvemos el resultado al modelo
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_call.id,
                "content": result
            }]
        })
        
        # El modelo genera la respuesta final
        final_response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            tools=tools,
            messages=messages
        )
        for block in final_response.content:
            if hasattr(block, "text"):
                print(f"Claude: {block.text}")
    else:
        print(f"Claude: {response.content[0].text}")

# Probamos
run_agent("¿Cuánto gana un AI Engineer en LATAM?")
run_agent("¿Cuál es la capital de Francia?")