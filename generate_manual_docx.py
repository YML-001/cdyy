#!/usr/bin/env python3
"""
将操作手册 MD 转换为 Word 格式（公文字体 + 自动目录）
- 标题：方正小标宋简体 20pt
- 正文：仿宋_GB2312 三号(16pt)
- 西文：Times New Roman
- 行距：1.5 倍
- 目录：自动生成，打开文档后右键目录可更新
"""
import os
import re
from docx import Document
from docx.shared import Pt, Cm, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MD_FILE = os.path.join(BASE_DIR, "操作手册.md")
OUT_FILE = os.path.join(BASE_DIR, "操作手册.docx")
IMG_DIR = os.path.join(BASE_DIR, "manual-screenshots")

def set_run_font(run, cn_font, en_font, size):
    run.font.size = Pt(size)
    run.font.name = en_font
    r = run._element
    rPr = r.find(qn('w:rPr'))
    if rPr is None:
        rPr = OxmlElement('w:rPr')
        r.insert(0, rPr)
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), en_font)
    rFonts.set(qn('w:hAnsi'), en_font)
    rFonts.set(qn('w:eastAsia'), cn_font)
    rFonts.set(qn('w:cs'), en_font)

def set_paragraph_spacing(paragraph, line_spacing=1.5):
    pPr = paragraph._element.find(qn('w:pPr'))
    if pPr is None:
        pPr = OxmlElement('w:pPr')
        paragraph._element.insert(0, pPr)
    spacing = pPr.find(qn('w:spacing'))
    if spacing is None:
        spacing = OxmlElement('w:spacing')
        pPr.append(spacing)
    spacing.set(qn('w:line'), str(int(240 * line_spacing)))
    spacing.set(qn('w:lineRule'), 'auto')
    spacing.set(qn('w:before'), '120')
    spacing.set(qn('w:after'), '120')

def add_toc(doc):
    """插入目录域代码，打开 Word 后按 Ctrl+A, F9 或右键目录更新即可"""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('目  录')
    run.bold = True
    set_run_font(run, '方正小标宋简体', 'Times New Roman', 20)
    set_paragraph_spacing(p, 1.5)

    paragraph = doc.add_paragraph()
    run = paragraph.add_run()
    fldChar1 = OxmlElement('w:fldChar')
    fldChar1.set(qn('w:fldCharType'), 'begin')
    run._element.append(fldChar1)

    run2 = paragraph.add_run()
    instrText = OxmlElement('w:instrText')
    instrText.set(qn('xml:space'), 'preserve')
    instrText.text = ' TOC \\o "1-3" \\h \\z \\u '
    run2._element.append(instrText)

    run3 = paragraph.add_run()
    fldChar2 = OxmlElement('w:fldChar')
    fldChar2.set(qn('w:fldCharType'), 'separate')
    run3._element.append(fldChar2)

    run4 = paragraph.add_run('（请右键此处选择"更新域"以生成目录）')
    set_run_font(run4, '仿宋_GB2312', 'Times New Roman', 12)
    run4.font.color.rgb = RGBColor(0x99, 0x99, 0x99)

    run5 = paragraph.add_run()
    fldChar3 = OxmlElement('w:fldChar')
    fldChar3.set(qn('w:fldCharType'), 'end')
    run5._element.append(fldChar3)

    doc.add_page_break()

def add_heading(doc, text, level):
    """使用 Word 原生 Heading 样式并自定义字体"""
    if level == 0:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.bold = True
        set_run_font(run, '方正小标宋简体', 'Times New Roman', 22)
        set_paragraph_spacing(p, 1.5)
        return p

    style_map = {1: 'Heading 1', 2: 'Heading 2', 3: 'Heading 3', 4: 'Heading 4'}
    style_name = style_map.get(level, 'Heading 4')
    p = doc.add_paragraph(style=style_name)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs:
        run.text = ''
    run = p.add_run(text)
    run.bold = True

    if level == 1:
        set_run_font(run, '方正小标宋简体', 'Times New Roman', 20)
    elif level == 2:
        set_run_font(run, '黑体', 'Times New Roman', 16)
    elif level == 3:
        set_run_font(run, '楷体_GB2312', 'Times New Roman', 16)
    else:
        set_run_font(run, '仿宋_GB2312', 'Times New Roman', 16)
    set_paragraph_spacing(p, 1.5)
    return p

def add_body_text(doc, text):
    p = doc.add_paragraph()
    run = p.add_run(text)
    set_run_font(run, '仿宋_GB2312', 'Times New Roman', 16)
    set_paragraph_spacing(p, 1.5)
    return p

def add_image(doc, img_path):
    if os.path.exists(img_path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        try:
            run.add_picture(img_path, width=Inches(5.5))
        except Exception:
            try:
                run.add_picture(img_path, width=Inches(4.0))
            except Exception:
                pass
        set_paragraph_spacing(p, 1.0)
        return True
    return False

def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ''
        p = cell.paragraphs[0]
        run = p.add_run(h)
        run.bold = True
        set_run_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ''
            p = cell.paragraphs[0]
            run = p.add_run(val)
            set_run_font(run, '仿宋_GB2312', 'Times New Roman', 14)
    doc.add_paragraph()

def parse_md_and_build_docx():
    with open(MD_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    doc = Document()
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(3.17)
        section.right_margin = Cm(3.17)

    title_added = False
    i = 0
    in_table = False
    table_headers = []
    table_rows = []

    while i < len(lines):
        line = lines[i].rstrip('\n')

        if line.strip() == '---':
            i += 1
            continue

        if line.startswith('# ') and not title_added:
            add_heading(doc, line[2:].strip(), 0)
            title_added = True
            doc.add_page_break()
            add_toc(doc)
            i += 1
            continue

        if line.startswith('## '):
            if in_table:
                add_table(doc, table_headers, table_rows)
                in_table = False
            add_heading(doc, line[3:].strip(), 1)
            i += 1
            continue

        if line.startswith('### '):
            if in_table:
                add_table(doc, table_headers, table_rows)
                in_table = False
            add_heading(doc, line[4:].strip(), 2)
            i += 1
            continue

        if line.startswith('#### '):
            if in_table:
                add_table(doc, table_headers, table_rows)
                in_table = False
            add_heading(doc, line[5:].strip(), 3)
            i += 1
            continue

        img_match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
        if img_match:
            if in_table:
                add_table(doc, table_headers, table_rows)
                in_table = False
            caption = img_match.group(1)
            img_path = os.path.join(BASE_DIR, img_match.group(2))
            if caption:
                p = doc.add_paragraph()
                run = p.add_run(f'图：{caption}')
                set_run_font(run, '仿宋_GB2312', 'Times New Roman', 12)
                run.font.color.rgb = RGBColor(0x64, 0x74, 0x8b)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_image(doc, img_path)
            i += 1
            continue

        if '|' in line and line.strip().startswith('|'):
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if not in_table:
                if all(re.match(r'^[-:]+$', c) for c in cells):
                    i += 1
                    continue
                in_table = True
                table_headers = cells
                table_rows = []
            else:
                if all(re.match(r'^[-:]+$', c) for c in cells):
                    i += 1
                    continue
                table_rows.append(cells)
            i += 1
            continue

        if in_table and not ('|' in line and line.strip().startswith('|')):
            add_table(doc, table_headers, table_rows)
            in_table = False

        if line.strip().startswith('- **') or line.strip().startswith('- '):
            text = line.strip().lstrip('- ')
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            p = doc.add_paragraph()
            run = p.add_run(f'● {text}')
            set_run_font(run, '仿宋_GB2312', 'Times New Roman', 16)
            set_paragraph_spacing(p, 1.5)
            p.paragraph_format.left_indent = Cm(0.74)
            i += 1
            continue

        if line.strip() == '':
            i += 1
            continue

        text = line.strip()
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^*]+)\*', r'\1', text)
        if text:
            add_body_text(doc, text)
        i += 1

    if in_table:
        add_table(doc, table_headers, table_rows)

    doc.save(OUT_FILE)
    print(f"Word 文档已生成: {OUT_FILE}")

if __name__ == '__main__':
    parse_md_and_build_docx()
