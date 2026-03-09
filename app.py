from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from tavily import TavilyClient
import anthropic
import os
from datetime import date

load_dotenv()

app = Flask(__name__, static_folder='static')
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
    messages = [{"role": "user", "content": user_message}]
    iterations = 0
    searches = []

    while iterations < 3:
        iterations += 1
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=f"""Hoy es {date.today()}. Eres un asistente que busca información real y actualizada. IMPORTANTE: Máximo 2 búsquedas por pregunta. Con los resultados que tengas, genera la mejor respuesta posible.""",
            tools=tools,
            messages=messages
        )

        if response.stop_reason == "tool_use":
            tool_call = next(b for b in response.content if b.type == "tool_use")
            query = tool_call.input["query"]
            searches.append(query)

            results = tavily.search(query=query, max_results=3)
            search_content = "\n".join([
                f"- {r['title']}: {r['content'][:200]}"
                for r in results["results"]
            ])

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
            answer = ""
            for block in response.content:
                if hasattr(block, "text"):
                    answer = block.text
            return {"answer": answer, "searches": searches}

    return {"answer": "Alcancé el límite de búsquedas.", "searches": searches}

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    result = run_agent(data["message"])
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, port=5000)