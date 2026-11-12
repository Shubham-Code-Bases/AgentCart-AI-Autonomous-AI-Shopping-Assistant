# AgentCart AI — Hackathon & Devpost Submission Guide

**Competition**: Build What's Next with PayPal and AI  
**Devpost**: [https://paypalaihackathon.devpost.com/](https://paypalaihackathon.devpost.com/)  
**GitHub Repository**: [https://github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant](https://github.com/Shubham-Code-Bases/AgentCart-AI-Autonomous-AI-Shopping-Assistant)  
**License**: MIT (Public & verified)

---

## 1. Submission Overview

- **Project Name**:
  ```text
  AgentCart AI — Autonomous AI Shopping Assistant with Purchase Security Guardrails
  ```
- **Tagline**:
  ```text
  Your AI-Powered Autonomous Shopping Assistant: Shop Smarter. Compare Better. Pay Securely.
  ```

---

## 2. Devpost Form Submission Content

### Elevator Pitch / Inspiration
Everyone is building AI agents that can browse the web and spend money. But what happens when the agent makes a mistake, gets tricked by prompt injection, or hallucinate a non-existent discount? Most agents today will rationalize a bad purchase you never authorized.

We built **AgentCart AI** on an uncompromising principle: **the model proposes, and a hard deterministic policy engine disposes**. Reasoning is separated from authorization. The AI understands natural language and ranks product candidates with evidence, while a deterministic security engine enforces strict spending rules before any money moves.

---

### What It Does

AgentCart AI turns a natural-language shopping request into a policy-verified, evidence-cited purchase and a transparent receipt using PayPal v2 Checkout.

The autonomous commerce loop executes across 8 distinct phases:
`PERCEIVE → SEARCH → SELECT → POLICY → APPROVAL → EXPLAIN → EXECUTE → CAPTURE → RECEIPT`

Money never moves before the policy engine runs. Every phase returns field-level evidence, allowing buyers and reviewers to audit why money did (or did not) move.

Three synchronized surfaces share one decision engine:
1. **AI Shopping Console (`/`)**: Natural-language request input, multi-signal candidate ranking, and human pre-approval thresholds. If a user asks for a luxury watch for $500, the request is immediately `BLOCKED` under rule `CATEGORY_NOT_ALLOWED`. If an item exceeds $100, it pauses in `awaiting_approval` until explicit human consent is given.
2. **Purchase Security Audit Grid (`/grid`)**: Powered by AG Grid Community, every catalog product is scored in real time. Dragging the *Simulated daily spend* slider demonstrates the `DAILY_LIMIT` rule dynamically flipping rows to `BLOCK` live. Supports CSV export and full filtering.
3. **Subscription Intelligence (`/renewals`)**: Analyzes past transaction history to project a 60-day renewal calendar, detect stealth price hikes (e.g. Netflix $15.49 &rarr; $22.99), flag duplicate billings ($59.99 charges days apart), and generate polite, ready-to-send dispute letters.

For external agents and developer integrations, the entire engine is exposed as a clean REST API described by an OpenAPI 3.0.3 specification, accompanied by a token-budgeted context block (~1.5k tokens) that can be dropped into an LLM system prompt.

---

### How We Built It

**Python 3 Standard Library Only.** No heavy frameworks, no external SDKs, zero build steps (`urllib`, `http.server`, `csv`, `re`, `dataclasses`, `hashlib`). A financial agent that reviewers and judges can read end-to-end is fundamentally more trustworthy than one obscured behind thousands of dependencies.

- **Purchase Security Engine (`paypilot/policy.py`)**: Five deterministic rules where the first violation halts execution: `BLOCKED_MERCHANT`, `CATEGORY_NOT_ALLOWED`, `MAX_PER_ORDER`, `DAILY_LIMIT`, and `APPROVAL_THRESHOLD`.
- **Cognitive Engines (`paypilot/reasoning.py`)**: Dual-engine architecture supporting any OpenAI-compatible LLM endpoint (e.g. Xiaomi MiMo, OpenAI, DeepSeek) with automatic, graceful degradation to a deterministic offline heuristic brain if the model is unreachable.
- **PayPal Integration (`paypilot/paypal.py`)**: PayPal v2 Checkout REST API (OAuth2 client credentials &rarr; create order with `intent=CAPTURE` &rarr; capture payment). Operates against the live PayPal Sandbox or an in-process mock engine for zero-setup offline testing.
- **Audit Grid (`paypilot/grid.py`)**: AG Grid Community with column definitions, custom status renderers, interactive daily limit slider, CSV export, and an offline HTML table fallback.
- **REST API & OpenAPI (`paypilot/api.py`, `openapi.yaml`, `paypilot/context.py`)**: Comprehensive REST endpoints, OpenAPI 3.0.3 document served at `/openapi.yaml` and interactive Swagger UI at `/docs`.
- **Subscription Intelligence (`paypilot/renewals.py`)**: Cadence detection, price-hike and duplicate detection, predictive calendar, and dispute nudge generation.

---

### Challenges We Overcame

1. **Strict Separation of Model & Policy**: Models must never have the final say on fund movement. The policy engine is isolated from prompt manipulation.
2. **Distinguishing Price Hikes from Seasonal Spikes**: Variable charges (utilities, coffee) fluctuate naturally; flagging every change creates noise. The engine only flags price hikes that persist into the latest charge.
3. **Conservative Savings Calculations**: Savings projections count cancellations at 100%, renegotiations at 15%, and reviews at 30% to prevent exaggerated claims.
4. **Injection-Safe JSON Embedding**: Grid data embedded in `<script>` blocks is escaped (`</` to `<\/`) to prevent crafted product names from escaping HTML tags (verified by automated tests).

---

### Accomplishments We're Proud Of

- **172 automated offline assertions** passing with zero failures.
- **Zero third-party package dependencies** — runs out of the box on Python 3.8+.
- **Zero-setup offline evaluation** allowing anyone to clone and verify in seconds without API keys.

---

### Technologies Used

`Python 3`, `Python Standard Library`, `PayPal REST API v2`, `PayPal Checkout`, `OAuth 2.0`, `AG Grid Community`, `OpenAPI 3.0.3`, `Swagger UI`, `Postman`, `REST API`

---

### Submission Categories & Sponsorships

- [x] **Best Use of PayPal + AI**
- [x] **Best Use of Agentic Commerce**
- [x] **Best Use of AG Grid / AG Studio** &mdash; Purchase Security Audit Grid (`/grid`)
- [x] **Best Use of APIMatic** &mdash; `openapi.yaml` and LLM agent context layer (`/api/v1/context`)
- [x] **Best Use of Postman** &mdash; `postman_collection.json`
- [x] **Best Use of Render** &mdash; `render.yaml` one-click deployment

