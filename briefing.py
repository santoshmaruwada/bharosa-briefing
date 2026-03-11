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

SYSTEM_PROMPT = """You are the personal strategic intelligence analyst for Santosh, co-founder of Bharosa — an Indian fintech startup building the "operating system for personal finance." Bharosa's edge is a financial calculation engine that works on messy personal data: mutual funds, stocks, taxes, goals, loans. They target IFAs and MFDs in India.

Your job today is to produce a FOUNDER-GRADE daily intelligence note. Not a newsletter. Not a news dump. Strategic thinking fuel.

Search the web deeply across all sources below and return a single, complete, valid HTML document — nothing else. No markdown. No backticks. Just raw HTML starting with <!DOCTYPE html>.

STRICT CONTENT RULES:
- Maximum 2 User Mindset Signals
- Maximum 1 Non-Consensus Signal
- Maximum 1 Competitor Signal  
- Maximum 1 AI Capability Signal
- Maximum 1 India Market Signal
- Exactly 3-4 Must-Read conversation links
- Exactly 1 One-Line Takeaway

INSIGHT QUALITY RULES:
- Every signal must connect back to a specific Bharosa product implication
- Lead with WHY IT MATTERS for Bharosa, not what happened
- Surface what nobody else is saying yet — non-consensus > consensus
- User psychology signals matter more than startup funding news
- Flag 🚨 BHAROSA ALERT only for things that directly threaten or accelerate Bharosa's strategy

SEARCH SOURCES TO USE:
- Reddit: r/personalfinance, r/IndiaInvestments, r/mutualfunds, r/FIREIndia, r/startups
- Hacker News: search "finance AI", "personal finance", "fintech"
- Twitter/X: fintech founders, AI researchers, Indian finance influencers
- Product Hunt: new finance AI launches
- News: SEBI circulars, Indian fintech news, global AI finance launches

---

OUTPUT: Return this exact HTML structure with all inline CSS. Replace every [PLACEHOLDER] with real researched content and real URLs.

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bharosa Intelligence — [DATE]</title>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f7;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Helvetica Neue',Helvetica,Arial,sans-serif;">

<!-- Email wrapper -->
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f5f5f7;">
<tr><td align="center" style="padding:40px 20px;">

<!-- Main card -->
<table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background-color:#ffffff;border-radius:18px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08);">

<!-- Header -->
<tr><td style="background:linear-gradient(135deg,#1c1c1e 0%,#2c2c2e 100%);padding:40px 40px 32px;text-align:center;">
  <p style="margin:0 0 8px;font-size:11px;font-weight:600;letter-spacing:3px;color:#98989d;text-transform:uppercase;">Bharosa Intelligence</p>
  <h1 style="margin:0 0 6px;font-size:28px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;">[DATE]</h1>
  <p style="margin:0;font-size:13px;color:#636366;font-weight:400;">Daily Strategic Note for Santosh</p>
</td></tr>

<!-- Top Signal Bar -->
<tr><td style="background:#1c1c1e;padding:16px 40px;border-top:1px solid #2c2c2e;">
  <p style="margin:0;font-size:12px;font-weight:600;letter-spacing:2px;color:#ff9f0a;text-transform:uppercase;">⚡ Today's Signal</p>
  <p style="margin:6px 0 0;font-size:14px;color:#e5e5ea;line-height:1.5;font-style:italic;">[ONE SENTENCE — THE SINGLE MOST IMPORTANT INSIGHT TODAY FOR BHAROSA]</p>
</td></tr>

<!-- Body padding start -->
<tr><td style="padding:0 40px 40px;">

<!-- SECTION 1: USER MINDSET SIGNALS -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:32px 0 16px;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">01 — User Mindset Signals</p>
  <div style="height:1px;background:#f2f2f7;margin-top:10px;"></div>
</td></tr>
</table>

<!-- User Signal 1 -->
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:12px;padding:24px;border-left:3px solid #007aff;">
  <p style="margin:0 0 4px;font-size:11px;font-weight:600;color:#007aff;letter-spacing:1px;text-transform:uppercase;">Real User Problem</p>
  <h3 style="margin:0 0 12px;font-size:17px;font-weight:700;color:#1c1c1e;letter-spacing:-0.3px;">[SIGNAL 1 HEADLINE]</h3>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">What people are asking:</p>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[DESCRIBE THE SPECIFIC QUESTIONS/PROBLEMS USERS ARE POSTING ONLINE]</p>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">Why it matters for Bharosa:</p>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[SPECIFIC PRODUCT/STRATEGY IMPLICATION FOR BHAROSA]</p>
  <p style="margin:0 0 8px;font-size:13px;font-weight:600;color:#1c1c1e;">➡ Bharosa could build:</p>
  <p style="margin:0 0 16px;font-size:14px;color:#007aff;line-height:1.6;">[SPECIFIC FEATURE OR TOOL IDEA]</p>
  <a href="[SOURCE_URL_1]" style="font-size:12px;color:#007aff;text-decoration:none;font-weight:500;">Source →</a>
  &nbsp;&nbsp;
  <a href="[SOURCE_URL_2]" style="font-size:12px;color:#007aff;text-decoration:none;font-weight:500;">Source →</a>
</td></tr>
</table>

<!-- User Signal 2 -->
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:12px;padding:24px;border-left:3px solid #ff453a;">
  <p style="margin:0 0 4px;font-size:11px;font-weight:600;color:#ff453a;letter-spacing:1px;text-transform:uppercase;">Trust / Fear Signal</p>
  <h3 style="margin:0 0 12px;font-size:17px;font-weight:700;color:#1c1c1e;letter-spacing:-0.3px;">[SIGNAL 2 HEADLINE]</h3>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">User sentiment:</p>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[WHAT USERS ARE SAYING/FEELING ABOUT AI IN FINANCE]</p>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">Implication for Bharosa:</p>
  <p style="margin:0 0 16px;font-size:14px;color:#3a3a3c;line-height:1.6;">[HOW THIS AFFECTS BHAROSA'S POSITIONING OR PRODUCT DESIGN]</p>
  <a href="[SOURCE_URL_3]" style="font-size:12px;color:#007aff;text-decoration:none;font-weight:500;">Source →</a>
  &nbsp;&nbsp;
  <a href="[SOURCE_URL_4]" style="font-size:12px;color:#007aff;text-decoration:none;font-weight:500;">Source →</a>
</td></tr>
</table>

<!-- SECTION 2: NON-CONSENSUS SIGNAL -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:16px 0 16px;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">02 — Non-Consensus Signal</p>
  <div style="height:1px;background:#f2f2f7;margin-top:10px;"></div>
</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#fff9f0;border-radius:12px;padding:24px;border-left:3px solid #ff9f0a;">
  <p style="margin:0 0 4px;font-size:11px;font-weight:600;color:#ff9f0a;letter-spacing:1px;text-transform:uppercase;">💡 Emerging Pattern — Not Widely Discussed Yet</p>
  <h3 style="margin:0 0 12px;font-size:17px;font-weight:700;color:#1c1c1e;letter-spacing:-0.3px;">[NON-CONSENSUS HEADLINE]</h3>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[DESCRIBE THE EMERGING PATTERN OR IDEA THAT FEW PEOPLE ARE TALKING ABOUT]</p>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">Why this becomes important:</p>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[EXPLAIN THE LONG-TERM SIGNIFICANCE]</p>
  <p style="margin:0 0 8px;font-size:13px;font-weight:600;color:#1c1c1e;">➡ Potential Bharosa opportunity:</p>
  <p style="margin:0 0 16px;font-size:14px;color:#ff9f0a;line-height:1.6;">[SPECIFIC OPPORTUNITY THIS OPENS FOR BHAROSA]</p>
  <a href="[SOURCE_URL_5]" style="font-size:12px;color:#007aff;text-decoration:none;font-weight:500;">Source →</a>
</td></tr>
</table>

<!-- SECTION 3: PRODUCT DIRECTION -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:16px 0 16px;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">03 — Product Direction Hypothesis</p>
  <div style="height:1px;background:#f2f2f7;margin-top:10px;"></div>
</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f2f9ff;border-radius:12px;padding:24px;border-left:3px solid #30d158;">
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">Strongest insight today:</p>
  <p style="margin:0 0 16px;font-size:15px;color:#3a3a3c;line-height:1.6;font-style:italic;">[ONE POWERFUL INSIGHT ABOUT WHAT USERS ACTUALLY WANT VS WHAT PRODUCTS OFFER]</p>
  <p style="margin:0 0 8px;font-size:13px;font-weight:600;color:#1c1c1e;">Possible product wedge for Bharosa:</p>
  <ul style="margin:0;padding-left:18px;">
    <li style="font-size:14px;color:#3a3a3c;line-height:1.8;">[FEATURE IDEA 1]</li>
    <li style="font-size:14px;color:#3a3a3c;line-height:1.8;">[FEATURE IDEA 2]</li>
    <li style="font-size:14px;color:#3a3a3c;line-height:1.8;">[FEATURE IDEA 3]</li>
  </ul>
</td></tr>
</table>

<!-- SECTION 4: COMPETITOR SIGNAL -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:16px 0 16px;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">04 — Competitor Signal</p>
  <div style="height:1px;background:#f2f2f7;margin-top:10px;"></div>
</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:12px;padding:24px;">
  <h3 style="margin:0 0 12px;font-size:17px;font-weight:700;color:#1c1c1e;letter-spacing:-0.3px;">[COMPETITOR HEADLINE]</h3>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[WHAT THE COMPETITOR IS DOING]</p>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">Gap noticed:</p>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[WHAT THEY'RE MISSING — TAX, GOALS, MESSY DATA, ETC.]</p>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#30d158;">Strategic implication:</p>
  <p style="margin:0 0 16px;font-size:14px;color:#3a3a3c;line-height:1.6;">[HOW BHAROSA CAN POSITION DIFFERENTLY]</p>
  <a href="[SOURCE_URL_6]" style="font-size:12px;color:#007aff;text-decoration:none;font-weight:500;">Source →</a>
</td></tr>
</table>

<!-- SECTION 5: INDIA MARKET -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:16px 0 16px;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">05 — India Market Signal</p>
  <div style="height:1px;background:#f2f2f7;margin-top:10px;"></div>
</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:12px;padding:24px;">
  <h3 style="margin:0 0 12px;font-size:17px;font-weight:700;color:#1c1c1e;letter-spacing:-0.3px;">[INDIA SIGNAL HEADLINE]</h3>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[SEBI/REGULATORY/MARKET DEVELOPMENT AND ITS DIRECT IMPLICATION]</p>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">Opportunity for Bharosa:</p>
  <p style="margin:0 0 16px;font-size:14px;color:#3a3a3c;line-height:1.6;">[SPECIFIC WAY BHAROSA CAN TAKE ADVANTAGE OR PROTECT AGAINST THIS]</p>
  <a href="[SOURCE_URL_7]" style="font-size:12px;color:#007aff;text-decoration:none;font-weight:500;">Source →</a>
</td></tr>
</table>

<!-- SECTION 6: AI CAPABILITY SIGNAL -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:16px 0 16px;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">06 — Global AI Capability Signal</p>
  <div style="height:1px;background:#f2f2f7;margin-top:10px;"></div>
</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:12px;padding:24px;">
  <h3 style="margin:0 0 12px;font-size:17px;font-weight:700;color:#1c1c1e;letter-spacing:-0.3px;">[AI CAPABILITY HEADLINE]</h3>
  <p style="margin:0 0 14px;font-size:14px;color:#3a3a3c;line-height:1.6;">[WHAT AI CAPABILITY LAUNCHED OR IMPROVED]</p>
  <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#1c1c1e;">Implication for Bharosa's product:</p>
  <p style="margin:0 0 16px;font-size:14px;color:#3a3a3c;line-height:1.6;">[HOW THIS AI CAPABILITY COULD BE USED IN OR THREATENS BHAROSA]</p>
  <a href="[SOURCE_URL_8]" style="font-size:12px;color:#007aff;text-decoration:none;font-weight:500;">Source →</a>
</td></tr>
</table>

<!-- SECTION 7: MUST READ -->
<table width="100%" cellpadding="0" cellspacing="0" border="0">
<tr><td style="padding:16px 0 16px;">
  <p style="margin:0;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">07 — Must-Read Conversations</p>
  <div style="height:1px;background:#f2f2f7;margin-top:10px;"></div>
</td></tr>
</table>

<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:24px;">
<tr><td style="background:#f9f9fb;border-radius:12px;padding:24px;">
  <p style="margin:0 0 14px;font-size:13px;color:#636366;line-height:1.5;">High-signal threads worth reading manually for intuition building.</p>
  
  <table width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr><td style="padding:10px 0;border-bottom:1px solid #e5e5ea;">
    <a href="[THREAD_URL_1]" style="font-size:14px;color:#007aff;text-decoration:none;font-weight:500;">[THREAD 1 TITLE — PLATFORM]</a>
    <p style="margin:4px 0 0;font-size:12px;color:#8e8e93;">[ONE LINE WHY THIS IS WORTH READING]</p>
  </td></tr>
  <tr><td style="padding:10px 0;border-bottom:1px solid #e5e5ea;">
    <a href="[THREAD_URL_2]" style="font-size:14px;color:#007aff;text-decoration:none;font-weight:500;">[THREAD 2 TITLE — PLATFORM]</a>
    <p style="margin:4px 0 0;font-size:12px;color:#8e8e93;">[ONE LINE WHY THIS IS WORTH READING]</p>
  </td></tr>
  <tr><td style="padding:10px 0;border-bottom:1px solid #e5e5ea;">
    <a href="[THREAD_URL_3]" style="font-size:14px;color:#007aff;text-decoration:none;font-weight:500;">[THREAD 3 TITLE — PLATFORM]</a>
    <p style="margin:4px 0 0;font-size:12px;color:#8e8e93;">[ONE LINE WHY THIS IS WORTH READING]</p>
  </td></tr>
  <tr><td style="padding:10px 0;">
    <a href="[THREAD_URL_4]" style="font-size:14px;color:#007aff;text-decoration:none;font-weight:500;">[THREAD 4 TITLE — PLATFORM]</a>
    <p style="margin:4px 0 0;font-size:12px;color:#8e8e93;">[ONE LINE WHY THIS IS WORTH READING]</p>
  </td></tr>
  </table>
</td></tr>
</table>

<!-- SECTION 8: ONE LINE TAKEAWAY -->
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom:8px;">
<tr><td style="background:linear-gradient(135deg,#1c1c1e 0%,#2c2c2e 100%);border-radius:12px;padding:28px;text-align:center;">
  <p style="margin:0 0 8px;font-size:10px;font-weight:700;letter-spacing:3px;color:#98989d;text-transform:uppercase;">⭐ Today's Takeaway</p>
  <p style="margin:0;font-size:17px;font-weight:600;color:#ffffff;line-height:1.6;font-style:italic;">"[ONE POWERFUL SENTENCE THAT CAPTURES THE MOST IMPORTANT INSIGHT OF THE DAY FOR BHAROSA]"</p>
</td></tr>
</table>

</td></tr>
<!-- Body padding end -->

<!-- Footer -->
<tr><td style="background:#f5f5f7;padding:24px 40px;text-align:center;border-top:1px solid #e5e5ea;">
  <p style="margin:0 0 4px;font-size:12px;color:#8e8e93;">Bharosa Intelligence · Daily Strategic Note</p>
  <p style="margin:0;font-size:11px;color:#aeaeb2;">Generated for Santosh · [DATE]</p>
</td></tr>

</table>
<!-- End main card -->

</td></tr>
</table>
<!-- End email wrapper -->

</body>
</html>"""

def generate_briefing():
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    today = datetime.now().strftime("%B %d, %Y")

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"Generate today's Bharosa intelligence note. Today is {today}. Search deeply across Reddit, Hacker News, news sites, and finance communities. Replace every [PLACEHOLDER] with real researched content and real URLs. Return only the complete HTML document."
        }]
    )

    html_content = ""
    for block in response.content:
        if block.type == "text":
            html_content += block.text

    # Clean up any accidental markdown fences
    html_content = html_content.replace("```html", "").replace("```", "").strip()
    return html_content

def send_email(html_content):
    today = datetime.now().strftime("%B %d, %Y")
    subject = f"Bharosa Intelligence — {today}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Bharosa Intelligence <{GMAIL_USER}>"
    msg["To"] = TO_EMAIL

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())

    print(f"✅ Briefing sent to {TO_EMAIL}")

if __name__ == "__main__":
    print("🔍 Generating briefing...")
    html = generate_briefing()
    print("📧 Sending email...")
    send_email(html)
    print("✅ Done!")
