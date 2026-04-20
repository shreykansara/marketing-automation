# Blostem Intelligence Platform - System Documentation

## 1. Overview
The Blostem platform is an end-to-end sales intelligence engine designed to transform market signals into actionable business deals. It utilizes a centralized company-first architecture and an AI-driven enrichment pipeline to prioritize high-intent opportunities.

---

## 2. Database Architecture (MongoDB)
All collections reside within the `pipeline_db` (or as configured in `.env`).

### 2.1 `signals`
Stores ingested market data (RSS, News API) and their AI-enriched counterparts.
*   **`_id`**: Primary Key (ObjectID).
*   **`hash`**: SHA-256 fingerprint for global deduplication (Unique Index).
*   **`title` / `content` / `url` / `source`**: Core signal metadata.
*   **`company_names`**: Array of normalized company names identified in the text.
*   **`category`**: Strategic classification (Funding, M&A, Hires, etc.).
*   **`relevance_score`**: AI-calculated intent score (0-100).
*   **`status`**: State machine (`raw` → `embedded` → `enriched` → `enrichment_failed`).
*   **`created_at`**: Internal timestamp for system lifecycle.
*   **TTL**: Documents are automatically deleted after **5 days** (432,000 seconds) via a TTL index.

### 2.2 `leads`
Consolidated company-level interest groups.
*   **`company`**: Unique normalized company name (Index).
*   **`company_id`**: Foreign Key to `companies._id`.
*   **`signal_ids`**: List of associated `signal._id` references.
*   **`emails`**: List of associated `email._id` references.
*   **`logs`**: Activity timeline (System events + Manual notes).

### 2.3 `deals`
The high-intent active sales pipeline.
*   **`company`**: Unique normalized company name (Unique Index).
*   **`company_id`**: Foreign Key to `companies._id`.
*   **`emails`**: List of associated `email._id` references.
*   **`logs`**: Full audit trail of the deal lifecycle.
*   **`intent_score`**: Qualitative metric for prioritization.

### 2.4 `companies`
The centralized master registry for all organizations identified by the system.
*   **`name`**: Unique normalized company name (Unique Index).
*   **`first_seen_at`**: Timestamp of first identification.
*   **`email_ids`**: List of associated contact email addresses.
*   **`is_lead_active`**: Boolean flag for current lead status.
*   **`is_deal_active`**: Boolean flag for current deal status.
*   **`is_archived`**: Boolean flag for archived status (mutually exclusive with active states).

### 2.5 `emails`
Unified storage for communication tracking.
*   **`sender` / `receiver`**: Participant addresses.
*   **`body` / `subject`**: Content and metadata.
*   **`timestamp`**: UTC transmission time.
*   **`is_logged`**: Flag indicating if the email has been pushed to a pipeline timeline.
*   **`company_id`**: Association with the master registry.

---

## 3. Core Lifecycle & Logic

### 3.1 Relational Linkage (PK/FK)
The platform uses the **Companies** collection as the primary registry. `Leads` and `Deals` documents store the parent company's `_id` in the `company_id` field. This ensures architectural consistency and enables unified communication history across the pipeline stages.

### 3.2 Signal Processing
Ingestion follows a strict path: Ingest → Hash → Embed → Enrich.
During the **Enrichment** phase, any identified company name is automatically registered in the `companies` collection.

### 3.3 Exclusivity Rule
A company is strictly exclusive to one pipeline stage:
*   It can exist as a **Lead** OR a **Deal**, but never both.
*   Promotion to a Deal triggers the immediate deletion of the Lead document and updates the `companies` active flags.

### 3.4 Lead Promotion
When a Lead is promoted to a Deal:
*   `logs` and `emails` are transferred entirely to preserve history.
*   `signal_ids` are dropped to minimize technical bloat.

---

## 4. API Specification
All endpoints are prefixed with `/api`. Documentation is available at `/docs`.

### 4.1 Signals
*   **`POST /api/signals/generate`**: Triggers signal ingestion and AI enrichment.
*   **`GET /api/signals`**: Retrieves signals in decreasing order of relevance.

### 4.2 Leads
*   **`POST /api/leads/generate`**: Aggregates enriched signals into unique leads.
*   **`GET /api/leads`**: Returns leads with calculated relevance.
*   **`POST /api/leads/manual`**: Manually inject a company into the lead pipeline.
*   **`PATCH /api/leads/{id}/logs`**: Adds a manual intelligence log.
*   **`DELETE /api/leads/{id}/logs/{log_id}`**: Removes a specific log entry.
*   **`DELETE /api/leads/{id}`**: Removes a lead and archives the company.

### 4.3 Deals
*   **`GET /api/deals`**: Primary pipeline. Uses **70/30 weighted average** of LLM log scores and signal history.
*   **`GET /api/deals/relevance-logs`**: Sorting focused specifically on log sentiment.
*   **`POST /api/deals/promote`**: Standard promotion endpoint for Lead -> Deal conversion.
*   **`POST /api/deals/manual`**: Directly inject a deal (or promote existing lead).
*   **`DELETE /api/deals/{id}`**: Removes a deal and archives the company.

### 4.4 Companies
*   **`GET /api/companies`**: Returns the master list of all identified organizations.
*   **`PATCH /api/companies/{id}/emails`**: Updates the contact directory for a company.
*   **`PATCH /api/companies/{id}/archive`**: Toggles archives and purges active pipeline records.

### 4.5 Emails
*   **`GET /api/emails`**: Fetches communications list with "is_loggable" detection.
*   **`POST /api/emails/`**: Saves an email (used by Browser Extension).
*   **`PATCH /api/emails/{id}/company`**: Manually tags an email to a company.
*   **`GET /api/emails/{id}/suggest-log`**: AI-driven log message suggestion.
*   **`POST /api/emails/{id}/log`**: Confirms a log and pushes it to the active pipeline.
*   **`POST /api/emails/generate`**: AI-driven outreach email generation.

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

