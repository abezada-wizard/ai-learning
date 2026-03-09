import anthropic
from dotenv import load_dotenv
from tavily import TavilyClient
import os
from datetime import date

load_dotenv()

client = anthropic.Anthropic()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

tools = [
    {
        "name": "search_web",
        "description": "Busca información actualizada y real en internet",
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
    
    iteration = 0
    max_iterations = 3
    
    while iteration < max_iterations:
        iteration += 1
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=f"""Hoy es {date.today()}. Eres un asistente que busca información real y actualizada. IMPORTANTE: Máximo 2 búsquedas por pregunta. Con los resultados que tengas, genera la mejor respuesta posible.""",
            tools=tools,
            messages=messages
        )
        
        if response.stop_reason == "tool_use":
            tool_call = next(b for b in response.content if b.type == "tool_use")
            print(f"\n→ Buscando: '{tool_call.input['query']}'")
            
            results = tavily.search(query=tool_call.input["query"], max_results=3)
            search_content = "\n".join([
                f"- {r['title']}: {r['content'][:200]}" 
                for r in results["results"]
            ])
            
            print(f"→ {len(results['results'])} resultados encontrados, procesando...\n")
            
            messages.append({"role": "assistant", "content": response.content})
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": search_content
                }]
            })
            
        else:
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"Claude: {block.text}")
            break
        if iteration >= max_iterations:
            print("Claude: Alcancé el límite de búsquedas. Aquí lo que encontré hasta ahora.")
            

# Probamos con algo real
run_agent("¿Cuáles son las últimas noticias sobre P&G hoy?")