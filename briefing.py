import anthropic
import smtplib
import os
import json
import re
import base64
import time
import urllib.request
import urllib.error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from pathlib import Path

# --- CONFIG ---
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL = os.environ["TO_EMAIL"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = "santoshmaruwada/bharosa-briefing"
RADAR_URL = "https://santoshmaruwada.github.io/bharosa-briefing/radar.html"
COVERAGE_LOG = "coverage_log.json"

# --- COMPETITOR LIST ---
COMPETITORS = [
    {"id": "groww", "name": "Groww", "geo": "India", "category": "Platform"},
    {"id": "kuvera", "name": "Kuvera / CRED", "geo": "India", "category": "Platform"},
    {"id": "indmoney", "name": "INDmoney", "geo": "India", "category": "AI Advisory"},
    {"id": "jarvis", "name": "Jarvis Invest", "geo": "India", "category": "AI-Native"},
    {"id": "zerodha", "name": "Zerodha", "geo": "India", "category": "Platform"},
    {"id": "smallcase", "name": "Smallcase", "geo": "India", "category": "Platform"},
    {"id": "investorai", "name": "InvestorAi", "geo": "India", "category": "AI-Native"},
    {"id": "etmoney", "name": "ET Money", "geo": "India", "category": "Platform"},
    {"id": "paytmmoney", "name": "Paytm Money", "geo": "India", "category": "Platform"},
    {"id": "angelone", "name": "Angel One", "geo": "India", "category": "Platform"},
    {"id": "upstox", "name": "Upstox", "geo": "India", "category": "Platform"},
    {"id": "tickertape", "name": "Tickertape", "geo": "India", "category": "AI Advisory"},
    {"id": "navi", "name": "Navi", "geo": "India", "category": "Platform"},
    {"id": "wealthy", "name": "Wealthy.in", "geo": "India", "category": "AI Advisory"},
    {"id": "dhan", "name": "Dhan", "geo": "India", "category": "Platform"},
    {"id": "orowealth", "name": "Orowealth", "geo": "India", "category": "AI Advisory"},
    {"id": "goalwise", "name": "Goalwise", "geo": "India", "category": "AI Advisory"},
    {"id": "finity", "name": "Finity", "geo": "India", "category": "Platform"},
    {"id": "plnr", "name": "PLNR", "geo": "India", "category": "AI-Native"},
    {"id": "mprofit", "name": "mProfit", "geo": "India", "category": "Platform"},
    {"id": "origin", "name": "Origin Financial", "geo": "Global", "category": "AI Advisory"},
    {"id": "wealthfront", "name": "Wealthfront", "geo": "Global", "category": "Robo-advisor"},
    {"id": "betterment", "name": "Betterment", "geo": "Global", "category": "Robo-advisor"},
    {"id": "portfoliopilot", "name": "PortfolioPilot", "geo": "Global", "category": "AI-Native"},
    {"id": "monarch", "name": "Monarch Money", "geo": "Global", "category": "Budgeting"},
    {"id": "copilot", "name": "Copilot Money", "geo": "Global", "category": "Budgeting"},
    {"id": "conquest", "name": "Conquest Planning", "geo": "Global", "category": "AI Advisory"},
    {"id": "cleo", "name": "Cleo", "geo": "Global", "category": "AI-Native"},
    {"id": "plum", "name": "Plum", "geo": "Global", "category": "Platform"},
    {"id": "ynab", "name": "YNAB", "geo": "Global", "category": "Budgeting"},
    {"id": "range", "name": "Range", "geo": "Global", "category": "AI Advisory"},
    {"id": "rocketmoney", "name": "Rocket Money", "geo": "Global", "category": "Budgeting"},
    {"id": "robinhood", "name": "Robinhood Gold", "geo": "Global", "category": "Platform"},
    {"id": "schwab", "name": "Schwab Intelligent", "geo": "Global", "category": "Robo-advisor"},
    {"id": "empower", "name": "Empower", "geo": "Global", "category": "AI Advisory"},
    {"id": "wally", "name": "Wally", "geo": "Global", "category": "Budgeting"},
    {"id": "acorns", "name": "Acorns", "geo": "Global", "category": "Platform"},
    {"id": "arta", "name": "Arta Finance", "geo": "Global", "category": "AI-Native"},
    {"id": "stashaway", "name": "StashAway", "geo": "Global", "category": "Robo-advisor"},
    {"id": "syfe", "name": "Syfe", "geo": "Global", "category": "Robo-advisor"},
    {"id": "endowus", "name": "Endowus", "geo": "Global", "category": "Platform"},
    {"id": "magnifi", "name": "Magnifi", "geo": "Global", "category": "AI-Native"},
    {"id": "moneylion", "name": "MoneyLion", "geo": "Global", "category": "Platform"},
    {"id": "bambu", "name": "Bambu", "geo": "Global", "category": "AI Advisory"},
    {"id": "savvy", "name": "Savvy Wealth", "geo": "Global", "category": "AI-Native"},
    {"id": "scalable", "name": "Scalable Capital", "geo": "Global", "category": "Robo-advisor"},
    {"id": "nutmeg", "name": "Nutmeg", "geo": "Global", "category": "Robo-advisor"},
    {"id": "addepar", "name": "Addepar", "geo": "Global", "category": "Platform"},
    {"id": "orion", "name": "Orion Advisor", "geo": "Global", "category": "Platform"},
    {"id": "perfios", "name": "Perfios", "geo": "Global", "category": "AI-Native"},
]

# --- COVERAGE MEMORY ---

def load_coverage_log():
    if not Path(COVERAGE_LOG).exists():
        return []
    try:
        with open(COVERAGE_LOG, "r") as f:
            data = json.load(f)
        today = datetime.now()
        log_date = datetime.fromisoformat(data.get("week_start", "2000-01-01"))
        days_since = (today - log_date).days
        if today.weekday() == 0 or days_since >= 7:
            return []
        return data.get("topics", [])
    except Exception:
        return []

def save_coverage_log(new_topics: list):
    existing = []
    week_start = datetime.now().isoformat()
    if Path(COVERAGE_LOG).exists():
        try:
            with open(COVERAGE_LOG, "r") as f:
                data = json.load(f)
            today = datetime.now()
            log_date = datetime.fromisoformat(data.get("week_start", "2000-01-01"))
            days_since = (today - log_date).days
            if today.weekday() != 0 and days_since < 7:
                existing = data.get("topics", [])
                week_start = data.get("week_start", week_start)
        except Exception:
            pass
    combined = list(dict.fromkeys(existing + new_topics))
    with open(COVERAGE_LOG, "w") as f:
        json.dump({"week_start": week_start, "topics": combined}, f, indent=2)

def extract_topics_from_html(html: str) -> list:
    patterns = [r'<h3[^>]*>(.*?)</h3>', r'font-weight:700[^>]*>(.*?)</p>']
    topics = []
    for pattern in patterns:
        matches = re.findall(pattern, html, re.DOTALL)
        for m in matches:
            clean = re.sub(r'<[^>]+>', '', m).strip()
            if 20 < len(clean) < 200:
                topics.append(clean[:150])
    return topics[:20]

def format_coverage_context(topics: list) -> str:
    if not topics:
        return ""
    day_names = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    today_name = day_names[datetime.now().weekday()]
    lines = "\n".join(f"- {t}" for t in topics)
    return f"""
ALREADY COVERED THIS WEEK — DO NOT REPEAT:
The following topics were already sent earlier this week.
Do NOT cover these again unless there is a genuinely significant new development.
If you must reference them, label it "Update:" and state only what is new.

{lines}

Today is {today_name}. Find fresh signals the team has not seen yet this week.
"""

# --- RADAR GENERATION — FACTS ONLY, WEB SEARCH VERIFIED ---

def generate_radar_data(client):
    """
    Research all 50 competitors using web search.
    Returns ONLY verified facts. No fallback numbers. No estimates.
    If a fact cannot be verified, the field is null/empty and won't be shown.
    """
    print("Generating Radar — web search verified facts only...")
    all_data = {c["id"]: {
        "name": c["name"],
        "geo": c["geo"],
        "category": c["category"],
        "description": None,
        "descriptionSource": None,
        "funding": None,
        "fundingSource": None,
        "fundingDate": None,
        "users": None,
        "usersSource": None,
        "latestNews": None,
        "latestNewsUrl": None,
        "latestNewsDate": None,
        "website": None,
    } for c in COMPETITORS}

    batch_size = 5
    total = len(COMPETITORS)

    for i in range(0, total, batch_size):
        batch = COMPETITORS[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (total + batch_size - 1) // batch_size
        names = [c["name"] for c in batch]
        ids = [c["id"] for c in batch]
        print(f"  Batch {batch_num}/{total_batches}: {', '.join(names)}")

        prompt = f"""You are a fact-checker for Bharosa's competitor intelligence dashboard.

Research these {len(batch)} companies using web search: {', '.join(names)}

STRICT RULES — read carefully:
1. Use web search to find information. Search multiple times per company if needed.
2. ONLY include data you actually found from a real URL source in your search results.
3. If you cannot find a verified figure — return null for that field. Never estimate or guess.
4. For funding: search "[company] funding raised total" and "[company] crunchbase" and "[company] series funding". Only report if you find it in Crunchbase, TechCrunch, Economic Times, VCCircle, Mint, or an official press release.
5. For users: search "[company] users customers million 2024 2025". Only report if a company executive, official press release, or verified journalist stated it explicitly.
6. For description: write 2 sentences based only on what you actually found. Include the most recent verified development. Do NOT use generic descriptions.
7. For latest news: find the single most recent news item about each company from the last 6 months.

Return ONLY a raw JSON array starting with [ and ending with ]. No markdown. No explanation. No code fences. No preamble.

IDs to use exactly: {json.dumps(ids)}

Return this exact schema for each:
[
  {{
    "id": "exact id from list above",
    "description": "2 verified sentences OR null if you found nothing specific",
    "descriptionSource": "URL where you found this OR null",
    "funding": "exact verified figure e.g. $3.5B total raised OR null if not found",
    "fundingSource": "exact URL of source OR null",
    "fundingDate": "date of most recent round e.g. March 2024 OR null",
    "users": "exact verified figure e.g. 50M registered users OR null if not found",
    "usersSource": "exact URL of source OR null",
    "latestNews": "one sentence describing most recent verified news item OR null",
    "latestNewsUrl": "URL of that news item OR null",
    "latestNewsDate": "date of that news item OR null",
    "website": "official website URL e.g. https://groww.in OR null"
  }}
]

CRITICAL: Return null — not empty string, not "—", not "unknown" — for any field you cannot verify. null means it will be hidden entirely from the dashboard."""

        max_retries = 2
        for attempt in range(max_retries):
            try:
                time.sleep(2)
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4000,
                    tools=[{"type": "web_search_20250305", "name": "web_search"}],
                    messages=[{"role": "user", "content": prompt}]
                )

                # Extract text blocks only
                raw = ""
                for block in response.content:
                    if hasattr(block, "text") and block.text:
                        raw += block.text

                raw = raw.strip()

                # Robust JSON extraction
                parsed = None
                for extractor in [
                    lambda t: json.loads(t),
                    lambda t: json.loads(re.sub(r'```[a-z]*\n?', '', t).strip()),
                    lambda t: json.loads(re.search(r'\[.*\]', t, re.DOTALL).group()) if re.search(r'\[.*\]', t, re.DOTALL) else None,
                ]:
                    try:
                        result = extractor(raw)
                        if result and isinstance(result, list):
                            parsed = result
                            break
                    except Exception:
                        continue

                if parsed:
                    for item in parsed:
                        cid = item.get("id")
                        if cid and cid in all_data:
                            # Only update with non-null values
                            for key, value in item.items():
                                if key != "id" and value is not None:
                                    all_data[cid][key] = value
                    print(f"    Batch {batch_num} OK — {len(parsed)} researched")
                    break
                else:
                    print(f"    Batch {batch_num} attempt {attempt+1} — parse failed")
                    if attempt < max_retries - 1:
                        time.sleep(3)

            except Exception as e:
                print(f"    Batch {batch_num} attempt {attempt+1} error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)

    return all_data


def build_radar_html(radar_data: dict, generated_at: str) -> str:
    """Build Radar HTML — facts only, nothing shown if unverified."""

    comp_js_list = []
    for c in COMPETITORS:
        cid = c["id"]
        d = radar_data.get(cid, {})
        obj = {
            "id": cid,
            "name": c["name"],
            "geo": c["geo"],
            "category": c["category"],
            "description": d.get("description"),
            "descriptionSource": d.get("descriptionSource"),
            "funding": d.get("funding"),
            "fundingSource": d.get("fundingSource"),
            "fundingDate": d.get("fundingDate"),
            "users": d.get("users"),
            "usersSource": d.get("usersSource"),
            "latestNews": d.get("latestNews"),
            "latestNewsUrl": d.get("latestNewsUrl"),
            "latestNewsDate": d.get("latestNewsDate"),
            "website": d.get("website"),
            "searchName": c["name"].lower(),
        }
        comp_js_list.append(json.dumps(obj))

    competitors_js = "[\n" + ",\n".join(comp_js_list) + "\n]"
    india_count = sum(1 for c in COMPETITORS if c["geo"] == "India")

    # Count how many have verified funding
    verified_funding = sum(1 for cid, d in radar_data.items() if d.get("funding"))
    verified_users = sum(1 for cid, d in radar_data.items() if d.get("users"))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bharosa Radar — {generated_at}</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0a0b;color:#e5e5ea;font-family:'DM Sans',sans-serif;min-height:100vh}}
body::before{{content:'';position:fixed;inset:0;background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");pointer-events:none;z-index:0;opacity:0.4}}
.sticky-bar{{position:sticky;top:0;z-index:100;background:rgba(10,10,11,0.95);backdrop-filter:blur(20px);border-bottom:1px solid #1c1c1e;padding:12px 32px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}}
.verified-badge{{background:#30d15822;color:#30d158;font-size:10px;font-weight:700;padding:3px 8px;border-radius:5px;margin-left:8px;letter-spacing:0.5px}}
.hero{{padding:48px 32px 32px;position:relative;z-index:1}}
.hero h1{{font-size:36px;font-weight:700;letter-spacing:-1px;margin-bottom:8px}}
.hero p{{color:#8e8e93;font-size:15px;margin-bottom:4px}}
.integrity-note{{background:#30d15812;border:1px solid #30d15833;border-radius:10px;padding:12px 16px;margin-bottom:28px;font-size:13px;color:#30d158;line-height:1.6}}
.stat-pills{{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:28px}}
.pill{{background:#1c1c1e;border:1px solid #2c2c2e;border-radius:10px;padding:14px 20px;text-align:center}}
.pill-num{{font-family:'DM Mono',monospace;font-size:24px;font-weight:500;display:block}}
.pill-label{{font-size:11px;color:#8e8e93;text-transform:uppercase;letter-spacing:1px;margin-top:2px}}
.controls{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:8px}}
.filter-btn{{background:#1c1c1e;border:1px solid #2c2c2e;color:#8e8e93;padding:7px 16px;border-radius:8px;font-size:13px;cursor:pointer;font-family:'DM Sans',sans-serif;transition:all 0.2s}}
.filter-btn.active,.filter-btn:hover{{background:#2c2c2e;color:#e5e5ea;border-color:#3a3a3c}}
.search-box{{background:#1c1c1e;border:1px solid #2c2c2e;color:#e5e5ea;padding:7px 14px;border-radius:8px;font-size:13px;font-family:'DM Sans',sans-serif;width:220px;outline:none}}
.search-box:focus{{border-color:#3a3a3c}}
.section-divider{{padding:12px 32px;font-size:11px;font-weight:700;letter-spacing:3px;color:#3a3a3c;text-transform:uppercase;border-top:1px solid #1c1c1e;margin-top:8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;padding:0 32px 32px;position:relative;z-index:1}}
.card{{background:#111113;border:1px solid #1c1c1e;border-radius:14px;padding:22px;transition:border-color 0.2s}}
.card:hover{{border-color:#2c2c2e}}
.card-top{{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:14px}}
.card-name{{font-size:17px;font-weight:700;letter-spacing:-0.3px}}
.card-cat{{font-size:12px;color:#636366;margin-top:3px}}
.badges{{display:flex;gap:6px;align-items:center;flex-shrink:0;margin-left:12px}}
.geo-badge{{background:#1c1c1e;color:#636366;padding:3px 8px;border-radius:5px;font-size:11px;border:1px solid #2c2c2e}}
.cat-badge{{background:#1c1c1e;color:#8e8e93;padding:3px 8px;border-radius:5px;font-size:11px;border:1px solid #2c2c2e}}
.desc-block{{margin-bottom:16px}}
.desc-text{{font-size:14px;color:#aeaeb2;line-height:1.65;margin-bottom:6px}}
.desc-source{{font-size:11px;color:#3a3a3c}}
.desc-source a{{color:#30d158;text-decoration:none;}}
.desc-source a:hover{{text-decoration:underline}}
.facts-grid{{display:flex;flex-direction:column;gap:10px;margin-bottom:16px}}
.fact-row{{background:#0a0a0b;border:1px solid #1c1c1e;border-radius:10px;padding:12px 14px}}
.fact-label{{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#636366;margin-bottom:4px;display:flex;align-items:center;gap:6px}}
.fact-verified-dot{{width:6px;height:6px;background:#30d158;border-radius:50%;display:inline-block;flex-shrink:0}}
.fact-value{{font-size:15px;font-weight:600;color:#e5e5ea;font-family:'DM Mono',monospace;margin-bottom:4px}}
.fact-meta{{font-size:11px;color:#636366}}
.fact-meta a{{color:#30d158;text-decoration:none}}
.fact-meta a:hover{{text-decoration:underline}}
.news-block{{background:#0a0a0b;border:1px solid #1c1c1e;border-radius:10px;padding:12px 14px;margin-bottom:16px}}
.news-label{{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#636366;margin-bottom:6px;display:flex;align-items:center;gap:6px}}
.news-text{{font-size:13px;color:#aeaeb2;line-height:1.6;margin-bottom:4px}}
.news-meta{{font-size:11px;color:#636366}}
.news-meta a{{color:#007aff;text-decoration:none}}
.links{{display:flex;gap:6px;flex-wrap:wrap}}
.link-btn{{background:#1c1c1e;border:1px solid #2c2c2e;color:#8e8e93;padding:6px 12px;border-radius:7px;font-size:12px;text-decoration:none;transition:all 0.2s;font-family:'DM Sans',sans-serif}}
.link-btn:hover{{background:#2c2c2e;color:#e5e5ea}}
.link-btn.primary{{background:#30d15822;border-color:#30d15844;color:#30d158}}
.link-btn.primary:hover{{background:#30d15833}}
.no-data-note{{font-size:12px;color:#3a3a3c;font-style:italic;margin-bottom:12px}}
.generated-note{{text-align:center;padding:32px;color:#3a3a3c;font-size:12px;font-family:'DM Mono',monospace;line-height:1.8;border-top:1px solid #1c1c1e}}
</style>
</head>
<body>

<div class="sticky-bar">
  <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px">
    <span style="font-size:13px;font-weight:600;">Bharosa Radar</span>
    <span class="verified-badge">&#10003; FACTS ONLY — WEB VERIFIED</span>
    <span style="font-size:12px;color:#636366;margin-left:4px;">Generated {generated_at}</span>
  </div>
  <div style="font-size:12px;color:#636366;">No estimates · No scores · No guesses</div>
</div>

<div class="hero">
  <h1>Competitor Intelligence</h1>
  <p style="margin-bottom:16px;">50 companies tracked. Every data point sourced from a real URL. If we couldn't verify it, it's not shown.</p>

  <div class="integrity-note">
    <strong>Data integrity policy:</strong> This dashboard shows only facts verified via live web search at generation time.
    Funding figures sourced from Crunchbase, TechCrunch, VCCircle, or official press releases.
    User counts sourced from company announcements or verified press coverage.
    Every fact has a clickable source link. If data was not publicly available, the field is hidden — not estimated.
  </div>

  <div class="stat-pills">
    <div class="pill"><span class="pill-num" style="color:#e5e5ea;">50</span><span class="pill-label">Tracked</span></div>
    <div class="pill"><span class="pill-num" style="color:#007aff;">{india_count}</span><span class="pill-label">India</span></div>
    <div class="pill"><span class="pill-num" style="color:#30d158;">{verified_funding}</span><span class="pill-label">Funding verified</span></div>
    <div class="pill"><span class="pill-num" style="color:#30d158;">{verified_users}</span><span class="pill-label">Users verified</span></div>
  </div>

  <div class="controls">
    <button class="filter-btn active" onclick="setFilter('all', event)">All</button>
    <button class="filter-btn" onclick="setFilter('india', event)">India</button>
    <button class="filter-btn" onclick="setFilter('global', event)">Global</button>
    <button class="filter-btn" onclick="setFilter('verified', event)">Has verified data</button>
    <input class="search-box" type="text" placeholder="Search by name or category..." oninput="setSearch(this.value)">
    <select class="filter-btn" onchange="setSort(this.value)" style="padding:7px 12px">
      <option value="name">Sort: A–Z</option>
      <option value="geo">Sort: India first</option>
      <option value="data">Sort: Most data</option>
    </select>
  </div>
</div>

<div id="india-divider" class="section-divider">India Players</div>
<div id="india-grid" class="grid"></div>
<div id="global-divider" class="section-divider">Global Players</div>
<div id="global-grid" class="grid"></div>

<div class="generated-note">
  Bharosa Radar · {generated_at}<br>
  All data sourced via live web search at generation time.<br>
  Hidden fields = data not publicly available or not found — never estimated.<br>
  Source links open the exact page where data was found.
</div>

<script>
const COMPETITORS = {competitors_js};

let currentFilter = 'all';
let currentSearch = '';
let currentSort = 'name';

function dataScore(c) {{
  let s = 0;
  if (c.description) s++;
  if (c.funding) s++;
  if (c.users) s++;
  if (c.latestNews) s++;
  return s;
}}

function buildCard(c) {{
  const encName = encodeURIComponent(c.name);
  const newsSearchUrl = `https://www.google.com/search?q=${{encName}}+fintech+news+2025+2026`;
  const fundSearchUrl = `https://www.google.com/search?q=${{encName}}+funding+crunchbase+raised`;
  const revSearchUrl = `https://www.google.com/search?q=${{encName}}+user+reviews+reddit+trustpilot`;
  const websiteUrl = c.website || `https://www.google.com/search?q=${{encName}}+official+website`;

  // Description block — only if verified
  let descHtml = '';
  if (c.description) {{
    const srcLink = c.descriptionSource
      ? `<a href="${{c.descriptionSource}}" target="_blank">source ↗</a>`
      : '';
    descHtml = `<div class="desc-block">
      <div class="desc-text">${{c.description}}</div>
      ${{srcLink ? `<div class="desc-source">${{srcLink}}</div>` : ''}}
    </div>`;
  }}

  // Facts — only show verified ones
  let factsHtml = '';
  const facts = [];

  if (c.funding) {{
    const srcLink = c.fundingSource ? `<a href="${{c.fundingSource}}" target="_blank">source ↗</a>` : '';
    const dateStr = c.fundingDate ? ` · ${{c.fundingDate}}` : '';
    facts.push(`<div class="fact-row">
      <div class="fact-label"><span class="fact-verified-dot"></span>Total Funding</div>
      <div class="fact-value">${{c.funding}}</div>
      <div class="fact-meta">${{dateStr}}${{srcLink ? ' · ' + srcLink : ''}}</div>
    </div>`);
  }}

  if (c.users) {{
    const srcLink = c.usersSource ? `<a href="${{c.usersSource}}" target="_blank">source ↗</a>` : '';
    facts.push(`<div class="fact-row">
      <div class="fact-label"><span class="fact-verified-dot"></span>Users</div>
      <div class="fact-value">${{c.users}}</div>
      <div class="fact-meta">${{srcLink}}</div>
    </div>`);
  }}

  if (facts.length > 0) {{
    factsHtml = `<div class="facts-grid">${{facts.join('')}}</div>`;
  }}

  // Latest news — only if verified
  let newsHtml = '';
  if (c.latestNews) {{
    const newsLink = c.latestNewsUrl ? `<a href="${{c.latestNewsUrl}}" target="_blank">Read →</a>` : '';
    const dateStr = c.latestNewsDate ? `${{c.latestNewsDate}} · ` : '';
    newsHtml = `<div class="news-block">
      <div class="news-label"><span class="fact-verified-dot"></span>Latest News</div>
      <div class="news-text">${{c.latestNews}}</div>
      <div class="news-meta">${{dateStr}}${{newsLink}}</div>
    </div>`;
  }}

  // If nothing verified at all
  const hasAnyData = c.description || c.funding || c.users || c.latestNews;
  const noDataHtml = !hasAnyData
    ? `<div class="no-data-note">No publicly available data found at generation time.</div>`
    : '';

  return `<div class="card" data-id="${{c.id}}" data-geo="${{c.geo.toLowerCase()}}" data-has-data="${{hasAnyData ? '1' : '0'}}">
    <div class="card-top">
      <div>
        <div class="card-name">${{c.name}}</div>
        <div class="card-cat">${{c.category}}</div>
      </div>
      <div class="badges">
        <span class="geo-badge">${{c.geo}}</span>
      </div>
    </div>
    ${{descHtml}}
    ${{factsHtml}}
    ${{newsHtml}}
    ${{noDataHtml}}
    <div class="links">
      ${{c.website ? `<a class="link-btn primary" href="${{c.website}}" target="_blank">Website ↗</a>` : ''}}
      <a class="link-btn" href="${{newsSearchUrl}}" target="_blank">News</a>
      <a class="link-btn" href="${{fundSearchUrl}}" target="_blank">Funding</a>
      <a class="link-btn" href="${{revSearchUrl}}" target="_blank">Reviews</a>
    </div>
  </div>`;
}}

function render() {{
  const indiaGrid = document.getElementById('india-grid');
  const globalGrid = document.getElementById('global-grid');
  indiaGrid.innerHTML = '';
  globalGrid.innerHTML = '';

  let sorted = [...COMPETITORS];
  if (currentSort === 'name') sorted.sort((a,b) => a.name.localeCompare(b.name));
  else if (currentSort === 'geo') sorted.sort((a,b) => a.geo === 'India' ? -1 : 1);
  else if (currentSort === 'data') sorted.sort((a,b) => dataScore(b) - dataScore(a));

  let indiaVisible = 0, globalVisible = 0;

  sorted.forEach(c => {{
    const geoMatch =
      currentFilter === 'all' ||
      (currentFilter === 'india' && c.geo === 'India') ||
      (currentFilter === 'global' && c.geo === 'Global') ||
      (currentFilter === 'verified' && c['has-data'] !== '0' && (c.description || c.funding || c.users || c.latestNews));

    const searchMatch = !currentSearch ||
      c.searchName.includes(currentSearch) ||
      c.category.toLowerCase().includes(currentSearch) ||
      c.geo.toLowerCase().includes(currentSearch);

    // For verified filter, check data directly
    const verifiedMatch = currentFilter !== 'verified' ||
      (c.description || c.funding || c.users || c.latestNews);

    if ((currentFilter === 'verified' ? verifiedMatch : geoMatch) && searchMatch) {{
      const html = buildCard(c);
      if (c.geo === 'India') {{ indiaGrid.innerHTML += html; indiaVisible++; }}
      else {{ globalGrid.innerHTML += html; globalVisible++; }}
    }}
  }});

  document.getElementById('india-divider').style.display = indiaVisible ? '' : 'none';
  document.getElementById('global-divider').style.display = globalVisible ? '' : 'none';
}}

function setFilter(f, event) {{
  currentFilter = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  if (event && event.target) event.target.classList.add('active');
  render();
}}

function setSearch(val) {{
  currentSearch = val.toLowerCase();
  render();
}}

function setSort(val) {{
  currentSort = val;
  render();
}}

render();
</script>
</body>
</html>"""
    return html


def push_radar_to_github(html_content: str) -> bool:
    if not GITHUB_TOKEN:
        print("No GITHUB_TOKEN — skipping radar push")
        return False
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/radar.html"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "bharosa-briefing"
        }
        sha = None
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req) as resp:
                sha = json.loads(resp.read()).get("sha")
        except urllib.error.HTTPError as e:
            if e.code != 404:
                print(f"  GitHub GET error: {e.code}")
        content_b64 = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")
        today = datetime.now().strftime("%B %d, %Y")
        payload = {"message": f"Radar update {today}", "content": content_b64}
        if sha:
            payload["sha"] = sha
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers=headers, method="PUT")
        with urllib.request.urlopen(req) as resp:
            if resp.status in (200, 201):
                print(f"  Radar pushed successfully → {RADAR_URL}")
                return True
            print(f"  Push failed: {resp.status}")
            return False
    except Exception as e:
        print(f"  Radar push error: {e}")
        return False


# --- BRIEFING ---

SYSTEM_PROMPT = """You are Bharosa's daily intelligence engine.

BHAROSA: Building a personal AI financial advisor — "Jarvis for your money." A system that understands your entire financial life (portfolios, taxes, ESOPs, loans, goals) and answers life questions like "Can I afford this house?" or "Should I exercise my ESOPs now or wait?"

Core moat: A financial CALCULATION ENGINE that does what LLMs can't — accurate math on messy personal data, tax logic, consequence modelling. The "Intel inside" for financial AI. LLMs handle conversation, Bharosa handles the hard math underneath.

India is beachhead. Ambition is global. Financial anxiety is universal.

COMPETITORS TO REFERENCE BY NAME:
India: INDmoney, Groww, Kuvera, ET Money, Scripbox, Wealth Monitor, mProfit, Perfios
Global: Monarch Money, Copilot Money, Wealthfront, Betterment, Orion, Addepar
AI threat: Generic GPT/Claude wrappers giving financial "advice" without real computation

YOUR JOB: Daily memo that makes Sahil and Santosh think "shit, we need to build this" or "this confirms we're early." Not a newsletter. Not a consulting report. A strategic shot of adrenaline.

TONE RULES:
- Write like a sharp operator, not an analyst
- Every signal = 3 lines max: What's happening, Why it matters, What Bharosa should do
- No big words. No "deterministic reasoning" or "orchestration framework"
- Simple, fast, punchy sentences. Like texting a cofounder at 9am.
- Signal first, framing after. Never bury the insight.

SIGNAL QUALITY:
- Reject anything generic. If you can swap "Bharosa" for "any fintech" — kill it.
- Every signal must connect to: messy personal data, calculation engine, life questions, or infrastructure-for-AI positioning
- Competitor mentions must name a specific company and state WHY they can't do what Bharosa does

REPETITION RULES:
- If a topic is in "ALREADY COVERED THIS WEEK" — skip unless major new development
- If referencing covered topic — label "Update:" and state only what is new

SEARCH FOR RAW HUMAN CONVERSATIONS:
- Reddit: r/personalfinance, r/financialindependence, r/fatFIRE, r/Bogleheads, r/UKPersonalFinance, r/IndiaInvestments, r/FIREIndia, r/tax
- Twitter/X: fintech founders, advisors, AI researchers
- Hacker News: AI + finance threads
- ONLY discussion threads with human replies in Worth Reading. Zero articles.

SECTION RULES:
Top Competitor Watch: Most newsworthy competitor move from last 48 hours. Named. Real source only.
AI Radar: 3-4 AI updates from last 24-48 hours. 2 lines max each.
World Signals: 3-4 global developments. 2 lines max each.
Events Radar: Mumbai/Bangalore only. Next 30 days. Skip if nothing found. Flag Mumbai for Santosh.

OUTPUT: Return ONLY raw HTML starting with <!DOCTYPE html>. No markdown. No backticks. No preamble. Stay under 8000 tokens.

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bharosa Intel -- [DATE]</title>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f7;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue',Helvetica,Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f5f5f7;">
<tr><td align="center" style="padding:32px 16px;">
<table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,0.06);">
<tr><td style="background:#1c1c1e;padding:32px 36px 24px;text-align:center;">
  <p style="margin:0 0 6px;font-size:10px;font-weight:600;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Bharosa Intel</p>
  <h1 style="margin:0 0 4px;font-size:24px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">[DATE]</h1>
</td></tr>
<tr><td style="background:#1c1c1e;padding:0 36px 24px;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr><td style="background:rgba(255,159,10,0.12);border-radius:10px;padding:16px 18px;border-left:3px solid #ff9f0a;">
    <p style="margin:0 0 4px;font-size:10px;font-weight:700;letter-spacing:2px;color:#ff9f0a;text-transform:uppercase;">Competitor Watch</p>
    <p style="margin:0 0 4px;font-size:15px;color:#ffffff;line-height:1.5;font-weight:600;">[NAMED COMPETITOR] -- [What they just did. One punchy sentence.]</p>
    <p style="margin:0;font-size:13px;color:#ff9f0a;line-height:1.5;">-- [What this means for Bharosa. What they are still missing.]</p>
  </td></tr>
  </table>
</td></tr>
<tr><td style="background:#fff8f0;padding:14px 36px;border-bottom:1px solid #f2f2f7;">
  <p style="margin:0 0 2px;font-size:10px;font-weight:700;letter-spacing:2px;color:#ff6b00;text-transform:uppercase;">Contrarian Bet</p>
  <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.5;font-weight:600;">[ONE SHARP SENTENCE challenging what most fintech founders believe. Must connect to why Bharosa wins.]</p>
</td></tr>
<tr><td style="padding:24px 36px 32px;">
<p style="margin:0 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">User Signals</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:16px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;border-left:3px solid #007aff;">
  <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[HEADLINE -- specific user anxiety. Short.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[What is happening -- one sentence from real discussion.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[Why it matters for Bharosa.]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#30d158;line-height:1.6;font-weight:600;">Build: [What Bharosa should build.]</p>
  <p style="margin:0;font-size:12px;color:#8e8e93;">vs <strong>[NAMED COMPETITOR]</strong>: [Why they can't do this.] <a href="[THREAD_URL]" style="color:#007aff;text-decoration:none;">Source</a></p>
</td></tr>
</table>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;border-left:3px solid #ff453a;">
  <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[HEADLINE -- trust barrier or AI resistance]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[What users are saying.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[Why it matters -- how Bharosa should present itself.]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#30d158;line-height:1.6;font-weight:600;">Build: [Specific UX or positioning action.]</p>
  <p style="margin:0;font-size:12px;color:#8e8e93;">vs <strong>[NAMED COMPETITOR]</strong>: [One sentence.] <a href="[THREAD_URL]" style="color:#007aff;text-decoration:none;">Source</a></p>
</td></tr>
</table>
<p style="margin:0 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">AI Capability for Bharosa</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;border-left:3px solid #af52de;">
  <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[HEADLINE -- AI development that changes what Bharosa can build]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[What changed.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[Why it matters for Bharosa specifically.]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#30d158;line-height:1.6;font-weight:600;">Do: [Specific action this week.]</p>
  <p style="margin:0;font-size:12px;color:#8e8e93;"><a href="[SOURCE_URL]" style="color:#007aff;text-decoration:none;">Source</a></p>
</td></tr>
</table>
<p style="margin:0 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Competitor and Market</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:12px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;">
  <p style="margin:0 0 6px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[NAMED COMPETITOR] -- [What they did]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[Where they stop -- life question they cannot answer.]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#007aff;line-height:1.6;font-weight:600;">Bharosa edge: [Architectural reason.]</p>
  <p style="margin:0;font-size:12px;color:#8e8e93;"><a href="[SOURCE_URL]" style="color:#007aff;text-decoration:none;">Source</a></p>
</td></tr>
</table>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;">
  <p style="margin:0 0 6px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[REGULATORY/MARKET SHIFT]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[What changed and why it matters.]</p>
  <p style="margin:0;font-size:14px;color:#30d158;line-height:1.6;font-weight:600;">Opportunity: [One sentence.]</p>
  <p style="margin:6px 0 0;font-size:12px;color:#8e8e93;"><a href="[SOURCE_URL]" style="color:#007aff;text-decoration:none;">Source</a></p>
</td></tr>
</table>
<p style="margin:0 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">What to Build</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f0faf4;border-radius:10px;padding:16px 18px;border-left:3px solid #30d158;">
  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;font-style:italic;">[ONE sentence synthesising today's signals into a product gap.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#1c1c1e;line-height:1.6;font-weight:700;">1. [FEATURE] -- [What it does, who it's for.]</p>
  <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.6;font-weight:700;">2. [FEATURE] -- [Buildable in 2-4 weeks.]</p>
</td></tr>
</table>
<p style="margin:0 0 6px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">AI Radar</p>
<p style="margin:0 0 12px;font-size:12px;color:#8e8e93;">What moved in AI today. Stay sharp.</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f5f0ff;border-radius:10px;padding:16px 18px;">
  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;"><strong style="color:#af52de;">&#9679;</strong>&nbsp;&nbsp;<strong>[AI UPDATE 1]</strong><br><span style="color:#3a3a3c;">[One sentence.]</span><br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source</a></span></p>
  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;"><strong style="color:#af52de;">&#9679;</strong>&nbsp;&nbsp;<strong>[AI UPDATE 2]</strong><br><span style="color:#3a3a3c;">[One sentence.]</span><br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source</a></span></p>
  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;"><strong style="color:#af52de;">&#9679;</strong>&nbsp;&nbsp;<strong>[AI UPDATE 3]</strong><br><span style="color:#3a3a3c;">[One sentence.]</span><br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source</a></span></p>
  <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.6;"><strong style="color:#af52de;">&#9679;</strong>&nbsp;&nbsp;<strong>[AI UPDATE 4]</strong><br><span style="color:#3a3a3c;">[One sentence.]</span><br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source</a></span></p>
</td></tr>
</table>
<p style="margin:0 0 6px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">World Signals</p>
<p style="margin:0 0 12px;font-size:12px;color:#8e8e93;">Things a well-informed founder should know today.</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f0f7ff;border-radius:10px;padding:16px 18px;">
  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;"><strong style="color:#007aff;">&#9679;</strong>&nbsp;&nbsp;<strong>[WORLD SIGNAL 1]</strong><br><span style="color:#3a3a3c;">[One sentence.]</span><br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source</a></span></p>
  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;"><strong style="color:#007aff;">&#9679;</strong>&nbsp;&nbsp;<strong>[WORLD SIGNAL 2]</strong><br><span style="color:#3a3a3c;">[One sentence.]</span><br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source</a></span></p>
  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;"><strong style="color:#007aff;">&#9679;</strong>&nbsp;&nbsp;<strong>[WORLD SIGNAL 3]</strong><br><span style="color:#3a3a3c;">[One sentence.]</span><br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source</a></span></p>
  <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.6;"><strong style="color:#007aff;">&#9679;</strong>&nbsp;&nbsp;<strong>[WORLD SIGNAL 4]</strong><br><span style="color:#3a3a3c;">[One sentence.]</span><br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source</a></span></p>
</td></tr>
</table>
<p style="margin:0 0 6px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Events Radar</p>
<p style="margin:0 0 12px;font-size:12px;color:#8e8e93;">Upcoming in Mumbai and Bangalore worth your time.</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f0fff4;border-radius:10px;padding:16px 18px;border-left:3px solid #30d158;">
  <p style="margin:0 0 12px;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong>[EVENT NAME]</strong>
    <span style="background:#e8f5e9;color:#30d158;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;margin-left:8px;text-transform:uppercase;">[CITY]</span>
    <span style="background:#f2f2f7;color:#636366;font-size:10px;font-weight:600;padding:2px 8px;border-radius:4px;margin-left:4px;">[DATE]</span><br>
    <span style="color:#3a3a3c;">[Why relevant.]</span><br>
    <span style="color:#30d158;font-size:13px;font-weight:600;">[IF MUMBAI: Santosh, this is in your city.]</span>
    <span style="font-size:12px;color:#8e8e93;margin-left:8px;"><a href="[EVENT_URL]" style="color:#007aff;text-decoration:none;">Details</a></span>
  </p>
</td></tr>
</table>
<p style="margin:0 0 6px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Worth Reading</p>
<p style="margin:0 0 12px;font-size:12px;color:#8e8e93;">Real discussions. Not articles. Build intuition.</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;">
  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;"><span style="background:#ff4500;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">r/</span><a href="[REDDIT_URL_1]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br><span style="font-size:12px;color:#8e8e93;">[Why read]</span></p>
  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;"><span style="background:#000000;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">X</span><a href="[TWITTER_URL_1]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br><span style="font-size:12px;color:#8e8e93;">[Why read]</span></p>
  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;"><span style="background:#ff6600;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">HN</span><a href="[HN_URL]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br><span style="font-size:12px;color:#8e8e93;">[Why read]</span></p>
  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;"><span style="background:#ff4500;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">r/</span><a href="[REDDIT_URL_2]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br><span style="font-size:12px;color:#8e8e93;">[Why read]</span></p>
  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;"><span style="background:#ff4500;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">r/</span><a href="[REDDIT_URL_3]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br><span style="font-size:12px;color:#8e8e93;">[Why read]</span></p>
  <p style="margin:0;font-size:14px;line-height:1.6;"><span style="background:#000000;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">X</span><a href="[TWITTER_URL_2]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br><span style="font-size:12px;color:#8e8e93;">[Why read]</span></p>
</td></tr>
</table>
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="background:#1c1c1e;border-radius:10px;padding:22px;text-align:center;">
  <p style="margin:0;font-size:16px;font-weight:600;color:#ffffff;line-height:1.5;">[ONE SENTENCE. The thing Sahil should remember all day. Make it stick.]</p>
</td></tr>
</table>
</td></tr>
<tr><td style="padding:20px 36px;text-align:center;border-top:1px solid #f2f2f7;">
  <p style="margin:0;font-size:11px;color:#aeaeb2;">Bharosa Intel -- [DATE]</p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""

USER_MESSAGE = """Generate today's Bharosa intelligence memo. Today is {date}.

{coverage_context}

SEARCH -- do all of these:
0. Competitor news first: "Groww new feature 2026" + "INDmoney launch 2026" + "Monarch Money update 2026" + "Wealthfront AI 2026"
1. Reddit: "reddit personal finance AI tool" + "reddit ESOP tax decision" + "reddit financial planning frustration"
2. Twitter/X: "AI financial advisor" + "personal finance AI"
3. Hacker News: "site:news.ycombinator.com personal finance AI"
4. Regulatory: recent SEBI, SEC, tax changes
5. AI news: latest model launches, AI company moves, capability upgrades
6. World news: major global events, India developments
7. Events: "fintech summit Mumbai 2026" + "wealth conference Bangalore 2026" + "AI summit Mumbai 2026"

RULES:
- 3 lines max per signal. AI/World items 2 lines max.
- No consulting language. Cofounder voice at 9am.
- All 6 Worth Reading links must be DISCUSSION THREADS only
- Name specific competitors always
- Events Radar: skip entirely if nothing found in next 30 days
- Covered topics: skip unless major new development, label "Update:"

Return only complete HTML. No markdown. No backticks."""

USER_MESSAGE_MONDAY = """Generate today's Bharosa intelligence memo. Today is {date} — Monday edition.

{coverage_context}

SEARCH -- do all of these:
0. Competitor news: "Groww new feature 2026" + "INDmoney launch 2026" + "Monarch Money update 2026"
1. WEEK IN REVIEW: biggest fintech, AI, India startup stories from last 7 days -- 5 sharp bullets
2. Reddit: "reddit personal finance AI tool" + "reddit ESOP tax decision"
3. Twitter/X: "AI financial advisor" + "personal finance AI"
4. Hacker News: "site:news.ycombinator.com personal finance AI"
5. Regulatory: recent SEBI, SEC, tax changes
6. AI news: latest model launches, AI company moves
7. World news: major global events, India developments
8. Events: "fintech summit Mumbai 2026" + "wealth conference Bangalore 2026" + "AI summit Mumbai 2026"

MONDAY SPECIAL -- include "Last Week" section right after Contrarian Bet, before User Signals:

<p style="margin:24px 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Last Week</p>
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;border-left:3px solid #ff9f0a;">
  <p style="margin:0 0 8px;font-size:13px;font-weight:700;color:#ff9f0a;text-transform:uppercase;letter-spacing:1px;">Week in Review</p>
  <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.7;">&#9679;&nbsp; [BIGGEST STORY]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.7;">&#9679;&nbsp; [SECOND DEVELOPMENT]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.7;">&#9679;&nbsp; [THIRD DEVELOPMENT]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.7;">&#9679;&nbsp; [FOURTH DEVELOPMENT]</p>
  <p style="margin:0;font-size:14px;color:#3a3a3c;line-height:1.7;">&#9679;&nbsp; [FIFTH DEVELOPMENT]</p>
</td></tr>
</table>

RULES:
- 3 lines max per signal. AI/World 2 lines max.
- No consulting language. Cofounder voice at 9am.
- All 6 Worth Reading links must be DISCUSSION THREADS only
- Name specific competitors always
- Events Radar: skip if nothing found
- Whole note readable in under 5 minutes

Return only complete HTML. No markdown. No backticks."""


def inject_radar_button(html_content: str, radar_url: str) -> str:
    radar_block = f"""
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:32px 0 0;border-top:1px solid #e5e5ea;">
  <tr><td style="padding:28px 36px 0;">
    <p style="margin:0 0 6px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Competitor Radar</p>
    <p style="margin:0 0 4px;font-size:13px;color:#8e8e93;line-height:1.5;">50 companies. Facts only — sourced via live web search. No scores. No estimates. If we couldn't verify it, it's not shown.</p>
    <p style="margin:0 0 20px;font-size:12px;color:#30d158;">Every data point has a clickable source link.</p>
    <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;">
      <tr>
        <td style="padding-right:10px;"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="background:#f2f2f7;border-radius:8px;padding:10px 16px;text-align:center;"><p style="margin:0;font-size:18px;font-weight:700;color:#1c1c1e;font-family:monospace;">50</p><p style="margin:2px 0 0;font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#98989d;">Tracked</p></td></tr></table></td>
        <td style="padding-right:10px;"><table cellpadding="0" cellspacing="0" border="0"><tr><td style="background:#f2f2f7;border-radius:8px;padding:10px 16px;text-align:center;"><p style="margin:0;font-size:18px;font-weight:700;color:#007aff;font-family:monospace;">20</p><p style="margin:2px 0 0;font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#98989d;">India</p></td></tr></table></td>
        <td><table cellpadding="0" cellspacing="0" border="0"><tr><td style="background:#f2f2f7;border-radius:8px;padding:10px 16px;text-align:center;"><p style="margin:0;font-size:18px;font-weight:700;color:#30d158;font-family:monospace;">&#10003;</p><p style="margin:2px 0 0;font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#98989d;">Verified</p></td></tr></table></td>
      </tr>
    </table>
    <table cellpadding="0" cellspacing="0" border="0" style="margin-bottom:16px;">
      <tr><td style="background:#1c1c1e;border-radius:10px;">
        <a href="{radar_url}" style="display:inline-block;padding:14px 32px;font-size:14px;font-weight:700;color:#ffffff;text-decoration:none;font-family:-apple-system,BlinkMacSystemFont,sans-serif;">Open Competitor Radar &nbsp;&#8594;</a>
      </td></tr>
    </table>
    <p style="margin:0;font-size:11px;color:#aeaeb2;">Opens in browser. Generated fresh this morning via live web search.</p>
  </td></tr>
</table>
"""
    if "</body>" in html_content:
        return html_content.replace("</body>", radar_block + "\n</body>", 1)
    return html_content + radar_block


def generate_briefing(client):
    today = datetime.now().strftime("%B %d, %Y")
    is_monday = datetime.now().weekday() == 0
    covered_topics = load_coverage_log()
    coverage_context = format_coverage_context(covered_topics)
    template = USER_MESSAGE_MONDAY if is_monday else USER_MESSAGE

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": template.format(date=today, coverage_context=coverage_context)}]
    )

    html_content = ""
    for block in response.content:
        if block.type == "text":
            text = block.text.strip()
            if "<!DOCTYPE" in text:
                html_content = text[text.index("<!DOCTYPE"):]
                break

    html_content = html_content.replace("```html", "").replace("```", "").strip()
    if html_content and not html_content.strip().endswith("</html>"):
        html_content += "\n</body></html>"

    if html_content:
        save_coverage_log(extract_topics_from_html(html_content))

    return html_content


def send_email(html_content):
    today = datetime.now().strftime("%B %d, %Y")
    is_monday = datetime.now().weekday() == 0
    subject = f"Bharosa Intel -- {'Monday Edition' if is_monday else today}"

    recipients = [
        "santosh@bharosa.finance",
        "prachi.khushlani@bharosa.finance",
        "arjit@bharosa.finance",
        "ayush@bharosa.finance",
        "lynelle@bharosa.finance",
        "abhishekraju.private@gmail.com",
        "ujjwal@bharosa.finance",
        "sahil@bharosa.finance",
    ]

    final_html = inject_radar_button(html_content, RADAR_URL)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Bharosa Intel <{GMAIL_USER}>"
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(f"Bharosa Intel -- {today}\n\nOpen in HTML email client to view.", "plain"))
    msg.attach(MIMEText(final_html, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, recipients, msg.as_string())

    print(f"Email sent to {len(recipients)} recipients")


if __name__ == "__main__":
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    print("Step 1: Generating daily briefing...")
    briefing_html = generate_briefing(client)
    print("Briefing generated.")

    print("Step 2: Researching 50 competitors via web search...")
    radar_data = generate_radar_data(client)
    print("Research complete.")

    print("Step 3: Building Radar HTML...")
    generated_at = datetime.now().strftime("%B %d, %Y at %I:%M %p IST")
    radar_html = build_radar_html(radar_data, generated_at)
    print("Radar HTML built.")

    print("Step 4: Pushing Radar to GitHub Pages...")
    push_radar_to_github(radar_html)

    print("Step 5: Sending email...")
    send_email(briefing_html)

    print("All done!")
