#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_cli_gte_simple.py - シンプルRAG CLI (簡潔出力＋非ストリーム版)
---------------------------------------------------------------------------
特徴:
- Ollamaモデル存在を完全一致で検証（未pullなら明示エラー）
- SentenceTransformer静音ロード（stdout/stderr抑止）
- LLM応答は非ストリーム（全応答一括表示）
- RAGあり／なしを明確に分けて出力（比較結果の重複表示なし）
- --compare, --save_report, --debug 対応
"""

import argparse
import sqlite3
import hnswlib
import numpy as np
import requests
import time
import warnings
import sys
import os
import subprocess
import contextlib
from datetime import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer
from transformers import logging as hf_logging


# ====== 引数定義 ======
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--model", default="Alibaba-NLP/gte-multilingual-base")
    p.add_argument("--ollama_model", default="granite3.3:2b")
    p.add_argument("--db", default="output/chunks.sqlite")
    p.add_argument("--index", default="output/hnsw_index.bin")
    p.add_argument("--limit", type=int, default=5)
    p.add_argument("--temperature", type=float, default=0.7)
    p.add_argument("--top_p", type=float, default=0.8)
    p.add_argument("--num_ctx", type=int, default=None, help="Ollamaのコンテキストウィンドウサイズ（未指定時はモデルのデフォルト値を使用）")
    p.add_argument("--num_predict", type=int, default=256, help="生成する最大トークン数")
    p.add_argument("--endpoint", default="http://localhost:11434")
    p.add_argument("--max_context_chars", type=int, default=3000)
    p.add_argument("--compare", action="store_true", help="RAGなしの回答も比較表示")
    p.add_argument("--save_report", action="store_true", help="結果をMarkdownレポートとして保存")
    p.add_argument("--debug", action="store_true", help="各ステップの処理時間を表示")
    return p.parse_args()


# ====== Ollamaモデル存在チェック（完全一致） ======
def check_ollama_model_exists(model_name):
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()
        found = False
        for line in lines[1:]:  # 1行目はヘッダー
            cols = line.split()
            if len(cols) > 0 and cols[0].strip().lower() == model_name.strip().lower():
                found = True
                break
        if not found:
            print(f"\n指定されたモデル '{model_name}' は Ollama に存在しません。")
            print("次のコマンドでモデルを取得してください：")
            print(f"  $ ollama pull {model_name}\n")
            sys.exit(1)
    except FileNotFoundError:
        print("\nエラー: Ollama がインストールされていません。")
        print("https://ollama.ai/download からインストールしてください。\n")
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("\nエラー: Ollamaのモデルリストを取得できませんでした。")
        print("Ollamaサービスが起動しているか確認してください。\n")
        sys.exit(1)


# ====== Ollama呼び出し（非ストリーム固定） ======
def query_ollama(prompt, model, endpoint, temperature=0.7, top_p=0.8, num_ctx=None, num_predict=256):
    url = f"{endpoint}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,  # 一括応答モード
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": num_predict
        }
    }
    # num_ctxが指定されている場合のみoptionsに追加
    if num_ctx is not None:
        payload["options"]["num_ctx"] = num_ctx
    try:
        r = requests.post(url, json=payload, timeout=600)
    except requests.exceptions.ConnectionError:
        print("\nエラー: Ollamaサーバーに接続できません。`ollama serve` が動作中か確認してください。\n")
        return ""
    if not r.ok:
        print(f"\nOllama APIエラー: {r.status_code} - {r.text}\n")
        return ""
    data = r.json()
    return data.get("response", "").strip()


# ====== RAG検索 ======
def retrieve_chunks(query_vec, index, db, limit=5, max_context_chars=3000):
    ids, _ = index.knn_query(query_vec, k=limit)
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    results, total_len = [], 0
    for i in ids[0]:
        cur.execute("SELECT content FROM chunks WHERE id=?", (int(i),))
        row = cur.fetchone()
        if not row:
            continue
        text = row[0]
        if total_len + len(text) > max_context_chars:
            break
        results.append(text)
        total_len += len(text)
    conn.close()
    return "\n".join(results)


# ====== レポート出力 ======
def save_report_md(query, response_rag, response_norag, times, args):
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = report_dir / f"rag_report_{ts}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# RAG CLI 実行レポート\n\n")
        f.write(f"**日時:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Ollamaモデル:** {args.ollama_model}\n\n")
        f.write(f"**ベクトルモデル:** {args.model}\n\n")
        f.write(f"**質問:** {query}\n\n")
        f.write(f"---\n\n")
        f.write(f"## RAGあり応答\n\n{response_rag.strip()}\n\n")
        if args.compare:
            f.write(f"## RAGなし応答\n\n{response_norag.strip()}\n\n")
        f.write(f"---\n\n")
        f.write("## 処理時間\n\n")
        for k, v in times.items():
            f.write(f"- {k}: {v:.3f} 秒\n")
    print(f"\nレポートを保存しました: {filename}\n")


# ====== メイン処理 ======
def main():
    args = parse_args()

    # Ollamaモデル存在確認
    check_ollama_model_exists(args.ollama_model)
    
    # num_ctxの情報表示
    if args.num_ctx is None:
        print(f"ℹ️  モデル '{args.ollama_model}' のデフォルトコンテキストウィンドウサイズを使用")
    else:
        print(f"ℹ️  コンテキストウィンドウサイズ: {args.num_ctx}")

    # 全ログ・警告を抑止
    warnings.filterwarnings("ignore")
    hf_logging.set_verbosity_error()

    # SentenceTransformer静音ロード
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
        model = SentenceTransformer(args.model, trust_remote_code=True)

    index = hnswlib.Index(space='cosine', dim=model.get_sentence_embedding_dimension())
    index.load_index(args.index)

    print("質問を入力してください。")
    print("(終了するには Ctrl+C)\n")

    while True:
        try:
            query = input("> ").strip()
            if not query:
                continue

            times = {}
            t_start = time.perf_counter()

            # 1. ベクトル化
            t_a = time.perf_counter()
            q_emb = model.encode([query], normalize_embeddings=True)
            t_b = time.perf_counter()
            times["ベクトル化"] = t_b - t_a

            # 2. RAG検索
            t_a = time.perf_counter()
            context = retrieve_chunks(q_emb, index, args.db, args.limit, args.max_context_chars)
            t_b = time.perf_counter()
            times["RAG検索"] = t_b - t_a

            # 3. RAGあり応答（非ストリーム）
            t_a = time.perf_counter()
            prompt_rag = f"以下の情報を参考に質問に答えてください。\n\n{context}\n\n質問: {query}\n\n回答:"
            print("\n[RAGあり応答]")
            response_rag = query_ollama(prompt_rag, args.ollama_model, args.endpoint,
                                        args.temperature, args.top_p, args.num_ctx, args.num_predict)
            print(response_rag)
            t_b = time.perf_counter()
            times["RAG付きLLM呼び出し"] = t_b - t_a

            # 4. RAGなし比較（--compare）
            response_norag = ""
            if args.compare:
                t_a = time.perf_counter()
                print("\n[RAGなし応答]")
                prompt_norag = f"質問: {query}\n\n回答:"
                response_norag = query_ollama(prompt_norag, args.ollama_model, args.endpoint,
                                              args.temperature, args.top_p, args.num_ctx, args.num_predict)
                print(response_norag)
                t_b = time.perf_counter()
                times["RAGなしLLM呼び出し"] = t_b - t_a

            # 5. レポート保存
            if args.save_report:
                save_report_md(query, response_rag, response_norag, times, args)

            # 6. 計測表示
            t_end = time.perf_counter()
            times["合計"] = t_end - t_start
            if args.debug:
                print("\n[DEBUG: 処理時間]")
                for k, v in times.items():
                    print(f"{k}: {v:.3f} 秒")

        except KeyboardInterrupt:
            print("\n終了します。")
            break


if __name__ == "__main__":
    main()
