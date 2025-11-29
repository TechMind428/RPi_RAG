#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
chunk_markdown_rag_optimized.py – RAG最適化版 Markdown分割スクリプト
-------------------------------------------------------------------
目的:
- Markdown文書を意味単位（見出し＋文ブロック）でチャンク化
- 日本語文区切りと半角統一を適用
- 正規化済みテキストをSQLiteに保存し、再現性を確保
"""

import os
import re
import sqlite3
import pathlib
import unicodedata

# ===== 設定 =====
BASE_DIR = pathlib.Path.home() / "pi5-rag"
SRC_DIR  = BASE_DIR / "processed"
DB_PATH  = BASE_DIR / "output/chunks.sqlite"
CHUNK_SIZE = 600  # 1チャンクの最大文字数（目安）

os.makedirs(BASE_DIR / "output", exist_ok=True)


# ===== 前処理関数 =====
def normalize_text(text: str) -> str:
    """半角統一 + 小文字化 + 不要記号除去"""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def clean_text(text: str) -> str:
    """Markdownノイズ除去"""
    text = re.sub(r"`+", "", text)
    text = re.sub(r"\!$begin:math:display$.*?$end:math:display$$begin:math:text$.*?$end:math:text$", "", text)  # 画像タグ
    text = re.sub(r"$begin:math:display$([^$end:math:display$]+)\]$begin:math:text$.*?$end:math:text$", r"\1", text)  # リンク文字のみ残す
    text = re.sub(r"<[^>]+>", " ", text)  # HTMLタグ除去
    text = re.sub(r"\n{2,}", "\n", text)
    return text.strip()


def sentence_split_ja(text: str):
    """日本語句点ベースの文区切り"""
    return [s.strip() for s in re.split(r'(?<=[。．！？])\s*', text) if s.strip()]


def chunk_by_sentence(text: str, size=CHUNK_SIZE):
    """文単位でチャンク化（指定文字数を超えないように）"""
    sentences = sentence_split_ja(text)
    chunks, current = [], ""
    for s in sentences:
        if len(current) + len(s) > size:
            chunks.append(current.strip())
            current = s
        else:
            current += " " + s
    if current.strip():
        chunks.append(current.strip())

    # 短すぎるチャンクを次と結合
    merged = []
    buf = ""
    for c in chunks:
        if len(buf) + len(c) < 200:
            buf += " " + c
        else:
            if buf.strip():
                merged.append(buf.strip())
            buf = c
    if buf.strip():
        merged.append(buf.strip())
    return merged


# ===== SQLite初期化 =====
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    section_title TEXT,
    chunk_index INTEGER,
    content TEXT,
    normalized TEXT
)
""")
conn.commit()


# ===== 主処理 =====
for md_file in SRC_DIR.glob("*.md"):
    text = clean_text(md_file.read_text(encoding="utf-8", errors="ignore"))
    text = normalize_text(text)

    # 既存データ削除（重複防止）
    cur.execute("DELETE FROM chunks WHERE source_file=?", (md_file.name,))

    # ## 見出し単位で分割
    sections = re.split(r"(?m)^##\s+", text)
    for sec in sections[1:]:
        try:
            title, body = sec.split("\n", 1)
        except ValueError:
            continue
        title = title.strip()
        chunks = chunk_by_sentence(body)
        print(f"{md_file.name} [{title}]: {len(chunks)} チャンク")

        for i, c in enumerate(chunks):
            cur.execute("""
                INSERT INTO chunks (source_file, section_title, chunk_index, content, normalized)
                VALUES (?, ?, ?, ?, ?)
            """, (md_file.name, title, i, c, normalize_text(c)))

conn.commit()
conn.close()
print(f"\n✅ チャンクデータを保存しました: {DB_PATH}")
