"""LangGraph state machine for the Survey → Proposal multi-agent workflow.

This module implements the Orchestrator (Lead Agent in DeerFlow terminology)
that coordinates the Survey Agent and Architect Agent in sequence:

    User messages → Survey Agent (collect data) → [complete?]
                                                      │
                                           ┌──────────┘
                                           ▼
                                    Architect Agent (generate proposal)
                                           │
                                           ▼
                                          END
"""

from __future__ import annotations

import logging

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph

from deerflow.multi_agent.agents.architect_agent import architect_agent_node
from deerflow.multi_agent.agents.survey_agent import survey_agent_node
from deerflow.multi_agent.state import MultiAgentState

logger = logging.getLogger(__name__)


def _route_after_survey(state: MultiAgentState) -> str:
    """Routing logic after the Survey Agent runs.

    - If survey is complete → hand off to Architect Agent immediately.
    - Otherwise → END (return the question to user and wait for next message).
    """
    survey_status = state.get("survey_status", "not_started")
    proposal_status = state.get("proposal_status", "pending")

    if survey_status == "completed" and proposal_status not in ("done", "generating"):
        logger.info("[Orchestrator] Survey complete → routing to architect_agent")
        return "architect_agent"

    logger.info("[Orchestrator] Survey in progress (status=%s) → END (waiting for user)", survey_status)
    return END


def _route_after_architect(state: MultiAgentState) -> str:
    """Routing logic after the Architect Agent runs.

    Always ends the graph after proposal generation.
    """
    return END


def make_survey_proposal_agent(config: RunnableConfig):
    """Factory function for the Survey → Proposal LangGraph workflow.

    This is the entry point registered in langgraph.json. The LangGraph
    server calls this factory per request to create a compiled graph.

    The graph persists state across user messages using the checkpointer
    configured in langgraph.json (async SQLite), keyed by thread_id so
    each Telegram conversation has its own isolated survey session.

    Args:
        config: LangGraph RunnableConfig (passed by the server at runtime).

    Returns:
        Compiled LangGraph StateGraph.
    """
    graph = StateGraph(MultiAgentState)

    # Nodes
    graph.add_node("survey_agent", survey_agent_node)
    graph.add_node("architect_agent", architect_agent_node)

    # Entry point: always start with Survey Agent
    graph.set_entry_point("survey_agent")

    # Conditional routing after Survey Agent
    graph.add_conditional_edges(
        "survey_agent",
        _route_after_survey,
        {
            "architect_agent": "architect_agent",
            END: END,
        },
    )

    # Architect Agent always ends
    graph.add_conditional_edges(
        "architect_agent",
        _route_after_architect,
        {END: END},
    )

    compiled = graph.compile()
    logger.info("[Orchestrator] survey_proposal_agent graph compiled successfully")
    return compiled
