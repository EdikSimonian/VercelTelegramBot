import json
from bot.clients import ai
from bot.config import MODEL, SYSTEM_PROMPT, BRAVE_API_KEY
from bot.history import get_history, save_history

# Tool definition — only active when BRAVE_API_KEY is set
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information, recent news, or facts you are unsure about.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"}
                },
                "required": ["query"],
            },
        },
    }
] if BRAVE_API_KEY else []


def ask_ai(user_id: int, user_message: str) -> str:
    history = get_history(user_id)
    history.append({"role": "user", "content": user_message})

    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    kwargs = {"model": MODEL, "messages": messages}
    if TOOLS:
        kwargs["tools"] = TOOLS
        kwargs["tool_choice"] = "auto"

    response = ai.chat.completions.create(**kwargs)
    message = response.choices[0].message

    # If the AI called the search tool, execute it and get a final response
    if message.tool_calls:
        from bot.search import web_search

        tool_call = message.tool_calls[0]
        query = json.loads(tool_call.function.arguments)["query"]

        try:
            search_results = web_search(query)
        except Exception as e:
            search_results = f"Search failed: {e}"

        # Build the follow-up conversation including the tool result
        followup = messages + [
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                ],
            },
            {"role": "tool", "tool_call_id": tool_call.id, "content": search_results},
        ]

        final = ai.chat.completions.create(model=MODEL, messages=followup)
        reply = final.choices[0].message.content
    else:
        reply = message.content

    history.append({"role": "assistant", "content": reply})
    save_history(user_id, history)
    return reply
