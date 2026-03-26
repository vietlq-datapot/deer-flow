"""Architect Agent — analyzes survey data and generates architecture proposal."""

from __future__ import annotations

import json
import logging
import re
import uuid
from pathlib import Path

from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig

from deerflow.multi_agent.state import MultiAgentState, ProposalOutput

logger = logging.getLogger(__name__)

_SKILLS_DIR = Path(__file__).parents[6] / "skills" / "proposal" / "SKILL.md"
_KB_DIR = Path(__file__).parents[6] / "knowledge_base"

_ARCHITECT_SYSTEM_PROMPT = """Bạn là Solution Architect chuyên Data & AI của KHantix. \
Nhiệm vụ: phân tích dữ liệu khảo sát khách hàng và sinh proposal kiến trúc giải pháp chuyên nghiệp.

{skill_content}

## Dữ liệu Khảo sát Khách hàng:
{survey_data_json}

## Reference Architectures (Knowledge Base):
{knowledge_base_content}

## Yêu cầu Output:
Sinh proposal đầy đủ theo cấu trúc trong skill.
Architecture diagram BẮT BUỘC dùng Mermaid syntax.

Trả lời BẮT BUỘC theo định dạng JSON trong block ```json ... ```:
{{
  "executive_summary": "<1 đoạn 3-5 câu tóm tắt bài toán và giải pháp>",
  "current_state_analysis": "<phân tích hiện trạng từ survey data>",
  "solution_architecture": {{
    "mermaid_diagram": "<Mermaid diagram code, không có ```mermaid wrapper>",
    "tech_stack": [
      {{"component": "...", "technology": "...", "purpose": "..."}}
    ],
    "integration_points": ["<điểm tích hợp 1>", "<điểm tích hợp 2>"]
  }},
  "implementation_roadmap": [
    {{
      "phase": 1,
      "name": "...",
      "duration": "...",
      "objectives": "...",
      "tasks": ["task 1", "task 2"],
      "deliverables": ["deliverable 1"]
    }}
  ],
  "cost_estimation": {{
    "phases": [
      {{"phase": 1, "name": "...", "setup_usd": 0, "monthly_usd": 0, "implementation_usd": 0}}
    ],
    "total_implementation_usd": 0,
    "total_monthly_opex_usd": 0,
    "roi_payback_months": 0,
    "assumptions": ["assumption 1"]
  }},
  "risks": [
    {{"risk": "...", "level": "High|Medium|Low", "probability": "High|Medium|Low", "mitigation": "..."}}
  ]
}}
"""


def _load_skill_content() -> str:
    try:
        return _SKILLS_DIR.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning("Proposal skill not found at %s", _SKILLS_DIR)
        return "Sinh proposal kiến trúc giải pháp từ survey data."


def _load_knowledge_base(survey_data: dict) -> str:
    """Load relevant knowledge base sections based on survey context."""
    sections = []
    budget = survey_data.get("annual_it_budget", "").lower()
    systems = " ".join(survey_data.get("current_systems", [])).lower()
    goals = " ".join(survey_data.get("goals", [])).lower()
    infra = survey_data.get("infrastructure", "").lower()

    # Select relevant reference architectures
    candidates = {
        "data_platform": _KB_DIR / "reference_architectures" / "data_platform.md",
        "ai_ml_pipeline": _KB_DIR / "reference_architectures" / "ai_ml_pipeline.md",
        "cloud_migration": _KB_DIR / "reference_architectures" / "cloud_migration.md",
    }

    relevance = {
        "data_platform": any(kw in goals + systems for kw in ["data", "analytics", "report", "báo cáo", "dữ liệu", "bi"]),
        "ai_ml_pipeline": any(kw in goals for kw in ["ai", "ml", "dự báo", "tự động", "predict", "automate"]),
        "cloud_migration": "on-premise" in infra or "on-prem" in infra or any(kw in goals for kw in ["cloud", "migrate", "đám mây"]),
    }

    # Always include at least 1 reference; default to data_platform
    if not any(relevance.values()):
        relevance["data_platform"] = True

    for key, is_relevant in relevance.items():
        if is_relevant and candidates[key].exists():
            try:
                content = candidates[key].read_text(encoding="utf-8")
                sections.append(f"### {key.replace('_', ' ').title()}\n{content[:3000]}")
            except OSError:
                pass

    # Always include pricing matrix
    pricing_path = _KB_DIR / "cost_templates" / "pricing_matrix.json"
    if pricing_path.exists():
        try:
            pricing = json.loads(pricing_path.read_text(encoding="utf-8"))
            sections.append(f"### Pricing Matrix\n```json\n{json.dumps(pricing, indent=2)[:2000]}\n```")
        except (OSError, json.JSONDecodeError):
            pass

    return "\n\n---\n\n".join(sections) if sections else "No reference architecture loaded."


def _extract_json_from_response(text: str) -> dict | None:
    """Extract JSON from LLM response."""
    match = re.search(r"```json\s*([\s\S]*?)\s*```", text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


def _format_proposal_summary(proposal: dict, company_name: str) -> str:
    """Format a concise Telegram-friendly summary of the proposal."""
    summary_parts = [f"🎯 *Proposal đã sẵn sàng cho {company_name or 'quý công ty'}!*\n"]

    if exec_sum := proposal.get("executive_summary"):
        summary_parts.append(f"📋 *Tóm tắt:*\n{exec_sum[:400]}\n")

    tech_stack = proposal.get("solution_architecture", {}).get("tech_stack", [])
    if tech_stack:
        top_techs = [f"  • {t.get('technology', '')} ({t.get('component', '')})" for t in tech_stack[:5]]
        summary_parts.append("🏗️ *Tech Stack chính:*\n" + "\n".join(top_techs) + "\n")

    roadmap = proposal.get("implementation_roadmap", [])
    if roadmap:
        phases_text = "\n".join(f"  • Phase {p.get('phase')}: {p.get('name')} ({p.get('duration', '')})" for p in roadmap)
        summary_parts.append(f"🗺️ *Lộ trình:*\n{phases_text}\n")

    cost = proposal.get("cost_estimation", {})
    total_impl = cost.get("total_implementation_usd")
    monthly_opex = cost.get("total_monthly_opex_usd")
    payback = cost.get("roi_payback_months")
    if total_impl or monthly_opex:
        cost_parts = []
        if total_impl:
            cost_parts.append(f"  • Implementation: ~${total_impl:,}")
        if monthly_opex:
            cost_parts.append(f"  • Monthly OpEx: ~${monthly_opex:,}/tháng")
        if payback:
            cost_parts.append(f"  • Payback: ~{payback} tháng")
        summary_parts.append("💰 *Chi phí ước tính:*\n" + "\n".join(cost_parts) + "\n")

    summary_parts.append("📎 Xem file proposal đính kèm để có đầy đủ chi tiết.")
    return "\n".join(summary_parts)


async def architect_agent_node(state: MultiAgentState, config: RunnableConfig) -> dict:
    """Architect agent node: generates architecture proposal from survey data.

    Reads the completed survey_data, uses LLM with proposal skill + knowledge base
    to generate a structured proposal, creates a .docx file, and returns the result.
    """
    from deerflow.models import create_chat_model

    survey_data = state.get("survey_data") or {}
    company_name = survey_data.get("company_name", "Khách hàng")

    logger.info("[ArchitectAgent] Generating proposal for %s", company_name)

    skill_content = _load_skill_content()
    kb_content = _load_knowledge_base(survey_data)

    system_prompt = _ARCHITECT_SYSTEM_PROMPT.format(
        skill_content=skill_content,
        survey_data_json=json.dumps(survey_data, ensure_ascii=False, indent=2),
        knowledge_base_content=kb_content,
    )

    llm = create_chat_model(thinking_enabled=False)

    try:
        response = await llm.ainvoke([{"role": "system", "content": system_prompt}, {"role": "user", "content": "Hãy sinh proposal cho khách hàng này."}])
        response_text = response.content if isinstance(response.content, str) else str(response.content)
        proposal_data = _extract_json_from_response(response_text)
    except Exception:
        logger.exception("[ArchitectAgent] LLM call failed")
        proposal_data = None

    if not proposal_data:
        error_msg = (
            f"❌ Xin lỗi, tôi gặp sự cố khi sinh proposal cho {company_name}. "
            "Vui lòng thử lại hoặc liên hệ hỗ trợ."
        )
        return {
            "messages": [AIMessage(content=error_msg)],
            "proposal_status": "error",
        }

    # Generate output files
    thread_id = config.get("configurable", {}).get("thread_id", "")
    docx_virtual_path = None
    diagram_png_path = None

    try:
        from deerflow.multi_agent.tools.docx_generator import generate_proposal_docx
        from deerflow.multi_agent.tools.mermaid_renderer import render_mermaid_diagram

        if thread_id:
            from deerflow.config.paths import get_paths

            paths = get_paths()
            outputs_dir = paths.sandbox_outputs_dir(thread_id)
            outputs_dir.mkdir(parents=True, exist_ok=True)

            # Generate Mermaid diagram
            mermaid_code = proposal_data.get("solution_architecture", {}).get("mermaid_diagram", "")
            if mermaid_code:
                diagram_png_path = await render_mermaid_diagram(mermaid_code, outputs_dir, company_name)

            # Generate .docx
            docx_host_path = await generate_proposal_docx(proposal_data, outputs_dir, company_name, diagram_png_path)
            if docx_host_path:
                # Convert host path to virtual path for channel manager
                relative = docx_host_path.relative_to(paths.sandbox_user_data_dir(thread_id))
                docx_virtual_path = f"/mnt/user-data/{relative}"
    except Exception:
        logger.exception("[ArchitectAgent] File generation failed")

    # Build proposal output
    proposal_output: ProposalOutput = {**proposal_data}  # type: ignore[typeddict-item]
    if docx_virtual_path:
        proposal_output["docx_path"] = docx_virtual_path
    if diagram_png_path:
        proposal_output["diagram_png_path"] = str(diagram_png_path)

    # Build reply message
    summary_text = _format_proposal_summary(proposal_data, company_name)

    # Add present_files tool call so channel manager delivers the docx via Telegram
    ai_message_kwargs: dict = {"content": summary_text}
    if docx_virtual_path:
        ai_message_kwargs["tool_calls"] = [
            {
                "id": f"tc_{uuid.uuid4().hex[:8]}",
                "name": "present_files",
                "args": {"filepaths": [docx_virtual_path]},
            }
        ]

    return {
        "messages": [AIMessage(**ai_message_kwargs)],
        "proposal_status": "done",
        "proposal_output": proposal_output,
    }
