from os import stat
from langgraph.config import get_stream_writer

from app.agent.state import AgentState
from app.services.prompt_service import get_prompt
from app.agent.llm import stream_chat_completion


async def generate(state: AgentState) -> dict:
    system_prompt = get_prompt("system_prompt")
    context = state.get("retrieved_context", "")
    history = state.get("conversation_history", [])
    user_message = state.get("user_message")
    scope_message = state.get("scope")
    classification = state.get("classification", "")

    writer = get_stream_writer()

    system_content = f"{system_prompt}\nConversation Scope: {scope_message}\n\n--- Context ---\n{context}"

    if classification == "CONTACT_INCOMPLETE":
        missing = state.get("missing_contact_fields", [])
        contact_data = state.get("contact_data", {})
        contact_instruction = get_prompt("contact_collect_prompt")
        contact_instruction = contact_instruction.replace(
            "{missing_fields}", ", ".join(missing)
        )
        provided_summary = "; ".join(f"{k}: {v}" for k, v in contact_data.items() if v)
        contact_instruction = contact_instruction.replace(
            "{provided_fields}", provided_summary or "none"
        )
        system_content = f"{system_content}\n\n{contact_instruction}"

    messages = [{"role": "system", "content": system_content}]

    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})

    messages.append({"role": "user", "content": user_message})

    full_response = ""
    async for token in stream_chat_completion(messages):
        full_response += token
        writer({"type": "token", "data": token})

    writer({"type": "done"})

    # full_response is collected by the streaming handler in the chat route
    # We store the prepared messages in state so the route can stream them
    return {"full_response": full_response}
