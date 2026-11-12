# AgentCart AI — 3-Minute Demo Video Recording Script

> **Purpose**: Public submission demo video (< 3 minutes) for the PayPal AI Hackathon and AI agent competitions.  
> **Target Duration**: 2:30 – 3:00 minutes. Speak at a clear, natural pace.  
> **Verification**: All commands verified (`python -m paypilot demo` passes all 4 scenarios, `python eval.py` passes 172/172 assertions, web server runs on port 8780).

---

## Pre-Recording Checklist (1 Minute)

1. Open a terminal in the project directory.
2. Set terminal font size to 16–18pt for clear legibility on video.
3. Close unrelated browser tabs and silence notifications.
4. Open your browser with these tabs ready:
   - `http://127.0.0.1:8780` (AgentCart AI Shopping Console)
   - `http://127.0.0.1:8780/grid` (Purchase Security Audit Grid)
   - `http://127.0.0.1:8780/renewals` (Subscription Intelligence)
   - `http://127.0.0.1:8780/docs` (OpenAPI Swagger UI)
5. Start screen recording (e.g., OBS Studio, Win+G Xbox Game Bar, or browser screen recorder).

---

## Timed Narration Script

### [0:00 – 0:25] Hook & Problem Statement
*(Visual: Terminal with clean black background, cursor blinking)*

> "This is **AgentCart AI** — an autonomous AI shopping assistant that can discover products, compare options, and pay securely, but *cannot* be tricked into an unauthorized purchase."
>
> "Most AI commerce agents today will happily rationalize a purchase you never authorized. AgentCart AI separates reasoning from authorization: **the model proposes, and a hard deterministic policy engine disposes**."
>
> "It is built entirely on the Python standard library with zero external dependencies. Everything you see runs offline with an in-process PayPal mock, and the exact same code path executes real checkouts in the live PayPal Sandbox."

---

### [0:25 – 0:55] Scenario 1: Happy Path (Allowed & Paid)
*(Visual: Type command into terminal and press Enter)*

```bash
python -m paypilot demo
```

*(Allow Scenario 1 to finish: Mom's gardening birthday gift under $50)*

> "First, the happy path. The user asks: *'Birthday gift for my mom, under $50 - she loves gardening.'*"
>
> "The agent parses the intent, ranks the catalog with field-level evidence — price, rating, matched signals — and selects the Deluxe Garden Tool Set at $34.99."
>
> "The policy engine checks all five guardrails: within the order limit, category allowed, daily budget safe. It creates a PayPal order and captures payment. Here is the PayPal capture ID, followed by the complete auditable decision trail."

---

### [0:55 – 1:25] Scenarios 2 & 3: Security Guardrails in Action
*(Visual: Point at Scenario 3 output: BLOCKED)*

> "Now the most critical part — what happens when a request violates spending policy?"
>
> "In Scenario 3, the request asks for a luxury watch for $500. The agent identifies a candidate, but the policy engine flags `CATEGORY_NOT_ALLOWED`. It immediately halts: status BLOCKED, zero dollars moved, and no PayPal order created."
>
> "The model cannot talk its way past this restriction because the guardrails are enforced by deterministic Python code, not a prompt."
>
> "In Scenario 4, an item priced at $129 exceeds the $100 approval threshold. The agent pauses in an `awaiting_approval` state, proceeding with PayPal capture only after receiving explicit human confirmation."

---

### [1:25 – 1:55] Interactive Web Console & Audit Grid
*(Visual: Switch to browser at `http://127.0.0.1:8780`)*

> "AgentCart AI includes a complete web console. Users can enter natural-language shopping requests, toggle human pre-approval, and inspect full decision provenance with product spotlight cards."

*(Visual: Switch to tab `/grid`)*

> "To audit policy coverage across the entire catalog, we have the **Purchase Security Audit Grid** powered by AG Grid. Every product is scored through the policy engine."
>
> "Notice this slider: as I drag *'Simulated daily spend'* toward the limit, rows dynamically flip to `BLOCK` in real time, demonstrating continuous budget protection. We can also export the complete audit to CSV."

---

### [1:55 – 2:20] Subscription Intelligence
*(Visual: Switch to tab `/renewals`)*

> "Autonomous commerce is more than just buying new items — it's about managing recurring spend. The **Subscription Intelligence** dashboard analyzes past transactions to project a 60-day renewal schedule."
>
> "It automatically flags stealth price hikes — like Netflix increasing from $15.49 to $22.99 — identifies duplicate charges, and generates polite, ready-to-send dispute letters."

---

### [2:20 – 2:45] Automated Verification & Architecture
*(Visual: Switch to terminal)*

```bash
python eval.py
```

*(Allow the test output to scroll: 172 passed, 0 failed)*

> "Reliability is backed by 172 automated offline assertions covering intent parsing, multi-signal ranking, policy edge cases, PayPal order capture, and API contracts. Zero third-party dependencies — anyone can clone and run it in 30 seconds."

---

### [2:45 – 3:00] Conclusion
> "AgentCart AI delivers the autonomy consumers want with the spending guardrails businesses and individuals require. Built on PayPal v2 Checkout. The repository is open-source under the MIT license on GitHub. Link is in the description. Thank you for watching!"

*(Stop recording)*

---

## Recording Review Checklist

- [ ] Scenario 1 displays `COMPLETED` and a `MOCK-CAPTURE-` ID.
- [ ] Scenario 3 displays `BLOCKED` with rule `CATEGORY_NOT_ALLOWED`.
- [ ] Scenario 4 displays `HOLD` &rarr; `human approved` &rarr; `COMPLETED`.
- [ ] Web console displays product spotlight card and decision trail.
- [ ] Audit Grid demonstrates the slider dynamically flipping rows to `BLOCK`.
- [ ] `eval.py` displays `172 passed, 0 failed`.
- [ ] Total video duration is under 3 minutes.

