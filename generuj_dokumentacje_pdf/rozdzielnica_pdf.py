#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["reportlab>=4"]
# ///
"""
rozdzielnica_pdf.py — łączy wynik skilli `obwody` i `rozdzielnica` w jeden PDF.

Wejście:
  obwody.csv  (skill obwody)        kod,kondygnacja,pomieszczenie,typ,cel,opis,kabel,uwagi
  moduly.csv  (skill rozdzielnica)  rzad,pozycja_od,pozycja_do,aparat,grupa,ilosc,moduly

Wyjście: PDF z (1) tabelą obwodów pogrupowaną po pomieszczeniach,
(2) podsumowaniem per typ / punkt zbiorczy, (3) poglądowym rysunkiem
rozdzielnicy z modułami na szynach DIN oraz (4) tabelą rozkładu rzędów.

Użycie (uv, bez instalacji w systemie):
  uv run rozdzielnica_pdf.py [--obwody obwody.csv] [--moduly moduly.csv]
                             [--out projekt.pdf] [--tytul "Dom ..."]
                             [--moduly-w-rzedzie 24]

Zależności (reportlab) uv pobierze sam z nagłówka PEP 723.
"""

import argparse
import csv
import glob
import os
import sys
from collections import Counter, OrderedDict, defaultdict

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# --------------------------------------------------------------------------
# Fonty z polskimi znakami
# --------------------------------------------------------------------------

FONT_CANDIDATES = [
    ("NotoSans", "NotoSans-Regular.ttf", "NotoSans-Bold.ttf"),
    ("DejaVuSans", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
    ("LiberationSans", "LiberationSans-Regular.ttf", "LiberationSans-Bold.ttf"),
]
FONT_DIRS = [
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    os.path.expanduser("~/.fonts"),
    os.path.expanduser("~/.local/share/fonts"),
    "C:/Windows/Fonts",
    "/Library/Fonts",
    "/System/Library/Fonts",
]


def _find_font(filename):
    for d in FONT_DIRS:
        if not os.path.isdir(d):
            continue
        hits = glob.glob(os.path.join(d, "**", filename), recursive=True)
        if hits:
            return hits[0]
    return None


def register_fonts():
    """Zwraca (font_regular, font_bold). Spada na Helvetica, gdy brak TTF."""
    for name, reg, bold in FONT_CANDIDATES:
        reg_path = _find_font(reg)
        bold_path = _find_font(bold)
        if reg_path and bold_path:
            pdfmetrics.registerFont(TTFont(name, reg_path))
            pdfmetrics.registerFont(TTFont(name + "-Bold", bold_path))
            return name, name + "-Bold"
    print(
        "UWAGA: nie znaleziono fontu TTF z polskimi znakami — używam Helvetica "
        "(polskie litery mogą być niepoprawne).",
        file=sys.stderr,
    )
    return "Helvetica", "Helvetica-Bold"


# --------------------------------------------------------------------------
# Wczytywanie CSV
# --------------------------------------------------------------------------

OBWODY_COLS = ["kod", "kondygnacja", "pomieszczenie", "typ", "cel", "opis", "kabel", "uwagi"]
MODULY_COLS = ["rzad", "pozycja_od", "pozycja_do", "aparat", "grupa", "ilosc", "moduly"]


def read_csv(path, required):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        sys.exit(f"{path}: plik jest pusty")
    missing = [c for c in required if c not in rows[0]]
    if missing:
        sys.exit(f"{path}: brak kolumn {missing} — oczekiwano nagłówka {','.join(required)}")
    return rows


def load_moduly(path):
    rows = read_csv(path, MODULY_COLS)
    out = []
    for r in rows:
        try:
            out.append(
                {
                    "rzad": int(r["rzad"]),
                    "od": int(r["pozycja_od"]),
                    "do": int(r["pozycja_do"]),
                    "aparat": r["aparat"].strip(),
                    "grupa": r["grupa"].strip(),
                    "ilosc": int(r["ilosc"] or 1),
                    "moduly": int(r["moduly"] or (int(r["pozycja_do"]) - int(r["pozycja_od"]) + 1)),
                }
            )
        except ValueError as e:
            sys.exit(f"{path}: błędny wiersz {r}: {e}")
    out.sort(key=lambda m: (m["rzad"], m["od"]))
    return out


# --------------------------------------------------------------------------
# Kolory grup (aparaty) i typów (obwody)
# --------------------------------------------------------------------------

GROUP_PALETTE = [
    colors.HexColor("#4e79a7"),
    colors.HexColor("#f28e2b"),
    colors.HexColor("#59a14f"),
    colors.HexColor("#e15759"),
    colors.HexColor("#b07aa1"),
    colors.HexColor("#76b7b2"),
    colors.HexColor("#edc948"),
    colors.HexColor("#ff9da7"),
    colors.HexColor("#9c755f"),
    colors.HexColor("#bab0ac"),
]
FREE_COLOR = colors.HexColor("#f2f2f2")
CEL_COLORS = {
    "rozdzielnica": colors.HexColor("#dbe9f6"),
    "centrala alarmowa": colors.HexColor("#fde2cf"),
    "szafa rack": colors.HexColor("#dff0d8"),
}


def group_colors(moduly):
    groups = OrderedDict()
    for m in moduly:
        if m["aparat"].upper() == "WOLNE":
            continue
        groups.setdefault(m["grupa"], None)
    for i, g in enumerate(groups):
        groups[g] = GROUP_PALETTE[i % len(GROUP_PALETTE)]
    return groups


def is_free(m):
    return m["aparat"].strip().upper() == "WOLNE"


def short_label(aparat):
    """Krótka etykieta na moduł: tekst przed nawiasem, skrócony."""
    base = aparat.split("(")[0].strip()
    repl = [
        ("rozłącznik główny", "FR"),
        ("różnicówka", "RCD"),
        ("lampka obecności faz", "L1L2L3"),
        ("eska", "MCB"),
        ("zasilacz", "PSU"),
        ("patch panel", "PATCH"),
        ("strefa niskonapięciowa", "LV"),
    ]
    low = base.lower()
    for a, b in repl:
        if low.startswith(a):
            base = b + base[len(a):]
            break
    return base


# --------------------------------------------------------------------------
# Rysunek rozdzielnicy
# --------------------------------------------------------------------------


class SwitchboardDrawing(Flowable):
    """Rysuje obudowę z rzędami szyn DIN i blokami aparatów."""

    def __init__(self, moduly, per_row, gcolors, font, font_bold, width, max_height=None):
        super().__init__()
        self.moduly = moduly
        self.per_row = per_row
        self.gcolors = gcolors
        self.font = font
        self.font_bold = font_bold
        self.rows = sorted({m["rzad"] for m in moduly})
        self.margin = 8 * mm
        self.row_h = 22 * mm
        self.row_gap = 6 * mm
        self.width = width
        self.max_height = max_height
        self._layout()

    def _layout(self):
        n = len(self.rows)
        self.height = self.margin * 2 + n * self.row_h + (n - 1) * self.row_gap
        if self.max_height and self.height > self.max_height:
            # zmniejsz rzędy proporcjonalnie, żeby rysunek zmieścił się na stronie
            k = (self.max_height - self.margin * 2) / (n * self.row_h + (n - 1) * self.row_gap)
            self.row_h = max(self.row_h * k, 10 * mm)
            self.row_gap = max(self.row_gap * k, 3 * mm)
            self.height = self.margin * 2 + n * self.row_h + (n - 1) * self.row_gap

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        c = self.canv
        W, H = self.width, self.height
        # obudowa
        c.setLineWidth(1.6)
        c.setStrokeColor(colors.HexColor("#333333"))
        c.setFillColor(colors.HexColor("#fafafa"))
        c.roundRect(0, 0, W, H, 3 * mm, stroke=1, fill=1)

        inner_w = W - 2 * self.margin - 10 * mm  # miejsce na etykietę rzędu po lewej
        x0 = self.margin + 10 * mm
        mod_w = inner_w / self.per_row

        by_row = defaultdict(list)
        for m in self.moduly:
            by_row[m["rzad"]].append(m)

        for i, r in enumerate(self.rows):
            y_top = H - self.margin - i * (self.row_h + self.row_gap)
            y_bot = y_top - self.row_h
            # etykieta rzędu
            c.setFont(self.font_bold, 8)
            c.setFillColor(colors.black)
            c.drawString(self.margin, y_bot + self.row_h / 2 - 3, f"R{r}")
            # szyna DIN
            c.setFillColor(colors.HexColor("#c9c9c9"))
            c.setStrokeColor(colors.HexColor("#8a8a8a"))
            c.setLineWidth(0.5)
            c.rect(x0, y_bot + self.row_h * 0.38, inner_w, self.row_h * 0.24, stroke=1, fill=1)
            # siatka modułów
            c.setStrokeColor(colors.HexColor("#dddddd"))
            c.setLineWidth(0.3)
            for k in range(self.per_row + 1):
                xx = x0 + k * mod_w
                c.line(xx, y_bot, xx, y_top)
            # bloki aparatów
            for m in by_row[r]:
                if m["do"] > self.per_row:
                    # blok wykracza poza rząd — przytnij, ale zaznacz
                    pass
                x = x0 + (m["od"] - 1) * mod_w
                w = (m["do"] - m["od"] + 1) * mod_w
                free = is_free(m)
                fill = FREE_COLOR if free else self.gcolors.get(m["grupa"], colors.grey)
                c.setFillColor(fill)
                c.setStrokeColor(colors.HexColor("#555555") if not free else colors.HexColor("#bbbbbb"))
                c.setLineWidth(0.8)
                if free:
                    c.setDash(2, 2)
                c.rect(x + 0.6, y_bot + 1.5, w - 1.2, self.row_h - 3, stroke=1, fill=1)
                c.setDash()
                # pojedyncze aparaty w bloku (ilosc > 1) — cienkie podziały
                if not free and m["ilosc"] > 1:
                    each = w / m["ilosc"]
                    c.setStrokeColor(colors.Color(0, 0, 0, alpha=0.35))
                    c.setLineWidth(0.5)
                    for k in range(1, m["ilosc"]):
                        xx = x + k * each
                        c.line(xx, y_bot + 1.5, xx, y_top - 1.5)
                # etykieta
                label = "WOLNE" if free else short_label(m["aparat"])
                if free:
                    txt_color = colors.HexColor("#666666")
                else:
                    lum = 0.299 * fill.red + 0.587 * fill.green + 0.114 * fill.blue
                    txt_color = colors.white if lum < 0.6 else colors.HexColor("#222222")
                c.setFillColor(txt_color)
                self._fit_text(c, label, x + w / 2, y_top - 7, w - 3, self.font_bold, 7)
                sub = f"{m['moduly']} mod" if free else (
                    f"{m['ilosc']}× / {m['moduly']} mod" if m["ilosc"] > 1 else f"{m['moduly']} mod"
                )
                self._fit_text(c, sub, x + w / 2, y_bot + 4, w - 3, self.font, 6)
            # numeracja pozycji
            c.setFont(self.font, 5)
            c.setFillColor(colors.HexColor("#777777"))
            for k in range(self.per_row):
                c.drawCentredString(x0 + (k + 0.5) * mod_w, y_bot - 5, str(k + 1))

    def _fit_text(self, c, text, cx, y, max_w, font, size):
        """Rysuje tekst wyśrodkowany; zmniejsza font albo obcina, gdy nie wchodzi."""
        s = size
        while s >= 4 and pdfmetrics.stringWidth(text, font, s) > max_w:
            s -= 0.5
        if s < 4:
            s = 4
            while text and pdfmetrics.stringWidth(text + "…", font, s) > max_w:
                text = text[:-1]
            text = text + "…" if text else ""
        if not text:
            return
        c.setFont(font, s)
        c.drawCentredString(cx, y, text)


# --------------------------------------------------------------------------
# Budowa dokumentu
# --------------------------------------------------------------------------


def build_pdf(obwody, moduly, out_path, title, per_row, font, font_bold):
    page = landscape(A4)
    doc = SimpleDocTemplate(
        out_path,
        pagesize=page,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=14 * mm,
        title=title,
        author="skills: obwody + rozdzielnica",
    )
    avail_w = page[0] - doc.leftMargin - doc.rightMargin

    ss = getSampleStyleSheet()
    st_h1 = ParagraphStyle("h1", parent=ss["Title"], fontName=font_bold, fontSize=18, spaceAfter=4)
    st_h2 = ParagraphStyle("h2", parent=ss["Heading2"], fontName=font_bold, fontSize=13, spaceBefore=8, spaceAfter=4)
    st_h3 = ParagraphStyle("h3", parent=ss["Heading3"], fontName=font_bold, fontSize=10.5, spaceBefore=6, spaceAfter=2)
    st_body = ParagraphStyle("body", parent=ss["Normal"], fontName=font, fontSize=9, leading=11)
    st_small = ParagraphStyle("small", parent=st_body, fontSize=7.5, leading=9)
    st_cell = ParagraphStyle("cell", parent=st_body, fontSize=7.5, leading=9)
    st_cell_b = ParagraphStyle("cellb", parent=st_cell, fontName=font_bold)
    st_center = ParagraphStyle("center", parent=st_body, alignment=TA_CENTER)

    story = []

    # ---------- strona tytułowa / podsumowanie ----------
    story.append(Paragraph(title, st_h1))
    story.append(Paragraph("Lista obwodów i poglądowy projekt rozdzielnicy smart home", st_center))
    story.append(Spacer(1, 6 * mm))

    by_typ = Counter(o["typ"] for o in obwody)
    by_cel = Counter(o["cel"] for o in obwody)
    rooms = OrderedDict()
    for o in obwody:
        rooms.setdefault((o["kondygnacja"], o["pomieszczenie"]), []).append(o)

    story.append(Paragraph("Podsumowanie", st_h2))
    summary = [
        [Paragraph("<b>Obwodów łącznie</b>", st_cell), str(len(obwody))],
        [Paragraph("<b>Pomieszczeń</b>", st_cell), str(len(rooms))],
    ]
    for cel in ["rozdzielnica", "centrala alarmowa", "szafa rack"]:
        if by_cel.get(cel):
            summary.append([Paragraph(f"<b>→ {cel}</b>", st_cell), str(by_cel[cel])])
    for cel in by_cel:
        if cel not in CEL_COLORS:
            summary.append([Paragraph(f"<b>→ {cel}</b>", st_cell), str(by_cel[cel])])
    t_sum = Table(summary, colWidths=[60 * mm, 25 * mm], hAlign="LEFT")
    t_sum.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    typ_rows = [["Typ", "Ilość"]] + [[t, str(n)] for t, n in sorted(by_typ.items(), key=lambda x: -x[1])]
    t_typ = Table(typ_rows, colWidths=[25 * mm, 18 * mm], hAlign="LEFT")
    t_typ.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("FONTNAME", (0, 1), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6e6e6")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ]
        )
    )

    used = sum(m["moduly"] for m in moduly if not is_free(m))
    free = sum(m["moduly"] for m in moduly if is_free(m))
    nrows = len({m["rzad"] for m in moduly})
    total = nrows * per_row
    mod_rows = [
        [Paragraph("<b>Obudowa</b>", st_cell), f"{nrows} rzędy × {per_row} modułów = {total}"],
        [Paragraph("<b>Zajęte moduły</b>", st_cell), str(used)],
        [Paragraph("<b>Wolne (rezerwa)</b>", st_cell), f"{free}  ({(free / total * 100) if total else 0:.0f}%)"],
    ]
    t_mod = Table(mod_rows, colWidths=[35 * mm, 50 * mm], hAlign="LEFT")
    t_mod.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )

    side = Table(
        [[t_sum, t_typ, t_mod]],
        colWidths=[95 * mm, 55 * mm, 95 * mm],
        hAlign="LEFT",
    )
    side.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(side)
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "Projekt poglądowy. Ostateczne przekroje kabli, dobór zabezpieczeń i zgodność z przepisami "
            "potwierdza elektryk z uprawnieniami.",
            st_small,
        )
    )
    story.append(PageBreak())

    # ---------- tabela obwodów ----------
    story.append(Paragraph("Tabela obwodów", st_h2))
    legend = "  ".join(
        f'<font backcolor="{c.hexval()}">&nbsp;&nbsp;&nbsp;</font> {name}' for name, c in CEL_COLORS.items()
    )
    story.append(Paragraph("Kolor wiersza = punkt zbiorczy: " + legend, st_small))
    story.append(Spacer(1, 2 * mm))

    col_w = [22, 16, 40, 40, 28, 0, 0, 0]
    # reszta szerokości na opis i uwagi
    rest = avail_w - sum(w * mm for w in col_w if w)
    widths = [
        22 * mm,  # kod
        14 * mm,  # typ
        30 * mm,  # cel
        rest * 0.45,  # opis
        40 * mm,  # kabel
        rest * 0.55,  # uwagi
    ]
    header = [Paragraph(h, st_cell_b) for h in ["Kod", "Typ", "Punkt zbiorczy", "Opis", "Kabel", "Uwagi"]]

    for (kond, pom), items in rooms.items():
        data = [header]
        styles = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]
        for i, o in enumerate(items, start=1):
            data.append(
                [
                    Paragraph(o["kod"], st_cell_b),
                    Paragraph(o["typ"], st_cell),
                    Paragraph(o["cel"], st_cell),
                    Paragraph(o["opis"], st_cell),
                    Paragraph(o["kabel"], st_cell),
                    Paragraph(o["uwagi"], st_cell),
                ]
            )
            bg = CEL_COLORS.get(o["cel"].strip().lower())
            if bg:
                styles.append(("BACKGROUND", (0, i), (-1, i), bg))
        t = Table(data, colWidths=widths, repeatRows=1)
        t.setStyle(TableStyle(styles))
        miejsce = items[0]["kod"].split("-")[0]
        story.append(
            KeepTogether(
                [
                    Paragraph(f"{miejsce} · {pom} <font size=8 color='#666666'>({kond}, {len(items)} obw.)</font>", st_h3),
                    t,
                ]
            )
        )
        story.append(Spacer(1, 3 * mm))

    story.append(PageBreak())

    # ---------- rozdzielnica — rysunek ----------
    gcolors = group_colors(moduly)
    story.append(Paragraph("Przykładowa rozdzielnica — rozkład aparatów", st_h2))
    story.append(
        Paragraph(
            f"Obudowa {nrows} × {per_row} modułów. Każdy rząd = jedna szyna DIN; blok z kilkoma aparatami "
            "(np. 8 esek) ma cienkie podziały. Pola kreskowane to rezerwa na przyszłe obwody.",
            st_small,
        )
    )
    story.append(Spacer(1, 3 * mm))
    n_leg_lines = (len(gcolors) + 1 + 4) // 5
    avail_h = page[1] - doc.topMargin - doc.bottomMargin - 30 * mm - n_leg_lines * 6 * mm
    story.append(SwitchboardDrawing(moduly, per_row, gcolors, font, font_bold, avail_w, max_height=avail_h))
    story.append(Spacer(1, 3 * mm))

    # legenda grup
    leg_cells = []
    for g, c in gcolors.items():
        leg_cells.append(Paragraph(f'<font backcolor="{c.hexval()}" color="{c.hexval()}">&nbsp;&nbsp;&nbsp;&nbsp;</font> {g}', st_small))
    leg_cells.append(Paragraph(f'<font backcolor="{FREE_COLOR.hexval()}" color="{FREE_COLOR.hexval()}">&nbsp;&nbsp;&nbsp;&nbsp;</font> WOLNE / rezerwa', st_small))
    per_line = 5
    leg_rows = [leg_cells[i : i + per_line] for i in range(0, len(leg_cells), per_line)]
    for r in leg_rows:
        while len(r) < per_line:
            r.append("")
    leg = Table(leg_rows, colWidths=[avail_w / per_line] * per_line, hAlign="LEFT")
    story.append(leg)

    # ---------- rozkład rzędów — tabela ----------
    story.append(PageBreak())
    story.append(Paragraph("Rozkład rzędów (moduly.csv)", st_h2))
    hdr = [Paragraph(h, st_cell_b) for h in ["Rząd", "Poz.", "Aparat", "Grupa", "Ilość", "Moduły"]]
    data = [hdr]
    styles = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 1), (1, -1), "CENTER"),
        ("ALIGN", (4, 1), (5, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 7.5),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    prev_row = None
    for i, m in enumerate(moduly, start=1):
        data.append(
            [
                str(m["rzad"]),
                f"{m['od']}–{m['do']}",
                Paragraph(m["aparat"], st_cell),
                Paragraph(m["grupa"], st_cell),
                str(m["ilosc"]) if not is_free(m) else "",
                str(m["moduly"]),
            ]
        )
        c = FREE_COLOR if is_free(m) else gcolors.get(m["grupa"])
        if c:
            # jasna wersja koloru grupy jako tło komórki "Grupa"
            light = colors.Color(1 - (1 - c.red) * 0.35, 1 - (1 - c.green) * 0.35, 1 - (1 - c.blue) * 0.35)
            styles.append(("BACKGROUND", (3, i), (3, i), light if not is_free(m) else FREE_COLOR))
        if prev_row is not None and m["rzad"] != prev_row:
            styles.append(("LINEABOVE", (0, i), (-1, i), 1.2, colors.black))
        prev_row = m["rzad"]
    t = Table(
        data,
        colWidths=[14 * mm, 18 * mm, avail_w - 14 * mm - 18 * mm - 55 * mm - 16 * mm - 18 * mm, 55 * mm, 16 * mm, 18 * mm],
        repeatRows=1,
    )
    t.setStyle(TableStyle(styles))
    story.append(t)
    story.append(Spacer(1, 4 * mm))

    # zestawienie zakupowe z moduly.csv
    story.append(Paragraph("Zestawienie aparatów (z rozkładu rzędów)", st_h2))
    agg = OrderedDict()
    for m in moduly:
        if is_free(m):
            continue
        key = (m["grupa"], m["aparat"])
        agg[key] = agg.get(key, 0) + m["ilosc"]
    data = [[Paragraph(h, st_cell_b) for h in ["Grupa", "Aparat", "Sztuk"]]]
    for (g, a), n in agg.items():
        data.append([Paragraph(g, st_cell), Paragraph(a, st_cell), str(n)])
    t = Table(data, colWidths=[55 * mm, avail_w - 55 * mm - 18 * mm, 18 * mm], repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (2, 1), (2, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 4 * mm))
    story.append(
        Paragraph(
            "Projekt poglądowy — wymaga weryfikacji elektryka z uprawnieniami i zgodności z aktualnymi normami.",
            st_small,
        )
    )

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont(font, 7)
        canvas.setFillColor(colors.grey)
        canvas.drawString(doc_.leftMargin, 8 * mm, title)
        canvas.drawRightString(page[0] - doc_.rightMargin, 8 * mm, f"strona {doc_.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


# --------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description="Łączy obwody.csv i moduly.csv w jeden PDF.")
    ap.add_argument("--obwody", default="obwody.csv", help="ścieżka do obwody.csv (skill obwody)")
    ap.add_argument("--moduly", default="moduly.csv", help="ścieżka do moduly.csv (skill rozdzielnica)")
    ap.add_argument("--out", default="projekt_instalacji.pdf", help="plik wyjściowy PDF")
    ap.add_argument("--tytul", default="Projekt instalacji smart home", help="tytuł na stronie głównej")
    ap.add_argument(
        "--moduly-w-rzedzie",
        type=int,
        default=None,
        help="liczba modułów w rzędzie obudowy (domyślnie: max pozycja_do z moduly.csv)",
    )
    args = ap.parse_args()

    sources = [
        (args.obwody, "--obwody", "obwody.csv", "skill `obwody`"),
        (args.moduly, "--moduly", "moduly.csv", "skill `rozdzielnica` (Faza 4)"),
    ]
    errors = []
    for path, opt, default, skill in sources:
        if not os.path.isfile(path):
            hint = (
                f"nie podano {opt}, więc szukałem domyślnego `{default}` w bieżącym katalogu ({os.getcwd()})"
                if path == default
                else f"ścieżka z {opt}"
            )
            errors.append(f"BŁĄD: brak pliku `{path}` — {hint}. Plik generuje {skill}.")
    if errors:
        sys.exit("\n".join(errors))
    out_dir = os.path.dirname(os.path.abspath(args.out))
    if not os.path.isdir(out_dir):
        sys.exit(f"BŁĄD: katalog wyjściowy nie istnieje: {out_dir}")

    obwody = read_csv(args.obwody, OBWODY_COLS)
    moduly = load_moduly(args.moduly)
    per_row = args.moduly_w_rzedzie or max(m["do"] for m in moduly)
    over = [m for m in moduly if m["do"] > per_row]
    if over:
        sys.exit(f"Bloki wykraczają poza {per_row} modułów w rzędzie: {[m['aparat'] for m in over]}")

    font, font_bold = register_fonts()
    build_pdf(obwody, moduly, args.out, args.tytul, per_row, font, font_bold)
    print(f"Zapisano: {args.out}  ({len(obwody)} obwodów, {len(moduly)} bloków aparatów)")


if __name__ == "__main__":
    main()

