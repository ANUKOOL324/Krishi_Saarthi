# KrishiSaarthi: System Architecture Diagram

This document contains the Mermaid diagram rendering the multi-agent system, communication flows, and Model Context Protocol (MCP) tool integration.

---

## Mermaid Diagram

```mermaid
graph TD
    %% Styling Classes
    classDef frontend fill:#E6F4EA,stroke:#137333,stroke-width:2px,color:#137333;
    classDef agent fill:#E8F0FE,stroke:#1A73E8,stroke-width:2px,color:#1A73E8;
    classDef mcp fill:#FFF4E5,stroke:#E27200,stroke-width:2px,color:#B06000;
    classDef data fill:#FCE8E6,stroke:#D93025,stroke-width:2px,color:#A51D24;

    %% Nodes
    User([Farmer / UI Client])
    Streamlit[Streamlit UI Dashboard]
    
    subgraph Multi-Agent Layer (Google ADK)
        Coord[Coordinator Agent]
        WeatherAgent[Weather Agent]
        CropAgent[Crop Suitability Agent]
        MarketAgent[Market Agent]
        SafetyAgent[Safety & Guardrails Agent]
        ReportAgent[Report Agent]
    end

    subgraph Tool Layer (FastMCP Server)
        get_weather[get_weather Tool]
        recommend_crop[recommend_crop Tool]
        get_mandi_price[get_mandi_price Tool]
    end

    subgraph Data & API Layer
        OM_API[Open-Meteo REST API]
        Crop_CSV[(crop_recommendation.csv)]
        Mandi_CSV[(mandi_prices.csv)]
    end

    %% Connections
    User -->|Enters soil parameters & city| Streamlit
    Streamlit -->|Launches run| Coord
    
    Coord -->|1. Request weather| WeatherAgent
    Coord -->|2. Request suitability| CropAgent
    Coord -->|3. Request mandi pricing| MarketAgent
    Coord -->|4. Audit safety| SafetyAgent
    Coord -->|5. Compile final plan| ReportAgent
    
    WeatherAgent -->|triggers| get_weather
    CropAgent -->|triggers| recommend_crop
    MarketAgent -->|triggers| get_mandi_price
    
    get_weather -->|HTTP GET| OM_API
    recommend_crop -->|KNN classification| Crop_CSV
    get_mandi_price -->|pandas query| Mandi_CSV
    
    ReportAgent -->|Markdown action plan| Streamlit
    Streamlit -->|Render dashboard| User

    %% Assign Styles
    class Streamlit frontend;
    class Coord,WeatherAgent,CropAgent,MarketAgent,SafetyAgent,ReportAgent agent;
    class get_weather,recommend_crop,get_mandi_price mcp;
    class OM_API,Crop_CSV,Mandi_CSV data;
```

---

## Component Specifications

1.  **Streamlit Dashboard**: Responsive, styled UI with NPK indicators, weather tabs, mandi tables, and progress loggers.
2.  **Coordinator Agent**: Sequential async engine written in Python that orchestrates execution, passing inputs from one agent's response to the next.
3.  **MCP Tools**: Exposes REST API calling, machine learning queries, and local pandas indexing to decoupling implementation details from agent planning.
4.  **Specialist Agents**: Modular LLM agents configured with custom instructions to focus on specific tasks (meteorology, agronomy, marketing, environmental safety, and technical reports).
