#!/usr/bin/env python3
"""
Generate Architecture_Explained.pdf — mirrors ArchitecturePage.tsx content.
Run: pip install -r requirements-pdf.txt && python generate_architecture_pdf.py
"""
import math
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    ListFlowable, ListItem,
)
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Polygon

PAGE_W, PAGE_H = A4
MARGIN = 48
CONTENT_W = PAGE_W - 2 * MARGIN

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
_styles = getSampleStyleSheet()

TITLE = ParagraphStyle("title", parent=_styles["Heading1"],
                        fontSize=20, spaceAfter=2, textColor=colors.HexColor("#1565C0"))
SUBTITLE = ParagraphStyle("subtitle", parent=_styles["Normal"],
                           fontSize=11, spaceAfter=10, textColor=colors.grey,
                           fontName="Helvetica-Oblique")
H2 = ParagraphStyle("h2", parent=_styles["Heading2"],
                     fontSize=13, spaceBefore=14, spaceAfter=4,
                     textColor=colors.HexColor("#2E7D32"))
BODY = ParagraphStyle("body", parent=_styles["Normal"],
                       fontSize=9.5, spaceAfter=4, leading=13)
BODY_BOLD = ParagraphStyle("bodyb", parent=BODY, fontName="Helvetica-Bold")
LI_STYLE = ParagraphStyle("li", parent=_styles["Normal"],
                            fontSize=9, leading=12, spaceAfter=1)


def _cs(fs=8.5):
    return ParagraphStyle("cs", fontName="Helvetica", fontSize=fs,
                           leading=fs + 3, spaceBefore=1, spaceAfter=1)


def _hs(fs=8.5):
    return ParagraphStyle("hs", fontName="Helvetica-Bold", fontSize=fs,
                           leading=fs + 3, spaceBefore=1, spaceAfter=1,
                           textColor=colors.white)


def P(text, style=None):
    """Shortcut to create a Paragraph."""
    return Paragraph(text, style or _cs())


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

class DrawingFlowable(Flowable):
    def __init__(self, drawing):
        super().__init__()
        self.drawing = drawing

    def wrap(self, availWidth, availHeight):
        return (self.drawing.width, self.drawing.height)

    def draw(self):
        self.drawing.drawOn(self.canv, 0, 0)


def _box(d, x, y, w, h, label, fill, stroke, fontsize=8.5):
    d.add(Rect(x, y, w, h, fillColor=colors.HexColor(fill),
               strokeColor=colors.HexColor(stroke), strokeWidth=1.2, rx=5, ry=5))
    d.add(String(x + w / 2, y + h / 2 - 3, label,
                 fontSize=fontsize, fillColor=colors.black, textAnchor="middle"))


def _arrow(d, x1, y1, x2, y2, dashed=False):
    sw = 0.7 if dashed else 0.9
    dash = [3, 3] if dashed else []
    col = colors.HexColor("#999999") if dashed else colors.HexColor("#333333")
    d.add(Line(x1, y1, x2, y2, strokeColor=col, strokeWidth=sw, strokeDashArray=dash))
    angle = math.atan2(y2 - y1, x2 - x1)
    sz = 4
    d.add(Polygon(
        [x2, y2,
         x2 - sz * math.cos(angle - math.pi / 6), y2 - sz * math.sin(angle - math.pi / 6),
         x2 - sz * math.cos(angle + math.pi / 6), y2 - sz * math.sin(angle + math.pi / 6)],
        fillColor=col, strokeColor=col, strokeWidth=0.3))


def _lbl(d, x1, y1, x2, y2, text, ox=0, oy=4):
    d.add(String((x1 + x2) / 2 + ox, (y1 + y2) / 2 + oy, text,
                 fontSize=6, fillColor=colors.HexColor("#666666"), textAnchor="middle"))


# ---------------------------------------------------------------------------
# System Architecture flowchart
# ---------------------------------------------------------------------------

def _system_flowchart():
    w = CONTENT_W
    h = 290
    d = Drawing(w, h)
    bh = 26
    gap = 40
    cx = w / 2
    off = 7

    def ry(row):
        return h - 28 - row * gap

    # Boxes
    bw0 = 100;  x0, y0 = cx - bw0 / 2, ry(0)
    _box(d, x0, y0, bw0, bh, "You (Browser)", "#E3F2FD", "#1976D2")

    bw1 = 120;  x1, y1 = cx - bw1 / 2, ry(1)
    _box(d, x1, y1, bw1, bh, "React Frontend", "#C8E6C9", "#388E3C")

    bw2 = 130;  x2, y2 = cx - bw2 / 2, ry(2)
    _box(d, x2, y2, bw2, bh, "FastAPI Backend", "#FFE0B2", "#F57C00")

    bw3 = 190;  x3, y3 = cx - bw3 / 2, ry(3)
    _box(d, x3, y3, bw3, bh, "AI Agent (LangChain + Gemini)", "#E1BEE7", "#7B1FA2")

    bw4 = 100;  x4, y4 = cx - bw4 / 2, ry(4)
    _box(d, x4, y4, bw4, bh, "Agent Tools", "#FFF9C4", "#F9A825")

    bw5 = 140;  sp = 30
    cx_l = cx - sp / 2 - bw5 / 2
    cx_r = cx + sp / 2 + bw5 / 2
    ccxt_x, ccxt_y = cx_l - bw5 / 2, ry(5)
    _box(d, ccxt_x, ccxt_y, bw5, bh, "MCP Client (CCXT)", "#B2EBF2", "#0097A7")
    db_x, db_y = cx_r - bw5 / 2, ry(5)
    _box(d, db_x, db_y, bw5, bh, "MongoDB Database", "#F8BBD0", "#C2185B")

    bw6 = 160;  bin_x, bin_y = cx_l - bw6 / 2, ry(6)
    _box(d, bin_x, bin_y, bw6, bh, "Crypto Exchange (Kraken/Binance)", "#FFF9C4", "#F57F17", fontsize=7.5)

    # Forward arrows (solid, left of center)
    _arrow(d, cx - off, y0, cx - off, y1 + bh)
    _lbl(d, cx - off, y0, cx - off, y1 + bh, "Type a message", ox=-48)
    _arrow(d, cx - off, y1, cx - off, y2 + bh)
    _lbl(d, cx - off, y1, cx - off, y2 + bh, "Send request", ox=-42)
    _arrow(d, cx - off, y2, cx - off, y3 + bh)
    _lbl(d, cx - off, y2, cx - off, y3 + bh, "Pass to agent", ox=-44)
    _arrow(d, cx - off, y3, cx - off, y4 + bh)
    _lbl(d, cx - off, y3, cx - off, y4 + bh, "Pick the right tool", ox=-52)

    # Tools -> CCXT / DB
    _arrow(d, x4, y4 + bh / 2, ccxt_x + bw5, ccxt_y + bh / 2)
    _lbl(d, x4, y4 + bh / 2, ccxt_x + bw5, ccxt_y + bh / 2, "Need market data?", oy=7)
    _arrow(d, x4 + bw4, y4 + bh / 2, db_x, db_y + bh / 2)
    _lbl(d, x4 + bw4, y4 + bh / 2, db_x, db_y + bh / 2, "Need wallet data?", oy=7)

    # CCXT -> Exchange
    cm = ccxt_x + bw5 / 2
    _arrow(d, cm - off, ccxt_y, cm - off, bin_y + bh)
    _lbl(d, cm - off, ccxt_y, cm - off, bin_y + bh, "Fetch live prices", ox=-48)

    # Return arrows (dashed, right of center)
    _arrow(d, cm + off, bin_y + bh, cm + off, ccxt_y, dashed=True)
    _lbl(d, cm + off, bin_y + bh, cm + off, ccxt_y, "Price data", ox=32)
    _arrow(d, ccxt_x + bw5, ccxt_y + bh / 2 + 3, x4, y4 + bh / 2 + 3, dashed=True)
    _arrow(d, db_x, db_y + bh / 2 + 3, x4 + bw4, y4 + bh / 2 + 3, dashed=True)
    _lbl(d, db_x, db_y + bh / 2 + 3, x4 + bw4, y4 + bh / 2 + 3, "Balance / history", oy=-8)
    _arrow(d, cx + off, y4 + bh, cx + off, y3, dashed=True)
    _lbl(d, cx + off, y4 + bh, cx + off, y3, "Tool result", ox=36)
    _arrow(d, cx + off, y3 + bh, cx + off, y2, dashed=True)
    _lbl(d, cx + off, y3 + bh, cx + off, y2, "NL reply", ox=30)
    _arrow(d, cx + off, y2 + bh, cx + off, y1, dashed=True)
    _lbl(d, cx + off, y2 + bh, cx + off, y1, "JSON response", ox=42)
    _arrow(d, cx + off, y1 + bh, cx + off, y0, dashed=True)
    _lbl(d, cx + off, y1 + bh, cx + off, y0, "Show answer", ox=38)

    return d


# ---------------------------------------------------------------------------
# Deployment flowchart
# ---------------------------------------------------------------------------

def _deploy_flowchart():
    w = CONTENT_W
    h = 120
    d = Drawing(w, h)
    bh = 24
    bw = 105
    gap_x = 16
    y_top = h - 35
    y_bot = 10

    cols = [30, 30 + bw + gap_x, 30 + 2 * (bw + gap_x)]

    _box(d, cols[0], y_top, bw, bh, "Browser (You)", "#E3F2FD", "#1976D2", 8)
    _box(d, cols[1], y_top, bw, bh, "Vercel (React)", "#C8E6C9", "#388E3C", 8)
    _box(d, cols[2], y_top, bw, bh, "Render (FastAPI)", "#FFE0B2", "#F57C00", 8)

    _box(d, cols[0], y_bot, bw, bh, "Kraken API", "#FFF9C4", "#F57F17", 8)
    _box(d, cols[1], y_bot, bw, bh, "MongoDB Atlas M0", "#F8BBD0", "#C2185B", 8)
    _box(d, cols[2], y_bot, bw, bh, "HKBU GenAI API", "#E1BEE7", "#7B1FA2", 8)

    _arrow(d, cols[0] + bw, y_top + bh / 2, cols[1], y_top + bh / 2)
    _lbl(d, cols[0] + bw, y_top + bh / 2, cols[1], y_top + bh / 2, "HTTPS", oy=6)
    _arrow(d, cols[1] + bw, y_top + bh / 2, cols[2], y_top + bh / 2)
    _lbl(d, cols[1] + bw, y_top + bh / 2, cols[2], y_top + bh / 2, "VITE_API_URL", oy=6)

    _arrow(d, cols[2] + bw / 4, y_top, cols[0] + bw / 2, y_bot + bh)
    _lbl(d, cols[2] + bw / 4, y_top, cols[0] + bw / 2, y_bot + bh, "CCXT", ox=-14)
    _arrow(d, cols[2] + bw / 2, y_top, cols[1] + bw / 2, y_bot + bh)
    _lbl(d, cols[2] + bw / 2, y_top, cols[1] + bw / 2, y_bot + bh, "pymongo", ox=4)
    _arrow(d, cols[2] + 3 * bw / 4, y_top, cols[2] + bw / 2, y_bot + bh)
    _lbl(d, cols[2] + 3 * bw / 4, y_top, cols[2] + bw / 2, y_bot + bh, "langchain", ox=18)

    return d


# ---------------------------------------------------------------------------
# Table builder helpers
# ---------------------------------------------------------------------------

def _make_table(data, col_widths, header_bg="#1565C0"):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def _numbered_list(items):
    """Return a ListFlowable with numbered items."""
    return ListFlowable(
        [ListItem(Paragraph(t, LI_STYLE)) for t in items],
        bulletType="1", start=1,
        bulletFontSize=8, bulletOffsetY=-1, leftIndent=18,
    )


# ---------------------------------------------------------------------------
# Build the PDF
# ---------------------------------------------------------------------------

def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "Architecture_Explained.pdf")
    doc = SimpleDocTemplate(out, pagesize=A4,
                            rightMargin=MARGIN, leftMargin=MARGIN,
                            topMargin=MARGIN, bottomMargin=MARGIN)
    story = []
    cs = _cs()
    hs = _hs()

    # ==================== PAGE 1: Title + Overview + System Architecture ====================

    story.append(Paragraph("Crypto Trading AI Agent", TITLE))
    story.append(Paragraph("How It Works \u2014 Explained for Everyone", SUBTITLE))

    # --- Overview ---
    story.append(Paragraph("Overview", H2))
    story.append(Paragraph(
        "This app lets you <b>trade cryptocurrency using natural language</b>. "
        "Instead of clicking buttons on an exchange, you just tell the AI what you want "
        "in plain English \u2014 like texting a friend who happens to be a trading expert.", BODY))

    overview_data = [
        [P("Step", _hs()), P("What Happens", _hs())],
        [P("<b>1. You chat</b>", cs), P('Type a message like \u201cBuy $100 of Bitcoin\u201d or \u201cWhat\u2019s the price of ETH?\u201d', cs)],
        [P("<b>2. AI understands</b>", cs), P("The AI agent figures out what you want and picks the right tool.", cs)],
        [P("<b>3. Real data, simulated trades</b>", cs), P("Prices come from a real exchange (Kraken in prod, Binance locally). Trades use a simulated wallet \u2014 no real money. You start with $10,000.", cs)],
        [P("<b>4. See results</b>", cs), P("The AI replies in plain English. Wallet and transaction history update automatically.", cs)],
    ]
    story.append(_make_table(overview_data, [CONTENT_W * 0.28, CONTENT_W * 0.72]))
    story.append(Spacer(1, 4))

    # --- System Architecture ---
    story.append(Paragraph("System Architecture", H2))
    story.append(Paragraph(
        "Follow the arrows from top to bottom. Solid = request, dashed = response. "
        "Left side handles <i>market data</i> (prices), right side handles <i>user data</i> (wallet).", BODY))
    story.append(DrawingFlowable(_system_flowchart()))

    legend_data = [
        [P("Component", _hs()), P("Description", _hs())],
        [P("Frontend", cs), P("React app (Vercel). Chat UI, wallet display, transaction history. REST API calls to backend.", cs)],
        [P("Backend + AI Agent", cs), P("Python FastAPI (Render). LangChain agent + Gemini 2.5 Flash interprets your language and calls tools.", cs)],
        [P("MCP Client (CCXT)", cs), P("CCXT library wrapper. Kraken in production (US-friendly), Binance locally. No API key needed.", cs)],
        [P("MongoDB Atlas", cs), P("Free M0 cloud database. Persists simulated wallet and transaction history across sessions.", cs)],
    ]
    story.append(_make_table(legend_data, [CONTENT_W * 0.25, CONTENT_W * 0.75]))

    # ==================== PAGE 2: Chat Flow + Buy Flow ====================
    story.append(PageBreak())

    # --- Chat Flow ---
    story.append(Paragraph("What Happens When You Chat", H2))
    story.append(Paragraph(
        "<b>Key takeaway:</b> The AI agent acts as a smart router. It reads your message, "
        "understands the intent, picks the right tool, and translates raw data into a "
        "human-friendly response. You never need to know which API to call.", BODY))
    story.append(Paragraph(
        'Example: you ask <i>\u201cWhat is the price of BTC?\u201d</i>', BODY))

    story.append(_numbered_list([
        "You type your question in the chat box and hit send.",
        "The React frontend sends a <i>POST /chat</i> request to the FastAPI backend.",
        "The AI agent (LangChain) passes your message to the Gemini LLM to understand intent.",
        "The LLM determines it needs price data and calls the <i>get_crypto_price</i> tool.",
        "The tool uses the CCXT library to query the exchange\u2019s public API for BTC/USDT.",
        "The exchange returns real-time market data (price, bid, ask, volume, 24h high/low).",
        "The LLM formats a natural-language reply and sends it back through the chain.",
        "The frontend displays the answer \u2014 the whole round trip takes 3\u20138 seconds.",
    ]))
    story.append(Spacer(1, 8))

    # --- Buy Flow ---
    story.append(Paragraph("What Happens When You Buy Crypto", H2))
    story.append(Paragraph(
        "<b>Key takeaway:</b> The buy operation is <i>atomic</i> \u2014 the tool checks your balance, "
        "fetches the price, updates the wallet, and records the transaction all in one step. "
        "If any step fails (e.g. insufficient funds), the agent reports the error.", BODY))
    story.append(Paragraph(
        'Example: you say <i>\u201cBuy $100 of ETH\u201d</i>', BODY))

    story.append(_numbered_list([
        "The AI recognizes you want to buy and calls <i>buy_crypto</i> with symbol and USD amount.",
        "The tool fetches the current ETH price from the exchange (e.g. $1,972.25).",
        "It calculates how much ETH $100 buys: 100 \u00f7 1972.25 = 0.05070 ETH.",
        "Your MongoDB wallet is updated: $100 deducted, 0.05070 ETH added.",
        "A transaction record is saved with price, amount, USD value, and timestamp.",
        "The AI confirms the trade in plain English with a breakdown.",
        "Your Wallet and Transactions pages refresh automatically via Redux state updates.",
    ]))
    story.append(Spacer(1, 8))

    # --- AI Agent Toolbox ---
    story.append(Paragraph("The AI Agent\u2019s Toolbox", H2))
    story.append(Paragraph(
        "The agent has 5 tools. Based on what you say, it automatically picks the right one "
        "(or multiple). Think of them like apps on a phone \u2014 the AI opens the right app.", BODY))

    tools_data = [
        [P("Tool", _hs()), P("Description", _hs())],
        [P("<b>Get Crypto Price</b>", cs), P("Fetches real-time price from the exchange (Kraken in prod, Binance locally).", cs)],
        [P("<b>Get Order Book</b>", cs), P("Shows current buy/sell orders. Useful for understanding market depth and liquidity.", cs)],
        [P("<b>Buy Crypto</b>", cs), P("Simulates buying crypto with USD. Fetches real price, calculates amount, updates wallet.", cs)],
        [P("<b>Check Balance</b>", cs), P("Returns wallet holdings with USD values. Shows how much of each crypto you own.", cs)],
        [P("<b>Transaction History</b>", cs), P("Lists recent trades: type, amount, price, and timestamp.", cs)],
    ]
    story.append(_make_table(tools_data, [CONTENT_W * 0.25, CONTENT_W * 0.75], header_bg="#F57C00"))

    # ==================== PAGE 3: Deployment + Comparison + Tech Stack ====================
    story.append(PageBreak())

    # --- Deployment ---
    story.append(Paragraph("Deployment Architecture", H2))
    story.append(Paragraph(
        "The entire stack runs on <b>free-tier services</b> ($0/month). "
        "Frontend is a static build on Vercel; backend is a web service on Render.", BODY))
    story.append(DrawingFlowable(_deploy_flowchart()))
    story.append(Spacer(1, 4))

    story.append(Paragraph(
        "<b>Why Kraken instead of Binance?</b> The backend runs on Render\u2019s servers in Oregon, USA. "
        "Binance blocks API requests from US IPs, so production uses Kraken (no geo-restrictions). "
        "Locally you can still use Binance. Configurable via <i>DEFAULT_EXCHANGE</i> env var.", BODY))

    deploy_data = [
        [P("Service", _hs()), P("Details", _hs())],
        [P("<b>Vercel (Free)</b>", cs), P("Hosts React static build. Auto-deploys on git push. Global CDN.", cs)],
        [P("<b>Render (Free)</b>", cs), P("Runs FastAPI backend. Sleeps after 15 min; cold start ~30\u201350s.", cs)],
        [P("<b>Kraken API</b>", cs), P("Public market data, no geo-restrictions. No API key required.", cs)],
        [P("<b>MongoDB Atlas M0</b>", cs), P("Free cloud database (512 MB). Wallet + transaction storage.", cs)],
    ]
    story.append(_make_table(deploy_data, [CONTENT_W * 0.25, CONTENT_W * 0.75]))
    story.append(Spacer(1, 8))

    # --- Comparison ---
    story.append(Paragraph("Normal Bitcoin Buying vs This App", H2))

    comp_data = [
        [P("Aspect", _hs()), P("Normal Bitcoin Buying", _hs()), P("This App (AI Agent)", _hs())],
        [P("How you interact", cs),
         P("Log into an exchange, navigate menus, click Buy, enter amount and price", cs),
         P('Type in plain English: \u201cBuy $100 of Bitcoin\u201d', cs)],
        [P("Understanding", cs),
         P("Must know where to click and what each field means", cs),
         P("AI understands natural language \u2014 no training needed", cs)],
        [P("Price lookup", cs),
         P("You check the price yourself", cs),
         P("AI fetches real-time price automatically", cs)],
        [P("Execution", cs),
         P("You confirm the order; real money is spent", cs),
         P("Simulated trade; no real money (demo wallet with $10k)", cs)],
        [P("Wallet &amp; history", cs),
         P("On the exchange\u2019s servers; log in to view", cs),
         P("In MongoDB; visible in app\u2019s Wallet and Transactions pages", cs)],
        [P("Best for", cs),
         P("Actual investing with real funds", cs),
         P("Learning, testing strategies, trying crypto risk-free", cs)],
    ]
    story.append(_make_table(comp_data, [CONTENT_W * 0.16, CONTENT_W * 0.42, CONTENT_W * 0.42],
                             header_bg="#2E7D32"))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<b>In short:</b> Normal buying = you do everything manually. "
        "This app = you chat, the AI does the work, and everything is simulated so you learn safely.", BODY))

    # --- Tech Stack ---
    story.append(Paragraph("Tech Stack", H2))
    stack_data = [
        [P("Layer", _hs()), P("Technology", _hs())],
        [P("Frontend", cs), P("React, TypeScript, Redux Toolkit, Vite", cs)],
        [P("Backend", cs), P("Python, FastAPI, LangChain", cs)],
        [P("AI Model", cs), P("Gemini 2.5 Flash (via HKBU GenAI API)", cs)],
        [P("Market Data", cs), P("CCXT \u2192 Kraken (prod) / Binance (local)", cs)],
        [P("Database", cs), P("MongoDB Atlas (cloud, free M0 tier)", cs)],
        [P("Hosting", cs), P("Vercel (frontend) + Render (backend) \u2014 $0/month", cs)],
    ]
    story.append(_make_table(stack_data, [CONTENT_W * 0.20, CONTENT_W * 0.80]))

    doc.build(story)
    print(f"PDF created: {out}")


if __name__ == "__main__":
    main()
