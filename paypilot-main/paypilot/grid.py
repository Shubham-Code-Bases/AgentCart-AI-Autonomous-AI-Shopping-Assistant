"""Purchase Security Audit Grid - the whole catalog scored against spending guardrails.

Why an audit grid? Because a single-agent demo proves one decision; a grid
proves the complete policy surface. Every product is evaluated through the same
deterministic policy engine that gates real money, so a reviewer can sort,
filter and inspect decisions at scale and verify that guardrails hold
everywhere - not just in one scripted scenario.

Zero build step: AG Grid Community is loaded from CDN with an offline HTML table
fallback so the console works anywhere.
"""
import json

from .policy import Policy, check

# ---------------------------------------------------------------- data layer

def audit_rows(products, policy=None, daily_spent=0.0):
    """Run every product through the policy engine. Pure, deterministic."""
    policy = policy or Policy()
    rows = []
    for p in products:
        d = check(policy, p, daily_spent=daily_spent)
        rows.append({
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "merchant": p.merchant,
            "price": p.price,
            "rating": p.rating,
            "stock": p.stock,
            "tags": ", ".join(p.tags),
            "decision": d.action,          # allow | block | hold
            "rule": d.rule,
            "reason": d.detail,
            "evidence": list(d.evidence),
        })
    return rows


def summarize(rows):
    out = {"total": len(rows), "allow": 0, "block": 0, "hold": 0,
           "exposure": 0.0, "blocked_value": 0.0}
    for r in rows:
        out[r["decision"]] = out.get(r["decision"], 0) + 1
        if r["decision"] == "allow":
            out["exposure"] += r["price"]
        elif r["decision"] == "block":
            out["blocked_value"] += r["price"]
    out["exposure"] = round(out["exposure"], 2)
    out["blocked_value"] = round(out["blocked_value"], 2)
    return out


# ------------------------------------------------------------------- HTML/CSS

_HEAD = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgentCart AI &middot; Purchase Security Audit Grid</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@32.3.3/styles/ag-grid.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community@32.3.3/styles/ag-theme-quartz.css">
<style>
:root{
  --primary:#4f46e5;--primary-hover:#4338ca;--primary-light:#eef2ff;
  --ink:#0f172a;--ink-soft:#334155;--mut:#64748b;--line:#e2e8f0;
  --bg:#f8fafc;--card-bg:#ffffff;
  --ok:#059669;--ok-bg:#ecfdf5;--warn:#d97706;--warn-bg:#fffbeb;--bad:#dc2626;--bad-bg:#fef2f2;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);line-height:1.5}
a{color:var(--primary);text-decoration:none;font-weight:500}
a:hover{color:var(--primary-hover);text-decoration:underline}

/* Header */
.navbar{background:#fff;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:100;box-shadow:0 1px 3px rgba(0,0,0,0.05)}
.nav-wrap{max-width:1180px;margin:0 auto;padding:12px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}
.nav-brand{display:flex;align-items:center;text-decoration:none}
.nav-links{display:flex;align-items:center;gap:14px;flex-wrap:wrap}
.nav-link{font-size:13.5px;font-weight:600;color:var(--ink-soft);padding:6px 10px;border-radius:8px;transition:all .15s}
.nav-link:hover,.nav-link.active{color:var(--primary);background:var(--primary-light);text-decoration:none}

.wrap{max-width:1180px;margin:0 auto;padding:24px 20px 60px}
header{margin-bottom:20px}
header h1{font-size:24px;font-weight:800;letter-spacing:-.02em;margin-bottom:6px;display:flex;align-items:center;gap:10px}
header p{color:var(--mut);font-size:14.5px;max-width:820px}

/* Controls Bar */
.bar{display:flex;gap:12px;flex-wrap:wrap;align-items:center;background:#fff;border:1px solid var(--line);border-radius:12px;padding:12px 16px;margin:16px 0 14px}
button{background:var(--primary);color:#fff;border:0;border-radius:8px;padding:8px 16px;font-size:13px;font-weight:600;cursor:pointer;transition:background .15s}
button:hover{background:var(--primary-hover)}
button.ghost{background:#f1f5f9;color:var(--ink-soft);border:1px solid var(--line)}
button.ghost:hover{background:#e2e8f0}
input[type=range]{width:180px;accent-color:var(--primary)}
label.ctl{font-size:13px;font-weight:600;color:var(--ink-soft);display:flex;gap:8px;align-items:center}
#spentVal{font-weight:700;color:var(--primary);background:var(--primary-light);padding:2px 8px;border-radius:6px}

/* KPIs */
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:14px}
.kpi{background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 16px}
.kpi .n{font-size:22px;font-weight:800;color:var(--ink)}
.kpi .l{font-size:11.5px;color:var(--mut);text-transform:uppercase;letter-spacing:.06em;font-weight:600;margin-top:2px}

#grid{height:540px;width:100%;border-radius:12px;overflow:hidden;border:1px solid var(--line);box-shadow:0 1px 3px rgba(0,0,0,0.05)}
.badge{display:inline-block;border-radius:6px;padding:2px 8px;font-size:11.5px;font-weight:700;color:#fff;letter-spacing:.02em}
.b-allow{background:var(--ok)}.b-block{background:var(--bad)}.b-hold{background:var(--warn)}

.ev{background:#fff;border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin-top:14px;box-shadow:0 1px 3px rgba(0,0,0,0.05)}
.ev h3{margin:0 0 6px;font-size:15px;color:var(--ink);display:flex;align-items:center;gap:8px}
.ev ul{margin:8px 0 0;padding-left:20px;color:var(--mut);font-size:13px}
table.fallback{border-collapse:collapse;width:100%;background:#fff;font-size:13px}
table.fallback th,table.fallback td{border-bottom:1px solid #eef0f3;padding:8px 10px;text-align:left}
table.fallback th{background:#f8fafc;color:var(--mut);font-weight:600}
.note{font-size:12.5px;color:var(--mut);margin-top:12px}
code{background:#f1f5f9;border:1px solid #e2e8f0;border-radius:4px;padding:1px 5px;font-size:12px;font-family:ui-monospace,monospace}
footer{margin-top:40px;padding-top:20px;border-top:1px solid var(--line);text-align:center;font-size:12.5px;color:var(--mut)}
</style></head><body>

<header class="navbar">
  <div class="nav-wrap">
    <a href="/" class="nav-brand" title="AgentCart AI">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 44" width="160" height="36" fill="none">
        <defs>
          <linearGradient id="acG2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#4f46e5"/><stop offset="60%" stop-color="#3b82f6"/><stop offset="100%" stop-color="#06b6d4"/>
          </linearGradient>
        </defs>
        <rect x="2" y="4" width="36" height="36" rx="9" fill="url(#acG2)"/>
        <path d="M10 13h3.2l2.8 11.2a1.2 1.2 0 0 0 1.2.9h11.2a1.2 1.2 0 0 0 1.2-.9l2.4-8.2H14" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="18" cy="29" r="1.6" fill="#ffffff"/><circle cx="27" cy="29" r="1.6" fill="#ffffff"/>
        <path d="M25 8.5c0 1.8 1.4 2.5 1.4 2.5s-1.4.7-1.4 2.5c0-1.8-1.4-2.5-1.4-2.5s1.4-.7 1.4-2.5z" fill="#fde047"/>
        <text x="46" y="28" font-family="-apple-system, sans-serif" font-size="20" font-weight="800" fill="#0f172a" letter-spacing="-0.03em">AgentCart</text>
        <rect x="150" y="12" width="28" height="19" rx="5" fill="#4f46e5"/>
        <text x="164" y="26" font-family="-apple-system, sans-serif" font-size="11" font-weight="700" fill="#ffffff" text-anchor="middle">AI</text>
      </svg>
    </a>
    <nav class="nav-links">
      <a href="/" class="nav-link">AI Shopping</a>
      <a href="/grid" class="nav-link active">Purchase Security Audit</a>
      <a href="/renewals" class="nav-link">Subscription Intelligence</a>
      <a href="/docs" class="nav-link">API Docs</a>
    </nav>
  </div>
</header>

<div class="wrap">
<header>
  <h1>&#x1F6E1;&#xFE0F; Purchase Security Audit Grid</h1>
  <p>Every catalog item is verified against AgentCart AI's deterministic spending policy engine. Sort, filter, and click any row to inspect the exact security rule and cited evidence &mdash; and adjust <em>already spent today</em> to watch the daily-limit rule flip rows to BLOCK in real time.</p>
</header>

<div class="kpis">__KPIS__</div>

<div class="bar">
  <label class="ctl">Simulated daily spend:
    <input type="range" id="spent" min="0" max="600" step="10" value="__SPENT__">
    <span id="spentVal">$__SPENT__</span>
  </label>
  <label class="ctl"><input type="checkbox" id="onlyBlocked"> Show blocked only</label>
  <button class="ghost" id="csv">&#x1F4E5; Export CSV</button>
  <button class="ghost" id="reset">Reset filters</button>
  <span class="note" id="mode" style="margin-top:0;margin-left:auto"></span>
</div>

<div id="grid" class="ag-theme-quartz"></div>

<div class="ev" id="ev">
  <h3>&#x1F50E; Rule &amp; Field-Level Evidence Inspector</h3>
  <p class="note">Click any product row above to inspect the exact policy rule and field-level evidence evaluated by the guardrail engine.</p>
</div>

<p class="note">Engine: <code>paypilot.policy.check()</code> &middot; Data: <code>examples/catalog.csv</code> &middot; API endpoint: <code>/api/rows</code> &middot; Zero build step AG Grid Community with offline table fallback.</p>

<footer>
  <p>AgentCart AI &mdash; Shop Smarter. Compare Better. Pay Securely.</p>
</footer>
</div>

<script src="https://cdn.jsdelivr.net/npm/ag-grid-community@32.3.3/dist/ag-grid-community.min.js"></script>
<script>
const ROWS = __ROWS__;
const fmt = n => '$' + Number(n).toFixed(2);
function badge(d){ return '<span class="badge b-'+d+'">'+d.toUpperCase()+'</span>'; }
const COLS = [
  {field:'id', headerName:'ID', width:90, pinned:'left'},
  {field:'name', headerName:'Product Name', flex:2, minWidth:180},
  {field:'category', headerName:'Category', width:130},
  {field:'merchant', headerName:'Merchant', width:150},
  {field:'price', headerName:'Price', width:110, type:'numericColumn',
   valueFormatter:p=>fmt(p.value)},
  {field:'rating', headerName:'Rating', width:100, type:'numericColumn',
   valueFormatter:p=>Number(p.value).toFixed(1)},
  {field:'stock', headerName:'Stock', width:90, type:'numericColumn'},
  {field:'decision', headerName:'Security Decision', width:140,
   cellRenderer:p=>badge(p.value),
   comparator:(a,b,_,_)=>a.localeCompare(b)},
  {field:'rule', headerName:'Cited Rule', width:190},
  {field:'reason', headerName:'Policy Evaluation', flex:2, minWidth:220, tooltipField:'reason'}
];
const DEFAULTS = {sortable:true, resizable:true, filter:true, flex:1};
const OPTS = {
  rowData: ROWS,
  columnDefs: COLS,
  defaultColDef: DEFAULTS,
  pagination: true,
  paginationPageSize: 25,
  sideBar: {toolPanels:['filters','columns'], defaultToolPanel:false},
  rowClassRules: {
    'row-block': p => p.data.decision === 'block',
    'row-hold':  p => p.data.decision === 'hold'
  },
  onRowClicked: e => {
    const d = e.data;
    document.getElementById('ev').innerHTML =
      '<h3>' + d.name + ' &mdash; ' + badge(d.decision) + ' <code>' + d.rule + '</code></h3>' +
      '<div style="margin:4px 0;font-size:13.5px;color:var(--ink-soft)">' + d.reason + '</div>' +
      '<ul>' + (d.evidence||[]).map(x => '<li>'+x+'</li>').join('') + '</ul>';
  }
};
let api = null;
function drawFallback(){
  const cols = ['id','name','category','merchant','price','rating','decision','rule'];
  let h = '<table class="fallback"><tr>' +
    cols.map(c=>'<th>'+c+'</th>').join('') + '</tr>';
  ROWS.forEach(r => {
    h += '<tr>' + cols.map(c =>
      '<td>' + (c==='decision' ? badge(r[c]) :
                (c==='price' ? fmt(r[c]) : r[c])) + '</td>').join('') + '</tr>';
  });
  document.getElementById('grid').innerHTML = h + '</table>';
  document.getElementById('mode').textContent = 'offline fallback (AG Grid CDN unreachable)';
}
if (typeof agGrid !== 'undefined' && agGrid.createGrid) {
  api = agGrid.createGrid(document.getElementById('grid'), OPTS);
  document.getElementById('mode').textContent = 'AG Grid Community (CDN)';
} else { drawFallback(); }
function reload(spent){
  fetch('/api/rows?spent=' + encodeURIComponent(spent))
    .then(r => r.json())
    .then(d => {
      ROWS.length = 0; d.rows.forEach(x => ROWS.push(x));
      if (api) { api.setGridOption('rowData', ROWS); }
      else { drawFallback(); }
      const k = d.summary;
      document.querySelector('.kpis').innerHTML =
        kpi(k.total,'items audited') + kpi(k.allow,'allowed') +
        kpi(k.block,'blocked') + kpi(k.hold,'needs approval') +
        kpi('$'+k.exposure,'buying power') + kpi('$'+k.blocked_value,'value protected');
    });
}
function kpi(n,l){ return '<div class="kpi"><div class="n">'+n+'</div><div class="l">'+l+'</div></div>'; }
const slider = document.getElementById('spent');
slider.addEventListener('input', e => {
  document.getElementById('spentVal').textContent = '$' + e.target.value;
  reload(e.target.value);
});
document.getElementById('csv').addEventListener('click', () => {
  if (api && api.exportDataAsCsv) { api.exportDataAsCsv({fileName:'agentcart-purchase-security-audit.csv'}); return; }
  const cols = Object.keys(ROWS[0]||{}).filter(c=>c!=='evidence');
  const esc = v => '"' + String(v==null?'':v).replace(/"/g,'""') + '"';
  const body = [cols.join(',')].concat(ROWS.map(r => cols.map(c=>esc(r[c])).join(','))).join('\\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([body],{type:'text/csv'}));
  a.download = 'agentcart-purchase-security-audit.csv'; a.click();
});
document.getElementById('reset').addEventListener('click', () => {
  if (!api) return;
  api.setFilterModel(null); api.setGridOption('quickFilterText','');
});
document.getElementById('onlyBlocked').addEventListener('change', e => {
  if (!api) return;
  if (e.target.checked) { api.setColumnFilterModel('decision', {filter:'block'}); }
  else { api.setColumnFilterModel('decision', null); }
  api.onFilterChanged();
});
</script></body></html>"""


def _kpis(s):
    def one(n, label):
        return '<div class="kpi"><div class="n">%s</div><div class="l">%s</div></div>' % (n, label)
    return (one(s["total"], "items audited") + one(s["allow"], "allowed")
            + one(s["block"], "blocked") + one(s["hold"], "needs approval")
            + one("$%s" % s["exposure"], "buying power")
            + one("$%s" % s["blocked_value"], "value protected"))


def _embed_json(obj):
    return (json.dumps(obj, ensure_ascii=False)
            .replace("</", "<\\/")
            .replace("<!--", "<\\!--"))


def render_grid_page(products, policy=None, daily_spent=0.0):
    policy = policy or Policy()
    rows = audit_rows(products, policy, daily_spent=daily_spent)
    page = (_HEAD
            .replace("__ROWS__", _embed_json(rows))
            .replace("__KPIS__", _kpis(summarize(rows)))
            .replace("__SPENT__", "%.0f" % daily_spent))
    return page


def rows_payload(products, policy=None, daily_spent=0.0):
    rows = audit_rows(products, policy, daily_spent=daily_spent)
    return {"rows": rows, "summary": summarize(rows), "daily_spent": daily_spent}
