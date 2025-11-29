#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_vector_db_gte.py
Raspberry Pi 5 向け RAG環境構築：ベクトルDB構築スクリプト（gte-multilingual-base対応）
"""

import os
import sqlite3
import numpy as np
import hnswlib
from sentence_transformers import SentenceTransformer

# ===============================================================
# 1. モデルロード
# ===============================================================
model_name = "Alibaba-NLP/gte-multilingual-base"
print(f"モデルロード中 ({model_name})...")

# trust_remote_code=True を追加
model = SentenceTransformer(model_name, trust_remote_code=True)

# 埋め込み次元を自動検出
sample_vec = model.encode(["次元確認テスト"])
dim = sample_vec.shape[1]
print(f"埋め込みベクトル次元: {dim}")

# ===============================================================
# 2. チャンクデータの読み込み
# ===============================================================
db_path = "output/chunks.sqlite"
if not os.path.exists(db_path):
    raise FileNotFoundError(f"SQLite DBが見つかりません: {db_path}")

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT id, content FROM chunks ORDER BY id")
rows = cur.fetchall()
conn.close()

total_chunks = len(rows)
print(f"チャンク総数: {total_chunks}")

# ===============================================================
# 3. ベクトル生成とHNSW登録
# ===============================================================
texts = []
ids = []
skipped = []

for i, (chunk_id, content) in enumerate(rows, start=1):
    text = (content or "").strip()
    if not text:
        skipped.append(chunk_id)
        continue
    texts.append(text)
    ids.append(chunk_id)

if not texts:
    raise RuntimeError("有効なチャンクデータがありません。")

print("ベクトル生成と登録中...")

embeddings = model.encode(
    texts,
    show_progress_bar=True,
    batch_size=16,
    normalize_embeddings=True
)

# ===============================================================
# 4. HNSWインデックス作成
# ===============================================================
num_elements = len(embeddings)
index = hnswlib.Index(space="cosine", dim=dim)
index.init_index(max_elements=num_elements, ef_construction=200, M=64)
index.add_items(embeddings, ids)
index.save_index("output/hnsw_index.bin")

# ===============================================================
# 5. 結果出力
# ===============================================================
print("===================================")
print("✅ HNSWインデックス作成完了")
print(f"出力ファイル: output/hnsw_index.bin")
print(f"登録ベクトル数: {num_elements} 件（id整合済）")
print(f"スキップされたチャンク: {len(skipped)} 件")
if skipped:
    print("例:", skipped[:10])
print("===================================")
