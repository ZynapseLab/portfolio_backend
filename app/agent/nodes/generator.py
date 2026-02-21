from langgraph.config import get_stream_writer

from app.agent.state import AgentState
from app.services.prompt_service import get_prompt
from app.agent.llm import stream_chat_completion


async def generate(state: AgentState) -> dict:
    system_prompt = get_prompt("system_prompt")
    context = state.get("retrieved_context", "")
    history = state.get("conversation_history", [])
    user_message = state["user_message"]

    writer = get_stream_writer()

    messages = [
        {
            "role": "system",
            "content": f"{system_prompt}\n\n--- Context ---\n{context}",
        }
    ]

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})

    full_response = ""
    async for token in stream_chat_completion(messages):
        full_response += token
        writer({"type": "token", "data": token})

    # full_response is collected by the streaming handler in the chat route
    # We store the prepared messages in state so the route can stream them
    return {"full_response": full_response}
