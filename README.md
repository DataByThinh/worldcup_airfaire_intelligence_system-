# ✈️ World Cup Airfare Intelligence System

**A production-grade data pipeline, ML prediction engine, and booking intelligence platform built for the 2026 FIFA World Cup**

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![React](https://img.shields.io/badge/React-Vite-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost-orange?style=flat-square)](https://xgboost.readthedocs.io)
[![Amadeus API](https://img.shields.io/badge/API-Amadeus-00439C?style=flat-square)](https://developers.amadeus.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)


</div>

> **What if you could predict airfare spikes before they happen — and tell travelers exactly when to book?**
>
> This system ingests real-time flight pricing data across multiple high-demand travel routes, processes it through a layered analytics pipeline, and delivers ML-driven booking recommendations through an interactive React dashboard.
> 
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/eac0dea5-cacf-4751-8f99-591c5643c507" />

## 🧠 What This System Does

The system answers three core business questions:

| Question | System Component |
|---|---|
| *What are flights costing right now?* | Real-time Amadeus ingestion pipeline |
| *How will prices change in the next 30 days?* | XGBoost fare prediction model |
| *Should I book now or wait?* | Rule-based + ML booking recommendation engine |

---

## 🏗️ Architecture

<img width="1500" height="850" alt="image" src="https://github.com/user-attachments/assets/e9706bdc-3422-4433-8b99-3e1fa0b440a3" />


## 🔄 Data Pipeline: Bronze → Silver → Gold

Built using a Bronze → Silver → Gold architecture inspired by modern analytics platforms.

🥉 **Bronze — Raw Ingestion**  
Stores append-only API responses with full historical traceability.

🥈 **Silver — Cleaned & Enriched**  
Standardizes fares, removes duplicates, and engineers booking intelligence features.

🥇 **Gold — Analytics & ML Ready**  
Delivers aggregated pricing metrics and optimized datasets powering the dashboard, recommendation engine, and ML models.

---

## 🤖 ML Model: Fare Prediction & Booking Intelligence

### Fare Prediction — XGBoost Regressor

Predicts airfare prices for a given route, airline, and departure window, then converts those predictions into traveler-facing booking recommendations.

**Feature set:**
- Days before departure
- Route
- Airline code
- Number of stops
- Departure date and month
- Flight duration
- Search date timing
- Historical route-level fare patterns

**Training approach:**
- Trained on collected airfare snapshots from the data pipeline
- Uses engineered time-based and route-based features
- Evaluated with regression metrics such as MAE and R²
- Generates predicted fare movement to support booking decisions

**Prediction outputs:**
- Estimated airfare price
- Route-level price trend
- Buy now vs. wait recommendation
- Cheaper alternative route signal

```text
Airfare Snapshots
        ↓
Feature Engineering
        ↓
XGBoost Regressor
        ↓
Fare Prediction
        ↓
Booking Recommendation
```


### Booking Recommendation Engine

Combines airfare predictions with route-level pricing signals to generate simple traveler-facing booking recommendations.

| Recommendation | Logic |
|---|---|
| **Book Now** | Current fare is relatively low and predicted prices are increasing |
| **Wait** | Current fare appears expensive and predicted prices remain stable or decline |
| **Monitor** | Price trend is unclear or route volatility is moderate |
| **Consider Alternative Route** | Similar nearby routes show lower predicted fares |

---

## 📊 Dashboard

Built with **React + Vite** to surface real-time airfare intelligence through interactive analytics and booking insights.

### Core Views

| View | Description |
|---|---|
| 🌍 **Route Explorer** | Compare live airfare trends across travel routes |
| 📈 **Fare Prediction** | Visualize projected airfare movement and pricing trends |
| 🧠 **Booking Signal** | ML-driven recommendation engine for booking decisions |
| 🔎 **Route Intelligence** | Discover lower-cost and alternative route options |

```text
Real-Time Flight Data
          ↓
Analytics Pipeline
          ↓
ML Prediction Engine
          ↓
Interactive React Dashboard
```

## 📁 Project Structure

```
worldcup-airfare-intelligence/
├── etl/
│   ├── ingest.py            # Amadeus API extraction
│   ├── transform.py         # Bronze → Silver transformation
│   └── run_pipeline.py      # Orchestration entrypoint
├── dbt/
│   ├── models/
│   │   ├── bronze/          # Raw source models
│   │   ├── silver/          # Cleaned + enriched
│   │   └── gold/            # Analytics aggregates
│   └── dbt_project.yml
├── ml/
│   ├── features.py          # Feature engineering from Gold layer
│   ├── train_model.py       # XGBoost training + tuning
│   ├── predict.py           # Inference interface
│   └── recommend.py         # Booking recommendation logic
├── api/
│   ├── main.py              # FastAPI app
│   └── routes/              # Endpoint definitions
├── frontend/
│   ├── src/
│   │   ├── components/      # Dashboard components
│   │   └── pages/           # Route explorer, heatmap, etc.
│   └── vite.config.js
├── sql/
│   └── init_schema.sql      # PostgreSQL schema
├── tests/
│   └── test_pipeline.py
├── docs/
│   ├── architecture_diagram.png   ← add this
│   ├── data_model.md
│   └── api_reference.md
├── .env.example
├── docker-compose.yml
└── README.md
```
---

## 👤 Author

**Thinh Nguyen**

Data Engineer/ Analytics Engineer/ Data Scientist

---

<div align="center">

*Built with ☕ and a lot of `pandas` DataFrames during the World Cup hype cycle.*

</div>

