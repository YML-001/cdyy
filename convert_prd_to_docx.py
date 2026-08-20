#!/usr/bin/env python3
"""将 PRD.md 转换为格式化的 Word 文档（PRD.docx）。"""
import os
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml, OxmlElement

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(BASE_DIR, "PRD.md")
OUT_FILE = os.path.join(BASE_DIR, "PRD.docx")

CN_FONT = "微软雅黑"
MONO_FONT = "Consolas"
H_COLORS = {1: RGBColor(0x1A, 0x3C, 0x6E), 2: RGBColor(0x2B, 0x57, 0x9A),
            3: RGBColor(0x3A, 0x6E, 0xA5), 4: RGBColor(0x5A, 0x7C, 0xA8)}
HEADER_FILL = "2B579A"


def set_font(run, name=CN_FONT, size=None, bold=None, color=None):
    run.font.name = name
    r = run._element
    rPr = r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:eastAsia'), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def add_runs_with_bold(paragraph, text, size=10.5, base_color=None):
    """解析 **加粗** 与 `代码` 行内标记。"""
    text = text.replace("\\(", "(").replace("\\)", ")")
    parts = re.split(r'(\*\*[^*]+\*\*|`[^`]+`)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            set_font(run, size=size, bold=True, color=base_color)
        elif part.startswith('`') and part.endswith('`'):
            run = paragraph.add_run(part[1:-1])
            set_font(run, name=MONO_FONT, size=size - 0.5, color=RGBColor(0xC0, 0x39, 0x2B))
        else:
            run = paragraph.add_run(part)
            set_font(run, size=size, color=base_color)


def add_heading(doc, text, level):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10 if level <= 2 else 6)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    sizes = {1: 18, 2: 14.5, 3: 12.5, 4: 11}
    set_font(run, size=sizes.get(level, 11), bold=True, color=H_COLORS.get(level, H_COLORS[4]))
    return p


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = 'Table Grid'
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        para = cell.paragraphs[0]
        add_runs_with_bold(para, h, size=9)
        for run in para.runs:
            run.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{HEADER_FILL}"/>')
        cell._tc.get_or_add_tcPr().append(shading)
    for ri, row in enumerate(rows):
        for ci in range(len(headers)):
            val = row[ci] if ci < len(row) else ''
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ''
            add_runs_with_bold(cell.paragraphs[0], val, size=9)
            if ri % 2 == 1:
                shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F2F6FC"/>')
                cell._tc.get_or_add_tcPr().append(shading)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_code_block(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    set_font(run, name=MONO_FONT, size=9, color=RGBColor(0x33, 0x33, 0x33))
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F5F5F5" w:val="clear"/>')
    p._element.get_or_add_pPr().append(shading)


def add_bullet(doc, text, indent=0):
    p = doc.add_paragraph(style='List Bullet')
    p.clear()
    if indent:
        p.paragraph_format.left_indent = Cm(0.75 + 0.6 * indent)
    p.paragraph_format.space_after = Pt(2)
    add_runs_with_bold(p, text, size=10.5)


def add_para(doc, text, size=10.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    add_runs_with_bold(p, text, size=size)


def add_quote(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.5)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    add_runs_with_bold(p, text, size=10, base_color=RGBColor(0x55, 0x55, 0x55))
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="FFF8E1" w:val="clear"/>')
    p._element.get_or_add_pPr().append(shading)


def split_table_row(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]


def is_separator(cells):
    return all(re.fullmatch(r':?-{2,}:?', c.strip()) for c in cells if c.strip() != '') and any(cells)


def build():
    with open(MD_FILE, encoding='utf-8') as f:
        lines = f.read().split('\n')

    doc = Document()
    normal = doc.styles['Normal']
    normal.font.name = CN_FONT
    normal.font.size = Pt(10.5)
    normal.element.rPr.rFonts.set(qn('w:eastAsia'), CN_FONT)
    sec = doc.sections[0]
    sec.top_margin = Cm(2.4); sec.bottom_margin = Cm(2.4)
    sec.left_margin = Cm(2.4); sec.right_margin = Cm(2.4)

    i = 0
    in_code = False
    code_lines = []
    while i < len(lines):
        line = lines[i]

        if line.strip().startswith('```'):
            if in_code:
                add_code_block(doc, '\n'.join(code_lines))
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue

        stripped = line.strip()

        if stripped == '' or stripped == '---':
            i += 1
            continue

        m = re.match(r'^(#{1,4})\s+(.*)$', stripped)
        if m:
            add_heading(doc, m.group(2).strip(), len(m.group(1)))
            i += 1
            continue

        if stripped.startswith('|') and i + 1 < len(lines) and '|' in lines[i + 1] and is_separator(split_table_row(lines[i + 1])):
            headers = split_table_row(line)
            rows = []
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append(split_table_row(lines[i]))
                i += 1
            add_table(doc, headers, rows)
            continue

        if stripped.startswith('>'):
            add_quote(doc, stripped.lstrip('> ').strip())
            i += 1
            continue

        bm = re.match(r'^(\s*)[-*]\s+(.*)$', line)
        if bm:
            indent = len(bm.group(1)) // 2
            add_bullet(doc, bm.group(2).strip(), indent)
            i += 1
            continue

        nm = re.match(r'^(\s*)\d+\.\s+(.*)$', line)
        if nm:
            add_bullet(doc, nm.group(2).strip(), len(nm.group(1)) // 2)
            i += 1
            continue

        add_para(doc, stripped)
        i += 1

    if in_code and code_lines:
        add_code_block(doc, '\n'.join(code_lines))

    doc.save(OUT_FILE)
    print(f"已生成: {OUT_FILE}")


if __name__ == '__main__':
    build()
