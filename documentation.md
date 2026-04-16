# Technical Documentation: Blostem Pipeline Intelligence System

This document provides a line-by-line technical breakdown and behavioral summary of each module within the robust Blostem Pipeline Intelligence platform. The system operates as a data-driven triad: ingesting market signals, transforming them into scored leads, and automatically converting qualified leads into pipeline deals.

## Table of Contents
1. [Architecture and Database](#architecture-and-database)
2. [Backend Modules](#backend-modules)
   - [Database Layer (`data/`)](#database-layer)
   - [Services Layer (`services/`)](#services-layer)
   - [API Routes (`routes/`)](#api-routes)
   - [Core Aggregator (`main.py`)](#core-aggregator)
3. [Frontend Modules](#frontend-modules)
   - [App.jsx (3-Column Funnel)](#appjsx-3-column-funnel)
   - [NextBestAction.jsx (Insight Pane)](#nextbestactionjsx-insight-pane)
   - [index.css](#indexcss)

---

## Architecture and Database

The platform runs on a **FastAPI** Python backend coupled with a **React (Vite)** frontend. 

For data persistence, the system natively integrates with **MongoDB Atlas** (cloud-hosted MongoDB). The database (`pipeline_db`) actively manages three collections:
1. `signals`: Raw external market ingestion payloads (funding, hiring, or product announcements).
2. `leads`: Grouped and scored signals, identifying intent bounds on a per-company basis.
3. `deals`: Officially qualified sales opportunities featuring stakeholder activation mapping.

Authentication and configuration are securely loaded into the system environment dynamically using standard `.env` schemas mapping the `MONGO_URI`.

---

## Backend Modules

The backend architecture strictly decouples logic into independent processing services communicating via lightweight generic models, eliminating monolithic routing bloat.

### Database Layer

#### `data/db.py`
**Purpose:** Serves as the global singleton connection node to the MongoDB Atlas cluster.
* Uses `python-dotenv` natively calling `load_dotenv()` to pull `MONGO_URI` securely.
* Bootstraps the `MongoClient` and exports strict collection variables: `deals_collection`, `signals_collection`, and `leads_collection` mapping to the backend namespaces.

#### `data/mock_data.py` / `seed_db.py`
**Purpose:** Bootstrapping utilities to safely populate the Atlas `deals` cluster for development fallback testing using structured test-driven dictionaries.

### Services Layer

The `services/` directory contains all pipeline lifecycle transformation mathematics perfectly separated into stages.

#### `services/ingestion.py`
**Purpose:** Generates structured dummy market behavior models dynamically pushing raw records into the system.
* `run_ingestion()`: Flushes randomly generated lists of payloads mimicking `TechCrunch` and `LinkedIn` events directly into MongoDB `signals_collection`. Maps fields safely such as `signal_type` ("funding", "hiring").

#### `services/lead_engine.py`
**Purpose:** Intermediate transformation unit parsing scattered signals and aggregating them structurally into discrete `leads`.
* `generate_leads()`: Scans all stored signals, grouping by `company`. It mathematically generates an `intent_score` dynamically capped at `100` constructed via logic parameters:
  * *(Total unique signals * 10)* + *(Distinct signal types * 15)* + *(Recency degradation curve assigning 20 points if under 2 days old)*.
* Employs native `upsert=True` flags during MongoDB execution targeting `leads_collection` explicitly.

#### `services/conversion.py`
**Purpose:** Fully automates the bottom-of-the-funnel pipeline by extracting high-value targets natively out of the `leads_collection`.
* `convert_leads_to_deals()`: Evaluates the cluster using strict logic requiring `intent_score >= 60`. It enforces strong deduplication checking verifying the target company isn't already inside the `deals` database, and finally maps successful criteria directly to a clean Deal dictionary payload structured cleanly with generic placeholder `stakeholders` mapped to native pipeline schemas.

#### `services/evaluation.py` & `services/activation.py` & `services/actions.py` & `services/priority.py`
**Purpose:** Legacy intelligence hooks mapped directly to tracking active `deals` health. 
* `evaluation.py`: Maps generic logic bounding `status` strings determining "High Priority", "Active", or "Stalled" boundaries dynamically based upon lack of responses.
* `actions.py`: Binds "Next Best Action" string recommendations calculating distinct confidence scoring variables assigning explicit instructions natively back to the output model dynamically mapping AI predictions.
* `priority.py`: Sorting matrix safely returning mathematical precedence back to the table renderer.

### API Routes

The REST framework partitions the distinct data nodes securely preventing overlap constraints via FastAPI `APIRouter()` logic bounded under `/api/`.

#### `routes/signals.py`
* `GET /api/signals`: Plucks and yields raw extraction models mathematically sorted vertically by timestamp.
* `POST /api/signals/ingest`: Instantiated manual webhook manually spinning the `ingestion.py` core on demand.

#### `routes/leads.py`
* `GET /api/leads`: Distributes scored lead aggregations vertically ordered by native `intent_score` mathematical priorities.
* `POST /api/leads/generate`: Calls out the `lead_engine.py` clustering node.

#### `routes/deals.py`
* `GET /api/deals`: Maps standard deal structures injecting fallback evaluations natively over `evaluate_deal()` without explicitly disrupting stored databases gracefully structuring presentation variables natively.
* `POST /api/deals/auto-generate`: Validating payload running the conversion service filtering and appending deals optimally safely isolating overlaps.
* `POST /api/deals/{id}/action`: Simple simulation parameter resetting activity thresholds securely modifying MongoDB parameters verifying mitigation sequences natively.

### Core Aggregator

#### `main.py`
**Purpose:** Execution bounds loading all generic parameters hooking `CORS` limits opening `allow_origins` strictly wrapping routers natively loading configurations on Uvicorn dynamically opening active listening nodes over `8000`.

---

## Frontend Modules

The frontend operates using React + Vite. The dashboard acts as a visual translation of the complete multi-stage pipeline flow pushing immediate visual boundaries separating elements strictly mathematically aligning formatting safely tracking `Promise.all` logic cleanly scaling metrics exactly rendering UI grids properly natively.

### `App.jsx` (3-Column Funnel)
**Purpose:** Primary single-page web rendering block. The dashboard is bisected structurally into a Flow visualization upper-pane, and a detailed Inspector lower-pane tightly tracking API state parameters.
* **Network Binding**: Executes `Promise.all` loading the triplet data models natively caching `signals`, `leads`, and `deals` asynchronously maintaining synchronization without overlap.
* **Layout Grid Engine (`.flow-container`)**: Eliminates classic table layouts prioritizing a 3-column flow mapping the journey logically:
  - **Column 1 (`Signals`)**: Fast-flowing metric cards binding chronological raw timestamps.
  - **Column 2 (`Leads`)**: Ranked aggregations highlighting thresholds `intent_score >= 60` safely bounding CSS border modifications organically natively showing structural weight.
  - **Column 3 (`Deals`)**: Output structured business endpoints mapping nested `action` instructions vertically tracking "Stalled" overrides via natively assigned highlight tags tracking strict boundaries smoothly binding mathematical confidence tags explicitly.
* **Trigger Modals**: Renders generation buttons actively waiting asynchronous requests hitting POST paths dynamically firing refresh logic gracefully resetting output lists accurately.

### `NextBestAction.jsx` (Insight Pane)
**Purpose:** Bottom-anchored detail panel providing drill-down transparency upon clicking any deal card mapped natively via `selectedDeal` hook bindings.
* Safely isolates unassigned targets securely. Maps explicitly evaluated intelligence flags including the mathematical `action_confidence` scoring output rendered precisely targeting specific Stakeholder roles dynamically evaluating responses and structural paths executing UI recommendations visually natively pushing API adjustments instantly safely.

### `index.css`
**Purpose:** Handles cascading logic overrides generating premium dashboard styling limits explicitly setting color metrics exactly wrapping grid limits optimally.
* Maps `--status-stalled` and `--brand-primary` parameters globally.
* Builds rigid `.flow-container` arrays securely tracking boundaries rendering elegant high-contrast visual cues isolating distinct stages explicitly mapping UI structures tightly matching expected outputs natively minimizing visual clutter effectively.
