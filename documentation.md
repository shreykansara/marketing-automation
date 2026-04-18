# Blostem Intelligence Platform - Database Specification

## 1. Overview
The Blostem platform utilizes a streamlined MongoDB database structure to manage market signals, sales leads, and deal tracking. The architecture prioritizes data purity by minimizing redundancy and deriving analytic metrics at runtime.

---

## 2. Database Collections

### 2.1 signals
Stores raw and enriched news data ingested from global sources.
*   `id`: Primary key (ObjectID).
*   `title`: Title of the news/signal.
*   `content`: Full content text.
*   `url`: Source URL.
*   `source`: Source identifier.
*   `hash`: SHA-256 unique fingerprint for deduplication.
*   `company_names`: Array of target companies identified in the signal.
*   `category`: Strategic category (e.g., funding, partnership).
*   `relevance_score`: Intent score calculated by AI.
*   `published`: Original publication timestamp.
*   `status`: Processing state (`raw`, `embedded`, `enriched`).
*   `embedding`: Vector representation for semantic search.

### 2.2 leads
Unique company opportunities identified from signals.
*   `id`: Primary key (ObjectID).
*   `company`: Unique company name (normalized).
*   `signal_ids`: Array of signal IDs associated with this company.
*   `emails`: Array of email IDs associated with this lead.
*   `logs`: Transactional history of all events related to this lead.

### 2.3 deals
Tracking of active engagements and sales outreach.
*   `id`: Primary key (ObjectID).
*   `company`: Normalized company name (Unique).
*   `emails`: Array of email IDs associated with this deal.
*   `intent_score`: Qualitative score for the deal opportunity.
*   `logs`: Transactional history of the deal lifecycle.

### 2.4 emails
Unified storage for all inbound and outbound communication.
*   `sender`: Sender email address.
*   `receiver`: Receiver email address.
*   `cc`: Array of CC addresses.
*   `bcc`: Array of BCC addresses.
*   `body`: Email content.
*   `subject`: Email subject line.
*   `timestamp`: Time of transmission/receipt.
*   `is_logged`: Flag indicating if the email has been recorded in lead/deal logs.

---

## 3. Lifecycle Logic
*   **Signals -> Leads**: Signals are aggregated into leads based on `company_names`. A lead is only created if neither a `lead` nor a `deal` exists for that company.
*   **Leads -> Deals**: When a lead is converted via the "Promote" endpoint, the `lead` document is deleted and a new `deal` document is created. **Signal IDs are dropped** to minimize history bloat, but emails and logs are retained.
*   **Exclusivity**: A company can only exist in either the `leads` or the `deals` collection, never both.

---

## 4. API Endpoints & Logic

### 4.1 Signals
*   **`POST /signals/generate`**: Synchronously fetches news/RSS and performs AI enrichment for all unique found signals.
*   **`GET /signals`**: Returns enriched signals sorted by `relevance_score` descending.

### 4.2 Leads
*   **`POST /leads/generate`**: Consolidates all enriched signals into unique company leads.
*   **`GET /leads`**: Lists leads sorted by signal-derived relevance.
*   **`PATCH /leads/{id}/logs`**: Adds a manual activity log.
*   **`DELETE /leads/{id}/logs/{log_id}`**: Deletes a specific log entry.

### 4.3 Deals
*   **`GET /deals`**: Primary pipeline view. Relevance is a weighted average: `(0.7 * LLM_Log_Score) + (0.3 * Avg_Signal_Score)`.
*   **`GET /deals/relevance-logs`**: Hot deals view. Relevance is calculated solely from the 3 most recent logs by an LLM.
*   **`POST /deals/promote`**: Converts a lead to a deal (transferring logs/emails, deleting lead, dropping signals).

### 4.4 Emails
*   **`GET /emails`**: Returns all indexed communications sorted by date (latest first).
