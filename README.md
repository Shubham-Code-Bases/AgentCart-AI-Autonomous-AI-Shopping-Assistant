# AgentCart AI

**Your AI-Powered Autonomous Shopping Assistant**  
*Shop Smarter. Compare Better. Pay Securely.*

---

## Overview

**AgentCart AI** is an autonomous AI shopping assistant with deterministic spending guardrails that discovers products, compares options, provides transparent purchase recommendations, and executes secure checkouts using PayPal.

Traditional AI shopping agents often act as unconstrained autonomous shoppers—risking unauthorized purchases, budget overruns, or buying from disreputable merchants. AgentCart AI solves this with a **"model proposes, policy disposes"** security architecture:

1. **Intelligent Discovery & Multi-Signal Ranking**: Parses natural language requests into structured intent, matches catalog candidates, and ranks them with field-level evidence.
2. **Purchase Security Audit**: Evaluates every potential purchase against hard deterministic policies (per-order caps, daily spending limits, category allowlists, merchant blocklists, and approval thresholds) **before** money moves.
3. **Secure PayPal Checkout**: Directly creates and captures orders via the PayPal v2 Checkout API in the live sandbox or against a zero-setup in-process mock.
4. **Transparent Audit Trail**: Every completed or blocked purchase includes an auditable decision trail and receipt citing exact product, policy, and payment details.
5. **Subscription Intelligence**: Proactively monitors recurring spend, detects silent price increases and duplicate charges, and drafts polite dispute nudges.

---

## Key Features

- **Intelligent Product Discovery**: Understands natural language requests (e.g., *"Birthday gift for my mom under $50 - she loves gardening"*) and extracts budget, recipient, occasion, and product signals.
- **AI-Powered Recommendations**: Employs multi-signal scoring algorithms to evaluate catalog candidates on rating, relevance, and value.
- **Smart Spending Protection**: Strict policy guardrails enforced deterministically without LLM hallucination:
  - `MAX_PER_ORDER`: Hard ceiling on single transaction size (default $200.00).
  - `DAILY_LIMIT`: Enforces aggregate 24-hour spending caps (default $500.00).
  - `CATEGORY_NOT_ALLOWED`: Whitelist-only purchases (defaults to garden, electronics, apparel, books).
  - `BLOCKED_MERCHANT`: Blacklist check for restricted merchants.
  - `APPROVAL_THRESHOLD`: Requires explicit human confirmation for items $\ge \$100.00$.
- **Secure PayPal Checkout**: Seamless PayPal v2 REST API integration (`/v2/checkout/orders` and `/v2/checkout/orders/{id}/capture`) with client-credentials OAuth2 authentication.
- **Transparent Purchase Decisions**: Full step-by-step audit provenance across 8 lifecycle phases: `PERCEIVE` &rarr; `SEARCH` &rarr; `SELECT` &rarr; `POLICY` &rarr; `APPROVAL` &rarr; `EXPLAIN` &rarr; `EXECUTE` &rarr; `CAPTURE`.
- **Purchase Security Audit Grid**: Interactive AG Grid Community interface (`/grid`) that evaluates every catalog item against the security engine in real time with an interactive simulated daily spend slider and CSV export.
- **Subscription Intelligence**: Recurring transaction analysis (`/renewals`) displaying a 60-day renewal calendar, detecting stealth price hikes and duplicate charges, and generating polite dispute letters.
- **Zero Third-Party Dependencies**: Built entirely on the **Python standard library** (Python 3.8+). No external packages required to install or run.
- **Dual Cognitive Brain**: Works out of the box with deterministic heuristics (offline) or connects to any OpenAI-compatible LLM endpoint (e.g. Xiaomi MiMo, OpenAI, DeepSeek, Anthropic via proxy). Automatically falls back to offline mode if the LLM is unavailable.
- **Comprehensive Test Suite**: 172 offline unit and integration assertions ensuring complete reliability.

---

## Technology Stack

- **Backend & Core Engine**: Python 3.8+ (Pure Standard Library: `http.server`, `urllib.request`, `dataclasses`, `json`, `csv`, `re`, `hashlib`)
- **Frontend & Visual Identity**: Semantic HTML5, Modern CSS3 with custom fintech styling, responsive flex/grid layouts, inline vector SVG brand assets.
- **Audit Grid**: AG Grid Community v32.3 (CDN-loaded with offline HTML table fallback).
- **Payment Gateway**: PayPal v2 Checkout API (Live Sandbox + In-Process Mock Engine).
- **API Documentation**: OpenAPI 3.0.3 specification with embedded Swagger UI console.

---

## Architecture Overview

```
User AI Shopping Request
          │
          ▼
   [1. PERCEIVE] ──► Parse occasion, recipient, budget, keywords (LLM or Heuristic)
          │
          ▼
   [2. SEARCH]   ──► Multi-signal catalog matching & scoring with cited evidence
          │
          ▼
   [3. SELECT]   ──► Best candidate selection (or price-ascending for cheapest)
          │
          ▼
   [4. POLICY]   ──► Deterministic Purchase Security Audit (ALLOW / HOLD / BLOCK)
          │
          ├──────────────────────────┐
          │ (BLOCK)                  │ (HOLD)
          ▼                          ▼
   [Security Block]           [Human Confirmation]
   No payment moved           Pre-approval required
   Audit receipt logged       (e.g., if price >= $100)
          │                          │
          └───────────┬──────────────┘
                      │ (ALLOW or APPROVED)
                      ▼
   [5. EXPLAIN]  ──► Natural language justification citing evidence
          │
          ▼
   [6. EXECUTE]  ──► PayPal v2 Create Order (`intent=CAPTURE`)
          │
          ▼
   [7. CAPTURE]  ──► PayPal v2 Capture Payment (Capture ID generated)
          │
          ▼
   [8. RECEIPT]  ──► Auditable plain-text and HTML receipt with decision trail
```

---

## Installation Instructions

AgentCart AI requires **Python 3.8 or higher** and has **zero third-party package dependencies**.

```bash
# 1. Clone repository
git clone https://github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant.git
cd paypilot-main

# 2. Verify Python version
python --version   # Python 3.8+

# 3. No pip install needed!
python -c "import paypilot; print('AgentCart AI loaded successfully!')"
```

---

## Environment Variable Configuration

Copy `.env.example` to `.env` or export environment variables in your shell:

| Variable | Default | Description |
|---|---|---|
| `AGENTCART_PAYPAL_MODE` | `mock` | `mock` (zero-setup offline simulation) or `live` (PayPal Sandbox) |
| `PAYPAL_CLIENT_ID` | `""` | PayPal Sandbox REST App Client ID (for live mode) |
| `PAYPAL_SECRET` | `""` | PayPal Sandbox REST App Secret (for live mode) |
| `AGENTCART_LLM_API_KEY` | `""` | API key for OpenAI-compatible LLM chat endpoint (optional) |
| `AGENTCART_LLM_BASE_URL` | `https://token-plan-cn.xiaomimimo.com/v1` | Base URL for LLM endpoint |
| `AGENTCART_LLM_MODEL` | `mimo-v2-flash` | Model identifier for LLM parsing and explanation |
| `PORT` | `8780` | Web server listening port |

*(Legacy environment variables `PAYPILOT_PAYPAL_MODE`, `PAYPILOT_LLM_API_KEY`, etc. remain fully supported for backward compatibility).*

---

## PayPal Sandbox Setup

By default, AgentCart AI runs in **mock mode**, requiring zero credentials. To connect to the live PayPal Sandbox:

1. Log in to the [PayPal Developer Dashboard](https://developer.paypal.com/).
2. Navigate to **Apps & Credentials** and click **Create App** (select Sandbox).
3. Copy your **Client ID** and **Secret Key**.
4. Set the environment variables:
   ```bash
   export AGENTCART_PAYPAL_MODE="live"
   export PAYPAL_CLIENT_ID="your_sandbox_client_id"
   export PAYPAL_SECRET="your_sandbox_secret"
   ```
5. Run the web console or CLI with the `--live` flag:
   ```bash
   python -m paypilot shop "wireless earbuds" --live --approve
   python -m paypilot serve --live
   ```

*Note on Live Mode:* PayPal's live checkout creates a real order and emits an `approve_url`. In a live customer scenario, the buyer approves in their browser before payment capture completes.

---

## How to Run the Project

### 1. Start the Modern Web Console
```bash
python -m paypilot serve --port 8780
```
Open your browser at [http://127.0.0.1:8780](http://127.0.0.1:8780):
- **`/`**: AgentCart AI Interactive Shopping Console & Hero Landing
- **`/grid`**: Purchase Security Audit Grid (AG Grid with real-time spend simulator)
- **`/renewals`**: Subscription Intelligence Dashboard (60-day schedule & dispute nudges)
- **`/docs`**: Interactive API Documentation (Swagger UI)
- **`/openapi.yaml`**: Machine-readable OpenAPI 3.0.3 specification

### 2. Run the Test Suite
```bash
python eval.py
```
*Executes all 172 test assertions across intent parsing, search ranking, policy rules, PayPal order execution, AG Grid generation, REST APIs, and subscription detection.*

### 3. Run Scripted Scenarios via CLI
```bash
python -m paypilot demo
```

### 4. Interactive Shopping CLI
```bash
# Allowed purchase under budget
python -m paypilot shop "Birthday gift for my mom, under $50 - she loves gardening"

# Cheapest-first search sorting
python -m paypilot shop "Find me the cheapest mechanical keyboard"

# Held by approval threshold ($129 >= $100) - pre-approved
python -m paypilot shop "Get me nice wireless earbuds under $150" --approve

# Blocked by category restriction (luxury category disallowed)
python -m paypilot shop "Buy a luxury watch for $500 as a treat"
```

### 5. Subscription Intelligence CLI
```bash
python -m paypilot renewals
```

### 6. Export Agent Context for External LLMs
```bash
python -m paypilot context --format markdown
python -m paypilot context --format json
```

---

## Demo Workflow

The demo scenarios illustrate the complete behavioral range of AgentCart AI:

| # | Request | Behavior & Outcome | Policy Status | Payment Execution |
|---|---|---|---|---|
| **1** | *"Birthday gift for my mom, under $50 - she loves gardening"* | Discovers Deluxe Garden Tool Set ($34.99). All 5 policy checks pass. | **ALLOW** | PayPal order created & captured |
| **2** | *"Find me the cheapest mechanical keyboard"* | Triggers price-ascending search; selects Mechanical Keyboard RGB ($79.99). | **ALLOW** | PayPal order created & captured |
| **3** | *"Buy a luxury watch for $500 as a treat"* | Matches Designer Sunglasses ($189.00). Category 'luxury' not on allowlist. | **BLOCK** | Payment safely aborted (zero money moved) |
| **4** | *"Get me nice wireless earbuds under $150"* | Selects Earbuds ($129.00). Price exceeds $100 threshold; pauses for approval. | **HOLD &rarr; ALLOW** | Paid only after human approval passed |
| **5** | **Audit Grid Simulation** | Reviewer drags *Already Spent Today* slider to $450; watch products dynamically flip to BLOCK. | **DYNAMIC** | Real-time guardrail verification |
| **6** | **Subscription Intelligence** | Scans transactions; detects Netflix +48% hike and Adobe duplicate bill; outputs dispute emails. | **AUDIT** | Projected annual savings quantified |

---

## REST API Reference

The full agent loop is exposed as clean JSON endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Liveness check, PayPal mode, brain engine status |
| `GET` | `/api/v1/catalog` | Filter and sort catalog items (`?category=&max_price=&q=&sort=`) |
| `GET` | `/api/v1/context` | Agent-consumable system prompt digest |
| `POST` | `/api/v1/quote` | Parse request and rank candidates &mdash; **never moves money** |
| `POST` | `/api/v1/policy/check` | Test `{product_id, daily_spent}` against guardrails |
| `POST` | `/api/v1/agent/run` | Execute the full autonomous loop with optional payment |
| `GET` | `/api/v1/renewals` | Retrieve detected subscriptions, flags, and recovery plan |

---

## Project Structure

```
paypilot-main/
├── paypilot/
│   ├── __init__.py           # Package version & metadata
│   ├── __main__.py           # Entrypoint for python -m paypilot
│   ├── agent.py              # Autonomous 8-phase shopping agent loop
│   ├── api.py                # REST API dispatch, endpoints & Swagger UI
│   ├── catalog.py            # CSV catalog loader & multi-signal search ranking
│   ├── cli.py                # Command-line interface (demo, shop, serve, renewals)
│   ├── context.py            # LLM prompt context assembler (token-budgeted)
│   ├── grid.py               # Purchase Security Audit Grid (AG Grid + fallback)
│   ├── mock_paypal.py        # In-process offline PayPal v2 engine
│   ├── paypal.py             # PayPal REST client (OAuth2, Orders, Capture)
│   ├── policy.py             # Deterministic spending guardrails engine
│   ├── reasoning.py          # Cognitive engines (LLM Brain + OfflineBrain)
│   ├── receipts.py           # Text & HTML receipt generators
│   ├── renewals.py           # Subscription Intelligence engine & UI
│   ├── static/
│   │   ├── logo.svg          # AgentCart AI official brand logo
│   │   └── favicon.svg       # AgentCart AI official browser favicon
│   └── web.py                # HTTP server, landing page & interactive console
├── examples/
│   ├── catalog.csv           # 17 catalog items across 5 categories
│   ├── requests.txt          # Sample user prompt requests
│   └── transactions.csv      # Sample transactions with planted hikes/duplicates
├── openapi.yaml              # OpenAPI 3.0.3 specification
├── postman_collection.json   # Postman collection for API testing
├── eval.py                   # 172-assertion offline verification suite
├── requirements.txt          # Explicit zero-dependency declaration
├── server.py                 # Standalone web server deployment entrypoint
├── .env.example              # Environment variables template
├── LICENSE                   # MIT License
└── README.md                 # Project documentation
```

---

## Third-Party Dependencies & Attribution

### Zero-Dependency Architecture
AgentCart AI is engineered to run on the **Python standard library alone** without external Python package dependencies.

### Client-Side CDN Components
- **[AG Grid Community](https://www.ag-grid.com/)** (v32.3.3, MIT License): Used for tabular policy exploration on `/grid`. If the CDN is unreachable, the system automatically falls back to an offline HTML table.
- **[Swagger UI](https://swagger.io/tools/swagger-ui/)** (v5, Apache 2.0 License): Used to render interactive API documentation on `/docs`. If offline, a structured fallback documentation page is displayed.

### Attribution & Heritage
- **Original Foundation**: This project is built upon the open-source **PayPilot** project originally created by Zhiyilang for the [PayPal AI Hackathon 2026](https://paypalaihackathon.devpost.com/) ("Build What's Next with PayPal and AI").
- **AgentCart AI Enhancements**:
  - Rebranded identity to **AgentCart AI** (*Your AI-Powered Autonomous Shopping Assistant*).
  - Modernized visual design system: new SVG logo, favicon, fintech color palette, improved spacing and typography.
  - Re-architected Web Landing Page featuring the 6 core pillars, modern hero section, interactive shopping console, and product cards.
  - Refactored terminology: Purchase Security Audit, Smart Purchase Decisions, Subscription Intelligence, Confirm Your Purchase.
  - Enhanced Purchase Security Audit Grid with real-time daily spend simulation and CSV export.
  - Enhanced Subscription Intelligence dashboard with interactive 60-day renewal calendar and dispute letter drafts.
  - Upgraded OpenAPI 3.0.3 and Postman collection documentation.
  - Maintained 100% backward compatibility, offline mock support, and all 172 passing test assertions.

---

## License

This project is licensed under the **MIT License** &mdash; see the [LICENSE](LICENSE) file for details.
