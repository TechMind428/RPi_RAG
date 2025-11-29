#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch.py – RAGデータ収集用自動ダウンローダ（2025-10 安定版）
------------------------------------------------------------
・seed.yaml に記載された URL（HTML/PDF）を一括取得
・403 Forbidden 対策 (User-Agent偽装)
・接続安定化 (timeout=60)
・URLパスを利用したファイル名生成（重複防止）
・拡張子補完 (.html 自動付与)
・日付付きログ保存 (files_YYYYMMDD.csv)
"""

import os
import hashlib
import time
import requests
import yaml
import pathlib
from urllib.parse import urlparse

# === パス設定 ============================================================
BASE_DIR = pathlib.Path.home() / "pi5-rag"
RAW_HTML = BASE_DIR / "raw/html"
RAW_PDF  = BASE_DIR / "raw/pdf"
MANIFEST = BASE_DIR / "manifests/seed.yaml"

timestamp = time.strftime("%Y%m%d")
LOG_FILE = BASE_DIR / "manifests" / f"files_{timestamp}.csv"

RAW_HTML.mkdir(parents=True, exist_ok=True)
RAW_PDF.mkdir(parents=True, exist_ok=True)

# === User-Agent設定（403対策） ==========================================
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0 Safari/537.36"
    )
}

# === 取得対象読み込み ===================================================
try:
    with open(MANIFEST, "r", encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    sources = manifest.get("sources", [])
except Exception as e:
    print(f"seed.yaml の読み込みに失敗しました: {e}")
    exit(1)

rows = []

# === 各URLの取得 =========================================================
for s in sources:
    url  = s.get("url")
    fmt  = s.get("format", "html").lower()
    lang = s.get("lang", "-")
    kind = s.get("kind", "-")

    if not url:
        continue

    parsed = urlparse(url)
    path = parsed.path.strip("/")

    # --- 改良版ファイル名生成ロジック ---
    if not path:
        fn = parsed.netloc.replace(".", "_") + ".html"
    else:
        # パスを安全にファイル名へ変換
        fn = (parsed.netloc + "_" + path.replace("/", "_")).replace(".", "_")
        # 拡張子補完
        if not fn.endswith(".html") and not fn.endswith(".htm") and fmt == "html":
            fn += ".html"
        elif fmt == "pdf" and not fn.endswith(".pdf"):
            fn += ".pdf"
    # ----------------------------------

    out = RAW_PDF / fn if fmt == "pdf" else RAW_HTML / fn

    print(f"Fetching: {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        r.raise_for_status()
        out.write_bytes(r.content)

        sha = hashlib.sha256(r.content).hexdigest()
        rows.append([str(out), len(r.content), sha, time.strftime("%Y-%m-%dT%H:%M:%S"), "OK"])

    except requests.exceptions.HTTPError as e:
        print(f"HTTPエラー: {e}")
        rows.append([url, 0, "-", time.strftime("%Y-%m-%dT%H:%M:%S"), f"HTTPError {e}"])

    except requests.exceptions.Timeout:
        print(f"Timeout: {url}")
        rows.append([url, 0, "-", time.strftime("%Y-%m-%dT%H:%M:%S"), "Timeout"])

    except Exception as e:
        print(f"Error fetching {url}: {e}")
        rows.append([url, 0, "-", time.strftime("%Y-%m-%dT%H:%M:%S"), f"Error {e}"])

# === ログ保存 ============================================================
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("path_or_url,size,sha256,timestamp,status\n")
    for p, sz, sha, t, st in rows:
        f.write(f"{p},{sz},{sha},{t},{st}\n")

print(f"\n完了: {len(rows)} 件のファイルを処理しました。")
print(f"ログファイル: {LOG_FILE}")
