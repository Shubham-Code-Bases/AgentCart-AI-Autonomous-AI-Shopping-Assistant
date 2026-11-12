"""Receipt rendering: plain text (CLI) and HTML (web UI / checkout receipt)."""
import html


def _summary_lines(res):
    p = res.chosen.product if res.chosen else None
    lines = [
        "AgentCart AI receipt",
        "=" * 60,
        "request      : %s" % res.request,
        "status       : %s" % res.status.upper(),
    ]
    if p:
        lines += [
            "product      : %s (%s)" % (p.name, p.id),
            "merchant     : %s" % p.merchant,
            "category     : %s" % p.category,
            "price        : $%.2f" % p.price,
            "rating       : %.1f/5" % p.rating,
        ]
    if res.policy:
        lines += ["policy       : %s (%s)" % (res.policy.action.upper(),
                                              res.policy.rule)]
    if res.order:
        lines += ["paypal order : %s" % res.order.get("id")]
    if res.capture_id:
        lines += ["capture id   : %s" % res.capture_id]
    if res.explanation:
        lines += ["why          : %s" % res.explanation]
    lines += ["", "decision trail:"]
    for s in res.steps:
        lines.append("  [%s] %s" % (s.phase, s.detail))
    return "\n".join(lines)


_STATUS_LABEL = {
    "completed": "Payment completed",
    "blocked": "Blocked by policy",
    "awaiting_approval": "Awaiting human approval",
    "no_match": "No matching product",
}


def _summary_html(res):
    e = html.escape
    p = res.chosen.product if res.chosen else None
    rows = [("AI Shopping Request", e(res.request)),
            ("Status", _STATUS_LABEL.get(res.status, res.status))]
    if p:
        rows += [("Product", "%s <code>%s</code>" % (e(p.name), e(p.id))),
                 ("Merchant", e(p.merchant)),
                 ("Category", e(p.category)),
                 ("Price", "$%.2f USD" % p.price),
                 ("Customer Rating", "%.1f / 5.0" % p.rating)]
    if res.policy:
        rows += [("Purchase Security Audit", "%s (%s)" % (e(res.policy.action.upper()),
                                                          e(res.policy.rule)))]
    if res.order:
        rows.append(("PayPal Order ID", "<code>%s</code>" % e(res.order.get("id"))))
    if res.capture_id:
        rows.append(("PayPal Capture ID", "<code>%s</code>" % e(res.capture_id)))
    if res.explanation:
        rows.append(("Smart Decision Why", e(res.explanation)))
    summary = "".join("<tr><th>%s</th><td>%s</td></tr>" % (k, v) for k, v in rows)
    trail = "".join(
        '<div class="step"><div class="phase">&#x25C9; %s</div>'
        '<div class="detail">%s</div><ul class="ev">%s</ul></div>'
        % (e(s.phase), e(s.detail),
           "".join("<li>%s</li>" % e(x) for x in s.evidence) or "<li>(no evidence)</li>")
        for s in res.steps)
    return summary, trail


def render(res):
    text = _summary_lines(res)
    summary, trail = _summary_html(res)
    doc = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgentCart AI &middot; Purchase Receipt</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<style>
 :root{--primary:#4f46e5;--ink:#0f172a;--mut:#64748b;--line:#e2e8f0;--bg:#f8fafc}
 body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);margin:0;padding:24px;line-height:1.5}
 .card{max-width:860px;margin:0 auto;background:#fff;border:1px solid var(--line);border-radius:14px;padding:28px;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
 .brand{display:flex;align-items:center;gap:10px;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--line)}
 h1{font-size:20px;font-weight:800;letter-spacing:-.02em;margin:0 0 16px;color:var(--ink)}
 table{border-collapse:collapse;width:100%;margin-bottom:24px}
 th,td{text-align:left;padding:10px 12px;border-bottom:1px solid #f1f5f9;font-size:13.5px;vertical-align:middle}
 th{width:160px;color:var(--mut);font-weight:600;background:#f8fafc}
 code{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:4px;padding:1px 6px;font-size:12.5px;font-family:ui-monospace,monospace}
 .step{border-left:3px solid var(--primary);padding:10px 14px;margin:10px 0;background:#f8fafc;border-radius:0 8px 8px 0}
 .phase{font-weight:700;font-size:11.5px;letter-spacing:.08em;color:var(--primary);text-transform:uppercase}
 .detail{font-size:13.5px;font-weight:500;margin:4px 0}
 ul.ev{margin:4px 0 0;padding-left:18px;color:var(--mut);font-size:12.5px}
 .footer-note{margin-top:24px;padding-top:16px;border-top:1px solid var(--line);font-size:12px;color:var(--mut);text-align:center}
</style></head><body><div class="card">
<div class="brand">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 44" width="160" height="36" fill="none">
    <defs>
      <linearGradient id="acGrec" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#4f46e5"/><stop offset="60%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#06b6d4"/>
      </linearGradient>
    </defs>
    <rect x="2" y="4" width="36" height="36" rx="9" fill="url(#acGrec)"/>
    <path d="M10 13h3.2l2.8 11.2a1.2 1.2 0 0 0 1.2.9h11.2a1.2 1.2 0 0 0 1.2-.9l2.4-8.2H14" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    <circle cx="18" cy="29" r="1.6" fill="#ffffff"/><circle cx="27" cy="29" r="1.6" fill="#ffffff"/>
    <path d="M25 8.5c0 1.8 1.4 2.5 1.4 2.5s-1.4.7-1.4 2.5c0-1.8-1.4-2.5-1.4-2.5s1.4-.7 1.4-2.5z" fill="#fde047"/>
    <text x="46" y="28" font-family="-apple-system, sans-serif" font-size="20" font-weight="800" fill="#0f172a" letter-spacing="-0.03em">AgentCart</text>
    <rect x="150" y="12" width="28" height="19" rx="5" fill="#4f46e5"/>
    <text x="164" y="26" font-family="-apple-system, sans-serif" font-size="11" font-weight="700" fill="#ffffff" text-anchor="middle">AI</text>
  </svg>
</div>
<h1>AgentCart AI Purchase Receipt</h1>
<table>__SUMMARY__</table>
<h1>Smart Purchase Decision Trail</h1>
__TRAIL__
<div class="footer-note">AgentCart AI &mdash; Autonomous Shopping Assistant with Purchase Security Guardrails.</div>
</div></body></html>""".replace("__SUMMARY__", summary).replace("__TRAIL__", trail)
    return text, doc
