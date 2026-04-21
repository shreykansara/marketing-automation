# 🌸 Blostem Intelligence Platform

> **Transforming Market Noise into Strategic Sales Pipeline.**

Blostem is an end-to-end sales intelligence engine that automates the transition from raw market signals to active business deals. Built with a focus on speed, intelligence, and premium aesthetics, Blostem empowers sales teams to act on high-intent opportunities the moment they surface.

---

## ✨ Key Features

- **🚀 Automated Signal Ingestion**: Real-time monitoring of NewsAPI and RSS feeds for market-moving events.
- **🧠 AI Enrichment Pipeline**: Automated entity extraction and strategic classification using Groq-powered LLMs.
- **📊 Growth Command Dashboard**: A high-density, glassmorphic overview of market pulse and priority alerts.
- **🧩 Gmail Extension**: Seamlessly ingest emails and generate AI outreach drafts directly within the Gmail interface.
- **⚖️ Smart Prioritization**: Advanced scoring algorithms (70/30 weighted logs-to-signals) to identify high-urgency deals.
- **📧 Unified Communications**: Browser extension support for tracking email interactions, generating AI outreach drafts, and managing communication history with secure deletion workflows.
- **🛡️ Clean Architecture**: A centralized company-first registry ensuring data consistency across Leads and Deals.

---

## 🏗️ Repository Structure

```text
├── backend/            # FastAPI Application & Business Logic
│   ├── core/           # Database, LLM, and Logger configurations
│   ├── routes/         # Modular API endpoints (Signals, Leads, Deals, etc.)
│   ├── services/       # Core business logic (Aggregation, Processing)
│   └── tasks/          # Intelligence pipeline tasks
├── frontend/           # React SPA (Vite + Lucide React)
│   ├── public/         # Static assets
│   └── src/            # Components, Pages, and Styling
├── documentation.md    # Detailed technical system documentation
└── README.md           # Project overview and quick start
```

---

## 🛠️ Quick Start

### 1. Prerequisites
- **Python 3.9+**
- **Node.js 18+**
- **MongoDB Instance** (Local or Atlas)
- **API Keys**: NewsAPI, Groq (defined in `.env`)

### 2. Backend Setup
```bash
# Install dependencies from root
pip install -r requirements.txt

# Start the API server
uvicorn backend.main:app --reload
```
*API docs available at `http://localhost:8000/docs`.*

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Application available at `http://localhost:5173`.*

---

## 📘 Documentation

For deep-dives into the database schema, API specification, and **Browser Extension** installation, please refer to the [System Documentation](file:///c:/Users/mr_sh/My%20Drive/LPU/Blostem%20Hackathon/documentation.md).

---

## 🎨 Aesthetics & Design
Blostem features a custom **Dark-Blue Glassmorphic Design System**. Every interaction is smoothed with subtle micro-animations and vibrant accent colors (Success: Emerald, Warning: Amber, Danger: Rose) to ensure a premium, modern experience.

---
*Built for the Blostem Hackathon.*
