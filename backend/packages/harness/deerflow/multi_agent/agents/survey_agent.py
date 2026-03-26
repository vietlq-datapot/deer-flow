"""Survey Agent — collects customer IT/business information via natural conversation."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from deerflow.multi_agent.state import MultiAgentState, SurveyData

logger = logging.getLogger(__name__)

_SKILLS_DIR = Path(__file__).parents[6] / "skills" / "survey" / "SKILL.md"

_SURVEY_SYSTEM_PROMPT = """Bạn là chuyên gia tư vấn Data & AI của KHantix. \
Nhiệm vụ của bạn là thu thập thông tin hiện trạng IT/Business của khách hàng \
qua hội thoại tự nhiên, thân thiện trên Telegram.

{skill_content}

## Dữ liệu đã thu thập cho đến nay:
{survey_data_json}

## Quy tắc trả lời:
- Tối đa 2 câu hỏi mỗi lượt (phù hợp Telegram)
- Acknowledge câu trả lời của khách trước khi hỏi tiếp
- Giọng điệu: thân thiện, ngắn gọn, rõ ràng
- Nếu câu trả lời mơ hồ → hỏi lại cụ thể hơn
- Khi đủ thông tin (completion >= 0.8) → tóm tắt và xác nhận trước khi kết thúc

## Trả lời BẮT BUỘC theo định dạng JSON trong block ```json ... ```:
{{
  "reply": "<tin nhắn gửi cho khách hàng>",
  "extracted_data": {{
    "<field_name>": "<value>"
  }},
  "completion_pct": <0.0 đến 1.0>,
  "is_complete": <true hoặc false>
}}

Các field hợp lệ trong extracted_data:
- company_name, industry, company_size, num_branches
- current_systems (list), infrastructure, annual_it_budget
- pain_points (list), goals (list), timeline
- data_sources (list), data_governance_level, ai_ml_experience
"""


def _load_skill_content() -> str:
    """Load the survey skill markdown content."""
    try:
        return _SKILLS_DIR.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Survey skill file not found at %s", _SKILLS_DIR)
        return "Thu thập thông tin tổ chức, hiện trạng công nghệ, pain points và goals của khách hàng."


def _extract_json_from_response(text: str) -> dict:
    """Extract JSON from LLM response, handling various formats."""
    # Try ```json ... ``` block first
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try raw JSON object
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    logger.warning("Could not extract JSON from survey agent response")
    return {
        "reply": text[:500] if text else "Xin chào! Hãy cho tôi biết tên công ty của bạn?",
        "extracted_data": {},
        "completion_pct": 0.0,
        "is_complete": False,
    }


def _build_greeting() -> dict:
    """Return the initial greeting when no messages exist."""
    return {
        "reply": (
            "Xin chào! Tôi là trợ lý tư vấn Data & AI của KHantix. 👋\n\n"
            "Tôi sẽ giúp bạn xây dựng một đề xuất giải pháp phù hợp với nhu cầu của công ty.\n\n"
            "Để bắt đầu, bạn có thể cho tôi biết:\n"
            "1. Tên công ty bạn đang làm việc là gì?\n"
            "2. Công ty hoạt động trong lĩnh vực nào?"
        ),
        "extracted_data": {},
        "completion_pct": 0.0,
        "is_complete": False,
    }


async def survey_agent_node(state: MultiAgentState, config: RunnableConfig) -> dict:
    """Survey agent node: conducts adaptive survey via natural conversation.

    Reads the latest user message, uses LLM to determine what to ask next
    (based on already-collected data), extracts any new data from the reply,
    and updates the shared state.
    """
    from deerflow.models import create_chat_model

    messages = state.get("messages", [])
    survey_data = state.get("survey_data") or {}
    survey_status = state.get("survey_status", "not_started")

    # Get last human message
    last_human_msg = ""
    for msg in reversed(messages):
        role = msg.get("role") if isinstance(msg, dict) else getattr(msg, "type", None)
        content = msg.get("content") if isinstance(msg, dict) else getattr(msg, "content", "")
        if role in ("human", "user"):
            last_human_msg = content if isinstance(content, str) else ""
            break

    # Initial greeting if no prior conversation
    if not last_human_msg and survey_status == "not_started":
        parsed = _build_greeting()
    else:
        skill_content = _load_skill_content()
        system_prompt = _SURVEY_SYSTEM_PROMPT.format(
            skill_content=skill_content,
            survey_data_json=json.dumps(survey_data, ensure_ascii=False, indent=2),
        )

        # Build message history for the LLM (last 10 messages to save context)
        history = []
        for msg in messages[-10:]:
            if isinstance(msg, dict):
                role = msg.get("role", msg.get("type", ""))
                content = msg.get("content", "")
            else:
                role = getattr(msg, "type", "")
                content = getattr(msg, "content", "")

            if role in ("human", "user"):
                history.append({"role": "user", "content": content})
            elif role in ("ai", "assistant"):
                if isinstance(content, str):
                    history.append({"role": "assistant", "content": content})

        llm = create_chat_model(thinking_enabled=False)
        llm_messages = [{"role": "system", "content": system_prompt}] + history

        try:
            response = await llm.ainvoke(llm_messages)
            response_text = response.content if isinstance(response.content, str) else str(response.content)
            parsed = _extract_json_from_response(response_text)
        except Exception:
            logger.exception("Survey agent LLM call failed")
            parsed = {
                "reply": "Xin lỗi, tôi gặp sự cố kỹ thuật. Bạn có thể thử lại không?",
                "extracted_data": {},
                "completion_pct": state.get("survey_completion_pct", 0.0),
                "is_complete": False,
            }

    # Build state updates
    reply_text = parsed.get("reply", "")
    extracted: SurveyData = parsed.get("extracted_data", {})
    completion_pct = float(parsed.get("completion_pct", 0.0))
    is_complete = bool(parsed.get("is_complete", False))

    new_status = "in_progress"
    if is_complete:
        new_status = "completed"
    elif survey_status == "not_started":
        new_status = "in_progress"
    else:
        new_status = survey_status

    logger.info(
        "[SurveyAgent] completion=%.0f%%, is_complete=%s, status=%s",
        completion_pct * 100,
        is_complete,
        new_status,
    )

    return {
        "messages": [AIMessage(content=reply_text)],
        "survey_data": extracted,
        "survey_status": new_status,
        "survey_completion_pct": completion_pct,
    }
