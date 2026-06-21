# KrishiSaarthi: Final Architecture Audit

This document presents a final architectural self-audit and submission readiness verification for KrishiSaarthi: Farm risk and market planning dashboard for the Kaggle AI Agents Capstone Project.

---

## 1. Capstone Track Alignment
- **Selected Track**: "Agents for Good"
- **Alignment Description**: 
  Smallholder farmers manage over 80% of agricultural holdings in developing regions but face volatile climates, soil nutrient degradation, and daily price fluctuations at local wholesale markets (APMC Mandis). Coordinating these factors manually is a high-cognitive-load, error-prone task.
  **KrishiSaarthi** addresses this challenge by providing localized, structured agronomic and economic planning via a multi-agent system. It directly supports sustainable land stewardship (preventing chemical overruns) and protects smallholder livelihoods (optimizing market placement and crop selections), aligning with United Nations Sustainable Development Goals (SDG 2: Zero Hunger, SDG 12: Responsible Consumption and Production).

---

## 2. Key Concepts Demonstrated

### Multi-Agent Orchestration (ADK)
The core decision logic runs sequentially on the Google Agent Development Kit (ADK) using LlmAgent constructs and an InMemoryRunner executor. Agent context is chained dynamically by passing intermediate findings downstream.

### Model Context Protocol (MCP) Server
External APIs, machine learning models, and CSV databases are cleanly decoupled from the reasoning agents using the Model Context Protocol (MCP). A FastMCP server hosts and executes the tools, keeping the LLM core decoupled from data access details.

### Antigravity Usage
The workspace was designed, implemented, and validated utilizing Antigravity, demonstrating agent-assisted development, automated testing verification, and UI refactoring.

### Security Features
- Absolute sanitization: `.env` is ignored by Git, and no credentials are hardcoded.
- UI Safety: API keys are read securely from the host environment variables or local `.env` and are never displayed in the normal frontend UI, printed in logs, or written to reports.
- Safe developer-only overrides are hidden behind collapsed controls for test iterations under Technical Settings.

### Deployability
Decoupled into standard Streamlit frontend, FastMCP tool registry, and standard python library directories. The application runs seamlessly locally or inside cloud container services (e.g. Streamlit Community Cloud or Hugging Face Spaces).

### Skill-Style Documentation
All tools and agents have clean, concise docstrings acting as documentation of operational capabilities, enabling programmatic discovery by MCP coordinators.

### Offline Fallback Reliability
Layered reliability designs:
- *API Fallback*: Geocoding and Open-Meteo REST APIs fall back to regional coordinate lookups and seasonal weather forecasting.
- *ML Fallback*: K-Nearest Neighbors soil suitability model falls back to a pure-Python Euclidean distance calculator if `scikit-learn` is absent.
- *LLM Fallback*: If primary Gemini API key is missing or encounters a 429 quota exhaustion, coordinator seamlessly transitions to OpenRouter fallback, and eventually down to a local Offline demo mode which performs full analytical compilation without LLM queries.

---

## 3. Architecture Overview

```
[ User Input (Soil Metrics, Location, Crop) ]
                      |
                      v
          +-----------------------+
          |   Coordinator Agent   |  <--- Routes execution (Gemini / OpenRouter / Offline)
          +-----------+-----------+
                      |
  +-----------------+-----------------+-----------------+-----------------+
  |                 |                 |                 |                 |
  v                 v                 v                 v                 v
+-----------+     +-----------+     +-----------+     +-----------+     +-----------+
|  Weather  |     |   Crop    |     |  Market   |     |  Safety   |     |  Report   |
|   Agent   |     |   Agent   |     |   Agent   |     |   Agent   |     |   Agent   |
+-----+-----+     +-----+-----+     +-----+-----+     +-----+-----+     +-----+-----+
      |                 |                 |                 |                 |
      | (MCP)           | (MCP)           | (MCP)           | (Audit)         | (Compile)
      v                 v                 v                 v                 v
+-----------+     +-----------+     +-----------+     +-----------+     +-----------+
|get_weather|     | recommend |     | get_mandi |     |Guardrails |     |Weekly Farm|
|   Tool    |     | _crop Tool|     | _price    |     |  Auditor  |     |Action Plan|
+-----------+     +-----------+     +-----------+     +-----------+     +-----------+
```

1. **Streamlit UI**: Allows inputs of soil NPK readings, pH, and local cities.
2. **Coordinator**: Executes 5 specialist agents in sequence.
3. **LLM Provider Tier**: Can run in **Gemini mode** (primary), **OpenRouter fallback** (LiteLLM secondary), or **Offline demo mode** (fully local).

---

## 4. MCP Tools Audit
The project includes 3 distinct tools exposed via FastMCP:
1. **`get_weather(location, days)`**: Resolves location coordinates and fetches forecast summaries. Falls back to synthetic regional weather generation.
2. **`recommend_crop(N, P, K, temperature, humidity, ph, rainfall)`**: Classifies soil metrics via KNN to suggest crops. Falls back to pure-math Python classification.
3. **`get_mandi_price(commodity, state, district)`**: Queries historical market averages. Employs district, state, and commodity-wide fallback loops with fuzzy crop name alias resolving.

---

## 5. Agents Audit
1. **Coordinator Agent**: Sequentially invokes and chains context between all agents.
2. **Weather Agent**: Assesses meteorology alerts for crop/soil hazards.
3. **Crop Agent**: Recommends crops and details soil nutrition needs.
4. **Market Agent**: Reviews APMC Mandi rates and suggests optimal sales strategies.
5. **Safety Agent**: Audits recommendations against chemical over-application and sustainability rules.
6. **Report Agent**: Compiles intermediate agent advices into the final Weekly Farm Plan.

---

## 6. Security Checklist
- [x] `.env` is ignored by `.gitignore`.
- [x] `.env.example` template exists.
- [x] API key input fields are hidden from normal Streamlit UI (configured vs missing status is displayed).
- [x] API keys are never printed, logged, or recorded in report outputs.
- [x] Weekly Farm Plan report outputs contain agricultural disclaimer and safety advisory notes.

---

## 7. Validation & Testing
- Command run: `python -m pytest`
- **Status**: PASSING
- **Test Count**: 8 tests passed cleanly.
- Tests mock ADK `InMemoryRunner` and LiteLLM completions, verifying the coordinator routes modes safely.

---

## 8. Submission Assets Audit
- [x] `README.md` is updated and complete.
- [x] `docs/architecture.png` diagram exists.
- [x] `docs/architecture.md` diagram details exist.
- [x] `submission/kaggle_writeup_draft.md` writeup exists.
- [x] `submission/video_script.md` presentation script exists.
- [x] `submission/demo_checklist.md` verification checklist exists.
- [x] `docs/screenshots/` folder contains required screenshots:
  - `home_ui.png` (Landing Page)
  - `agent_trace.png` (Agent Trace status section)
  - `final_report.png` (Generated Weekly Plan)
  - `test_results.png` (Passing Pytest terminal)

---

## 9. Final Self-Recommendation

**READY FOR KAGGLE SUBMISSION**
