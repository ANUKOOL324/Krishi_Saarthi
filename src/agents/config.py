"""
Agent configuration — environment loading and model defaults.

Loads API keys from .env via python-dotenv and sets the default LLM model
identifier used by all ADK agents.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def check_config():
    if not os.environ.get("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY environment variable is not set. Please set it in a .env file or environment.", file=sys.stderr)
        return False
    return True

DEFAULT_MODEL = "gemini-2.5-flash"
