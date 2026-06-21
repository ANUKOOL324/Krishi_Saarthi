"""
Safety Agent — farming safety and environmental sustainability auditor.

Inspects the proposed weekly farm plan for pesticide overuse, unsustainable
crop choices in drought areas, and overconfident handling instructions.
Does not use external tools — operates purely on the compiled agent outputs.
"""

from google.adk.agents import LlmAgent
from src.agents.config import DEFAULT_MODEL

safety_agent = LlmAgent(
    name="safety_agent",
    model=DEFAULT_MODEL,
    instruction=(
        "You are a farming safety and environmental sustainability auditor. Your role is to inspect "
        "the proposed weekly farm plan and crop recommendations. Check for: \n"
        "1. Unsupported pesticide or chemical fertilizer suggestions.\n"
        "2. Unsustainable farming choices (e.g. water-intensive crops in drought areas).\n"
        "3. Overconfident claims or unsafe handling instructions.\n"
        "If you find issues, flag them clearly with warnings and recommend safer, organic, or "
        "sustainable alternatives. If the advice is safe, confirm it with a concise approval."
    )
)
