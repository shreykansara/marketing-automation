# Blostem Intelligence Platform - System Documentation

## 1. Overview
The Blostem platform is an end-to-end sales intelligence engine designed to transform market signals into actionable business deals. It utilizes a 4-collection MongoDB architecture and an AI-driven enrichment pipeline to prioritize high-intent opportunities.

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
*   **`status`**: State machine (`raw` → `enriched` → `processed`).
*   **`created_at`**: Internal timestamp for system lifecycle.
*   **TTL**: Documents are automatically deleted after **5 days** (432,000 seconds) via a TTL index on `created_at`.

### 2.2 `leads`
Consolidated company-level interest groups.
*   **`company`**: Unique normalized company name (Index).
*   **`company_id`**: Foreign Key to `companies._id`.
*   **`signal_ids`**: List of associated `signal._id` references.
*   **`emails`**: List of associated `email._id` references.
*   **`logs`**: Activity timeline (System events + Manual notes).
*   **`relevance`**: Derived average of associated signal scores.

### 2.3 `deals`
The high-intent active sales pipeline.
*   **`company`**: Unique normalized company name (Unique Index).
*   **`company_id`**: Foreign Key to `companies._id`.
*   **`emails`**: List of associated `email._id` references.
*   **`logs`**: Full audit trail of the deal lifecycle.
*   **`intent_score`**: Derived qualitative metric for prioritization.

### 2.4 `companies`
The centralized master registry for all organizations identified by the system.
*   **`name`**: Unique normalized company name (Unique Index).
*   **`first_seen_at`**: Timestamp of first identification in a signal.
*   **`email_ids`**: List of associated `email._id` references for unified history.

### 2.5 `emails`
Unified storage for all communication tracking.
*   **`sender` / `receiver`**: Participant addresses.
*   **`body` / `subject`**: Content and metadata.
*   **`timestamp`**: UTC transmission time.
*   **`is_logged`**: Boolean flag indicating if the email has been recorded in a timeline.

---

## 3. Core Lifecycle & Logic

### 3.1 Relational Linkage (PK/FK)
The platform uses the **Companies** collection as the primary registry. 
*   **Primary Key**:Every company has a unique `_id`.
*   **Foreign Key**: `Leads` and `Deals` documents store the parent company's `_id` in the `company_id` field. This ensures architectural consistency even if company names are modified.

### 3.2 Signal Processing
Ingestion follows a strict path: Ingest → Hash → Embed → Enrich.
During the **Enrichment** phase, any identified company name is automatically upserted into the `companies` collection. If the company already exists, the record is preserved; if new, it is registered with a `first_seen_at` timestamp.

### 3.2 Exclusivity Rule
A company is strictly exclusive to one pipeline stage:
*   It can exist as a **Lead** OR a **Deal**, but never both simultaneously.
*   Promotion to a Deal triggers the immediate deletion of the Lead document.

### 3.2 Lead Promotion
When a Lead is promoted to a Deal:
*   `logs` and `emails` are transferred entirely to preserve history.
*   `signal_ids` are dropped to minimize technical bloat, though the original signals remain in the signals collection until their TTL expires.

---

## 4. API Specification
All endpoints are prefixed with `/api`. Documentation is available at `/docs`.

### 4.1 Signals
*   **`POST /api/signals/generate`**: Triggers signal ingestion and AI enrichment.
*   **`GET /api/signals`**: Retrieves signals in decreasing order of relevance.

### 4.2 Leads
*   **`POST /api/leads/generate`**: Aggregates enriched signals into unique leads.
*   **`GET /api/leads`**: Returns leads with intent scores.
*   **`PATCH /api/leads/{id}/logs`**: Adds a manual intelligence log.
*   **`DELETE /api/leads/{id}/logs/{log_id}`**: Removes a specific log.

### 4.3 Deals
*   **`GET /api/deals`**: Primary pipeline (Smart Urgency view). Uses **70/30 weighted average** of LLM log scores and signal history.
*   **`POST /api/deals/promote`**: Standard promotion endpoint for Lead -> Deal conversion.

### 4.4 Companies
*   **`GET /api/companies`**: Returns the master list of all identified organizations.
*   **`PATCH /api/companies/{id}/emails`**: Manually updates the contact directory (List of Email IDs) for a company.

### 4.5 Emails
*   **`GET /api/emails`**: Fetches unified communications list.
*   **`POST /api/emails/generate`**: AI-driven email generation for outreach.

---

## 5. Frontend Architecture (React SPA)
The system is built as a high-density, glassmorphic Single Page Application.

*   **Dashboard**: Real-time "Growth Command" with priority alerts.
*   **Explore Signals**: Market scanner for new intelligence.
*   **Lead Manager**: Intent consolidation and pipeline promotion.
*   **Active Pipeline**: Smart deal tracking with urgency-based sorting.
*   **Company Registry**: Master identity management and contact curation.
*   **Communications**: Unified inbox for interaction logging.

**UX Integrity**: All destructive actions (e.g., Log Deletion) are protected by themed `ConfirmModal` UI components rather than browser alerts.
