"""State definitions for the Survey → Proposal multi-agent workflow."""

from typing import Annotated, Literal, NotRequired, TypedDict

from langgraph.graph import MessagesState


class SurveyData(TypedDict, total=False):
    """Structured data collected during the customer survey."""

    # Group 1: Organization info
    company_name: str
    industry: str
    company_size: str  # e.g. "50-200 employees"
    num_branches: str

    # Group 2: Technology landscape
    current_systems: list[str]  # ERP, CRM, BI tools in use
    infrastructure: str  # "on-premise" | "cloud" | "hybrid"
    annual_it_budget: str  # budget range

    # Group 3: Pain points & goals
    pain_points: list[str]
    goals: list[str]
    timeline: str  # desired implementation timeline

    # Group 4: Data & AI readiness (optional)
    data_sources: list[str]
    data_governance_level: str  # "none" | "basic" | "advanced"
    ai_ml_experience: str


def merge_survey_data(existing: SurveyData | None, new: SurveyData | None) -> SurveyData:
    """Reducer: merge survey data dicts so updates accumulate across turns."""
    if existing is None:
        return new or {}
    if new is None:
        return existing
    merged = dict(existing)
    for k, v in (new or {}).items():
        if v is not None:
            if isinstance(v, list) and isinstance(merged.get(k), list):
                # Deduplicate list fields
                merged[k] = list(dict.fromkeys(merged[k] + v))
            else:
                merged[k] = v
    return merged  # type: ignore[return-value]


class ProposalOutput(TypedDict, total=False):
    """Structured output from the Architect Agent."""

    executive_summary: str
    current_state_analysis: str
    solution_architecture: dict  # {mermaid_diagram, tech_stack, integration_points}
    implementation_roadmap: list  # [{phase, name, duration, tasks, deliverables}]
    cost_estimation: dict  # {phases, total, roi_payback_months}
    risks: list  # [{risk, level, probability, mitigation}]
    # File paths (virtual /mnt/user-data/outputs/ paths)
    docx_path: str
    diagram_png_path: str


class MultiAgentState(MessagesState):
    """Shared state for the Survey → Proposal workflow.

    Extends MessagesState so the LangGraph server's message accumulation
    (add_messages reducer) works correctly for conversation history.
    """

    # Survey Agent fields
    survey_data: Annotated[SurveyData, merge_survey_data]
    survey_status: Literal["not_started", "in_progress", "completed"]
    survey_completion_pct: float

    # Architect Agent fields
    proposal_status: NotRequired[Literal["pending", "generating", "done", "error"]]
    proposal_output: NotRequired[ProposalOutput | None]
