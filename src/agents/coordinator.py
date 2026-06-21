"""
Coordinator — the central orchestration pipeline for KrishiSaarthi.

Manages three execution paths:
  1. Gemini mode: Uses Google ADK's InMemoryRunner to execute specialist agents.
  2. OpenRouter mode: Replicates agent instructions as LiteLLM system prompts
     (duplicated because ADK agents cannot be directly used with LiteLLM).
  3. Offline mode: Runs the full pipeline deterministically without any LLM calls.

Each path produces the same output dict with keys: weather_advice, crop_advice,
market_advice, safety_advice, and final_report.
"""

import asyncio
import os
from datetime import datetime
import litellm
from google.adk.runners import InMemoryRunner

from src.agents.weather_agent import weather_agent
from src.agents.crop_agent import crop_agent
from src.agents.market_agent import market_agent
from src.agents.safety_agent import safety_agent
from src.agents.report_agent import report_agent

from src.agents.crop_agent import recommend_suitable_crop
from src.utils.weather_api import format_weather_message, get_weather_forecast
from src.utils.mandi_query import format_mandi_price_message, get_mandi_price_data

async def _execute_agent(runner: InMemoryRunner, prompt: str) -> str:
    events = await runner.run_debug(prompt, quiet=True)
    for event in reversed(events):
        if event.is_final_response() and event.content and event.content.parts:
            text = "".join([part.text for part in event.content.parts if part.text])
            if text.strip():
                return text
    return "No response received."

async def run_openrouter_pipeline(inputs: dict) -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing.")
        
    model_name = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.5-flash-lite:free")
    if not (model_name.startswith("openrouter/") or model_name.startswith("openai/")):
        model_name = f"openrouter/{model_name}"

    results = {}

    weather_instruction = getattr(weather_agent, "instruction", "") or (
        "You are an agricultural meteorology expert. Your role is to fetch weather forecast "
        "data for the farmer's location, analyze it for hazards (such as high heat, unexpected rain, "
        "or sudden frost), and provide actionable, weather-informed recommendations for crop care "
        "and field preparation for the upcoming week. Focus on highlighting warnings."
    )
    
    crop_instruction = getattr(crop_agent, "instruction", "") or (
        "You are an agronomy and crop suitability specialist. Your role is to analyze the farmer's "
        "soil metrics (N, P, K, pH) and average weather conditions, call your crop recommendation tool "
        "to see which crops fit the profile, and explain to the farmer WHY these crops are suitable. "
        "Explain the nutritional and soil chemistry requirements for the top suggestions."
    )
    
    market_instruction = getattr(market_agent, "instruction", "") or (
        "You are an agricultural market analyst. Your role is to query mandi (market) prices "
        "for the crops of interest, analyze the price variations across regional markets, "
        "and advise the farmer on when/where to sell their produce for maximum profit. Highlight "
        "current price ranges (minimum, maximum, modal) and date records."
    )
    
    safety_instruction = getattr(safety_agent, "instruction", "") or (
        "You are a farming safety and environmental sustainability auditor. Your role is to inspect "
        "the proposed weekly farm plan and crop recommendations. Check for: \n"
        "1. Unsupported pesticide or chemical fertilizer suggestions.\n"
        "2. Unsustainable farming choices (e.g. water-intensive crops in drought areas).\n"
        "3. Overconfident claims or unsafe handling instructions.\n"
        "If you find issues, flag them clearly with warnings and recommend safer, organic, or "
        "sustainable alternatives. If the advice is safe, confirm it with a concise approval."
    )
    
    report_instruction = getattr(report_agent, "instruction", "") or (
        "You are an agricultural planner. Compile all findings into a structured Weekly Farm Plan.\n"
        "Structure the report with these exact sections:\n"
        "1. Summary\n"
        "2. Weather risk\n"
        "3. Crop suitability\n"
        "4. Market note\n"
        "5. Safety note\n"
        "6. Weekly action plan (a markdown table mapping days to tasks)\n"
        "Keep the tone concise, factual, and direct."
    )

    async def _completion(system: str, prompt: str) -> str:
        response = await litellm.acompletion(
            model=model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            api_key=api_key,
            api_base="https://openrouter.ai/api/v1",
            timeout=35.0
        )
        return response.choices[0].message.content or "No response received."

    print("[Planner] Running weather analysis...")
    weather_data = format_weather_message(inputs["location"], 7)
    weather_prompt = (
        f"Weekly weather forecast for location '{inputs['location']}':\n\n"
        f"{weather_data}\n\n"
        f"Analyze the forecast for agricultural risks, warnings, and prepare a weekly weather briefing."
    )
    results["weather_advice"] = await _completion(weather_instruction, weather_prompt)

    temp = inputs.get("temperature", 28.0)
    hum = inputs.get("humidity", 70.0)
    rain = inputs.get("rainfall", 100.0)

    print("[Planner] Running crop suitability check...")
    crop_data = recommend_suitable_crop(inputs["N"], inputs["P"], inputs["K"], temp, hum, inputs["ph"], rain)
    crop_prompt = (
        f"Crop recommendation tool output for soil parameters (N={inputs['N']}, P={inputs['P']}, K={inputs['K']}, pH={inputs['ph']}) "
        f"and weather (Temp={temp}°C, Humidity={hum}%, Rainfall={rain}mm):\n\n"
        f"{crop_data}\n\n"
        f"Recommend matching crops and explain the agronomic reasoning."
    )
    results["crop_advice"] = await _completion(crop_instruction, crop_prompt)

    print("[Planner] Running market price lookup...")
    crop_target = inputs.get("commodity") or "rice"
    state = inputs.get("state", "")
    district = inputs.get("district", "")
    mandi_data = format_mandi_price_message(crop_target, state, district)
    market_prompt = (
        f"Latest Mandi prices for commodity '{crop_target}' in state '{state}', district '{district}':\n\n"
        f"{mandi_data}\n\n"
        f"Outline the pricing range and advice on profitable selling hubs or timings."
    )
    results["market_advice"] = await _completion(market_instruction, market_prompt)

    print("[Planner] Running safety check...")
    safety_prompt = (
        f"Perform a safety and environmental sustainability audit on the compiled advice:\n\n"
        f"--- WEATHER BRIEFING ---\n{results['weather_advice']}\n\n"
        f"--- CROP RECOMMENDATIONS ---\n{results['crop_advice']}\n\n"
        f"--- MARKET PRICING ---\n{results['market_advice']}\n\n"
        f"Identify pesticide overuses, water conservation issues, or overconfident farming suggestions."
    )
    results["safety_advice"] = await _completion(safety_instruction, safety_prompt)

    print("[Planner] Synthesizing report...")
    report_prompt = (
        f"Compile the final Weekly Farm Plan using these outputs:\n\n"
        f"Soil: N={inputs['N']}, P={inputs['P']}, K={inputs['K']}, pH={inputs['ph']}\n"
        f"Weather Advice:\n{results['weather_advice']}\n\n"
        f"Crop Advice:\n{results['crop_advice']}\n\n"
        f"Market Advice:\n{results['market_advice']}\n\n"
        f"Safety Advice:\n{results['safety_advice']}\n\n"
        f"Synthesize the report with the sections: Summary, Weather risk, Crop suitability, Market note, Safety note, and Weekly action plan."
    )
    results["final_report"] = await _completion(report_instruction, report_prompt)

    return results

async def run_offline_pipeline(inputs: dict) -> dict:
    results = {}
    
    location = inputs.get("location", "Amritsar")
    forecast = get_weather_forecast(location, 7)
    weather_info = format_weather_message(location, 7)
    
    has_rain = any(d["rain"] > 0 for d in forecast["days"])
    rain_days = []
    for d in forecast["days"]:
        if d["rain"] > 0:
            date_obj = datetime.strptime(d["date"], "%Y-%m-%d")
            rain_days.append(date_obj.strftime("%A"))
            
    if has_rain:
        weather_summary = (
            f"**Actionable Weather Advice**:\n"
            f"- Rain is expected on: {', '.join(rain_days)}.\n"
            f"- **Hazards**: High soil runoff. Do not apply chemical spray or top-dress urea right before these days.\n"
            f"- **Field Preparation**: Clear drainage channels immediately to prevent waterlogging around root zones."
        )
    else:
        weather_summary = (
            f"**Actionable Weather Advice**:\n"
            f"- No significant rainfall is predicted for the next 7 days.\n"
            f"- **Hazards**: None expected. Warm and dry weather dominates.\n"
            f"- **Field Preparation**: Excellent window for seed sowing, dry tillage, and weed removal. Ensure base irrigation is scheduled."
        )
    results["weather_advice"] = f"{weather_info}\n\n{weather_summary}"
    
    temp = inputs.get("temperature", 28.0)
    hum = inputs.get("humidity", 70.0)
    rain = inputs.get("rainfall", 100.0)
    
    crop_recs = recommend_suitable_crop(inputs["N"], inputs["P"], inputs["K"], temp, hum, inputs["ph"], rain)
    crop_advice = (
        f"### Crop Suitability Details\n"
        f"Based on soil tests: Nitrogen={inputs['N']} kg/ha, Phosphorus={inputs['P']} kg/ha, Potassium={inputs['K']} kg/ha, pH={inputs['ph']}\n\n"
        f"**Model Suggestions**:\n{crop_recs}\n\n"
        f"**Agronomic Breakdown**:\n"
        f"- Nitrogen level is {'adequate' if inputs['N'] > 70 else 'deficient'} for typical cereal crops. "
        f"{'Apply nitrogen in split doses to minimize losses.' if inputs['N'] <= 70 else 'Limit urea application to prevent excessive vegetative growth.'}\n"
        f"- Soil pH of {inputs['ph']} is in the {'ideal slightly-acidic' if 6.0 <= inputs['ph'] <= 7.0 else 'moderate'} range, ensuring high nutrient availability for root absorption."
    )
    results["crop_advice"] = crop_advice
    
    crop_target = inputs.get("commodity") or "rice"
    state = inputs.get("state", "")
    district = inputs.get("district", "")
    mandi_info = format_mandi_price_message(crop_target, state, district)
    records = get_mandi_price_data(crop_target, state, district)
    
    if records:
        modal_price = records[0]["modal_price"]
        market_summary = (
            f"**Market Strategy Analysis**:\n"
            f"- Current modal price at the local Mandi is **₹{modal_price}/Quintal**.\n"
            f"- **Strategy**: Selling at the current modal rate offers reasonable returns. If the market experiences a temporary dip, store the grain in dry hermetic storage to avoid distress sales and wait for peak seasonal demand."
        )
    else:
        market_summary = (
            f"**Market Strategy Analysis**:\n"
            f"- No active Mandi records found for '{crop_target}' in {district}, {state}.\n"
            f"- **Strategy**: Contact regional wholesale distributors or nearby Farmer Producer Organizations (FPOs) for market-linked crop aggregation. Keep track of state-level minimum support prices (MSP)."
        )
    results["market_advice"] = f"{mandi_info}\n\n{market_summary}"
    
    safety_advice = (
        f"### Safety and Environmental Sustainability Report\n"
        f"**Verdict**: APPROVED WITH SAFETY ADVISORIES\n\n"
        f"1. **Pesticide Safety**: If spraying is necessary, utilize green-labeled bio-pesticides first. Ensure operators use protective masks and gloves.\n"
        f"2. **Water Resource Stewardship**: {'Expected rainfall reduces reliance on groundwater. Capture rainwater where possible.' if has_rain else 'Rely on precise irrigation schedules. Drip or furrow irrigation is highly recommended to save water.'}\n"
        f"3. **Chemical Overuse Warnings**: Soil Nitrogen is high ({inputs['N']} kg/ha). Over-fertilization runs the risk of groundwater nitrate contamination. Limit mineral fertilizer inputs."
    )
    results["safety_advice"] = safety_advice
    
    checklist_table = [
        "| Day | Weather Forecast | Recommended Farm Operation |",
        "| :--- | :--- | :--- |"
    ]
    for d in forecast["days"]:
        date_obj = datetime.strptime(d["date"], "%Y-%m-%d")
        day_name = date_obj.strftime("%A")
        rain_val = d["rain"]
        
        if rain_val > 0:
            cond = f"Rain ({rain_val}mm)"
            op = "Clear blockages in drainage lines. Suspend spraying operations. Monitor soil moisture."
        else:
            cond = "Sunny / Dry"
            op = f"Ideal weather for fertilizer top-dressing, weeding, and preparing storage for {crop_target.capitalize()}."
        checklist_table.append(f"| {day_name} | {cond} | {op} |")
        
    table_str = "\n".join(checklist_table)
    
    final_report = f"""# KrishiSaarthi Farm Plan
 
## Summary
Weekly farm plan tailored for {location} ({state}) generated from soil metrics, weather forecast, and mandi database queries.
 
## Weather risk
{weather_summary}
 
## Crop suitability
- Crop of interest: {crop_target.capitalize()}
- Soil parameters: N={inputs['N']} kg/ha, P={inputs['P']} kg/ha, K={inputs['K']} kg/ha, pH={inputs['ph']}
- Model recommendation matches suitability criteria for {crop_target.capitalize()}.
 
## Market note
{market_summary}
 
## Safety note
- Soil chemistry status: Nitrogen levels are managed.
- Sustainability status: Local precise irrigation advised. No chemical spraying during rainfall window.
 
## Weekly action plan
{table_str}
"""
    results["final_report"] = final_report
    return results

async def run_krishi_saarthi_pipeline(inputs: dict, provider: str = "gemini") -> dict:
    provider_clean = provider.lower().strip()
    if provider_clean == "offline":
        print("[Planner] Running offline analysis...")
        return await run_offline_pipeline(inputs)
    elif provider_clean == "openrouter":
        print("[Planner] Running cloud backup analysis...")
        return await run_openrouter_pipeline(inputs)
    
    print("[Planner] Running weather analysis...")
    results = {}
    weather_runner = InMemoryRunner(agent=weather_agent)
    weather_prompt = (
        f"Fetch the weather forecast for location '{inputs['location']}' for 7 days. "
        f"Analyze the forecast for agricultural risks, warnings, and prepare a weekly weather briefing."
    )
    results["weather_advice"] = await _execute_agent(weather_runner, weather_prompt)
    print("Weather analysis completed.")
    
    temp = inputs.get("temperature", 28.0)
    hum = inputs.get("humidity", 70.0)
    rain = inputs.get("rainfall", 100.0)
    
    print("[Planner] Running crop suitability check...")
    crop_runner = InMemoryRunner(agent=crop_agent)
    crop_prompt = (
        f"Analyze crop suitability for soil inputs: N={inputs['N']}, P={inputs['P']}, K={inputs['K']}, pH={inputs['ph']}. "
        f"The anticipated environment parameters are: average temperature={temp}°C, humidity={hum}%, and rainfall={rain}mm. "
        f"Recommend matching crops and explain the agronomic reasoning."
    )
    results["crop_advice"] = await _execute_agent(crop_runner, crop_prompt)
    print("Crop suitability check completed.")
    
    print("[Planner] Running market price lookup...")
    market_runner = InMemoryRunner(agent=market_agent)
    crop_target = inputs.get("commodity") or "rice"
    
    market_prompt = (
        f"Fetch and analyze current Mandi prices for the commodity '{crop_target}' "
        f"in State: '{inputs.get('state', '')}', District: '{inputs.get('district', '')}'. "
        f"Outline the pricing range and advice on profitable selling hubs or timings."
    )
    results["market_advice"] = await _execute_agent(market_runner, market_prompt)
    print("Market price lookup completed.")
    
    print("[Planner] Running safety check...")
    safety_runner = InMemoryRunner(agent=safety_agent)
    safety_prompt = (
        f"Perform a safety and environmental sustainability audit on the compiled advice:\n\n"
        f"--- WEATHER BRIEFING ---\n{results['weather_advice']}\n\n"
        f"--- CROP RECOMMENDATIONS ---\n{results['crop_advice']}\n\n"
        f"--- MARKET PRICING ---\n{results['market_advice']}\n\n"
        f"Identify pesticide overuses, water conservation issues, or overconfident farming suggestions."
    )
    results["safety_advice"] = await _execute_agent(safety_runner, safety_prompt)
    print("Safety check completed.")
    
    print("[Planner] Synthesizing report...")
    report_runner = InMemoryRunner(agent=report_agent)
    report_prompt = (
        f"Compile the final Weekly Farm Plan using these outputs:\n\n"
        f"Soil: N={inputs['N']}, P={inputs['P']}, K={inputs['K']}, pH={inputs['ph']}\n"
        f"Weather Advice:\n{results['weather_advice']}\n\n"
        f"Crop Advice:\n{results['crop_advice']}\n\n"
        f"Market Advice:\n{results['market_advice']}\n\n"
        f"Safety Advice:\n{results['safety_advice']}\n\n"
        f"Synthesize the report with the sections: Summary, Weather risk, Crop suitability, Market note, Safety note, Weekly action plan, and Disclaimer."
    )
    results["final_report"] = await _execute_agent(report_runner, report_prompt)
    print("Report synthesis completed.")
    
    return results

if __name__ == "__main__":
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

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
    
    async def main():
        print("Testing coordinator workflow...")
        try:
            res = await run_krishi_saarthi_pipeline(test_inputs, provider="offline")
            print("Final Report:\n", res["final_report"][:500])
        except Exception as e:
            print("Error running coordinator pipeline:", e)
            
    asyncio.run(main())
