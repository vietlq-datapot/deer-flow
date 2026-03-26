"""Multi-Agent POC: Survey → Proposal workflow.

Inspired by DeerFlow 2.0 SuperAgent Harness architecture.
Implements a 2-agent system:
  - Survey Agent: Collects customer IT/business information via Telegram
  - Architect Agent: Analyzes survey data and generates architecture proposal
"""

from deerflow.multi_agent.graph import make_survey_proposal_agent

__all__ = ["make_survey_proposal_agent"]
