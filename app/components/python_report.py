"""
PropIntel AI - PDF Lender Assessment Report Generator
Produces a formatted, print-ready two-page PDF for loan application attachment.
Uses only latin-1 safe characters to stay compatible with fpdf2 core fonts.
"""

from fpdf import FPDF
from datetime import datetime
import re

# ── Colour palette (R, G, B) ────────────────────────────────────────────────
C_BG       = (8,   8,  14)
C_PANEL    = (18,  18,  28)
C_BORDER   = (50,  50,  70)
C_CYAN     = (0,  190, 220)
C_GREEN    = (0,  200, 140)
C_AMBER    = (215, 150,  25)
C_RED      = (215,  50,  60)
C_WHITE    = (235, 233, 228)
C_MUTED    = (130, 128, 145)
C_DARK     = (15,  15,  25)


def _safe(text: str) -> str:
    """Strip or replace characters that are outside latin-1."""
    replacements = {
        "\u2713": "OK",   # ✓
        "\u2717": "X",    # ✗
        "\u2714": "OK",
        "\u2718": "X",
        "\u2191": "+",    # ↑
        "\u2193": "-",    # ↓
        "\u00b7": ".",    # ·
        "\u2022": "-",    # •
        "\u25cf": "*",
        "\u26a0": "!",    # ⚠
        "\u2605": "*",    # ★
        "\u2764": "<3",
        "\u2026": "...",
        "\u20b9": "Rs.",  # ₹  — fallback if somehow present as literal
    }
    for char, sub in replacements.items():
        text = text.replace(char, sub)
    # Drop anything still outside latin-1
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _dec_color(decision: str):
    return {"APPROVE": C_GREEN, "REVIEW": C_AMBER, "REJECT": C_RED}.get(decision, C_CYAN)


# ── Main PDF class ──────────────────────────────────────────────────────────
class LenderReport(FPDF):
    def __init__(self, result: dict):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.result    = result
        self.val       = result.get("valuation", {})
        self.liq       = result.get("liquidity", {})
        self.conf      = result.get("confidence", {})
        self.fraud     = result.get("fraud_flags", [])
        self.loc       = result.get("location_resolved", {})
        self.prox      = result.get("proximity_data", {})
        self.rec       = result.get("lender_recommendation", {})
        self.drivers   = result.get("key_drivers", [])
        self.prop_sum  = _safe(result.get("property_summary", "—"))
        self.generated = datetime.now().strftime("%d %B %Y, %H:%M")
        self.decision  = self.rec.get("decision", "REVIEW")
        self.dec_col   = _dec_color(self.decision)
        self.set_margins(0, 0, 0)
        self.set_auto_page_break(False)

    # ── colour helpers ───────────────────────────────────────────────────────
    def _fill(self, c):    self.set_fill_color(*c)
    def _ink(self, c):     self.set_text_color(*c)
    def _stroke(self, c):  self.set_draw_color(*c)

    def _rect(self, x, y, w, h, c, style="F"):
        self._fill(c); self.rect(x, y, w, h, style)

    def _rule(self, x1, y1, x2, y2, c=C_BORDER, lw=0.2):
        self._stroke(c); self.set_line_width(lw); self.line(x1, y1, x2, y2)

    # ── text helpers ─────────────────────────────────────────────────────────
    def _label(self, x, y, text, size=6.5, color=C_MUTED):
        self.set_xy(x, y)
        self.set_font("Helvetica", "B", size)
        self._ink(color)
        self.cell(0, 3, _safe(text).upper())

    def _val(self, x, y, text, size=12, color=C_WHITE, w=0):
        self.set_xy(x, y)
        self.set_font("Helvetica", "B", size)
        self._ink(color)
        self.cell(w if w else 0, 6, _safe(str(text)))

    def _body(self, x, y, text, w=0, size=7.5, color=C_MUTED, align="L"):
        self.set_xy(x, y)
        self.set_font("Helvetica", "", size)
        self._ink(color)
        self.multi_cell(w if w else self.w - x - 14, 4, _safe(str(text)), align=align)

    def _section(self, y, title):
        """Dark section header bar. Returns new y."""
        self._rect(14, y, 182, 7, C_PANEL)
        self._rule(14, y, 14, y + 7, self.dec_col, lw=0.9)
        self._rule(14, y + 7, 196, y + 7, C_BORDER)
        self.set_xy(18, y + 1.8)
        self.set_font("Helvetica", "B", 7.5)
        self._ink(C_CYAN)
        self.cell(0, 4, _safe(title).upper())
        return y + 9

    def _bar(self, x, y, w, h, pct, color):
        """Render a horizontal progress bar."""
        self._rect(x, y, w, h, C_BORDER)
        filled = max(0.0, min(1.0, pct)) * w
        if filled > 0:
            self._rect(x, y, filled, h, color)

    # ── header / footer ──────────────────────────────────────────────────────
    def header(self):
        self._rect(0, 0, 210, 22, C_BG)
        # Brand wordmark
        self.set_xy(14, 6)
        self.set_font("Helvetica", "B", 15)
        self._ink(C_CYAN);  self.cell(18, 8, "Prop")
        self.set_font("Helvetica", "", 15)
        self._ink((100, 100, 130)); self.cell(13, 8, "Intel")
        self.set_font("Helvetica", "B", 15)
        self._ink(C_WHITE); self.cell(10, 8, " AI")
        # Subtitle
        self.set_xy(14, 14.5)
        self.set_font("Helvetica", "", 5.5)
        self._ink(C_MUTED)
        self.cell(0, 3, "COLLATERAL VALUATION  |  LIQUIDITY INTELLIGENCE  |  RISK ASSESSMENT")
        # Right side
        self.set_xy(100, 6)
        self.set_font("Helvetica", "B", 7)
        self._ink(C_MUTED)
        self.cell(96, 4, "LENDER ASSESSMENT REPORT", align="R")
        self.set_xy(100, 10.5)
        self.set_font("Helvetica", "", 6)
        self._ink(C_MUTED)
        self.cell(96, 3, f"Generated: {_safe(self.generated)}", align="R")
        # Cyan rule
        self._rule(0, 22, 210, 22, C_CYAN, lw=0.35)

    def footer(self):
        self._rect(0, 284, 210, 13, C_BG)
        self._rule(0, 284, 210, 284, C_BORDER, lw=0.25)
        self.set_xy(14, 287.5)
        self.set_font("Helvetica", "", 5.5)
        self._ink(C_MUTED)
        self.cell(0, 3.5, "PropIntel AI v2.0  |  Team TE-08, PICT Pune  |  Poonawalla Fincorp AI Hackathon  |  CONFIDENTIAL - FOR LENDER USE ONLY")
        self.set_xy(0, 287.5)
        self.cell(196, 3.5, f"Page {self.page_no()}", align="R")

    # ── Page 1 ────────────────────────────────────────────────────────────────
    def build_page1(self):
        self.add_page()
        y = 26

        # Property summary bar
        self._rect(14, y, 182, 9, C_PANEL)
        self._rule(14, y, 196, y, C_BORDER)
        self._rule(14, y + 9, 196, y + 9, C_BORDER)
        self.set_xy(17, y + 2.5)
        self.set_font("Helvetica", "B", 7.5)
        self._ink(C_CYAN); self.cell(26, 4, "PROPERTY")
        self.set_font("Helvetica", "", 7.5)
        self._ink(C_WHITE); self.cell(0, 4, self.prop_sum)
        y += 12

        # ── DECISION BANNER ───────────────────────────────────────────────────
        dec_labels = {
            "APPROVE": "APPROVED FOR LENDING",
            "REVIEW":  "MANUAL REVIEW REQUIRED",
            "REJECT":  "DO NOT PROCEED",
        }
        dec_prefix = {"APPROVE": "[PASS]", "REVIEW": "[!]", "REJECT": "[FAIL]"}

        self._rect(14, y, 182, 20, C_PANEL)
        self._rect(14, y, 3,  20, self.dec_col)          # left stripe
        self._stroke(self.dec_col)
        self.set_line_width(0.4)
        self.rect(14, y, 182, 20)

        self.set_xy(20, y + 4)
        self.set_font("Helvetica", "B", 13)
        self._ink(self.dec_col)
        self.cell(0, 6, f"{dec_prefix[self.decision]}  {dec_labels[self.decision]}")

        self.set_xy(20, y + 12)
        self.set_font("Helvetica", "", 7)
        self._ink(C_MUTED)
        self.cell(0, 4,
            f"Safe Loan: {_safe(self.rec.get('safe_loan_display','—'))}   |   "
            f"LTV: {self.rec.get('ltv_ratio','—')}   |   "
            f"Confidence: {self.conf.get('percentage','—')}   |   "
            f"Risk Level: {self.rec.get('risk_level','—')}"
        )
        y += 24

        # ── 4 METRIC CARDS ────────────────────────────────────────────────────
        cards = [
            ("MARKET VALUE",   _safe(self.val.get("market_value_display","—")),   "ML estimate",            C_GREEN),
            ("DISTRESS VALUE", _safe(self.val.get("distress_value_display","—")), "90-day forced sale",     C_AMBER),
            ("RESALE INDEX",   f"{self.liq.get('resale_index','—')}/100",         self.liq.get("grade","—"),C_CYAN),
            ("TIME TO SELL",   _safe(self.liq.get("time_to_sell_display","—")),   "Expected resale window", C_CYAN),
        ]
        cw = 44
        for i, (lbl, v, sub, col) in enumerate(cards):
            cx = 14 + i * (cw + 1.3)
            self._rect(cx, y, cw, 20, C_PANEL)
            self._rect(cx, y, cw, 1.5, col)
            self._label(cx + 3, y + 4, lbl)
            self._val(cx + 3, y + 8.5, v, size=10, color=col, w=cw - 6)
            self._body(cx + 3, y + 15, sub, w=cw - 6, size=6)
        y += 24

        # ── VALUATION BREAKDOWN ───────────────────────────────────────────────
        y = self._section(y, "Valuation Breakdown")

        self._rect(14, y, 90, 40, C_PANEL)
        self._rect(106, y, 90, 40, C_PANEL)

        # Left: circle rate details
        cr = self.loc.get("circle_rate_sqft", 0)
        zone = self.loc.get("circle_rate_zone", "—").replace("_", " ").title()
        found = "Exact locality match" if self.loc.get("locality_found_in_db") else "Using city-level average"
        self._label(17, y + 3, "Government Circle Rate")
        self._val(17, y + 8, f"Rs. {cr:,.0f} / sqft", size=10, color=C_WHITE)
        self._body(17, y + 15, f"Zone: {zone}", size=7)
        self._body(17, y + 20, found, size=7, color=C_GREEN if self.loc.get("locality_found_in_db") else C_AMBER)
        self._rule(17, y + 26, 102, y + 26, C_BORDER)
        self._label(17, y + 28, "AI Market Rate")
        self._val(17, y + 33, f"Rs. {self.val.get('price_per_sqft', 0):,.0f} / sqft", size=10, color=C_GREEN)

        # Right: key drivers
        self._label(109, y + 3, "Key Value Drivers")
        dy = y + 9
        for driver in self.drivers[:5]:
            col = C_GREEN if driver.startswith("+") else C_RED if driver.startswith("-") else C_CYAN
            self.set_xy(109, dy)
            self.set_font("Helvetica", "B", 7)
            self._ink(col)
            self.multi_cell(85, 4.5, _safe(driver))
            dy += 6.5
        y += 44

        # ── LIQUIDITY ANALYSIS ────────────────────────────────────────────────
        y = self._section(y, "Liquidity Analysis")

        self._rect(14, y, 90, 46, C_PANEL)
        self._rect(106, y, 90, 46, C_PANEL)

        ri = self.liq.get("resale_index", 0)
        gc = C_GREEN if ri >= 70 else C_AMBER if ri >= 40 else C_RED
        self._label(17, y + 3, "Resale Index")
        self._val(17, y + 8, f"{ri} / 100", size=13, color=gc)
        self._bar(17, y + 18, 80, 3, ri / 100, gc)
        self._body(17, y + 23, f"Grade: {self.liq.get('grade','—')}", size=7)
        self._rule(17, y + 28, 102, y + 28, C_BORDER)
        self._label(17, y + 30, "Time to Sell")
        self._val(17, y + 35, _safe(self.liq.get("time_to_sell_display", "—")), size=10, color=C_AMBER)
        self._label(17, y + 41, "Absorption Rate")
        self._body(17, y + 45, _safe(self.liq.get("absorption_rate_pct", "—")), size=8, color=C_WHITE)

        # Right: factor bars
        self._label(109, y + 3, "Factor Breakdown")
        fy = y + 9
        for factor in self.liq.get("factor_breakdown", [])[:4]:
            sc = factor.get("score", 0)
            fc = C_GREEN if sc >= 70 else C_AMBER if sc >= 40 else C_RED
            self.set_xy(109, fy)
            self.set_font("Helvetica", "", 7)
            self._ink(C_MUTED)
            self.cell(70, 3.5, _safe(factor.get("factor", "")))
            self.set_xy(179, fy)
            self.set_font("Helvetica", "B", 7)
            self._ink(fc)
            self.cell(0, 3.5, f"{sc}/100")
            fy += 4.5
            self._bar(109, fy, 85, 2, sc / 100, fc)
            fy += 5
        y += 50

        # ── LENDER RECOMMENDATION ─────────────────────────────────────────────
        y = self._section(y, "Lender Recommendation")
        self._rect(14, y, 182, 28, C_PANEL)
        self._rect(14, y, 3, 28, self.dec_col)
        self._stroke(self.dec_col)
        self.set_line_width(0.3)
        self.rect(14, y, 182, 28)

        metrics = [
            ("SAFE LOAN AMOUNT",  _safe(self.rec.get("safe_loan_display", "—")),           C_GREEN),
            ("LTV RATIO",         self.rec.get("ltv_ratio", "—"),                          C_CYAN),
            ("DISTRESS RECOVERY", _safe(self.rec.get("distress_recovery_assured", "—")),   C_AMBER),
        ]
        for i, (lbl, v, c) in enumerate(metrics):
            mx = 20 + i * 58
            self._label(mx, y + 4, lbl)
            self._val(mx, y + 9, v, size=10, color=c)

        notes = [n for n in self.rec.get("notes", []) if n.strip()][:4]
        self.set_xy(20, y + 19)
        self.set_font("Helvetica", "", 6.5)
        self._ink(C_MUTED)
        note_text = "  |  ".join(_safe(n.strip().lstrip("- ").lstrip("* ")) for n in notes)
        self.multi_cell(174, 3.5, note_text)

    # ── Page 2 ────────────────────────────────────────────────────────────────
    def build_page2(self):
        self.add_page()
        y = 26

        # ── FRAUD DETECTION ───────────────────────────────────────────────────
        y = self._section(y, "Fraud Detection & Anomaly Flags")

        if not self.fraud:
            self._rect(14, y, 182, 12, C_PANEL)
            self._rect(14, y, 3, 12, C_GREEN)
            self.set_xy(20, y + 4)
            self.set_font("Helvetica", "B", 8)
            self._ink(C_GREEN)
            self.cell(0, 4, "No fraud indicators detected. Data is internally consistent.")
            y += 16
        else:
            for flag in self.fraud:
                sev = flag.get("severity", "LOW")
                fc  = {"HIGH": C_RED, "MEDIUM": C_AMBER, "LOW": C_CYAN}.get(sev, C_CYAN)
                self._rect(14, y, 182, 22, C_PANEL)
                self._rect(14, y, 3, 22, fc)
                # Badge
                self._fill(fc)
                self.rect(20, y + 4, 16, 5, "F")
                self.set_xy(20, y + 4.5)
                self.set_font("Helvetica", "B", 5.5)
                self._ink(C_DARK)
                self.cell(16, 4, sev, align="C")
                # Text
                self.set_xy(40, y + 3.5)
                self.set_font("Helvetica", "B", 8)
                self._ink(C_WHITE)
                self.cell(0, 4.5, _safe(flag.get("code", "")))
                self._body(40, y + 9,  _safe(flag.get("message", "")),        w=150, size=7)
                self._body(40, y + 15, _safe(f"Rec: {flag.get('recommendation','')}"), w=150, size=6.5, color=(160, 140, 80) if sev == "MEDIUM" else C_MUTED)
                y += 25

        # ── CONFIDENCE BREAKDOWN ──────────────────────────────────────────────
        y = self._section(y, "Confidence Analysis")
        self._rect(14, y, 182, 46, C_PANEL)

        breakdown = self.conf.get("breakdown", {})
        conf_metrics = [
            ("Data Completeness", breakdown.get("data_completeness", 0)),
            ("Signal Agreement",  breakdown.get("signal_agreement",  0)),
            ("Anomaly Score",     breakdown.get("anomaly_score",     0)),
        ]
        for i, (lbl, pct) in enumerate(conf_metrics):
            mx = 17 + i * 61
            col = C_GREEN if pct >= 0.75 else C_AMBER if pct >= 0.5 else C_RED
            self._label(mx, y + 4, lbl)
            self._val(mx, y + 9, f"{pct * 100:.0f}%", size=12, color=col)
            self._bar(mx, y + 19, 56, 2.5, pct, col)

        self._rule(17, y + 28, 195, y + 28, C_BORDER)
        interp = _safe(self.conf.get("interpretation", ""))
        self._label(17, y + 31, "Interpretation")
        self._body(17, y + 36, interp, w=176, size=7)
        concerns = self.conf.get("concerns", [])
        if concerns:
            self._body(17, y + 41, "! " + "   |  ".join(_safe(c) for c in concerns[:3]),
                       w=176, size=6.5, color=C_AMBER)
        y += 50

        # ── PROXIMITY INTELLIGENCE ────────────────────────────────────────────
        y = self._section(y, "Location & Proximity Intelligence")
        self._rect(14, y, 182, 58, C_PANEL)

        lat = self.loc.get("latitude")
        lon = self.loc.get("longitude")
        if lat and lon:
            self._label(17, y + 3, "Geocoded Coordinates")
            self._val(17, y + 8, f"{lat:.5f} N,  {lon:.5f} E", size=8, color=C_CYAN)
        self._rule(17, y + 15, 195, y + 15, C_BORDER)

        amenities = [
            ("Metro Station",  self.prox.get("distance_to_metro_km"),    2, 5),
            ("Highway",        self.prox.get("distance_to_highway_km"),  2, 5),
            ("Hospital",       self.prox.get("distance_to_hospital_km"), 1, 3),
            ("School",         self.prox.get("distance_to_school_km"),   1, 2),
            ("Mall / Market",  self.prox.get("distance_to_mall_km"),     3, 6),
            ("IT Park",        self.prox.get("distance_to_it_park_km"),  3, 8),
        ]
        for i, (lbl, dist, good, warn) in enumerate(amenities):
            cx = 17 + (i % 3) * 62
            ry = y + 18 + (i // 3) * 19
            if dist is None:
                col, ds = C_MUTED, "N/A"
            elif dist < good:
                col, ds = C_GREEN, f"{dist:.1f} km"
            elif dist < warn:
                col, ds = C_AMBER, f"{dist:.1f} km"
            else:
                col, ds = C_RED,   f"{dist:.1f} km"
            # Signal dot
            self._fill(col)
            self.ellipse(cx, ry + 1.5, 4, 4, "F")
            self._label(cx + 7, ry + 1, lbl)
            self._val(cx + 7, ry + 6, ds, size=9, color=col)
        y += 62

        # ── DOCUMENTS CHECKLIST ───────────────────────────────────────────────
        y = self._section(y, "Required Documents Checklist")
        self._rect(14, y, 182, 36, C_PANEL)

        docs = [
            "Sale Deed / Agreement to Sale",
            "Encumbrance Certificate (past 13 years)",
            "Property Tax Receipt (latest)",
            "RERA Registration Certificate",
            "Builder NOC & Approved Building Plan",
            "Occupancy Certificate",
            "Photo ID & Address Proof of Borrower",
            "Bank Statements (last 6 months)",
        ]
        for i, doc in enumerate(docs):
            cx = 17 + (i % 2) * 92
            ry = y + 4 + (i // 2) * 7.5
            self._stroke(C_BORDER)
            self.set_line_width(0.3)
            self.rect(cx, ry + 1, 3.5, 3.5)
            self.set_xy(cx + 6, ry)
            self.set_font("Helvetica", "", 7)
            self._ink(C_MUTED)
            self.cell(0, 5, doc)
        y += 40

        # ── DISCLAIMER ────────────────────────────────────────────────────────
        self._rect(14, y, 182, 14, (12, 12, 20))
        self._stroke(C_BORDER)
        self.set_line_width(0.25)
        self.rect(14, y, 182, 14)
        self.set_xy(17, y + 2.5)
        self.set_font("Helvetica", "I", 6)
        self._ink(C_MUTED)
        self.multi_cell(178, 3.5,
            "DISCLAIMER: This report is generated by an AI-powered system using synthetic and publicly available data. "
            "It is intended as a decision-support tool for trained lending professionals only and does not constitute "
            "a formal appraisal or legal valuation. Lenders must conduct independent physical inspection, title verification, "
            "and regulatory due diligence before sanctioning any loan. PropIntel AI accepts no liability for lending decisions "
            "made solely on the basis of this report."
        )


def generate_pdf(result: dict) -> bytes:
    """Generate a two-page PDF lender report and return as raw bytes."""
    pdf = LenderReport(result)
    pdf.build_page1()
    pdf.build_page2()
    return bytes(pdf.output())