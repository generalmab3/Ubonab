"""Build an RTL PDF of slides/index.html (presentation pages, no speaker notes)."""

import re
import sys
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF

ROOT = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
OUT = ROOT / "defense.pdf"


def fa(s):
    s = (s or "").replace("\xa0", " ").strip()
    if not s:
        return ""
    return get_display(arabic_reshaper.reshape(s))


def tidy_math(s):
    s = s.replace("\\,", " ").replace("\\quad", "  ").replace("\\qquad", "   ")
    s = s.replace("\\mathrm", "").replace("\\text", "").replace("\\mathbf", "")
    s = s.replace("\\operatorname", "").replace("\\mathcal", "")
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
    s = s.replace("\\bar", "")
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
        notes = re.search(r'class="notes">(.*?)</div>', raw, re.S)
        imgs = re.findall(r'<img class="fig" src="([^"]+)"', raw)
        tables = table_lines(raw)
        body = re.sub(r'<div class="notes">.*?</div>', "", raw, flags=re.S)
        body = re.sub(r"<table[\s\S]*?</table>", "", body)
        body = re.sub(r"<h1>.*?</h1>|<h2>.*?</h2>|<p class=\"kicker\">.*?</p>", "", body, flags=re.S)
        body = re.sub(r"<img[^>]*>", "", body)
        title_txt = ""
        if title:
            title_txt = title.group(1) or title.group(2)
        out.append(
            {
                "kicker": kick.group(1) if kick else "",
                "title": title_txt,
                "body": strip_tags(body),
                "notes": strip_tags(notes.group(1)) if notes else "",
                "imgs": imgs,
                "tables": tables,
            }
        )
    return out


class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", "", 9)
        self.set_text_color(95, 83, 78)
        self.cell(
            0,
            6,
            fa("جلسه دفاع · یادگیری فیزیک‌آگاه با قیود سخت · بابازاد · بناب"),
            align="R",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.set_draw_color(31, 74, 66)
        self.set_line_width(0.5)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("DejaVu", "", 9)
        self.set_text_color(95, 83, 78)
        self.cell(0, 8, fa("صفحه %s" % self.page_no()), align="C")


def main():
    html_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "index.html"
    if not html_path.is_absolute():
        html_path = (Path.cwd() / html_path).resolve()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else OUT
    if not out.is_absolute():
        out = (Path.cwd() / out).resolve()
    slides = blocks(html_path.read_text(encoding="utf-8"))
    pdf = PDF(orientation="L", format="A4", unit="mm")
    pdf.set_auto_page_break(True, 16)
    pdf.set_margins(16, 16, 16)
    pdf.add_font("DejaVu", "", FONT)
    pdf.add_font("DejaVu", "B", FONTB)
    w = pdf.w - pdf.l_margin - pdf.r_margin
    for s in slides:
        pdf.add_page()
        pdf.set_font("DejaVu", "", 11)
        pdf.set_text_color(47, 111, 100)
        if s["kicker"]:
            pdf.cell(w, 7, fa(s["kicker"]), align="R", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("DejaVu", "B", 18)
        pdf.set_text_color(20, 41, 36)
        pdf.multi_cell(w, 9, fa(s["title"] or " "), align="R")
        pdf.ln(2)
        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(28, 25, 23)
        if s["body"]:
            pdf.multi_cell(w, 7, fa(s["body"]), align="R")
            pdf.ln(1)
        if s["tables"]:
            pdf.set_font("DejaVu", "", 11)
            for line in s["tables"]:
                pdf.multi_cell(w, 6.2, fa(line), align="R")
            pdf.ln(1)
        for src in s["imgs"]:
            img = (ROOT / src).resolve()
            if img.exists():
                try:
                    pdf.image(str(img), x=pdf.l_margin + 28, w=w - 56)
                    pdf.ln(3)
                except Exception:
                    pass
    pdf.output(out)
    print("wrote", out, "pages", pdf.page_no(), "slides", len(slides))


if __name__ == "__main__":
    main()
