import anthropic
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# --- CONFIG ---
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]
TO_EMAIL = os.environ["TO_EMAIL"]

SYSTEM_PROMPT = """You are Bharosa's daily intelligence engine.

BHAROSA: Building a personal AI financial advisor — "Jarvis for your money." A system that understands your entire financial life (portfolios, taxes, ESOPs, loans, goals) and answers life questions like "Can I afford this house?" or "Should I exercise my ESOPs now or wait?"

Core moat: A financial CALCULATION ENGINE that does what LLMs can't — accurate math on messy personal data, tax logic, consequence modelling. The "Intel inside" for financial AI. LLMs handle conversation, Bharosa handles the hard math underneath.

India is beachhead. Ambition is global. Financial anxiety is universal.

COMPETITORS TO REFERENCE BY NAME:
India: INDmoney, Groww, Kuvera, ET Money, Scripbox, Wealth Monitor, mProfit, Perfios
Global: Monarch Money, Copilot Money, Wealthfront, Betterment, Orion, Addepar
AI threat: Generic GPT/Claude wrappers giving financial "advice" without real computation

YOUR JOB: Daily memo that makes Sahil and Santosh think "shit, we need to build this" or "this confirms we're early." Not a newsletter. Not a consulting report. A strategic shot of adrenaline.

TONE RULES — THIS IS CRITICAL:
- Write like a sharp operator, not an analyst
- Every signal = 3 lines max: What's happening → Why it matters → What Bharosa should do
- No big words. No "deterministic reasoning" or "orchestration framework" or "probabilistic modelling"
- Simple, fast, punchy sentences. Like texting a cofounder, not writing a whitepaper.
- The whole note must be readable in under 4 minutes
- Signal first, framing after. Never bury the insight.
- Create urgency. Create paranoia. Create focus.

SIGNAL QUALITY:
- Reject anything generic. If you can swap "Bharosa" for "any fintech" — kill it.
- Every Bharosa-specific signal must connect to: messy personal data, calculation engine, life questions, or infrastructure-for-AI positioning
- Competitor mentions must name a specific company and state WHY they can't do what Bharosa does (architectural reason, one sentence)
- The AI Radar and World Signals sections are broader — they don't need to be Bharosa-specific. They exist to keep founders informed and pattern-matching across domains.

SEARCH FOR RAW HUMAN CONVERSATIONS:
- Reddit globally: r/personalfinance, r/financialindependence, r/fatFIRE, r/Bogleheads, r/UKPersonalFinance, r/IndiaInvestments, r/FIREIndia, r/tax
- Twitter/X: fintech founders, advisors, AI researchers debating money tools
- Hacker News: AI + finance threads with real skepticism
- ONLY discussion threads with human replies in the Worth Reading section. Zero articles. Zero press releases.

SECTION-SPECIFIC RULES:

AI Radar section:
- 3-4 quick-hit AI updates from the last 24-48 hours
- Can include: model launches, capability upgrades, AI policy moves, major AI company actions, open source releases, research breakthroughs
- Each update = 2 lines max: what happened + why it's interesting
- These are FYI signals — founder should know what's moving in AI today
- If any update has a direct Bharosa implication, flag it with "→ Bharosa angle:" in one sentence

World Signals section:
- 3-4 notable global actions, events, or decisions from the last 24-48 hours
- Can include: regulatory moves, economic shifts, geopolitical events, major company decisions, cultural shifts, India-specific developments
- Each = 2 lines max: what happened + why a founder should care
- Think: things a well-informed founder would want to know at breakfast
- Not everything needs a Bharosa connection — general awareness matters too

OUTPUT: Return ONLY raw HTML starting with <!DOCTYPE html>. No markdown. No backticks. No preamble. Stay under 8000 tokens.

---

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bharosa Intel — [DATE]</title>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f7;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue',Helvetica,Arial,sans-serif;">

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f5f5f7;">
<tr><td align="center" style="padding:32px 16px;">

<table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 2px 16px rgba(0,0,0,0.06);">

<!-- HEADER -->
<tr><td style="background:#1c1c1e;padding:32px 36px 24px;text-align:center;">
  <p style="margin:0 0 6px;font-size:10px;font-weight:600;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Bharosa Intel</p>
  <h1 style="margin:0 0 4px;font-size:24px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">[DATE]</h1>
</td></tr>

<!-- TOP SIGNAL -->
<tr><td style="background:#1c1c1e;padding:0 36px 24px;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr><td style="background:rgba(255,159,10,0.12);border-radius:10px;padding:16px 18px;border-left:3px solid #ff9f0a;">
    <p style="margin:0 0 4px;font-size:10px;font-weight:700;letter-spacing:2px;color:#ff9f0a;text-transform:uppercase;">Build This Week</p>
    <p style="margin:0;font-size:15px;color:#ffffff;line-height:1.5;font-weight:600;">[ONE SENTENCE — the single most important thing to build or prioritise this week. No fluff. Direct.]</p>
  </td></tr>
  </table>
</td></tr>

<!-- NON-CONSENSUS -->
<tr><td style="background:#fff8f0;padding:14px 36px;border-bottom:1px solid #f2f2f7;">
  <p style="margin:0 0 2px;font-size:10px;font-weight:700;letter-spacing:2px;color:#ff6b00;text-transform:uppercase;">Contrarian Bet</p>
  <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.5;font-weight:600;">[ONE SHARP SENTENCE challenging what most fintech founders or users believe about personal finance + AI. Must connect to why Bharosa's approach wins.]</p>
</td></tr>

<!-- BODY -->
<tr><td style="padding:24px 36px 32px;">

<!-- USER SIGNALS -->
<p style="margin:0 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">User Signals</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:16px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;border-left:3px solid #007aff;">
  <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[HEADLINE — specific user anxiety or behaviour. Short.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[What's happening — one sentence paraphrasing real online discussion.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[Why it matters — one sentence connecting to Bharosa's vision.]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#30d158;line-height:1.6;font-weight:600;">→ Build: [What Bharosa should build. One sentence.]</p>
  <p style="margin:0;font-size:12px;color:#8e8e93;">vs <strong>[NAMED COMPETITOR]</strong>: [Why they can't do this — one sentence.] · <a href="[THREAD_URL]" style="color:#007aff;text-decoration:none;">Source →</a></p>
</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;border-left:3px solid #ff453a;">
  <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[HEADLINE — trust barrier or resistance to AI financial tools]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[What users are saying — real sentiment, one sentence.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[Why it matters — what this means for how Bharosa should present itself.]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#30d158;line-height:1.6;font-weight:600;">→ Build: [Specific UX or positioning action.]</p>
  <p style="margin:0;font-size:12px;color:#8e8e93;">vs <strong>[NAMED COMPETITOR]</strong>: [One sentence.] · <a href="[THREAD_URL]" style="color:#007aff;text-decoration:none;">Source →</a></p>
</td></tr>
</table>

<!-- AI CAPABILITY (Bharosa-specific) -->
<p style="margin:0 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">AI Capability for Bharosa</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;border-left:3px solid #af52de;">
  <p style="margin:0 0 8px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[HEADLINE — AI development that changes what Bharosa can build]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[What changed — one sentence. Plain language.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[Why it matters for Bharosa specifically — strengthens the engine, unlocks a feature, etc.]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#30d158;line-height:1.6;font-weight:600;">→ Do: [Specific action this week.]</p>
  <p style="margin:0;font-size:12px;color:#8e8e93;"><a href="[SOURCE_URL]" style="color:#007aff;text-decoration:none;">Source →</a></p>
</td></tr>
</table>

<!-- COMPETITOR + MARKET -->
<p style="margin:0 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Competitor & Market</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:12px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;">
  <p style="margin:0 0 6px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[NAMED COMPETITOR] → [What they did, 5-8 words]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[Where they stop — the life question they still can't answer. One sentence.]</p>
  <p style="margin:0 0 8px;font-size:14px;color:#007aff;line-height:1.6;font-weight:600;">Bharosa edge: [One sentence — architectural reason.]</p>
  <p style="margin:0;font-size:12px;color:#8e8e93;"><a href="[SOURCE_URL]" style="color:#007aff;text-decoration:none;">Source →</a></p>
</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;">
  <p style="margin:0 0 6px;font-size:15px;font-weight:700;color:#1c1c1e;line-height:1.4;">[REGULATORY/MARKET SHIFT — short headline]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#3a3a3c;line-height:1.6;">[What changed and why it matters. One sentence.]</p>
  <p style="margin:0;font-size:14px;color:#30d158;line-height:1.6;font-weight:600;">→ Opportunity: [One sentence.]</p>
  <p style="margin:6px 0 0;font-size:12px;color:#8e8e93;"><a href="[SOURCE_URL]" style="color:#007aff;text-decoration:none;">Source →</a></p>
</td></tr>
</table>

<!-- PRODUCT DIRECTION -->
<p style="margin:0 0 14px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">What to Build</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f0faf4;border-radius:10px;padding:16px 18px;border-left:3px solid #30d158;">
  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;font-style:italic;">[ONE sentence synthesising today's signals into a product gap.]</p>
  <p style="margin:0 0 6px;font-size:14px;color:#1c1c1e;line-height:1.6;font-weight:700;">1. [FEATURE NAME] — [What it does, who it's for, one sentence.]</p>
  <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.6;font-weight:700;">2. [FEATURE NAME] — [Buildable in 2-4 weeks. Addresses a signal from today.]</p>
</td></tr>
</table>

<!-- AI RADAR -->
<p style="margin:0 0 6px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">AI Radar</p>
<p style="margin:0 0 12px;font-size:12px;color:#8e8e93;">What moved in AI today. Stay sharp.</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f5f0ff;border-radius:10px;padding:16px 18px;">

  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong style="color:#af52de;">&#9679;</strong>&nbsp;&nbsp;<strong>[AI UPDATE 1 HEADLINE — 5-8 words]</strong><br>
    <span style="color:#3a3a3c;">[One sentence — what happened and why it's interesting.]</span>
    [IF BHAROSA-RELEVANT: <span style="color:#af52de;font-weight:600;">→ Bharosa angle: [one sentence]</span>]
    <br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source →</a></span>
  </p>

  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong style="color:#af52de;">&#9679;</strong>&nbsp;&nbsp;<strong>[AI UPDATE 2 HEADLINE]</strong><br>
    <span style="color:#3a3a3c;">[One sentence.]</span>
    <br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source →</a></span>
  </p>

  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong style="color:#af52de;">&#9679;</strong>&nbsp;&nbsp;<strong>[AI UPDATE 3 HEADLINE]</strong><br>
    <span style="color:#3a3a3c;">[One sentence.]</span>
    <br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source →</a></span>
  </p>

  <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong style="color:#af52de;">&#9679;</strong>&nbsp;&nbsp;<strong>[AI UPDATE 4 HEADLINE]</strong><br>
    <span style="color:#3a3a3c;">[One sentence.]</span>
    <br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source →</a></span>
  </p>

</td></tr>
</table>

<!-- WORLD SIGNALS -->
<p style="margin:0 0 6px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">World Signals</p>
<p style="margin:0 0 12px;font-size:12px;color:#8e8e93;">Things a well-informed founder should know today.</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f0f7ff;border-radius:10px;padding:16px 18px;">

  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong style="color:#007aff;">&#9679;</strong>&nbsp;&nbsp;<strong>[WORLD SIGNAL 1 — headline, 5-10 words]</strong><br>
    <span style="color:#3a3a3c;">[One sentence — what happened and why a founder should care.]</span>
    <br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source →</a></span>
  </p>

  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong style="color:#007aff;">&#9679;</strong>&nbsp;&nbsp;<strong>[WORLD SIGNAL 2]</strong><br>
    <span style="color:#3a3a3c;">[One sentence.]</span>
    <br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source →</a></span>
  </p>

  <p style="margin:0 0 10px;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong style="color:#007aff;">&#9679;</strong>&nbsp;&nbsp;<strong>[WORLD SIGNAL 3]</strong><br>
    <span style="color:#3a3a3c;">[One sentence.]</span>
    <br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source →</a></span>
  </p>

  <p style="margin:0;font-size:14px;color:#1c1c1e;line-height:1.6;">
    <strong style="color:#007aff;">&#9679;</strong>&nbsp;&nbsp;<strong>[WORLD SIGNAL 4]</strong><br>
    <span style="color:#3a3a3c;">[One sentence.]</span>
    <br><span style="font-size:12px;color:#8e8e93;"><a href="[URL]" style="color:#007aff;text-decoration:none;">Source →</a></span>
  </p>

</td></tr>
</table>

<!-- RAW CONVERSATIONS -->
<p style="margin:0 0 6px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Worth Reading</p>
<p style="margin:0 0 12px;font-size:12px;color:#8e8e93;">Real discussions. Not articles. Build intuition.</p>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:20px;">
<tr><td style="background:#f9f9fb;border-radius:10px;padding:16px 18px;">

  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;">
    <span style="background:#ff4500;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">r/</span>
    <a href="[REDDIT_URL_1]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br>
    <span style="font-size:12px;color:#8e8e93;">[Why read — one line]</span>
  </p>

  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;">
    <span style="background:#000000;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">X</span>
    <a href="[TWITTER_URL_1]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br>
    <span style="font-size:12px;color:#8e8e93;">[Why read]</span>
  </p>

  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;">
    <span style="background:#ff6600;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">HN</span>
    <a href="[HN_URL]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br>
    <span style="font-size:12px;color:#8e8e93;">[Why read]</span>
  </p>

  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;">
    <span style="background:#ff4500;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">r/</span>
    <a href="[REDDIT_URL_2]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br>
    <span style="font-size:12px;color:#8e8e93;">[Why read]</span>
  </p>

  <p style="margin:0 0 10px;font-size:14px;line-height:1.6;">
    <span style="background:#ff4500;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">r/</span>
    <a href="[REDDIT_URL_3]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br>
    <span style="font-size:12px;color:#8e8e93;">[Why read]</span>
  </p>

  <p style="margin:0;font-size:14px;line-height:1.6;">
    <span style="background:#000000;color:white;font-size:10px;font-weight:700;padding:2px 6px;border-radius:4px;margin-right:6px;">X</span>
    <a href="[TWITTER_URL_2]" style="color:#007aff;text-decoration:none;font-weight:600;">[Thread title]</a><br>
    <span style="font-size:12px;color:#8e8e93;">[Why read]</span>
  </p>

</td></tr>
</table>

<!-- TAKEAWAY -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="background:#1c1c1e;border-radius:10px;padding:22px;text-align:center;">
  <p style="margin:0;font-size:16px;font-weight:600;color:#ffffff;line-height:1.5;">[ONE SENTENCE. The thing Sahil should remember all day. Make it stick.]</p>
</td></tr>
</table>

</td></tr>

<!-- FOOTER -->
<tr><td style="padding:20px 36px;text-align:center;border-top:1px solid #f2f2f7;">
  <p style="margin:0;font-size:11px;color:#aeaeb2;">Bharosa Intel · [DATE]</p>
</td></tr>

</table>
</td></tr>
</table>

</body>
</html>"""

USER_MESSAGE = """Generate today's Bharosa intelligence memo. Today is {date}.

SEARCH — do all of these:
1. Reddit GLOBAL: "reddit personal finance AI tool" + "reddit ESOP tax decision" + "reddit financial planning frustration" — r/personalfinance, r/fatFIRE, r/Bogleheads, r/UKPersonalFinance, r/IndiaInvestments, r/tax
2. Twitter/X: "AI financial advisor" + "personal finance AI" — find real debates
3. Hacker News: "site:news.ycombinator.com personal finance AI" or "financial agent"
4. Competitors: recent moves by INDmoney, Groww, Monarch Money, Copilot Money, Wealthfront
5. Regulatory: recent SEBI, SEC, tax changes affecting personal finance
6. AI news today: latest model launches, AI company moves, capability upgrades, AI policy changes, open source releases
7. World news: major global events, economic shifts, regulatory moves, India developments — things a founder should know

WRITING RULES — follow these exactly:
- Every signal = 3 lines max: What's happening / Why it matters / What to build
- AI Radar items = 2 lines max: What happened / Why it's interesting
- World Signal items = 2 lines max: What happened / Why a founder should care
- No consulting language. No "deterministic" or "orchestration" or "probabilistic"
- Write like you're texting a cofounder at 9am
- Signal first, context after. Never bury the insight.
- Whole note readable in under 4 minutes
- All 6 conversation links must be DISCUSSION THREADS, not articles
- Name specific competitors in every comparison

Return only the complete HTML. No markdown. No backticks."""


def generate_briefing():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%B %d, %Y")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": USER_MESSAGE.format(date=today)
        }]
    )

    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    html_content = html_content.replace("```html", "").replace("```", "").strip()
    return html_content


def send_email(html_content):
    today = datetime.now().strftime("%B %d, %Y")
    subject = f"Bharosa Intel — {today}"

    recipients = [
        "santosh@bharosa.finance",
        "prachi.khushlani@bharosa.finance",
        "arjit@bharosa.finance",
        "ayush@bharosa.finance",
        "lynelle@bharosa.finance",
        "ujjwal@bharosa.finance",
        "sahil@bharosa.finance",
    ]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Bharosa Intel <{GMAIL_USER}>"
    msg["To"] = ", ".join(recipients)

    plain_text = f"Bharosa Intel — {today}\n\nOpen in an HTML email client to view."
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, recipients, msg.as_string())

    print(f"Sent to {len(recipients)} recipients")


if __name__ == "__main__":
    print("Generating...")
    html = generate_briefing()
    print("Sending...")
    send_email(html)
    print("Done!")
