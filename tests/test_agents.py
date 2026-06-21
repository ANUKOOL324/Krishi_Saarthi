import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agents.coordinator import run_krishi_saarthi_pipeline

async def mock_run_debug(self, prompt, *args, **kwargs):
    from google.adk.events import Event
    from google.genai import types
    
    p_lower = prompt.lower()
    if "weekly action plan" in p_lower or "final farmer-friendly" in p_lower:
        text = (
            "# KrishiSaarthi Farm Plan\n"
            "- Weather looks stable.\n"
            "- Crop recommended is Rice.\n"
            "- Mandi price is ₹2450.\n"
            "- Sustainability warning: Use safe pesticide rates."
        )
    elif "sustainability audit" in p_lower:
        text = "Mock Safety: Recommended operations approved. Caution advised with pesticide sprays."
    elif "suitability for soil" in p_lower:
        text = "Mock Crop: NPK matches Rice as primary recommendations. Cotton is secondary choice."
    elif "mandi prices" in p_lower:
        text = "Mock Market: Rice at Amritsar Mandi trading at ₹2450/quintal. Suggest selling next week."
    elif "weather forecast" in p_lower:
        text = "Mock Weather: 7 days of clear skies. Low risk of frost. Daily temperature range 20-32°C."
    else:
        text = "Mock default response."
        
    event = Event(
        author="agent",
        content=types.Content(parts=[types.Part(text=text)])
    )
    return [event]

@pytest.mark.asyncio
@patch("google.adk.runners.InMemoryRunner.run_debug", mock_run_debug)
async def test_coordinator_pipeline():
    test_inputs = {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "ph": 6.2,
        "location": "Amritsar",
        "state": "Punjab",
        "district": "Amritsar",
        "commodity": "rice"
    }
    
    results = await run_krishi_saarthi_pipeline(test_inputs)
    
    assert "weather_advice" in results
    assert "crop_advice" in results
    assert "market_advice" in results
    assert "safety_advice" in results
    assert "final_report" in results
    
    assert "Mock Weather" in results["weather_advice"]
    assert "Mock Crop" in results["crop_advice"]
    assert "Mock Market" in results["market_advice"]
    assert "Mock Safety" in results["safety_advice"]
    assert "# KrishiSaarthi Farm Plan" in results["final_report"]

class MockChoiceMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, content):
        self.message = MockChoiceMessage(content)

class MockLiteLLMResponse:
    def __init__(self, content):
        self.choices = [MockChoice(content)]

async def mock_acompletion(*args, **kwargs):
    messages = kwargs.get("messages", [])
    prompt = messages[-1]["content"] if messages else ""
    p_lower = prompt.lower()
    
    if "weekly action plan" in p_lower or "final farmer-friendly" in p_lower:
        text = (
            "# KrishiSaarthi Farm Plan (OpenRouter)\n"
            "- Weather looks stable.\n"
            "- Crop recommended is Rice.\n"
            "- Mandi price is ₹2450.\n"
            "- Sustainability warning: Use safe pesticide rates."
        )
    elif "safety and environmental" in p_lower or "sustainability audit" in p_lower:
        text = "Mock OpenRouter Safety: Recommended operations approved. Caution advised with pesticide sprays."
    elif "crop suitability" in p_lower or "suitability for soil" in p_lower or "crop recommendation" in p_lower:
        text = "Mock OpenRouter Crop: NPK matches Rice as primary recommendations. Cotton is secondary choice."
    elif "mandi prices" in p_lower:
        text = "Mock OpenRouter Market: Rice at Amritsar Mandi trading at ₹2450/quintal. Suggest selling next week."
    elif "weather forecast" in p_lower:
        text = "Mock OpenRouter Weather: 7 days of clear skies. Low risk of frost. Daily temperature range 20-32°C."
    else:
        text = "Mock OpenRouter default response."
        
    return MockLiteLLMResponse(text)

@pytest.mark.asyncio
@patch("litellm.acompletion", mock_acompletion)
@patch.dict(os.environ, {"OPENROUTER_API_KEY": "mock_key", "OPENROUTER_MODEL": "google/gemini-2.5-flash-lite:free"})
async def test_coordinator_pipeline_openrouter():
    test_inputs = {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "ph": 6.2,
        "location": "Amritsar",
        "state": "Punjab",
        "district": "Amritsar",
        "commodity": "rice"
    }
    
    results = await run_krishi_saarthi_pipeline(test_inputs, provider="openrouter")
    
    assert "weather_advice" in results
    assert "crop_advice" in results
    assert "market_advice" in results
    assert "safety_advice" in results
    assert "final_report" in results
    
    assert "Mock OpenRouter Weather" in results["weather_advice"]
    assert "Mock OpenRouter Crop" in results["crop_advice"]
    assert "Mock OpenRouter Market" in results["market_advice"]
    assert "Mock OpenRouter Safety" in results["safety_advice"]
    assert "# KrishiSaarthi Farm Plan (OpenRouter)" in results["final_report"]

@pytest.mark.asyncio
async def test_coordinator_pipeline_offline():
    test_inputs = {
        "N": 90.0,
        "P": 42.0,
        "K": 43.0,
        "ph": 6.2,
        "location": "Amritsar",
        "state": "Punjab",
        "district": "Amritsar",
        "commodity": "rice"
    }
    
    results = await run_krishi_saarthi_pipeline(test_inputs, provider="offline")
    
    assert "weather_advice" in results
    assert "crop_advice" in results
    assert "market_advice" in results
    assert "safety_advice" in results
    assert "final_report" in results
    
    assert "Weather Forecast for Amritsar" in results["weather_advice"]
    assert "Crop Suitability Details" in results["crop_advice"]
    assert "Latest Mandi Prices for Rice" in results["market_advice"]
    assert "APPROVED WITH SAFETY ADVISORIES" in results["safety_advice"]
    assert "# KrishiSaarthi Farm Plan" in results["final_report"]
