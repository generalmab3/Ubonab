"""Build a study PDF from slides/index.html (RTL Persian, DejaVu)."""

import re
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = ROOT / "defense-handbook.pdf"


def fa(s):
    s = (s or "").replace("\xa0", " ").strip()
    if not s:
        return ""
    return get_display(arabic_reshaper.reshape(s))


def tidy_math(s):
    s = s.replace("\\,", " ").replace("\\quad", "  ").replace("\\qquad", "   ")
    s = s.replace("\\mathrm", "").replace("\\text", "").replace("\\mathbf", "")
    s = s.replace("\\bigl", "").replace("\\bigr", "")
    s = s.replace("\\Bigl", "").replace("\\Bigr", "")
    s = s.replace("\\left", "").replace("\\right", "")
    s = s.replace("\\min", "min").replace("\\max", "max")
    s = s.replace("\\tanh", "tanh").replace("\\clip", "clip")
    s = s.replace("\\frac", " ").replace("\\tfrac", " ")
    s = s.replace("\\sum", "sum ").replace("\\pm", "±")
    s = s.replace("\\le", "≤").replace("\\ge", "≥").replace("\\neq", "≠")
    s = s.replace("\\times", "×").replace("\\cdot", "·")
    s = s.replace("\\star", "*").replace("\\hat", "")
    s = s.replace("\\Delta", "Δ").replace("\\eta", "η").replace("\\kappa", "κ")
    s = s.replace("\\mathcal", "").replace("\\mathrm", "")
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    s = s.replace("{", "").replace("}", "")
    s = s.replace("\\", "")
    return s


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</(p|div|li|h1|h2|h3|tr|pre)>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&nbsp;", " ").replace("&lt;", "<").replace("&gt;", ">")
    s = tidy_math(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n[ \t]+", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def table_lines(raw):
    lines = []
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.S):
        cells = [strip_tags(c) for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", row, re.S)]
        cells = [c for c in cells if c]
        if cells:
            lines.append("  |  ".join(cells))
    return lines


def blocks(html):
    out = []
    for raw in re.findall(r"<section class=\"slide[^\"]*\">(.*?)</section>", html, re.S):
        kick = re.search(r'class="kicker">([^<]+)', raw)
        title = re.search(r"<h1>([^<]+)</h1>|<h2>([^<]+)</h2>", raw)
        q = re.search(r'class="q">([^<]+)', raw)
        notes = re.search(r'class="notes">(.*?)</div>', raw, re.S)
        imgs = re.findall(r'<img class="fig" src="([^"]+)"', raw)
        codes = [strip_tags(c) for c in re.findall(r"<pre class=\"code\">(.*?)</pre>", raw, re.S)]
        tables = table_lines(raw)
        body = re.sub(r'<div class="notes">.*?</div>', "", raw, flags=re.S)
        body = re.sub(r"<pre class=\"code\">.*?</pre>", "", body, flags=re.S)
        body = re.sub(r"<table[\s\S]*?</table>", "", body)
        body = re.sub(r"<h1>.*?</h1>|<h2>.*?</h2>|<p class=\"kicker\">.*?</p>", "", body, flags=re.S)
        body = re.sub(r'<img[^>]*>', "", body)
        title_txt = ""
        if title:
            title_txt = title.group(1) or title.group(2)
        elif q:
            title_txt = q.group(1)
        out.append(
            {
                "kicker": kick.group(1) if kick else "",
                "title": title_txt,
                "body": strip_tags(body),
                "notes": strip_tags(notes.group(1)) if notes else "",
                "imgs": imgs,
                "codes": codes,
                "tables": tables,
            }
        )
    return out


class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "", 9)
        self.set_text_color(90, 99, 95)
        self.cell(
            0,
            6,
            fa("درسنامه دفاع · یادگیری فیزیک‌آگاه با قیود سخت · بابازاد · بناب"),
            align="R",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_draw_color(176, 137, 62)
        self.set_line_width(0.6)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(4)

    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(90, 99, 95)
        self.cell(0, 8, fa("صفحه %s" % self.page_no()), align="C")


def main():
    slides = blocks(HTML)
    pdf = PDF(orientation="L", format="A4", unit="mm")
    pdf.set_auto_page_break(True, 16)
    pdf.set_margins(16, 18, 16)
    pdf.add_font("DejaVu", "", FONT)
    pdf.add_font("DejaVu", "B", FONTB)
    w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.add_page()
    pdf.set_font("DejaVu", "B", 22)
    pdf.set_text_color(14, 79, 76)
    pdf.multi_cell(w, 12, fa("درسنامه جلسه دفاع"), align="R")
    pdf.set_font("DejaVu", "", 14)
    pdf.multi_cell(
        w,
        8,
        fa("یادگیری فیزیک‌آگاه با قیود سخت برای مدیریت انرژی ریزشبکه متصل به شبکه"),
        align="R",
    )
    pdf.ln(2)
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(w, 7, fa("محمد امیر بابازاد · استاد راهنما: دکتر بابک آذرنوید · دانشگاه بناب · شهریور ۱۴۰۵"), align="R")
    pdf.ln(3)
    pdf.set_font("DejaVu", "B", 14)
    pdf.multi_cell(w, 8, fa("فهرست اسلایدها"), align="R")
    pdf.set_font("DejaVu", "", 11)
    for i, s in enumerate(slides, 1):
        line = "%02d. %s — %s" % (i, s["kicker"] or "—", s["title"] or "")
        pdf.multi_cell(w, 6, fa(line), align="R")

    for s in slides:
        pdf.add_page()
        pdf.set_font("DejaVu", "", 11)
        pdf.set_text_color(27, 124, 116)
        if s["kicker"]:
            pdf.cell(w, 7, fa(s["kicker"]), align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "B", 18)
        pdf.set_text_color(14, 79, 76)
        pdf.multi_cell(w, 9, fa(s["title"] or " "), align="R")
        pdf.ln(2)
        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(19, 32, 28)
        if s["body"]:
            pdf.multi_cell(w, 7, fa(s["body"]), align="R")
            pdf.ln(1)
        if s["tables"]:
            pdf.set_font("DejaVu", "", 11)
            for line in s["tables"]:
                pdf.multi_cell(w, 6.2, fa(line), align="R")
            pdf.ln(1)
        if s["codes"]:
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(24, 34, 31)
            for c in s["codes"]:
                pdf.multi_cell(w, 5.5, c, align="L")
            pdf.set_text_color(19, 32, 28)
            pdf.ln(1)
        for src in s["imgs"]:
            img = (ROOT / src).resolve()
            if img.exists():
                try:
                    pdf.image(str(img), x=pdf.l_margin + 36, w=w - 72)
                    pdf.ln(3)
                except Exception:
                    pass
        if s["notes"]:
            pdf.set_fill_color(255, 248, 232)
            pdf.set_text_color(74, 64, 48)
            pdf.set_font("DejaVu", "B", 11)
            pdf.multi_cell(w, 7, fa("یادداشت گوینده / پاسخ داور"), align="R", fill=True)
            pdf.set_font("DejaVu", "", 11)
            pdf.multi_cell(w, 6.5, fa(s["notes"]), align="R", fill=True)
    pdf.output(OUT)
    print("wrote", OUT, "pages", pdf.page_no(), "slides", len(slides))


if __name__ == "__main__":
    main()
