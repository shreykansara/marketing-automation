# Technical Documentation: Blostem Adaptive Intelligence Pipeline

This document provides a comprehensive, low-level technical breakdown of the Blostem platform architecture, services, and intelligence layers.

---

## 1. System Architecture Overview
The platform is built as an **adaptive control loop** for B2B sales automation. It ingests market signals, aggregates them into leads, converts leads to deals, and then applies a memory-aware decision engine to manage post-deal activation and re-engagement.

**Core Stack:**
- **Backend**: FastAPI (Python)
- **Database**: MongoDB Atlas
- **Frontend**: React (Vite)
- **Intelligence**: Rule-based adaptive logic with historical memory.

---

## 2. Backend Service Layer (`/backend/services`)

The core business logic is modularized into specialized services.

### 2.1 Deal Evaluation (`evaluation.py`)
**Primary Function**: `evaluate_deal_state(deal: Dict)`
- **Scope**: Single Deal.
- **Responsibility**: State Assessment ONLY.
- **Logic**:
    - Calculates **Health Status**: `Active`, `Stalled` (7+ days inactive), or `At Risk` (unresponsive stakeholders).
    - Computes **Urgency Score (0-100)**: Weighted based on Deal Value (20%), Signal Weight (30%), and Decay-adjusted Intent (50%).
    - Identifies **Risk Reason**: Standardized string describing why a deal is stalled or at risk.
- **Details**: Time-aware; uses `datetime.now(timezone.utc)` for accurate decay and stall calculations.

### 2.2 Adaptive Decision Engine (`decision_engine.py`)
**Primary Function**: `compute_decision(deal: Dict, evaluation_packet: Dict)`
- **Scope**: Single Deal.
- **Responsibility**: Adaptive Control Logic.
- **Historical Memory**: Consumes `deal['decision_history']` to ensure behavior follows past outcomes.
- **Key Rules**:
    1. **Engagement Suppression**: If a `replied` outcome exists within the last 7 days, suppresses all automation (`no_action`).
    2. **Intent-Aware Cooldown**: Prevents repeated outreach for the same intent within a 72-hour window (`delay_action`).
    3. **Failure-Based Escalation**: If 2+ attempts for a specific intent are `ignored`, pivots target to `senior_sales` (`escalate`).
    4. **Stalled Deadlock Detection**: If a deal is `Stalled` for 10+ days with no recent outreach (5 days), triggers `manual_queue` escalation.
- **Output**: Returns a decision packet containing `decision`, `action_intent`, `priority`, and a detailed `reasoning` string.

### 2.3 Activation & Outreach (`activation.py`, `outreach_engine.py`)
- **Activation Refinement**: `refine_activation_context(deal, decision_packet)`
    - Selects the optimal **Target Role** (CTO, CMO, etc.) and **Channel** (Email, LinkedIn, Direct Call) based on the intended action.
- **Outreach Execution**: `execute_outreach_generation(deal, activation_context)`
    - **Attempt Management**: Calculates `attempt_number` by scanning history.
    - **Message Generation**: Uses intent-based templates with dynamic variables from signals.
    - **Sequence Creation**: Generates a 2-step sequence (Day 0 and Day 2 follow-up).
    - **Memory Logging**: Atomically `$push`es a `pending` entry into `deals_collection.decision_history` and upserts to `outreach_sequences`.

### 2.4 Feedback & Learning (`feedback_loop.py`)
**Functions**:
- `process_interaction_feedback(deal_id, outcome, outreach_id)`: Maps external feedback (opened, replied, ignored) to standardized outcomes.
- `simulate_feedback_loop()`: Global utility to randomly process all `pending_delivery` sequences for demo purposes.
- **Impact**: When `replied` is received, it resets `last_activity` and marks all stakeholders as responded, clearing the `At Risk` status.

### 2.5 Signal & Lead Intelligence (`lead_engine.py`, `priority.py`)
- **Lead Generation**: `generate_leads()`
    - **Scope**: Global (All signals).
    - Groups signals by company, calculates `intent_score` (Count + Multi-source + Recency), and upserts to `leads`.
- **Global Prioritization**: `prioritize_deals(deals_list: List)`
    - **Scope**: Batch.
    - Ranks deals based on Status weight, Normalized Value, Action Confidence, and Activation Stage (Signed/Testing/Live).

---

## 3. Signal Engine (`/backend/services/signal_engine`)

The Signal Engine is a sophisticated ingestion pipeline for market intelligence.

### 3.1 Processor (`processor.py`)
- **Process Signal**: `process_signal(raw_item)`
    - Extracts company entities using regex/NLP.
    - Classifies signals into types (Funding, Leadership change, etc.).
    - Generates **SHA-256 Fingerprints** for strict deduplication.
- **Orchestrator**: `run_ingestion_pipeline_async()`
    - Concurrently fetches from all sources and runs the processing chain.

### 3.2 Ingestion & Scheduling
- **Fetchers (`ingestion/fetchers.py`)**: Supports `NewsAPI` (with retries and key redaction) and multi-source `RSS` feeds.
- **Scheduler (`scheduler.py`)**: Uses `APScheduler` to trigger the ingestion pipeline every 6 hours in a background thread.

---

## 4. Data Layer (`/backend/data/db.py`)

The system persists state across several MongoDB collections:
- **`deals`**: Core deal data, stakeholders, signals, and the critical `decision_history` (Memory).
- **`signals`**: De-duplicated market events with fingerprints.
- **`leads`**: Aggregated intent data per company.
- **`outreach_sequences`**: Generated messaging and delivery status.
- **`companies`**: Normalized company records.

---

## 5. API Interface (`/backend/routes`)

| Endpoint | Method | Purpose |
| :--- | :---: | :--- |
| `/api/deals` | GET | Returns all deals enriched with live evaluation and adaptive decisions. |
| `/api/deals/{id}/evaluate-and-trigger` | POST | Executes the full orchestrator: Eval -> Decide -> Activate -> Execute. |
| `/api/deals/auto-generate` | POST | Triggers the conversion pipeline (Leads -> Deals). |
| `/api/signals/ingest` | POST | Manually triggers the ingestion pipeline. |
| `/api/leads/generate` | POST | Aggregates raw signals into scored leads. |
| `/api/outreach/sequences` | GET | Lists all generated and pending outreach sequences. |

---

## 6. Frontend Architecture (`/frontend/src`)

The UI is built as a real-time command center for activation intelligence.

- **`App.jsx`**: Manages global state, deal selection, and "System Sync" orchestration.
- **`DealList.jsx`**: Sidebar component displaying prioritized deals with status chips and urgency scores.
- **`DecisionView.jsx`**: The "Intelligence Center". Renders the decision reasoning, risk assessment, and provides the "Trigger Evaluation" action button.
- **`HistoryTimeline.jsx`**: Visualizes the `decision_history` array, showing the progression of automation attempts and their outcomes.

---
*Documentation updated: 2026-04-17*
