"""
PDF 生成服務
使用 reportlab 將 Notion Blocks 轉換為 PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT
from io import BytesIO
from typing import List, Dict, Any
import os
import emoji


def register_fonts():
    """註冊中文字體和 Emoji 字體"""
    # 1. 註冊中文字體
    chinese_font = 'Helvetica'
    font_paths = [
        # Windows System Fonts
        "C:\\Windows\\Fonts\\msjh.ttc",  # Microsoft JhengHei
        "C:\\Windows\\Fonts\\msjh.ttf",
        "C:\\Windows\\Fonts\\mingliu.ttc", # MingLiU
        "C:\\Windows\\Fonts\\simhei.ttf",   # SimHei
        # macOS System Fonts
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path, subfontIndex=0))
                chinese_font = 'ChineseFont'
                break
            except:
                continue

    # 2. 註冊 Emoji/Symbol 字體 (用於顯示符號)
    # 使用 Segoe UI Emoji (Windows 10/11 預設 Emoji 字體)
    emoji_font_path = "C:\\Windows\\Fonts\\seguiemj.ttf"
    if not os.path.exists(emoji_font_path):
        # 回退到 Segoe UI Symbol
        emoji_font_path = "C:\\Windows\\Fonts\\seguisym.ttf"

    if os.path.exists(emoji_font_path):
        try:
            pdfmetrics.registerFont(TTFont('EmojiFont', emoji_font_path))
        except:
            pass

    return chinese_font


    return chinese_font


def wrap_emojis(text: str) -> str:
    """
    使用 emoji 套件將 Emoji 轉換為 <font name="EmojiFont"> 包裹
    """
    if not text:
        return text
        
    def replace_func(chars, data_dict):
        return f'<font face="EmojiFont">{chars}</font>'
        
    return emoji.replace_emoji(text, replace=replace_func)


def get_styles(font_name: str):
    """取得帶有中文字體的樣式"""
    styles = getSampleStyleSheet()
    
    # 標題樣式
    styles.add(ParagraphStyle(
        name='ChineseTitle',
        fontName=font_name,
        fontSize=18,
        leading=24,
        spaceAfter=12,
    ))
    
    # H2 樣式
    styles.add(ParagraphStyle(
        name='ChineseH2',
        fontName=font_name,
        fontSize=14,
        leading=20,
        spaceBefore=12,
        spaceAfter=6,
    ))
    
    # H3 樣式
    styles.add(ParagraphStyle(
        name='ChineseH3',
        fontName=font_name,
        fontSize=12,
        leading=18,
        spaceBefore=8,
        spaceAfter=4,
    ))
    
    # 正文樣式
    styles.add(ParagraphStyle(
        name='ChineseBody',
        fontName=font_name,
        fontSize=10,
        leading=16,
        spaceAfter=6,
    ))
    
    # 引用樣式
    styles.add(ParagraphStyle(
        name='ChineseQuote',
        fontName=font_name,
        fontSize=10,
        leading=16,
        leftIndent=20,
        spaceAfter=6,
        textColor='#555555',
    ))
    
    # 列表項樣式
    styles.add(ParagraphStyle(
        name='ChineseListItem',
        fontName=font_name,
        fontSize=10,
        leading=16,
        leftIndent=20,
        spaceAfter=4,
    ))
    
    return styles


def notion_blocks_to_elements(blocks: List[Dict[str, Any]], styles) -> list:
    """將 Notion Blocks 轉換為 reportlab 元素"""
    elements = []
    
    def process_rich_text(rich_text: List[Dict]) -> str:
        result = ''
        for t in rich_text:
            content = t.get('text', {}).get('content', '')
            # 轉義 HTML 特殊字符
            content = content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            # 包裹 Emoji
            content = wrap_emojis(content)

            annotations = t.get('annotations', {})
            if annotations.get('bold'):
                content = f'<b>{content}</b>'
            if annotations.get('italic'):
                content = f'<i>{content}</i>'
            result += content
        return result
    
    for block in blocks:
        block_type = block.get('type', '')
        
        if block_type == 'callout':
            callout = block.get('callout', {})
            icon = callout.get('icon', {}).get('emoji', '💡')
            icon_html = wrap_emojis(icon) # 處理 icon
            text = process_rich_text(callout.get('rich_text', []))
            elements.append(Paragraph(f'{icon_html} {text}', styles['ChineseQuote']))
            
        elif block_type == 'heading_2':
            text = process_rich_text(block.get('heading_2', {}).get('rich_text', []))
            elements.append(Paragraph(text, styles['ChineseH2']))
            
        elif block_type == 'heading_3':
            text = process_rich_text(block.get('heading_3', {}).get('rich_text', []))
            elements.append(Paragraph(text, styles['ChineseH3']))
            
        elif block_type == 'bulleted_list_item':
            text = process_rich_text(block.get('bulleted_list_item', {}).get('rich_text', []))
            elements.append(Paragraph(f'• {text}', styles['ChineseListItem']))
            
        elif block_type == 'code':
            code_block = block.get('code', {})
            text = process_rich_text(code_block.get('rich_text', []))
            # Code block 通常不處理 emoji or html, 用 Preformatted
            # 但如果包含 unicode emoji, ReportLab 預設字體會掛掉。
            # 這裡簡化處理，不 wrap code block 的 emoji（因為 Preformatted 不支援多字體混合）
            elements.append(Preformatted(text, styles['ChineseBody']))
            elements.append(Spacer(1, 6))
            
        elif block_type == 'quote':
            text = process_rich_text(block.get('quote', {}).get('rich_text', []))
            elements.append(Paragraph(f'❝ {text}', styles['ChineseQuote']))
            
        elif block_type == 'toggle':
            toggle = block.get('toggle', {})
            text = process_rich_text(toggle.get('rich_text', []))
            elements.append(Paragraph(f'<b>▸ {text}</b>', styles['ChineseBody']))
            # 處理 toggle 內的子元素
            children = toggle.get('children', [])
            if children:
                child_elements = notion_blocks_to_elements(children, styles)
                elements.extend(child_elements)
    
    return elements


def generate_pdf(title: str, blocks: List[Dict[str, Any]]) -> bytes:
    """
    生成 PDF 檔案
    """
    # 註冊字體
    font_name = register_fonts()
    styles = get_styles(font_name)
    
    # 建立 PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm,
        rightMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # 建立元素列表
    elements = []
    
    # 標題
    # 標題也可能包含 emoji
    elements.append(Paragraph(wrap_emojis(title), styles['ChineseTitle']))
    elements.append(Spacer(1, 12))
    
    # 轉換 Notion Blocks
    content_elements = notion_blocks_to_elements(blocks, styles)
    elements.extend(content_elements)
    
    # 建立 PDF
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.getvalue()
