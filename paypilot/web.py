"""AgentCart AI - Web Demo UI.

Your AI-Powered Autonomous Shopping Assistant.
Shop Smarter. Compare Better. Pay Securely.

Serves the agent console showing the full loop:
natural-language intent, ranked candidates, spending security guardrails,
payment execution via PayPal, and transparent receipts.

Run:  python -m paypilot serve --port 8780
Mode: mock by default (no keys needed). Set PAYPAL_CLIENT_ID/PAYPAL_SECRET and
start with `serve --live` to point at the real sandbox.
"""
import html
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .agent import ShopAgent
from .catalog import load_catalog
from .grid import render_grid_page, rows_payload
from .mock_paypal import MockPayPal
from .paypal import PayPalClient
from .policy import Policy
from .reasoning import get_brain
from .renewals import (analyze, parse_transactions_csv, render_renewals_page)

E = html.escape

FAVICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 36" width="36" height="36" fill="none">
  <defs>
    <linearGradient id="acFav" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4f46e5"/>
      <stop offset="60%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
  </defs>
  <rect width="36" height="36" rx="8" fill="url(#acFav)"/>
  <path d="M8 11h3.2l2.8 11.2a1.2 1.2 0 0 0 1.2.9h11.2a1.2 1.2 0 0 0 1.2-.9l2.4-8.2H12" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="16" cy="27" r="1.6" fill="#ffffff"/>
  <circle cx="25" cy="27" r="1.6" fill="#ffffff"/>
  <path d="M23 6.5c0 1.8 1.4 2.5 1.4 2.5s-1.4.7-1.4 2.5c0-1.8-1.4-2.5-1.4-2.5s1.4-.7 1.4-2.5z" fill="#fde047"/>
  <circle cx="27.5" cy="12" r="0.9" fill="#a5f3fc"/>
</svg>"""

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 44" width="180" height="40" fill="none">
  <defs>
    <linearGradient id="acLogoG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4f46e5"/>
      <stop offset="60%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#06b6d4"/>
    </linearGradient>
    <linearGradient id="acAiG" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#4f46e5"/>
    </linearGradient>
  </defs>
  <rect x="2" y="4" width="36" height="36" rx="9" fill="url(#acLogoG)"/>
  <path d="M10 13h3.2l2.8 11.2a1.2 1.2 0 0 0 1.2.9h11.2a1.2 1.2 0 0 0 1.2-.9l2.4-8.2H14" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="18" cy="29" r="1.6" fill="#ffffff"/>
  <circle cx="27" cy="29" r="1.6" fill="#ffffff"/>
  <path d="M25 8.5c0 1.8 1.4 2.5 1.4 2.5s-1.4.7-1.4 2.5c0-1.8-1.4-2.5-1.4-2.5s1.4-.7 1.4-2.5z" fill="#fde047"/>
  <circle cx="29.5" cy="14" r="0.9" fill="#a5f3fc"/>
  <text x="46" y="28" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="20" font-weight="800" fill="#0f172a" letter-spacing="-0.03em">AgentCart</text>
  <rect x="150" y="12" width="28" height="19" rx="5" fill="url(#acAiG)"/>
  <text x="164" y="26" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="11" font-weight="700" fill="#ffffff" text-anchor="middle" letter-spacing="0.05em">AI</text>
</svg>"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgentCart AI &middot; Your Personal AI Shopping Assistant</title>
<meta name="description" content="AgentCart AI - Your AI-Powered Autonomous Shopping Assistant. Shop Smarter. Compare Better. Pay Securely.">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<style>
:root {
  --primary: #4f46e5;
  --primary-hover: #4338ca;
  --primary-light: #eef2ff;
  --accent: #06b6d4;
  --ink: #0f172a;
  --ink-soft: #334155;
  --mut: #64748b;
  --line: #e2e8f0;
  --line-strong: #cbd5e1;
  --bg: #f8fafc;
  --card-bg: #ffffff;
  --ok: #059669;
  --ok-bg: #ecfdf5;
  --warn: #d97706;
  --warn-bg: #fffbeb;
  --bad: #dc2626;
  --bad-bg: #fef2f2;
  --radius: 14px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 12px rgba(15,23,42,0.08);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: var(--bg);
  color: var(--ink);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}
a { color: var(--primary); text-decoration: none; font-weight: 500; transition: color 0.15s; }
a:hover { color: var(--primary-hover); text-decoration: underline; }

/* Top Navigation Bar */
.navbar {
  background: #ffffff;
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}
.nav-wrap {
  max-width: 1040px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.nav-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
}
.nav-link {
  font-size: 13.5px;
  font-weight: 600;
  color: var(--ink-soft);
  padding: 6px 10px;
  border-radius: 8px;
  transition: all 0.15s ease;
}
.nav-link:hover, .nav-link.active {
  color: var(--primary);
  background: var(--primary-light);
  text-decoration: none;
}
.nav-badges {
  display: flex;
  gap: 8px;
  align-items: center;
}
.env-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 11.5px;
  font-weight: 600;
  padding: 3px 9px;
  border-radius: 999px;
  background: #f1f5f9;
  color: var(--mut);
  border: 1px solid var(--line);
}
.env-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

/* Page Container */
.wrap {
  max-width: 1040px;
  margin: 0 auto;
  padding: 32px 20px 80px;
}

/* Hero Section */
.hero {
  text-align: center;
  padding: 24px 10px 36px;
}
.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--primary);
  background: var(--primary-light);
  padding: 4px 12px;
  border-radius: 999px;
  margin-bottom: 14px;
}
.hero h1 {
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--ink);
  line-height: 1.2;
  margin-bottom: 12px;
}
.hero-sub {
  font-size: 17px;
  color: var(--mut);
  max-width: 680px;
  margin: 0 auto 24px;
  line-height: 1.5;
}
.hero-ctas {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  padding: 10px 20px;
  border-radius: 10px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: all 0.15s ease;
  text-decoration: none;
}
.btn-primary {
  background: var(--primary);
  color: #ffffff;
  box-shadow: 0 2px 6px rgba(79, 70, 229, 0.35);
}
.btn-primary:hover {
  background: var(--primary-hover);
  color: #ffffff;
  text-decoration: none;
  transform: translateY(-1px);
}
.btn-secondary {
  background: #ffffff;
  color: var(--ink);
  border: 1px solid var(--line-strong);
}
.btn-secondary:hover {
  background: #f8fafc;
  border-color: var(--primary);
  color: var(--primary);
  text-decoration: none;
}

/* Feature Grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
  gap: 16px;
  margin: 32px 0 36px;
}
.feature-card {
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s ease;
}
.feature-card:hover {
  transform: translateY(-2px);
  border-color: #cbd5e1;
  box-shadow: var(--shadow-md);
}
.feature-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-bottom: 12px;
  background: var(--primary-light);
  color: var(--primary);
}
.feature-card h3 {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 6px;
  color: var(--ink);
}
.feature-card p {
  font-size: 13px;
  color: var(--mut);
  line-height: 1.45;
}

/* Interactive Card */
.card {
  background: var(--card-bg);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 24px;
  margin-top: 24px;
  box-shadow: var(--shadow-sm);
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--line);
}
.card-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--ink);
  display: flex;
  align-items: center;
  gap: 8px;
}

label {
  display: block;
  font-weight: 600;
  font-size: 13.5px;
  margin-bottom: 8px;
  color: var(--ink-soft);
}
textarea {
  width: 100%;
  min-height: 84px;
  border: 1px solid var(--line-strong);
  border-radius: 10px;
  padding: 12px 14px;
  font-size: 14.5px;
  font-family: inherit;
  color: var(--ink);
  background: #ffffff;
  resize: vertical;
  transition: border-color 0.15s, box-shadow 0.15s;
}
textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}

.row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  margin-top: 14px;
}
.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 13px;
  color: var(--ink-soft);
  cursor: pointer;
  margin-bottom: 0;
}
.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: var(--primary);
  cursor: pointer;
}

.chips-label {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--mut);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.chips-wrap {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}
.chip {
  background: #f1f5f9;
  border: 1px solid var(--line);
  color: var(--ink-soft);
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 12.5px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s ease;
}
.chip:hover {
  background: var(--primary-light);
  border-color: #c7d2fe;
  color: var(--primary);
  transform: translateY(-1px);
}

/* Status Badges */
.status {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border-radius: 8px;
  padding: 4px 10px;
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 0.02em;
}
.st-completed { background: var(--ok-bg); color: var(--ok); border: 1px solid #a7f3d0; }
.st-blocked { background: var(--bad-bg); color: var(--bad); border: 1px solid #fecaca; }
.st-awaiting_approval { background: var(--warn-bg); color: var(--warn); border: 1px solid #fde68a; }
.st-no_match { background: #f1f5f9; color: var(--mut); border: 1px solid var(--line); }

/* Result Details Table */
table.res-table {
  border-collapse: collapse;
  width: 100%;
  margin: 12px 0 20px;
}
table.res-table th, table.res-table td {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--line);
  font-size: 13.5px;
  vertical-align: middle;
}
table.res-table th {
  width: 160px;
  color: var(--mut);
  font-weight: 600;
  background: #f8fafc;
}
table.res-table td {
  color: var(--ink);
}

/* Product Spotlight Card */
.product-spotlight {
  display: flex;
  gap: 18px;
  align-items: center;
  background: #f8fafc;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}
.prod-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  background: var(--primary-light);
  color: var(--primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
.prod-info { flex: 1; min-width: 220px; }
.prod-name { font-size: 16px; font-weight: 700; color: var(--ink); }
.prod-meta { font-size: 12.5px; color: var(--mut); margin-top: 2px; }
.prod-price { font-size: 20px; font-weight: 800; color: var(--ink); text-align: right; }

/* Decision Trail / Timeline */
.timeline {
  position: relative;
  margin: 16px 0 8px;
  padding-left: 20px;
}
.timeline::before {
  content: "";
  position: absolute;
  left: 6px;
  top: 6px;
  bottom: 6px;
  width: 2px;
  background: #e2e8f0;
}
.step {
  position: relative;
  margin-bottom: 16px;
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 12px 16px;
  transition: all 0.15s ease;
}
.step:hover {
  border-color: #cbd5e1;
  box-shadow: 0 2px 6px rgba(0,0,0,0.03);
}
.step::before {
  content: "";
  position: absolute;
  left: -20px;
  top: 16px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--primary);
  border: 2px solid #ffffff;
  box-shadow: 0 0 0 2px var(--primary);
}
.phase {
  font-weight: 700;
  font-size: 11.5px;
  letter-spacing: 0.08em;
  color: var(--primary);
  text-transform: uppercase;
}
.detail {
  font-size: 14px;
  font-weight: 500;
  color: var(--ink);
  margin: 4px 0;
}
ul.ev {
  margin: 6px 0 0;
  padding-left: 18px;
  color: var(--mut);
  font-size: 12.5px;
  line-height: 1.5;
}

code {
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 1px 6px;
  font-size: 12.5px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
.mode {
  font-size: 12.5px;
  color: var(--mut);
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed var(--line);
}

/* How It Works Section */
.how-it-works {
  margin-top: 48px;
  padding-top: 32px;
  border-top: 1px solid var(--line);
}
.how-it-works h2 {
  font-size: 22px;
  font-weight: 800;
  text-align: center;
  margin-bottom: 24px;
  color: var(--ink);
}
.steps-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}
.hiw-step {
  background: #ffffff;
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}
.hiw-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 800;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}
.hiw-step h4 {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 6px;
}
.hiw-step p {
  font-size: 13px;
  color: var(--mut);
}

/* Footer */
footer {
  margin-top: 60px;
  padding: 28px 0;
  border-top: 1px solid var(--line);
  text-align: center;
  color: var(--mut);
  font-size: 13px;
}
footer p { margin: 6px 0; }
.footer-links {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

@media (max-width: 640px) {
  .hero h1 { font-size: 26px; }
  .hero-sub { font-size: 15px; }
  .nav-wrap { flex-direction: column; align-items: flex-start; }
  .nav-links { width: 100%; justify-content: flex-start; }
}
</style>
</head>
<body>

<!-- Navigation Bar -->
<header class="navbar">
  <div class="nav-wrap">
    <a href="/" class="nav-brand" title="AgentCart AI">
      __LOGO__
    </a>
    <nav class="nav-links">
      <a href="/" class="nav-link active">AI Shopping</a>
      <a href="/grid" class="nav-link">Purchase Security Audit</a>
      <a href="/renewals" class="nav-link">Subscription Intelligence</a>
      <a href="/docs" class="nav-link">API Docs</a>
    </nav>
    <div class="nav-badges">
      <span class="env-badge"><span class="env-dot"></span>PayPal: __MODE__</span>
      <span class="env-badge">Brain: __BRAIN__</span>
    </div>
  </div>
</header>

<main class="wrap">
  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-tag">&#x2728; Autonomous Agentic Commerce</div>
    <h1>Your Personal AI Shopping Assistant</h1>
    <p class="hero-sub">Discover products, compare prices, make smarter purchasing decisions and complete secure purchases with AI-powered assistance.</p>
    <div class="hero-ctas">
      <a href="#shop-form" class="btn btn-primary" onclick="document.getElementById('req').focus()">Start Shopping &darr;</a>
      <a href="#how-it-works" class="btn btn-secondary">Explore How It Works</a>
    </div>
  </section>

  <!-- 6 Core Value Features Grid -->
  <section class="features-grid">
    <div class="feature-card">
      <div class="feature-icon">&#x1F50D;</div>
      <h3>Intelligent Product Discovery</h3>
      <p>Natural-language intent parsing extracts occasion, recipient, keywords, and explicit budget limits with zero prompt engineering.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">&#x2B50;</div>
      <h3>AI-Powered Recommendations</h3>
      <p>Multi-signal ranking algorithm evaluates catalog candidates and scores rating, relevance, and value with cited evidence.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">&#x1F6E1;&#xFE0F;</div>
      <h3>Smart Spending Protection</h3>
      <p>Hard deterministic policy checks run before money moves: per-order caps, daily budgets, and merchant safety blocklists.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">&#x1F4B3;</div>
      <h3>Secure PayPal Checkout</h3>
      <p>End-to-end PayPal v2 Checkout API order creation and capture in the live PayPal sandbox or zero-setup offline mock.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">&#x1F4CB;</div>
      <h3>Transparent Purchase Decisions</h3>
      <p>Every recommendation includes a complete auditable decision trail citing exact catalog and policy rationale.</p>
    </div>
    <div class="feature-card">
      <div class="feature-icon">&#x1F504;</div>
      <h3>Subscription Intelligence</h3>
      <p>Continuous spend analysis detects quiet price hikes, double-billings, and prepares polite ready-to-send dispute nudges.</p>
    </div>
  </section>

  <!-- Interactive Shopping Assistant Console -->
  <div class="card" id="shop-form">
    <div class="card-header">
      <div class="card-title">&#x1F6D2; AI Shopping Request</div>
      <span style="font-size:12.5px;color:var(--mut)">Policy Guardrails Active</span>
    </div>
    <form method="post" action="/run">
      <label for="req">What should AgentCart AI find and buy for you?</label>
      <textarea id="req" name="request" placeholder="e.g. Birthday gift for my mom, under $50 - she loves gardening">__REQUEST__</textarea>
      <div class="row">
        <button type="submit" class="btn btn-primary">Start Shopping</button>
        <label class="checkbox-label">
          <input type="checkbox" name="approve" value="1" __CHECKED__>
          <strong>Confirm Your Purchase:</strong> Pre-approve orders above the $100 approval threshold
        </label>
      </div>
    </form>
    
    <div style="margin-top:18px">
      <div class="chips-label">Quick Scenario Tests:</div>
      <div class="chips-wrap">
        __CHIPS__
      </div>
    </div>
    
    <div class="mode">
      Payment Engine: <strong>PayPal __MODE__</strong> &middot; Cognitive Engine: <strong>__BRAIN__ brain</strong> &middot; Catalog: <strong>17 verified products</strong>
    </div>
  </div>

  __RESULT__

  <!-- How It Works Section -->
  <section class="how-it-works" id="how-it-works">
    <h2>How AgentCart AI Works</h2>
    <div class="steps-row">
      <div class="hiw-step">
        <div class="hiw-num">1</div>
        <h4>Perceive &amp; Search</h4>
        <p>The AI extracts intent, recipient, and budget, then scans and ranks available products with field-level evidence.</p>
      </div>
      <div class="hiw-step">
        <div class="hiw-num">2</div>
        <h4>Security Guardrails</h4>
        <p>Before touching money, deterministic spending rules enforce category permissions, order caps, and human approvals.</p>
      </div>
      <div class="hiw-step">
        <div class="hiw-num">3</div>
        <h4>Secure Checkout</h4>
        <p>Approved transactions execute via PayPal v2 Checkout, returning an auditable receipt with full decision provenance.</p>
      </div>
    </div>
  </section>
</main>

<footer>
  <div class="footer-links">
    <a href="/">AgentCart AI Home</a>
    &middot; <a href="/grid">Purchase Security Audit Grid</a>
    &middot; <a href="/renewals">Subscription Intelligence</a>
    &middot; <a href="/docs">API Docs (Swagger UI)</a>
    &middot; <a href="/openapi.yaml">OpenAPI Spec</a>
  </div>
  <p><strong>AgentCart AI</strong> &mdash; Your AI-Powered Autonomous Shopping Assistant.</p>
  <p style="font-size:12px;color:var(--mut)">Shop Smarter. Compare Better. Pay Securely. Built on the PayPal AI Hackathon foundation.</p>
</footer>

</body>
</html>"""


def _chips(scenarios):
    return "".join('<span class="chip" onclick="document.getElementById(\'req\').value=this.textContent">%s</span>'
                   % E(s[0]) for s in scenarios)


_STATUS_LABELS = {
    "completed": "Payment Completed",
    "blocked": "Blocked by Purchase Security Policy",
    "awaiting_approval": "Awaiting Human Approval",
    "no_match": "No Matching Product Found",
}


def _result_html(res):
    if res is None:
        return ""
    p = res.chosen.product if res.chosen else None

    spotlight = ""
    if p:
        cat_icons = {
            "garden": "&#x1F33F;", "electronics": "&#x1F5A5;&#xFE0F;",
            "apparel": "&#x1F9E5;", "books": "&#x1F4DA;", "luxury": "&#x231A;"
        }
        icon = cat_icons.get(p.category.lower(), "&#x1F4E6;")
        spotlight = f"""
        <div class="product-spotlight">
          <div class="prod-icon">{icon}</div>
          <div class="prod-info">
            <div class="prod-name">{E(p.name)} <code>{E(p.id)}</code></div>
            <div class="prod-meta">Merchant: <strong>{E(p.merchant)}</strong> &middot; Category: <strong>{E(p.category)}</strong> &middot; Rating: <strong>&#x2605; {p.rating:.1f}/5.0</strong></div>
          </div>
          <div class="prod-price">${p.price:.2f}</div>
        </div>
        """

    rows = [("Status", '<span class="status st-%s">%s</span>'
             % (E(res.status), E(_STATUS_LABELS.get(res.status, res.status))))]
    if p:
        rows += [("Selected Product", "%s <code>%s</code>" % (E(p.name), E(p.id))),
                 ("Merchant", E(p.merchant)),
                 ("Category", E(p.category)),
                 ("Price", "$%.2f USD" % p.price),
                 ("Customer Rating", "%.1f / 5.0" % p.rating)]
    if res.policy:
        action_color = "var(--ok)" if res.policy.action == "allow" else ("var(--warn)" if res.policy.action == "hold" else "var(--bad)")
        rows.append(("Purchase Security Audit",
                     f'<strong style="color:{action_color}">{E(res.policy.action.upper())}</strong> &mdash; <code>{E(res.policy.rule)}</code>'))
    if res.order:
        rows.append(("PayPal Order ID", "<code>%s</code>" % E(res.order.get("id"))))
    if res.capture_id:
        rows.append(("PayPal Capture ID", "<code>%s</code>" % E(res.capture_id)))
    if res.explanation:
        rows.append(("AI Justification", "<em>%s</em>" % E(res.explanation)))

    summary = "".join("<tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in rows)

    trail = "".join(
        '<div class="step">'
        '<div class="phase">&#x25C9; %s</div>'
        '<div class="detail">%s</div>'
        '<ul class="ev">%s</ul>'
        '</div>'
        % (E(s.phase), E(s.detail),
           "".join("<li>%s</li>" % E(x) for x in s.evidence) or "<li>(no additional evidence cited)</li>")
        for s in res.steps)

    return (f"""
    <div class="card" style="margin-top:28px">
      <div class="card-header">
        <div class="card-title">&#x1F4CA; Smart Purchase Decision</div>
        <span class="status st-{E(res.status)}">{E(_STATUS_LABELS.get(res.status, res.status))}</span>
      </div>
      {spotlight}
      <table class="res-table">{summary}</table>
      <div class="card-title" style="margin-top:24px;font-size:15px">&#x1F9E0; Decision Trail &amp; Audit Evidence</div>
      <div class="timeline">{trail}</div>
    </div>
    """)


def _render_page(request, checked, result, mode="mock (offline)", brain="offline"):
    from .cli import SCENARIOS
    page = PAGE
    for key, val in (("__REQUEST__", E(request)),
                     ("__CHECKED__", checked),
                     ("__CHIPS__", _chips(SCENARIOS)),
                     ("__MODE__", mode),
                     ("__BRAIN__", brain),
                     ("__RESULT__", result),
                     ("__LOGO__", LOGO_SVG)):
        page = page.replace(key, val)
    return page


def make_handler(catalog_path, live):
    agent_state = {"brain": "offline"}

    def fresh_agent():
        products = load_catalog(catalog_path)
        brain = get_brain(prefer_llm=True)
        agent_state["brain"] = "llm" if brain.__class__.__name__ == "LLMBrain" else "offline"
        if live:
            paypal = PayPalClient(
                client_id=os.environ.get("PAYPAL_CLIENT_ID", ""),
                secret=os.environ.get("PAYPAL_SECRET", ""))
        else:
            paypal = PayPalClient(mock=MockPayPal())
        return ShopAgent(products, brain=brain, paypal=paypal)

    products_cache = load_catalog(catalog_path)

    txn_path = os.environ.get("PAYPILOT_TRANSACTIONS") or os.environ.get("AGENTCART_TRANSACTIONS") or os.path.join(
        os.path.dirname(__file__), "..", "examples", "transactions.csv")
    try:
        with open(txn_path, encoding="utf-8-sig") as f:
            txns_cache = parse_transactions_csv(f.read())
    except OSError:
        txns_cache = []

    def make_agent(daily_spent=0.0):
        brain = get_brain(prefer_llm=True)
        if live:
            paypal = PayPalClient(
                client_id=os.environ.get("PAYPAL_CLIENT_ID", ""),
                secret=os.environ.get("PAYPAL_SECRET", ""))
        else:
            paypal = PayPalClient(mock=MockPayPal())
        agent = ShopAgent(products_cache, brain=brain, paypal=paypal,
                          daily_spent=daily_spent)
        agent.mode = "sandbox" if live else "mock"
        return agent

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def _send(self, body, code=200, ctype="text/html; charset=utf-8"):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def _query(self):
            return {k: v[0] for k, v in
                    parse_qs(urlparse(self.path).query).items() if v}

        def _spent(self):
            try:
                return max(0.0, float(self._query().get("spent", "0")))
            except (TypeError, ValueError):
                return 0.0

        def do_GET(self):
            path = urlparse(self.path).path
            if path in ("/favicon.ico", "/favicon.svg"):
                self._send(FAVICON_SVG, ctype="image/svg+xml")
                return
            if path in ("/logo.svg", "/static/logo.svg"):
                self._send(LOGO_SVG, ctype="image/svg+xml")
                return
            if path.startswith("/healthz"):
                self._send('{"ok":true}', ctype="application/json")
                return
            if path.startswith("/api/rows"):
                payload = rows_payload(products_cache, Policy(),
                                       daily_spent=self._spent())
                self._send(json.dumps(payload, ensure_ascii=False),
                           ctype="application/json")
                return
            if path.startswith("/grid"):
                self._send(render_grid_page(products_cache, Policy(),
                                            daily_spent=self._spent()))
                return
            if path.startswith("/openapi.yaml") or path.startswith("/openapi.yml"):
                from .api import load_spec
                self._send(load_spec(), ctype="application/yaml; charset=utf-8")
                return
            if path.startswith("/docs"):
                from .api import render_docs
                self._send(render_docs())
                return
            if path.startswith("/renewals"):
                self._send(render_renewals_page(txns_cache))
                return
            if path.startswith("/api/"):
                from .api import dispatch, ok, to_json
                if path.startswith("/api/v1/renewals"):
                    self._send(to_json(ok(analyze(txns_cache))[1]), 200,
                               "application/json")
                    return
                status, body = dispatch(products_cache, make_agent, live,
                                        path, "GET", self._query(), None)
                self._send(to_json(body), status, "application/json")
                return
            page = _render_page("", "", "",
                                mode="LIVE sandbox" if live else "mock (offline)")
            self._send(page)

        def do_POST(self):
            if not self.path.startswith("/run"):
                path = urlparse(self.path).path
                if not path.startswith("/api/"):
                    self._send("not found", 404, "text/plain")
                    return
                from .api import dispatch, to_json
                n = int(self.headers.get("Content-Length", 0))
                raw = self.rfile.read(n).decode("utf-8", errors="replace")
                try:
                    payload = json.loads(raw) if raw else {}
                except ValueError:
                    status, body = (400, {
                        "ok": False,
                        "error": {"code": "INVALID_JSON",
                                  "message": "request body is not valid JSON"}})
                    self._send(to_json(body), status, "application/json")
                    return
                status, body = dispatch(products_cache, make_agent, live,
                                        path, "POST", {}, payload)
                self._send(to_json(body), status, "application/json")
                return
            n = int(self.headers.get("Content-Length", 0))
            form = parse_qs(self.rfile.read(n).decode("utf-8"))
            request = (form.get("request") or [""])[0].strip()
            approve = (form.get("approve") or [""])[0] == "1"
            if not request:
                self._send("empty request", 400, "text/plain")
                return
            agent = fresh_agent()
            res = agent.run(request, approve=approve)
            page = _render_page(request, "checked" if approve else "",
                                _result_html(res),
                                mode="LIVE sandbox" if live else "mock (offline)",
                                brain=agent_state["brain"])
            self._send(page)

    return Handler


def serve(port=None, catalog_path=None, live=False):
    if port is None:
        port = int(os.environ.get("PORT", "8780"))
    if catalog_path is None:
        catalog_path = os.environ.get("AGENTCART_CATALOG") or os.environ.get("PAYPILOT_CATALOG") or os.path.join(
            os.path.dirname(__file__), "..", "examples", "catalog.csv")
    handler = make_handler(catalog_path, live)
    httpd = ThreadingHTTPServer(("0.0.0.0", port), handler)
    print("AgentCart AI web demo running on http://127.0.0.1:%d  (PayPal mode: %s)"
          % (port, "LIVE sandbox" if live else "mock (offline)"))
    httpd.serve_forever()
