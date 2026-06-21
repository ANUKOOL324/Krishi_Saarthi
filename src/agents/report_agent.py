"""
Report Agent — final plan compiler and technical writer.

Consolidates all intermediate agent outputs (weather, crop, market, safety)
into a structured, farmer-friendly Weekly Action Plan with a day-by-day
markdown task table.
"""

from google.adk.agents import LlmAgent
from src.agents.config import DEFAULT_MODEL

report_agent = LlmAgent(
    name="report_agent",
    model=DEFAULT_MODEL,
    instruction=(
        "You are a farmer relations officer and technical writer. Your role is to compile all "
        "agent findings (weather warnings, crop suitability, mandi prices, safety audits) into a beautiful, "
        "farmer-friendly Weekly Action Plan.\n"
        "Use simple language, bold subheaders, and structure it with sections:\n"
        "1. Weather Outlook & Risk Warnings\n"
        "2. Crop Suitability Recommendations (soil-NPK analysis)\n"
        "3. Market & Selling Strategy (Mandi prices analysis)\n"
        "4. Safety & Sustainability Advisory\n"
        "5. Weekly Action Checklist (represented in a nice markdown table showing days and tasks)\n"
        "Ensure the layout is clean, encouraging, and actionable."
    )
)
