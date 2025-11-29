#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
convert_to_md.py  –  HTML/PDF を Markdown に変換するスクリプト
------------------------------------------------------------
・raw/html と raw/pdf の中身を処理して processed/*.md に保存
・HTML → trafilatura で本文抽出
・PDF → pdfminer.six でテキスト化
・UTF-8 エンコーディングで保存
"""

import os
import pathlib
import trafilatura
from pdfminer.high_level import extract_text

# ディレクトリ設定
BASE_DIR = pathlib.Path.home() / "pi5-rag"
HTML_DIR = BASE_DIR / "raw/html"
PDF_DIR  = BASE_DIR / "raw/pdf"
OUT_DIR  = BASE_DIR / "processed"

OUT_DIR.mkdir(parents=True, exist_ok=True)

def html_to_md(html_path, out_path):
    """HTMLをMarkdown化（本文抽出）"""
    try:
        html_data = html_path.read_text(encoding="utf-8", errors="ignore")
        extracted = trafilatura.extract(html_data, output_format="markdown")
        if not extracted:
            extracted = trafilatura.extract(html_data) or ""
        out_path.write_text(extracted, encoding="utf-8")
        print(f"HTML → MD 変換完了: {html_path.name}")
    except Exception as e:
        print(f"HTML変換エラー: {html_path.name} ({e})")

def pdf_to_md(pdf_path, out_path):
    """PDFをMarkdown化（単純テキスト変換）"""
    try:
        text = extract_text(str(pdf_path))
        out_path.write_text(text, encoding="utf-8")
        print(f"PDF → MD 変換完了: {pdf_path.name}")
    except Exception as e:
        print(f"PDF変換エラー: {pdf_path.name} ({e})")

# HTML処理
for html_file in HTML_DIR.glob("*.html"):
    out_file = OUT_DIR / (html_file.stem + ".md")
    html_to_md(html_file, out_file)

# PDF処理
for pdf_file in PDF_DIR.glob("*.pdf"):
    out_file = OUT_DIR / (pdf_file.stem + ".md")
    pdf_to_md(pdf_file, out_file)

print("\n全ファイルの変換処理が完了しました。")
print(f"出力先: {OUT_DIR}")
