# Kaggle AI Agents Capstone Project: KrishiSaarthi Writeup

**Project Title**: KrishiSaarthi: Farm risk and market planning dashboard  
**Track**: Agents for Good  
**Author**: Anukool  

---

## 1. Abstract & Problem Statement

Smallholder farmers face fragmented decision-making channels. They must independently consult weather forecasts (to avoid frost or rain washouts), test soil chemistry (to select appropriate crops), and monitor regional market pricing (APMC Mandis) to make profitable sales. Coordinating these sources is complex, often leading to sub-optimal crop selections, low market returns, and environmental soil degradation due to excessive chemical application.

**KrishiSaarthi** solves this by unifying weather hazards, soil-NPK chemical matching, and mandi prices into a safety-audited **Weekly Farm Plan** using a multi-agent orchestration framework.

---

## 2. Solution Overview & Technical Innovation

KrishiSaarthi is built using a modern, decoupled architecture:
1.  **Google Agent Development Kit (ADK)**: Manages agent reasoning loops, instructions, memory, and programmatic session executions.
2.  **Model Context Protocol (MCP)**: Implements tool separations via a FastMCP server, allowing agents to interface with REST APIs, machine learning engines, and local databases via a unified tool protocol.
3.  **Resilience & Reliability Fallbacks**:
    - **Dual-Mode KNN Classifier**: Recommends crops using a K-Nearest Neighbors classifier on standardized NPK soil and climate parameters. If ML dependencies are missing or fail to build, a custom pure-Python mathematical KNN runs automatically.
    - **API Fallbacks**: If the geocoding or Open-Meteo forecast API is offline, the weather module synthesizes realistic local seasonal climates to prevent application crashes during field use.
    - **Multi-Mode LLM Providers & Fallbacks**:
      - *Gemini mode*: Primary official execution mode.
      - *OpenRouter fallback*: Uses LiteLLM to query OpenRouter models, serving as an automatic fallback if Gemini triggers 429 quota exhaustion.
      - *Offline demo mode*: A local simulation compiling weather forecasts, KNN crop suitability, and mandi prices CSV data deterministically into farm plans without querying any external LLM.
4.  **Credential Safety & Secrets Management**:
    - *Environment Ingestion*: All API keys are loaded via `.env` or system environment variables, keeping credentials entirely out of the repository codebase (enforced by `.gitignore`).
    - *UI Protection*: The normal Streamlit user interface hides raw text fields for API keys, verifying connection status dynamically from environment settings. Temporary developer overrides are hidden inside collapsed expanders, ensuring zero risk of credential exposure during public demos or video captures.

---

## 3. Multi-Agent Architecture & Coordination Flow

The coordination uses a sequential, contextual routing pipeline managed by a **Coordinator Agent** inside `src/agents/coordinator.py`:

```
[Soil Inputs, Location, Crop Interest]
                |
                v
       +-----------------+
       |   Coordinator   |
       +--------+--------+
                |
                +---> Weather Agent (Examines weather alerts/risks)
                |
                +---> Crop Agent (Matches NPK chemistry to crop needs)
                |
                +---> Market Agent (Queries APMC Mandi rates & selling spots)
                |
                +---> Safety Agent (Audits recommendations for conservation & safety)
                |
                +---> Report Agent (Compiles everything into a Markdown weekly table)
```

### Agent Roles:
- **Weather Agent**: Calls `get_weather` tool. Identifies weather warnings (frost, storm, drought).
- **Crop Agent**: Calls `recommend_crop` tool. Explains the chemistry behind NPK matching.
- **Market Agent**: Calls `get_mandi_price` tool. Analyzes modal pricing to advise on crop sales.
- **Safety Agent**: Audits the plan to flag water-intensive crops in drought regions or unsafe pesticide recommendations.
- **Report Agent**: Combines findings into a tabular Monday-to-Sunday action plan.

---

## 4. Evaluation & Test Results

The system includes a dedicated `pytest` suite validating both tools and agent coordination logic:
1.  `test_tools.py` checks geocoding parameters, crop suitability classifications, mandi alias resolving (e.g. "paddy" to "rice"), and fallback engines.
2.  `test_agents.py` mocks the ADK `InMemoryRunner` and LiteLLM completions to test the coordinator pipeline under Gemini ADK, OpenRouter, and Offline modes without spending API credits or making external network requests.
**Validation Results**: All 8 tests pass cleanly.

---

## 5. Alignment with "Agents for Good" & Future Scope

### Social Impact

India has approximately **146 million smallholder farm holdings** (source: Agriculture Census of India, 2015-16), and over 80% of the country's arable land is managed by families farming less than 2 hectares. These farmers currently navigate a fragmented ecosystem:

| Challenge | Current State | With KrishiSaarthi |
|-----------|--------------|---------------------|
| Weather planning | Manual weather app checks, no hazard mapping | Automated 7-day forecast with agricultural hazard alerts |
| Crop selection | Trial-and-error or word of mouth | Data-driven NPK/pH soil matching via ML classifier |
| Market pricing | Travel to Mandi or call brokers | Instant multi-market APMC price comparison with selling strategy |
| Safety auditing | None (chemical overuse is common) | Dedicated safety agent flags pesticide, water, and soil risks |

By consolidating these decisions into a single weekly plan, KrishiSaarthi reduces the information gap that contributes to post-harvest and pre-harvest crop losses. The Safety Agent directly addresses the environmental cost of unchecked chemical farming — India accounts for a disproportionate share of global pesticide poisoning incidents relative to its pesticide consumption volume (source: WHO Pesticide Poisoning Report, 2020).

### Future Scope
- **Multilingual Support**: Integrating translation engines and speech-to-text tools to allow farmers to input soil readings and receive plans in regional Indian languages (Hindi, Punjabi, Kannada, Marathi).
- **IoT Sensor Integrations**: Connecting the Streamlit front-end directly to affordable soil moisture and NPK hardware sensors for real-time field data collection.
- **Predictive Market Modeling**: Moving from historical APMC averages to seasonal crop supply trend forecasting.
