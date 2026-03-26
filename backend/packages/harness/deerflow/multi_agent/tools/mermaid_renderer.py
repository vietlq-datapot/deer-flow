"""Render Mermaid diagram code to PNG using mmdc CLI (optional)."""

from __future__ import annotations

import asyncio
import logging
import shutil
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_MMDC_TIMEOUT = 30  # seconds


async def render_mermaid_diagram(
    mermaid_code: str,
    outputs_dir: Path,
    company_name: str = "diagram",
) -> Path | None:
    """Render Mermaid diagram to PNG using mmdc CLI.

    Falls back gracefully if mmdc is not installed — returns None and
    the calling code should use the raw Mermaid code as fallback.

    Args:
        mermaid_code: Mermaid diagram source code (without ``` wrappers).
        outputs_dir: Directory to save the PNG file.
        company_name: Used for filename generation.

    Returns:
        Path to the generated PNG file, or None if rendering failed.
    """
    mmdc_path = shutil.which("mmdc") or shutil.which("mermaid")
    if not mmdc_path:
        logger.info("[MermaidRenderer] mmdc not found; skipping diagram rendering")
        return None

    safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in company_name)[:30]
    output_png = outputs_dir / f"architecture_{safe_name}.png"

    # Write mermaid source to a temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False, encoding="utf-8") as f:
        f.write(mermaid_code)
        tmp_input = Path(f.name)

    try:
        proc = await asyncio.create_subprocess_exec(
            mmdc_path,
            "-i", str(tmp_input),
            "-o", str(output_png),
            "-b", "white",
            "-w", "1200",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=_MMDC_TIMEOUT)
        except asyncio.TimeoutError:
            proc.kill()
            logger.warning("[MermaidRenderer] mmdc timed out after %ds", _MMDC_TIMEOUT)
            return None

        if proc.returncode != 0:
            logger.warning(
                "[MermaidRenderer] mmdc failed (exit=%d): %s",
                proc.returncode,
                stderr.decode(errors="replace")[:500],
            )
            return None

        if output_png.is_file():
            logger.info("[MermaidRenderer] Diagram rendered to %s", output_png)
            return output_png

        logger.warning("[MermaidRenderer] mmdc succeeded but output file missing: %s", output_png)
        return None
    except Exception:
        logger.exception("[MermaidRenderer] Unexpected error during rendering")
        return None
    finally:
        tmp_input.unlink(missing_ok=True)
