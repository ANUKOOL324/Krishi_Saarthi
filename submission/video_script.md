# KrishiSaarthi: Presentation & Demo Video Script

**Title**: KrishiSaarthi - Farm risk and market planning dashboard  
**Target Duration**: 3 Minutes (180 Seconds)  
**Format**: Screen capture with voiceover  

---

## Act 1: The Problem & The Solution (0:00 - 0:30)
- **Visual**: Show the Streamlit home screen with the soil parameters sliders and the title.
- **Voiceover**:  
  "Hello Kaggle judges! Welcome to KrishiSaarthi, our project for the 'Agents for Good' track. Smallholder farmers operate in complex environments where operational data is highly fragmented. To plan their week, they must separately consult weather forecasts, check soil suitability, and track market APMC mandi prices. KrishiSaarthi unifies these sources into a safety-audited Weekly Farm Plan using a multi-agent orchestration framework built on the Google Agent Development Kit and Model Context Protocol."

---

## Act 2: Architecture & Tools (0:30 - 1:15)
- **Visual**: Slide showing the system architecture diagram, or show the docs/architecture.md file rendering in the IDE.
- **Voiceover**:  
  "Our architecture is designed to be highly modular. We use a Coordinator Agent to sequentially run five specialized agents: Weather, Crop, Market, Safety, and Report.  
  To keep our agents clean, we expose all database queries and API connections as Model Context Protocol (MCP) tools. Our tools include an Open-Meteo weather forecast tool, a K-Nearest Neighbors soil suitability classifier, and a regional market APMC query engine.  
  The system is designed with multiple layers of fallback resilience. If external REST APIs are offline or machine learning libraries fail to build, our tools fall back to seasonal climate generators and custom pure-Python mathematical KNN classification. For execution reliability, the system supports automatic fallback from Gemini mode to OpenRouter fallback, and eventually down to a local Offline demo mode."

---

## Act 3: Live Demo (1:15 - 2:30)
- **Visual**: Switch to the running Streamlit dashboard. Point to the Run Mode dropdown set to "Offline demo mode" and show the clean connection status message.
- **Voiceover**:  
  "Here is the farm planning dashboard. In the sidebar, we can select our Run Mode. The application supports Gemini mode, OpenRouter fallback, and Offline demo mode. For compliance and security, all API keys are loaded directly from the system environment or local .env file, meaning the main UI exposes no raw key input fields. For this run, we will use Offline demo mode.
  I'll configure our soil parameters, location, and primary crop of interest, and click the 'Generate Plan' button."
- **Visual**: Point to the Planning Process Status step list as the steps update to completed.
- **Voiceover**:  
  "Once triggered, the dashboard displays our visual process status board. The coordinator runs each agent in sequence: weather analysis, crop suitability check, market data query, safety review, and weekly plan compilation."
- **Visual**: Scroll down and walk through the compiled tabs (Weekly Farm Plan, Weather Risk, Crop Suitability, Market Note, Safety Note). Point to the disclaimer at the bottom.
- **Voiceover**:  
  "Here is the synthesized plan. The dashboard presents our Weekly Farm Plan, followed by detailed tabs for weather risks, soil recommendations, market trends, and safety checks. At the bottom, we provide a standard agricultural decision-support disclaimer. If a cloud API experiences quota limits, the dashboard will warn the user and attempt backup fallbacks automatically."

---

## Act 4: Impact & Safety (2:30 - 3:00)
- **Visual**: Highlight the Safety Note section in the report.
- **Voiceover**:  
  "To support agricultural best practices, our Safety Agent audits all recommendations to flag excessive chemical usage or unsustainable crops in drought-prone areas.  
  Looking ahead, we aim to extend the platform by adding voice inputs in regional Indian languages and connecting directly to low-cost soil hardware probes.  
  Thank you for your time, and we hope KrishiSaarthi helps farmers make better, safer decisions."
