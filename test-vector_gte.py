#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import hnswlib
from sentence_transformers import SentenceTransformer

# ======= 設定 =======
DB_PATH = "output/chunks.sqlite"
INDEX_PATH = "output/hnsw_index.bin"
MODEL_NAME = "Alibaba-NLP/gte-multilingual-base"
K = 5  # 近傍数
# ====================

print(f"モデルロード中 ({MODEL_NAME})...")
# GTEモデルは trust_remote_code=True が必要
model = SentenceTransformer(MODEL_NAME, trust_remote_code=True)

print("HNSWインデックス読み込み中...")
index = hnswlib.Index(space="cosine", dim=768)
index.load_index(INDEX_PATH)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ======== 検索クエリ ========
query = input("検索したい内容を入力してください: ").strip()
print(f"\n[検索クエリ] {query}")

# ======== ベクトル化 + 近傍検索 ========
qvec = model.encode([query])
labels, distances = index.knn_query(qvec, k=K)

print("\n=== 近傍チャンク ===")
for i, (lbl, dist) in enumerate(zip(labels[0], distances[0])):
    chunk_id = int(lbl)
    cur.execute("SELECT content FROM chunks WHERE id=?", (chunk_id,))
    row = cur.fetchone()
    text = row[0].strip().replace("\n", " ") if row and row[0] else "(空)"
    print(f"\n{i+1}. id={chunk_id}  距離={dist:.4f}")
    print("本文抜粋:", text[:100], "...")

    # 前後1件を参考として表示
    for adj in [chunk_id - 1, chunk_id + 1]:
        cur.execute("SELECT content FROM chunks WHERE id=?", (adj,))
        adj_row = cur.fetchone()
        if adj_row and adj_row[0]:
            adj_text = adj_row[0].strip().replace("\n", " ")
            print(f"  ├─ 参考(id={adj}): {adj_text[:100]} ...")

conn.close()
