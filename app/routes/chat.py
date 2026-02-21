import time
from collections.abc import AsyncGenerator

import orjson
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.agent.graph import compiled_graph
from app.agent.llm import stream_chat_completion
from app.config import settings
from app.models.chat import ChatRequest
from app.models.jwt_payload import JWTPayload
from app.services.conversation_service import (
    append_message,
    get_active_messages,
    get_or_create_conversation,
    increment_messages_used,
)
from app.services.langsmith_tracer import get_trace_config
from app.services.jwt_service import set_jwt_cookie
from app.services.log_service import write_log
from app.services.rate_limit_service import (
    build_rate_limit_response,
    check_chat_rate_limit,
)
from app.utils.datetime_utils import get_reset_at, utc_today
from app.utils.ip import get_client_ip

router = APIRouter()


def _ndjson_line(data: dict) -> bytes:
    return orjson.dumps(data) + b"\n"


@router.post("/chat")
async def chat(body: ChatRequest, request: Request):
    start = time.monotonic()
    ip = get_client_ip(request)
    date = utc_today()
    scope = body.scope
    request_id = getattr(request.state, "request_id", "unknown")

    # Rate limit check
    allowed, used = await check_chat_rate_limit(ip, scope, date)
    if not allowed:
        rl = build_rate_limit_response(settings.CHAT_DAILY_LIMIT, used)
        content = orjson.dumps(rl.model_dump())
        return StreamingResponse(
            iter([content + b"\n"]),
            status_code=429,
            media_type="application/x-ndjson",
            headers={
                "X-Messages-Used": str(used),
                "X-Messages-Limit": str(settings.CHAT_DAILY_LIMIT),
                "X-Reset-At": get_reset_at(),
            },
        )

    # Conversation management
    conversation = await get_or_create_conversation(ip, scope, date)
    conversation_id = conversation["id"]
    new_used = await increment_messages_used(conversation_id)
    await append_message(conversation_id, "user", body.message)
    history = await get_active_messages(ip, scope, date)

    # Prepare graph input
    input_state = {
        "user_message": body.message,
        "scope": scope,
        "conversation_history": history[:-1],  # Exclude current message
        "ip": ip,
    }

    async def event_generator() -> AsyncGenerator[bytes, None]:
        classification = None
        full_response = ""

        # Run the graph to get classification and routing
        trace_config = get_trace_config(request_id, ip, scope)
        result = await compiled_graph.ainvoke(input_state, config=trace_config)
        classification = result.get("classification", "unknown")

        # If the graph produced a full_response (reject/contact), stream it
        if result.get("full_response"):
            full_response = result["full_response"]
            for i in range(0, len(full_response), 4):
                chunk = full_response[i : i + 4]
                yield _ndjson_line({"type": "token", "data": chunk})
        elif result.get("_messages"):
            # IN_DOMAIN path: stream from LLM
            messages = result["_messages"]
            async for token in stream_chat_completion(messages):
                full_response += token
                yield _ndjson_line({"type": "token", "data": token})

        async for event in compiled_graph.astream(input_state, stream_mode="custom"):
            yield _ndjson_line(event)

        # Post-stream: save assistant response and log
        if full_response:
            await append_message(conversation_id, "assistant", full_response)

        elapsed = (time.monotonic() - start) * 1000
        write_log(request_id, ip, scope, "ok", elapsed, classification)

    response = StreamingResponse(
        event_generator(),
        media_type="application/x-ndjson",
        headers={
            "X-Messages-Used": str(new_used),
            "X-Messages-Limit": str(settings.CHAT_DAILY_LIMIT),
            "X-Reset-At": get_reset_at(),
        },
    )

    payload = JWTPayload(ip=ip, scope=scope, messages_used=new_used, date=date)
    set_jwt_cookie(response, payload)

    return response
