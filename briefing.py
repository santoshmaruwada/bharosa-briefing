"""
briefing.py — Bharosa Morning Intelligence Brief
─────────────────────────────────────────────────
Runs Mon / Wed / Fri via GitHub Actions.
Calls Anthropic API (claude-sonnet-4-6, web_search enabled).
Sends one HTML email to the full team.

GitHub Secrets required:
  ANTHROPIC_API_KEY
  GMAIL_USER          sender Gmail address
  GMAIL_APP_PASSWORD  Gmail app password (Google Account → Security → App passwords)

Run locally:
  export ANTHROPIC_API_KEY=sk-ant-...
  export GMAIL_USER=you@gmail.com
  export GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
  python briefing.py
"""

import anthropic
import json
import os
import re
import smtplib
import sys
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


# ── Config ─────────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY  = os.environ["ANTHROPIC_API_KEY"]
GMAIL_USER         = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]

MODEL      = "claude-sonnet-4-6"
MAX_TOKENS = 16000

RECIPIENTS = [
    "santosh@bharosa.finance",
    "prachi.khushlani@bharosa.finance",
    "arjit@bharosa.finance",
    "ayush@bharosa.finance",
    "lynelle@bharosa.finance",
    "abhishekraju.private@gmail.com",
    "ujjwal@bharosa.finance",
    "sahil@bharosa.finance",
]

COVERAGE_LOG = "coverage_log.json"


# ── Coverage memory (avoids repeating topics within the same week) ──────────

def load_coverage_log():
    if not Path(COVERAGE_LOG).exists():
        return []
    try:
        with open(COVERAGE_LOG, "r") as f:
            data = json.load(f)
        today      = datetime.now()
        log_date   = datetime.fromisoformat(data.get("week_start", "2000-01-01"))
        days_since = (today - log_date).days
        if today.weekday() == 0 or days_since >= 7:
            return []
        return data.get("topics", [])
    except Exception:
        return []


def save_coverage_log(new_topics: list):
    existing   = []
    week_start = datetime.now().isoformat()
    if Path(COVERAGE_LOG).exists():
        try:
            with open(COVERAGE_LOG, "r") as f:
                data = json.load(f)
            today      = datetime.now()
            log_date   = datetime.fromisoformat(data.get("week_start", "2000-01-01"))
            days_since = (today - log_date).days
            if today.weekday() != 0 and days_since < 7:
                existing   = data.get("topics", [])
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
        for m in re.findall(pattern, html, re.DOTALL):
            clean = re.sub(r'<[^>]+>', '', m).strip()
            if 20 < len(clean) < 200:
                topics.append(clean[:150])
    return topics[:20]


def format_coverage_context(topics: list) -> str:
    if not topics:
        return ""
    day_names  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    today_name = day_names[datetime.now().weekday()]
    lines = "\n".join(f"- {t}" for t in topics)
    return (
        f"ALREADY COVERED THIS WEEK - DO NOT REPEAT:\n{lines}\n\n"
        f"Today is {today_name}. Find fresh signals the team has not seen yet this week. "
        f"If you must reference a covered topic, label it 'Update:' and state only what is new."
    )


# ── Prompts ─────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the strategic intelligence engine for Bharosa - a high-fidelity personal finance AI for India.

WHAT BHAROSA IS:
Bharosa is a deterministic financial truth engine, not a chatbot layered on finance.
It replaces the blind spots of general AI with:
  - Zero-hallucination calculation: XIRR, CAGR, LTCG/STCG, demergers, splits, bonuses - exact
  - Messy data ingestion: duplicate transactions, corrupt imports, corporate actions - handled
  - Sovereign architecture: runs fully on-device or private cloud, data never leaves the user
  - India-specific regulatory logic: SEBI, AMFI, ITR schedules - baked in, not bolted on
  - Family office logic for everyone: the intelligence a 500Cr AUM client gets, for 50L

WHAT BHAROSA IS NOT: a chatbot, a robo-advisor, a CA tool, a tax filer, an Indian fintech brand.

YOUR JOB: A Mon/Wed/Fri intelligence note that makes Sahil and Santosh think
"shit, we need to build this" or "this confirms we're early."
Not a newsletter. Not a consulting report. A strategic shot of adrenaline.

YOUR AUDIENCE - two personas in one email:
  1. GROWTH AND STRATEGY (Santosh) - competitive moves, consumer signals, GTM triggers, battle card updates, regulatory narratives
  2. ENGINEERING AND PRODUCT (Ujjwal and devs) - build signals, architecture decisions, accuracy benchmarks, India data moats, sovereign stack triggers

TONE RULES:
  - Write like a sharp operator, not an analyst
  - Every signal = 3 lines max: What's happening / Why it matters / What Bharosa should do
  - No big words. Simple, fast, punchy sentences. Like texting a cofounder at 9am.
  - Signal first, framing after. Never bury the insight.

SIGNAL QUALITY - enforce strictly:
  - Reject any signal that could apply to any fintech startup. Must be specific to Bharosa's exact positioning.
  - Every threat must name the specific competitor or regulatory body
  - Every build signal must name the exact feature or architectural decision implied
  - Source every signal with a real URL from your searches
  - The contrarian take must challenge something the Indian IFA/MFD/fintech industry CURRENTLY believes

SIGNAL TAXONOMY - use exactly these labels:
  THREAT - competitor move or regulatory shift directly threatening Bharosa's positioning
  BUILD  - consumer signal or technical development implying Bharosa should build something specific
  WATCH  - slow-moving signal needing monitoring before action
  INFO   - market fact that strengthens Bharosa's existing narrative

SECTIONS TO PRODUCE in this exact order:
  1. HEADER - date, day, signal count summary
  2. TOP SIGNAL - single most important insight, 3 sentences max, immediate action
  3. COMPETITIVE RADAR (Growth) - 3 signals about Perplexity Finance, Claude Cowork, INDmoney, Groww, Smallcase, Zerodha, Perfios, or any new entrant
  4. MARKET AND CONSUMER SIGNALS (Growth) - 2-3 signals from Reddit/Twitter/HN/Quora threads about Indian investor pain points
  5. REGULATORY WATCH (Growth) - 1-2 signals from SEBI, RBI, AMFI, MeitY, ITR
  6. BUILD SIGNALS (Engineering) - 3-4 signals implying specific features or architectural work
  7. INDIA DATA MOAT (Engineering) - 1 signal about a gap in India financial data infrastructure Bharosa can own
  8. CONTRARIAN TAKE - one sharp paragraph challenging a belief the Indian fintech/IFA industry holds right now
  9. BATTLE CARD UPDATE - one specific competitor comparison row that needs updating today, and why
  10. WORTH READING - 4-6 actual Reddit/HN/Twitter DISCUSSION THREADS (not articles), with a one-line why-read each
  11. FOLLOW-UP PROMPTS - 3 questions the reader can ask their AI to go deeper

MONDAY ONLY - insert a LAST WEEK section between TOP SIGNAL and COMPETITIVE RADAR:
  - 5 bullet points: biggest fintech, AI, India startup, regulatory, and world stories from the past 7 days
  - Each bullet: one punchy sentence. Real event. Real source.

MANDATORY SEARCH SEQUENCE - run ALL before writing a single word:
  1. Perplexity Finance portfolio India 2026
  2. Claude financial services wealth management 2026
  3. site:reddit.com mutual fund IFA advisor India complaint
  4. site:reddit.com XIRR portfolio tracker India
  5. SEBI AI financial advice regulation India 2026
  6. Groww OR INDmoney OR Smallcase AI feature launch 2026
  7. India fintech personal finance AI launch 2026
  8. RBI data localisation financial data India 2026
  9. on-device LLM finance edge inference 2026
  10. NPS EPF CDSL data API India fintech 2026

OUTPUT: Return ONLY raw HTML starting with <!DOCTYPE html>. Inline CSS only (no style tags). No markdown. No preamble."""


USER_PROMPT_BASE = """Generate today's Bharosa Morning Brief. Today is {date}, {day}.

{coverage_context}

{monday_instruction}

Run ALL 10 searches in the mandatory sequence before writing anything.

QUALITY GATE - verify before finalising:
  - Every signal names a specific company, product, or regulatory body
  - Every action line is concrete (not "monitor this" unless it is a WATCH signal)
  - The contrarian take is about Indian IFA/fintech beliefs specifically, not generic AI skepticism
  - The battle card update names the specific row and the specific change needed
  - Worth Reading has actual discussion thread URLs (Reddit/HN/Twitter), not editorial articles
  - All source URLs came from your searches

Replace ALL placeholders with real content. Return ONLY complete HTML starting with <!DOCTYPE html>.

HTML TEMPLATE:

<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bharosa Brief - DATE_PLACEHOLDER</title></head>
<body style="margin:0;padding:0;background-color:#f5f5f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f5f5f7;">
<tr><td align="center" style="padding:32px 16px;">
<table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;">

<tr><td style="background:#1c1c1e;padding:32px 36px 20px;">
  <p style="margin:0 0 4px;font-size:10px;font-weight:600;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Bharosa Intelligence</p>
  <p style="margin:0 0 16px;font-size:24px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">Morning Brief - [INSERT FULL DATE]</p>
  <table cellpadding="0" cellspacing="0"><tr>
    <td style="background:#3a0e0e;border-radius:6px;padding:4px 10px;"><span style="font-size:11px;font-weight:700;color:#ff6b6b;">[N] Threats</span></td>
    <td style="width:6px;"></td>
    <td style="background:#0a2e1a;border-radius:6px;padding:4px 10px;"><span style="font-size:11px;font-weight:700;color:#34c759;">[N] Build</span></td>
    <td style="width:6px;"></td>
    <td style="background:#2e2200;border-radius:6px;padding:4px 10px;"><span style="font-size:11px;font-weight:700;color:#ff9f0a;">[N] Watch</span></td>
    <td style="width:6px;"></td>
    <td style="background:#001a2e;border-radius:6px;padding:4px 10px;"><span style="font-size:11px;font-weight:700;color:#0a84ff;">[N] Info</span></td>
  </tr></table>
</td></tr>

<tr><td style="padding:24px 36px 0;">
  <p style="margin:0 0 10px;font-size:10px;font-weight:700;letter-spacing:2px;color:#98989d;text-transform:uppercase;">Top signal today</p>
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#fff9e6;border-radius:10px;border-left:3px solid #ff9f0a;">
  <tr><td style="padding:16px 18px;">
    <p style="margin:0 0 6px;font-size:15px;font-weight:700;color:#1c1c1e;">[TOP SIGNAL HEADLINE]</p>
    <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.6;">[TOP SIGNAL BODY - 2 sentences]</p>
    <p style="margin:0;font-size:13px;font-weight:700;color:#ff9500;">-> [TOP SIGNAL ACTION - one concrete thing]</p>
  </td></tr>
  </table>
</td></tr>

[MONDAY ONLY: INSERT LAST WEEK BLOCK HERE - see pattern below]

<tr><td style="padding:24px 36px 4px;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#636366;text-transform:uppercase;">Growth and Strategy</p>
</td></tr>

<tr><td style="padding:8px 36px 0;">
  <p style="margin:0 0 10px;font-size:12px;font-weight:600;color:#98989d;text-transform:uppercase;letter-spacing:1px;">Competitive radar</p>
  [INSERT 3 SIGNAL BLOCKS - see signal block pattern below]
</td></tr>

<tr><td style="padding:20px 36px 0;">
  <p style="margin:0 0 10px;font-size:12px;font-weight:600;color:#98989d;text-transform:uppercase;letter-spacing:1px;">Market and consumer signals</p>
  [INSERT 2-3 SIGNAL BLOCKS]
</td></tr>

<tr><td style="padding:20px 36px 0;">
  <p style="margin:0 0 10px;font-size:12px;font-weight:600;color:#98989d;text-transform:uppercase;letter-spacing:1px;">Regulatory watch</p>
  [INSERT 1-2 SIGNAL BLOCKS]
</td></tr>

<tr><td style="padding:24px 36px 4px;border-top:1px solid #f2f2f7;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#007aff;text-transform:uppercase;">Engineering and Product</p>
</td></tr>

<tr><td style="padding:8px 36px 0;">
  <p style="margin:0 0 10px;font-size:12px;font-weight:600;color:#98989d;text-transform:uppercase;letter-spacing:1px;">Build signals</p>
  [INSERT 3-4 SIGNAL BLOCKS]
</td></tr>

<tr><td style="padding:20px 36px 0;">
  <p style="margin:0 0 10px;font-size:12px;font-weight:600;color:#98989d;text-transform:uppercase;letter-spacing:1px;">India data moat - own this before anyone else</p>
  [INSERT 1 SIGNAL BLOCK with border-left:3px solid #30d158 on the outer table]
</td></tr>

<tr><td style="padding:24px 36px 0;border-top:1px solid #f2f2f7;">
  <p style="margin:0 0 10px;font-size:10px;font-weight:700;letter-spacing:2px;color:#98989d;text-transform:uppercase;">Contrarian take</p>
  <table width="100%" cellpadding="0" cellspacing="0" style="border-left:3px solid #ff375f;background:#fff5f7;border-radius:0 8px 8px 0;">
  <tr><td style="padding:14px 18px;">
    <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.7;">[CONTRARIAN PARAGRAPH - challenges a specific Indian IFA/MFD belief]</p>
  </td></tr>
  </table>
</td></tr>

<tr><td style="padding:20px 36px 0;">
  <p style="margin:0 0 10px;font-size:10px;font-weight:700;letter-spacing:2px;color:#98989d;text-transform:uppercase;">Battle card update</p>
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9f9fb;border-radius:10px;border-left:3px solid #007aff;">
  <tr><td style="padding:14px 18px;">
    <p style="margin:0 0 4px;font-size:11px;font-weight:700;color:#636366;text-transform:uppercase;letter-spacing:1px;">Row: [SPECIFIC ROW NAME e.g. Direct Portfolio Ingestion]</p>
    <p style="margin:0 0 8px;font-size:14px;color:#1c1c1e;line-height:1.6;">[WHY THIS ROW NEEDS UPDATING TODAY]</p>
    <p style="margin:0;font-size:13px;font-weight:700;color:#007aff;">-> [SPECIFIC CHANGE TO MAKE]</p>
  </td></tr>
  </table>
</td></tr>

<tr><td style="padding:20px 36px 0;">
  <p style="margin:0 0 4px;font-size:10px;font-weight:700;letter-spacing:2px;color:#98989d;text-transform:uppercase;">Worth reading</p>
  <p style="margin:0 0 12px;font-size:12px;color:#8e8e93;">Real discussions. Not articles. Build intuition.</p>
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9f9fb;border-radius:10px;">
  <tr><td style="padding:16px 18px;">
    [INSERT 4-6 WORTH READING ITEMS - see pattern below]
  </td></tr>
  </table>
</td></tr>

<tr><td style="padding:20px 36px 28px;">
  <p style="margin:0 0 10px;font-size:10px;font-weight:700;letter-spacing:2px;color:#98989d;text-transform:uppercase;">Ask your AI to go deeper</p>
  [INSERT 3 FOLLOW-UP PROMPT BLOCKS - see pattern below]
</td></tr>

<tr><td style="background:#f5f5f7;padding:18px 36px;text-align:center;border-top:1px solid #e5e5ea;">
  <p style="margin:0 0 3px;font-size:11px;color:#8e8e93;">Bharosa Intelligence - Mon / Wed / Fri</p>
  <p style="margin:0;font-size:10px;color:#aeaeb2;">Generated [FULL DATE] - Powered by Anthropic + web search</p>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>

SIGNAL BLOCK PATTERN - use for every signal:
<table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e5ea;border-radius:8px;margin-bottom:10px;">
<tr><td style="padding:14px 16px;">
  <table cellpadding="0" cellspacing="0" style="margin-bottom:8px;"><tr>
    <td style="background:[BADGE_BG];border-radius:4px;padding:3px 9px;"><span style="font-size:11px;font-weight:700;color:[BADGE_TEXT];">[LABEL]</span></td>
  </tr></table>
  <p style="margin:0 0 6px;font-size:14px;font-weight:600;color:#1c1c1e;">[HEADLINE - 10 words max, specific]</p>
  <p style="margin:0 0 8px;font-size:13px;color:#3a3a3c;line-height:1.6;">[BODY - what happened and why it matters to Bharosa specifically]</p>
  <p style="margin:0 0 6px;font-size:13px;font-weight:700;color:#34c759;">-> [ACTION - concrete thing Bharosa should do or build]</p>
  <p style="margin:0;font-size:11px;color:#aeaeb2;"><a href="[REAL_SOURCE_URL]" style="color:#007aff;text-decoration:none;">[source domain]</a></p>
</td></tr>
</table>

Badge colours: THREAT bg=#3a0e0e text=#ff6b6b / BUILD bg=#0a2e1a text=#34c759 / WATCH bg=#2e2200 text=#ff9f0a / INFO bg=#001a2e text=#0a84ff

WORTH READING ITEM PATTERN:
<p style="margin:0 0 12px;font-size:14px;line-height:1.6;">
  <span style="background:[PLATFORM_BG];color:#fff;font-size:10px;font-weight:700;padding:2px 7px;border-radius:4px;margin-right:6px;">[PLATFORM]</span>
  <a href="[REAL_THREAD_URL]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br>
  <span style="font-size:12px;color:#8e8e93;">[Why read - one line]</span>
</p>
Platform bg: Reddit #ff4500 / HN #ff6600 / X #000000

FOLLOW-UP PROMPT PATTERN:
<table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e5ea;border-radius:8px;margin-bottom:8px;">
<tr><td style="padding:12px 16px;"><p style="margin:0;font-size:13px;color:#3a3a3c;">[PROMPT QUESTION]</p></td></tr>
</table>

LAST WEEK BLOCK PATTERN (Mondays only - insert after TOP SIGNAL row):
<tr><td style="padding:20px 36px 0;">
  <p style="margin:0 0 10px;font-size:10px;font-weight:700;letter-spacing:2px;color:#98989d;text-transform:uppercase;">Last week</p>
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f9f9fb;border-radius:10px;border-left:3px solid #ff9f0a;">
  <tr><td style="padding:16px 18px;">
    <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.7;">- [STORY 1 - biggest fintech news from last 7 days]</p>
    <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.7;">- [STORY 2 - AI news from last 7 days]</p>
    <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.7;">- [STORY 3 - India startup news from last 7 days]</p>
    <p style="margin:0 0 8px;font-size:14px;color:#3a3a3c;line-height:1.7;">- [STORY 4 - regulatory or policy news]</p>
    <p style="margin:0;font-size:14px;color:#3a3a3c;line-height:1.7;">- [STORY 5 - global markets or macro signal]</p>
  </td></tr>
  </table>
</td></tr>
"""

MONDAY_INSTRUCTION = """MONDAY EDITION: Include the LAST WEEK section between the TOP SIGNAL row and the COMPETITIVE RADAR row.
Search for: biggest fintech news past 7 days, India startup news past 7 days, AI launches past 7 days, global macro past week.
All 5 bullet points must be real events from the last 7 days with specific company/entity names."""


# ── Generation ───────────────────────────────────────────────────────────────

def generate_briefing() -> str:
    client    = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    now       = datetime.now()
    date      = now.strftime("%B %d, %Y")
    day       = now.strftime("%A")
    is_monday = now.weekday() == 0

    covered_topics   = load_coverage_log()
    coverage_context = format_coverage_context(covered_topics)
    monday_instruction = MONDAY_INSTRUCTION if is_monday else ""

    print(f"[briefing] Generating {day}, {date}{' (Monday edition)' if is_monday else ''} ...")

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": USER_PROMPT_BASE.format(
                date=date,
                day=day,
                coverage_context=coverage_context,
                monday_instruction=monday_instruction,
            )
        }]
    )

    html = ""
    for block in response.content:
        if block.type == "text" and block.text.strip():
            html = block.text.strip()

    # Strip markdown code fences if model wrapped output
    html = re.sub(r"^```(?:html)?\s*", "", html, flags=re.IGNORECASE).strip()
    html = re.sub(r"\s*```$", "", html).strip()

    # Find start of actual HTML
    match = re.search(r"<!DOCTYPE html>", html, re.IGNORECASE)
    if match:
        html = html[match.start():]

    if not html.lower().strip().startswith("<!doctype"):
        raise ValueError(f"Model did not return valid HTML. Got: {html[:300]}")

    if not html.strip().lower().endswith("</html>"):
        html += "\n</body></html>"

    print(f"[briefing] HTML generated - {len(html):,} chars")
    save_coverage_log(extract_topics_from_html(html))
    return html


# ── Email delivery ───────────────────────────────────────────────────────────

def send_email(html: str) -> None:
    now       = datetime.now()
    is_monday = now.weekday() == 0
    date_str  = now.strftime("%B %d, %Y")
    subject   = f"Bharosa Brief - {'Monday Edition - ' if is_monday else ''}{date_str}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"Bharosa Intel <{GMAIL_USER}>"
    msg["To"]      = ", ".join(RECIPIENTS)

    plain = f"Bharosa Morning Brief - {date_str}\nOpen in an HTML email client to view."
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html,  "html"))

    print(f"[email] Sending to {len(RECIPIENTS)} recipients via smtp.gmail.com:465 ...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, RECIPIENTS, msg.as_string())
    print(f"[email] Sent: {subject}")


# ── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        html = generate_briefing()
        send_email(html)
        print("[done] Brief delivered.")
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)
