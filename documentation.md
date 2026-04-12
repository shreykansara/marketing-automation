# Technical Documentation: Blostem Pipeline & Activation Intelligence MVP

This document provides a line-by-line technical breakdown and behavioral summary of each module within the Blostem Pipeline & Activation Intelligence system.

## Table of Contents
1. [Backend Modules](#backend-modules)
   - [mock_data.py](#mock_datapy)
   - [main.py](#mainpy)
2. [Frontend Modules](#frontend-modules)
   - [App.jsx](#appjsx)
   - [DealRow.jsx](#dealrowjsx)
   - [NextBestAction.jsx](#nextbestactionjsx)
   - [index.css](#indexcss)

---

## Backend Modules

The backend is built with FastAPI (Python) to provide high-performance, lightweight API endpoints.

### `mock_data.py`
**Purpose:** Simulates a live production database for the MVP. It defines the mock pipeline of prospects, stakeholders, and outreach templates.

* `get_current_time()`: Helper function returning a UTC-aware datetime, used to generate dynamic "last activity" timestamps so the stale logic doesn't break over time.
* `deals`: A list of dictionaries. Each dictionary represents a B2B deal and contains:
  * `id`: Unique deal identifier.
  * `company`: Name of the prospect.
  * `stage`: Current pipeline stage (Lead, Negotiation, Signed, Activation, Live).
  * `status`: Initializes as "Active", later mutated by the intelligence engine.
  * `last_activity`: ISO formatted timestamp representing the last time Blostem interacted with the prospect.
  * `value`: Estimated deal value in USD.
  * `stakeholders`: A nested list of key contacts at the company. Each contact holds flags like `contacted` (boolean), `responded` (boolean), and `intent_score` (integer).
* `templates`: A dictionary storing the hardcoded messaging texts tailored for specific roles (e.g., CTO, Compliance Officer).

### `main.py`
**Purpose:** Houses the FastAPI server, the Intelligence Rules Engine, and the REST endpoints.

* **Setup & Middleware:**
  * Initializes the `FastAPI()` app.
  * Adds `CORSMiddleware` to allow requests from the React frontend running on a different port (5173).
* **Intelligence Logic:**
  * `evaluate_stall_risk(deal)`: 
    * Parses the `last_activity` string into a datetime object.
    * Compares it against the current datetime. If the difference is >= 7 days, returns `"Stalled"`.
    * Iterates over the `deal['stakeholders']`. If any stakeholder has `contacted == True` but `responded == False`, returns `"At Risk"`.
    * Defaults to `"Active"` if neither condition is met.
  * `determine_next_action(deal)`: 
    * Takes a deal and determines actionable next steps based on the current pipeline `stage`.
    * If `Signed`: Checks for an "Integration Manager". If missing, advises identifying one. If present, advises sending API/Sandbox docs.
    * Global Check: Iterates through all stakeholders. If `contacted` but not `responded`, generates a `follow_up` action targeting that specific stakeholder.
    * If `Negotiation`: Checks for a "Compliance Officer". If missing, suggests scheduling a compliance review.
    * Fallback: If no actions are found, suggests `outreach` for "Lead", or `monitor` (All good) for everything else.
* **API Endpoints:**
  * `GET /api/deals`: Iterates over the `deals` list from `mock_data.py`. For each deal, it injects the evaluated `status` and `next_actions`, returning the full list to the frontend.
  * `GET /api/deals/{deal_id}/actions`: Retrieves a specific deal, runs the intelligence engines, and returns its specific actions.
  * `POST /api/deals/{deal_id}/action`: Simulates a user executing a recommended action.
    * Expects a JSON payload with `action_type` and optionally `stakeholder_name`.
    * If `follow_up`: Looks up the specific stakeholder, pulls their specific outreach template, updates the deal's `last_activity` to *now* (clearing the stall), and sets the stakeholder's `responded` status to `True` (simulating risk mitigation).
    * Returns a success message.

---

## Frontend Modules

The frontend is a Vite + React application providing a responsive, premium dashboard view.

### `App.jsx`
**Purpose:** The root application component that maintains state, fetches intelligence data, and renders the layout grid.

* **State Management:**
  * `deals`: Holds the array of pipeline data returned from the backend.
  * `loading`: Boolean indicating if a network request is active.
  * `selectedDeal`: Holds the object of whichever deal row the user clicks on.
* **Data Fetching:**
  * `fetchDeals()`: Async function hitting `http://localhost:8000/api/deals`. It updates the `deals` array and strategically updates `selectedDeal` with fresh data so the sidebar intelligence refreshes instantly when actions are taken.
  * `useEffect()`: Calls `fetchDeals` on the initial mount.
* **Computed Statistics:**
  * Calculates `totalPipeline`, `activeDeals`, `stalledDeals`, and `atRiskDeals` dynamically using standard JavaScript array methods (`reduce` and `filter`).
* **Component Rendering:**
  * Renders the top Header with a "Refresh" button.
  * Renders the Top Metric Cards (`stats-grid`), passing the computed statistics.
  * Renders the main content grid consisting of the Deals Table (generating a `DealRow` for each deal) and the Intelligence Sidebar (rendering `NextBestAction`).

### `DealRow.jsx`
**Purpose:** A stateless functional component mapping out a single table row for a specific deal.

* **Props:** `deal` (data object), `selected` (boolean), `onClick` (function).
* **Helper Functions:**
  * `getStatusBadge()`: Takes the string status (e.g., "At Risk"), strips whitespace, and maps it to specific CSS badge classes ensuring colored pills render successfully.
  * `formatCurrency()`: Safely translates integers into US Dollar strings utilizing Javascript's `Intl.NumberFormat`.
* **Behavior:** Renders the table cells (`<td>`) containing company name, stage, value, badge, and date. Fires the `onClick` prop upstream when clicked.

### `NextBestAction.jsx`
**Purpose:** The intelligence sidebar that breaks down the system's recommendations for a `selectedDeal`.

* **State:** `loadingAction` holds the index of the action currently being triggered to show a spinner.
* **Component Lifecycle / Behavior:**
  * If `deal` is null (none selected): Renders a placeholder "empty state".
  * `handleTriggerAction(action, idx)`:
    * Triggered when a user clicks the "Simulate Action" button.
    * Sets the spinner.
    * Sends a `POST` request to `/api/deals/{id}/action` sending the `action.type` and `stakeholder_name`.
    * Awaits success, then calls `onActionTriggered()` (which points back to `fetchDeals` in `App.jsx`) to universally refresh the dashboard and clear out completed actions.
* **Rendering:**
  * Displays company header and financial value.
  * Iterates over `deal.next_actions`.
  * Dynamically maps standard internal "types" (like `schedule_call`) to human-readable headers (like *"Compliance Review"*).
  * Renders action buttons. Certain action types like `monitor` are rendered as read-only statuses instead of actionable buttons.
  * Iterates over `deal.stakeholders` to print out an intent and communication summary for each contact associated with the account.

### `index.css`
**Purpose:** Provides the global styling, design tokens, and components for the UI, establishing the high-end enterprise aesthetic.

* **Design Tokens (CSS Variables):** 
  * Defined in `:root`. Exposes primary brand colors, semantic status colors (active, risk, stalled), backgrounds, text colors, and shadows.
* **Typography:** Integrates `Inter` for standard legibility and `Outfit` for specialized, dynamic headers.
* **Component Styles:**
  * `.dashboard-header h1`: Uses a custom `-webkit-text-fill-color: transparent` to achieve the metallic silver-gradient look.
  * `.stat-card`: Utilizes hover pseudo-selectors to enforce modern card elevations `transform: translateY(-2px)`.
  * `.deals-table`: Responsive standard table construction.
  * **Badges & Spinners:** Clean pill selectors and a custom `@keyframes spin` definition for network delays. 
* **Responsiveness:** Implements basic `@media (max-width: 1024px)` to collapse the 2-column sidebar into a single-column stacked format on smaller devices.
