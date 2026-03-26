"""Cost estimation helpers using the pricing matrix knowledge base."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_PRICING_PATH = Path(__file__).parents[6] / "knowledge_base" / "cost_templates" / "pricing_matrix.json"


def load_pricing_matrix() -> dict:
    """Load the pricing matrix from the knowledge base."""
    try:
        return json.loads(_PRICING_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("Could not load pricing matrix from %s", _PRICING_PATH)
        return {}


def estimate_cost(
    solution_type: str,
    company_size: str = "",
    budget_range: str = "",
    num_phases: int = 3,
) -> dict:
    """Estimate implementation and operational costs.

    Args:
        solution_type: One of "data_platform", "ml_platform", "cloud_migration".
        company_size: Company size description (used to determine scale).
        budget_range: Customer's stated budget range.
        num_phases: Number of implementation phases.

    Returns:
        Dict with cost breakdown suitable for ProposalOutput.cost_estimation.
    """
    pricing = load_pricing_matrix()
    if not pricing:
        return {"assumptions": ["Pricing matrix not available. Manual estimation required."]}

    # Determine scale from company size
    size_lower = company_size.lower()
    if any(x in size_lower for x in ["<50", "< 50", "dưới 50", "nhỏ", "small", "startup"]):
        scale = "small"
    elif any(x in size_lower for x in [">500", "> 500", "lớn", "large", "enterprise"]):
        scale = "large"
    else:
        scale = "medium"

    impl_key_map = {
        "data_platform": {"small": "data_platform_basic", "medium": "data_platform_full", "large": "data_platform_full"},
        "ml_platform": {"small": "ml_platform_pilot", "medium": "ml_platform_pilot", "large": "ml_platform_full"},
        "cloud_migration": {"small": "cloud_migration_small", "medium": "cloud_migration_small", "large": "cloud_migration_large"},
    }

    impl_services = pricing.get("implementation_services", {})
    impl_key = impl_key_map.get(solution_type, {}).get(scale)
    impl_info = impl_services.get(impl_key, {}) if impl_key else {}

    total_impl = impl_info.get("usd", 0)
    duration = impl_info.get("duration_months", num_phases * 2)

    # Monthly OpEx estimate
    infra = pricing.get("infrastructure", {})
    monthly_compute = infra.get("cloud_compute", {}).get(scale, {}).get("monthly_usd", 0)
    monthly_db = infra.get("managed_database", {}).get(f"postgresql_{scale}", {}).get("monthly_usd", 0)
    total_monthly_opex = monthly_compute + monthly_db

    # ROI benchmarks
    roi = pricing.get("roi_benchmarks", {}).get(solution_type, {})
    payback_months = roi.get("typical_payback_months", 18)

    # Phase breakdown (evenly split)
    phases_cost = []
    per_phase_impl = total_impl // num_phases if num_phases else total_impl
    for i in range(1, num_phases + 1):
        phases_cost.append({
            "phase": i,
            "name": f"Phase {i}",
            "setup_usd": per_phase_impl if i == 1 else 0,
            "monthly_usd": total_monthly_opex if i == num_phases else 0,
            "implementation_usd": per_phase_impl,
        })

    return {
        "phases": phases_cost,
        "total_implementation_usd": total_impl,
        "total_monthly_opex_usd": total_monthly_opex,
        "roi_payback_months": payback_months,
        "assumptions": [
            f"Scale: {scale} (based on company size: {company_size or 'unspecified'})",
            "Costs are estimates in USD, subject to vendor negotiation",
            "Does not include internal team costs",
            impl_info.get("description", ""),
        ],
    }
