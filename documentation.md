# Blostem Intelligence Platform - System Documentation

## 1. Overview
The Blostem platform is an end-to-end sales intelligence engine designed to transform market signals into actionable business deals. It utilizes a centralized company-first architecture and an AI-driven enrichment pipeline to prioritize high-intent opportunities.

---

## 2. Database Architecture (MongoDB)
All collections reside within the `pipeline_db` (or as configured in `.env`).

## 2. Database Architecture (MongoDB)
All collections reside within the `pipeline_db` (or as configured in `.env`).

### 2.1 `companies`
The centralized master registry and source of truth for pipeline state.
*   **`_id`**: Primary Key (ObjectID).
*   **`name`**: Unique normalized company name (Unique Index).
*   **`emails`**: List of associated contact email addresses.
*   **`status`**: Mutual exclusivity state (`null` | `lead` | `deal`).
*   **`flag`**: Active lifecycle state (`active` | `archived`).
*   **`created_at`**: Timestamp of first registration.

### 2.2 `signals`
Stores ingested market data (RSS, News API) and their AI-enriched counterparts.
*   **`_id`**: Primary Key (ObjectID).
*   **`company_ids`**: List of Relational References to `companies._id`.
*   **`hash`**: SHA-256 fingerprint for global deduplication (Unique Index).
*   **`title` / `content` / `url` / `source`**: Core signal metadata.
*   **`category`**: Strategic classification (Funding, M&A, Hires, etc.).
*   **`relevance_score`**: AI-calculated intent score (0-100).
*   **`status`**: State machine (`raw` → `embedded` → `enriched` → `failed`).
*   **TTL**: Documents are automatically deleted after **5 days** via a TTL index.

### 2.3 `leads`
Consolidated company-level interest groups.
*   **`_id`**: Primary Key (ObjectID).
*   **`company_id`**: Foreign Key to `companies._id`.
*   **`relevance_score`**: Aggregate score derived from linked signals.
*   **`status`**: Internal state (`active` | `archived`).

### 2.4 `deals`
The high-intent active sales pipeline.
*   **`_id`**: Primary Key (ObjectID).
*   **`company_id`**: Foreign Key to `companies._id`.
*   **`lead_id`**: Reference to the original lead for history preservation.
*   **`intent_score`**: Qualitative metric for prioritization.
*   **`stage_history`**: Array of timestamped transitions (e.g., Lead → Open → Contacted).

### 2.5 `emails`
Unified content storage for communication tracking.
*   **`sender` / `receiver`**: Participant addresses.
*   **`body` / `subject`**: Content metadata.
*   **`company_id`**: Relational link to the master registry.
*   **`lead_id` / `deal_id`**: Optional links to specific pipeline entities.
*   **`is_logged`**: Flag indicating if an AI summary has been pushed to the logs.

### 2.6 `logs`
**NEW**: Centralized activity timeline for all entities.
*   **`entity_id`**: Relational Key pointing to either a Lead _id or Deal _id.
*   **`timestamp`**: UTC time of the event.
*   **`type`**: Event classification (`SYSTEM`, `MANUAL`, `EMAIL`, `SIGNAL`).
*   **`message`**: Readable event description.

---

## 3. Core Lifecycle & Logic

### 3.1 Relational Normalization (Hydration)
The platform has transitioned from embedded arrays to a normalized relational model. API responses utilize MongoDB `$lookup` aggregations to **hydrate** objects with necessary metadata (e.g., retrieving company names and activity timelines for a lead).

### 3.2 Signal Ingestion
During enrichment, the system resolves company mentions to `ObjectIds`. If a company is unknown, it is automatically created in the `companies` collection before the signal is linked.

### 3.3 State Machine & Exclusivity
The `companies.status` field is the **Single Source of Truth** for pipeline exclusivity. 
*   **Promotion**: Promoting a lead to a deal updates `companies.status = 'deal'`, creates a new deal record, and updates all associated `logs` and `emails` to point to the new Deal ID. The Lead record is kemudian purged.
*   **Archival**: Setting `companies.flag = 'archived'` automatically clears active status and drops the entity from priority views.

---

## 4. API Specification

### 4.1 Signals
*   **`GET /api/signals`**: Returns enriched signals with hydrated company names.

### 4.2 Leads
*   **`GET /api/leads`**: Returns leads hydrated with company info and `logs` timeline.
*   **`POST /api/leads/manual`**: Resolve/Register company and inject into pipeline.

### 4.3 Deals
*   **`GET /api/deals`**: Returns deals hydrated with company info and `logs` timeline.
*   **`POST /api/deals/promote`**: Standard Lead -> Deal conversion (handles relational log migration).

### 4.4 Companies
*   **`GET /api/companies`**: Master registry retrieval.
*   **`PATCH /api/companies/{id}/emails`**: Updates the company's contact directory.

### 4.5 Emails
*   **`GET /api/emails`**: Communication feed with hydrated company context.
*   **`POST /api/emails/{id}/log`**: Pushes an AI summary to the centralized `logs` collection.
*   **`DELETE /api/emails/{id}`**: Permanently removes an email record from the system. Requires user confirmation on frontend.

---

## 5. Frontend Architecture (React SPA)
The system is built as a high-density, glassmorphic Single Page Application using Vite.

*   **Dashboard**: Real-time "Growth Command" with priority alerts.
*   **Explore Signals**: Market scanner for new intelligence.
*   **Lead Manager**: Intent consolidation and pipeline promotion.
*   **Active Pipeline**: Smart deal tracking with urgency-based sorting.
*   **Company Registry**: Master identity management and contact curation.
*   **Communications**: Unified inbox for interaction logging.

---

## 6. Local Development Setup

### 6.1 Prerequisites
- **Node.js** (v18+)
- **Python** (v3.9+)
- **MongoDB** (A valid `MONGO_URI` in `.env`)

### 6.2 Step 1: Backend
1. Ensure your virtual environment is active.
2. **Start the API Server**:
   ```bash
   uvicorn backend.main:app --reload
   ```
   *Note: Background pipelines now run as standard FastAPI endpoints.*

### 6.3 Step 2: Frontend
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   npm run dev
   ```
   The application will be available at `http://localhost:5173`.

---

## 7. Browser Extension (Email Ingester)
The Blostem ecosystem includes a Chrome Extension designed for deep Gmail integration.

### 7.1 Features
- **Save to Blostem**: Injects a button into the Gmail reading pane to extract and sync email interaction data directly to the master registry.
- **✨ AI Outreach**: Injects a button into the Gmail Compose window. It detects the recipient, fetches their signal/deal history from the Blostem API, and generates a context-aware outreach draft directly in the textbox.

### 7.2 Installation
1. Navigate to the `Extension` directory.
2. Open Chrome and go to `chrome://extensions/`.
3. Enable **Developer mode**.
4. Click **Load unpacked** and select the extension folder.
5. Ensure the extension is pointed to the correct backend URI (configurable in `manifest.json` host_permissions and `content.js` fetch calls).

