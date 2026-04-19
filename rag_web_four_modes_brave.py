#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_web_four_modes.py - RAG + Web検索 4つのモード検証システム
---------------------------------------------------------------------------
4つのモード:
1. 選択モード (Selection): ユーザーが検索方式を選択
2. フォールバックモード (Fallback): RAG結果を評価し、必要に応じてWeb検索
3. ハイブリッドモード (Hybrid): RAGとWeb検索を並行実行して統合
4. 比較モード (Comparison): 3つの方式すべてを実行して比較
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
import concurrent.futures
from datetime import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer
from transformers import logging as hf_logging

# .envファイルから環境変数を読み込む（python-dotenv不要）
def load_env_file(env_path='.env'):
    """
    .envファイルを読み込んで環境変数に設定
    python-dotenvがなくても動作する
    """
    if not os.path.exists(env_path):
        return
    
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # コメント行と空行をスキップ
                if not line or line.startswith('#'):
                    continue
                # KEY=VALUE形式を解析
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 引用符を削除
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value
    except Exception as e:
        print(f"警告: .envファイルの読み込みに失敗しました: {e}")

# .envファイルを読み込む
load_env_file()


# ====== タイミング計測クラス ======
class TimingLogger:
    """詳細なタイミング計測とログ出力"""
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.timings = []
        self.start_time = None
        self.current_section = None
    
    def start(self, section_name):
        """セクションの開始"""
        if not self.enabled:
            return
        self.current_section = section_name
        self.start_time = time.perf_counter()
        print(f"[TIMING] {section_name} 開始...")
    
    def end(self, details=""):
        """セクションの終了"""
        if not self.enabled or self.start_time is None:
            return
        elapsed = time.perf_counter() - self.start_time
        self.timings.append({
            "section": self.current_section,
            "elapsed": elapsed,
            "details": details
        })
        print(f"[TIMING] {self.current_section} 完了: {elapsed:.3f}秒 {details}")
        self.start_time = None
        return elapsed
    
    def get_summary(self):
        """タイミングサマリーを取得"""
        if not self.timings:
            return "タイミング情報なし"
        
        total = sum(t["elapsed"] for t in self.timings)
        summary = [f"\n{'='*60}"]
        summary.append("タイミングサマリー")
        summary.append(f"{'='*60}")
        
        for t in self.timings:
            percentage = (t["elapsed"] / total * 100) if total > 0 else 0
            details = f" ({t['details']})" if t['details'] else ""
            summary.append(f"{t['section']:<30} {t['elapsed']:>8.3f}秒 ({percentage:>5.1f}%){details}")
        
        summary.append(f"{'-'*60}")
        summary.append(f"{'合計':<30} {total:>8.3f}秒 (100.0%)")
        summary.append(f"{'='*60}\n")
        
        return "\n".join(summary)
    
    def get_report_section(self):
        """レポート用のセクションを生成"""
        if not self.timings:
            return ""
        
        total = sum(t["elapsed"] for t in self.timings)
        lines = ["\n#### タイミング詳細\n"]
        
        for t in self.timings:
            percentage = (t["elapsed"] / total * 100) if total > 0 else 0
            details = f" - {t['details']}" if t['details'] else ""
            lines.append(f"- **{t['section']}**: {t['elapsed']:.3f}秒 ({percentage:.1f}%){details}")
        
        lines.append(f"\n**合計処理時間**: {total:.3f}秒\n")
        
        return "\n".join(lines)


# ====== 引数定義 ======
def parse_args():
    p = argparse.ArgumentParser(description="RAG + Web検索 4つのモード検証システム")
    
    # 基本設定
    p.add_argument("--model", default="Alibaba-NLP/gte-multilingual-base", help="ベクトル化モデル")
    p.add_argument("--ollama_model", default="granite3.3:2b", help="Ollamaモデル")
    p.add_argument("--db", default="output/chunks.sqlite", help="チャンクデータベース")
    p.add_argument("--index", default="output/hnsw_index.bin", help="HNSWインデックス")
    p.add_argument("--endpoint", default="http://localhost:11434", help="Ollama APIエンドポイント")
    
    # RAG設定
    p.add_argument("--limit", type=int, default=5, help="取得するチャンク数")
    p.add_argument("--max_context_chars", type=int, default=3000, help="最大コンテキスト文字数")
    
    # LLM設定
    p.add_argument("--temperature", type=float, default=0.7, help="LLM温度パラメータ")
    p.add_argument("--top_p", type=float, default=0.8, help="LLM top_pパラメータ")
    p.add_argument("--num_ctx", type=int, default=None, help="コンテキストウィンドウサイズ")
    p.add_argument("--num_predict", type=int, default=256, help="生成する最大トークン数")
    
    # モード選択
    p.add_argument("--mode", choices=["selection", "fallback", "hybrid", "comparison"], 
                   default="selection", help="実行モード")
    p.add_argument("--search_type", choices=["rag", "web", "hybrid"], 
                   default="rag", help="選択モードでの検索タイプ")
    
    # Web検索設定
    p.add_argument("--web_max_results", type=int, default=5, help="Web検索の最大結果数")
    
    # 品質評価設定
    p.add_argument("--quality_threshold", type=float, default=0.5, 
                   help="フォールバックモードの品質閾値")
    
    # 出力設定
    p.add_argument("--query", type=str, help="質問（指定しない場合は対話モード）")
    p.add_argument("--save_report", action="store_true", help="結果をMarkdownレポートとして保存")
    p.add_argument("--log_file", type=str, default=None, help="ログファイル名（指定しない場合は日付ベース）")
    p.add_argument("--debug", action="store_true", help="デバッグ情報を表示")
    
    return p.parse_args()


# ====== Ollamaモデル存在チェック ======
def check_ollama_model_exists(model_name):
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, check=True
        )
        lines = result.stdout.strip().splitlines()
        found = False
        for line in lines[1:]:
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


# ====== Ollama呼び出し ======
def query_ollama(prompt, model, endpoint, temperature=0.7, top_p=0.8, num_ctx=None, num_predict=256, timer=None):
    """Ollama APIを呼び出してLLM応答を取得（タイミング計測付き）"""
    if timer:
        timer.start("LLM生成")
    
    url = f"{endpoint}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": num_predict
        }
    }
    if num_ctx is not None:
        payload["options"]["num_ctx"] = num_ctx
    
    if timer:
        timer.start("API呼び出し")
    
    try:
        r = requests.post(url, json=payload, timeout=600)
    except requests.exceptions.ConnectionError:
        if timer:
            timer.end("エラー: 接続失敗")
            timer.end()  # LLM生成
        print("\nエラー: Ollamaサーバーに接続できません。\n")
        return ""
    
    if timer:
        timer.end()
    
    if not r.ok:
        if timer:
            timer.end()  # LLM生成
        print(f"\nOllama APIエラー: {r.status_code} - {r.text}\n")
        return ""
    
    if timer:
        timer.start("レスポンス処理")
    
    data = r.json()
    response = data.get("response", "").strip()
    
    if timer:
        timer.end(f"{len(response)}文字")
        timer.end()  # LLM生成
    
    return response


# ====== RAG検索クラス ======
class RAGSearcher:
    def __init__(self, model, index, db, limit=5, max_context_chars=3000):
        self.model = model
        self.index = index
        self.db = db
        self.limit = limit
        self.max_context_chars = max_context_chars
        self.model_loaded = False
    
    def search(self, query, timer=None):
        """RAG検索を実行（タイミング計測付き）"""
        if timer:
            timer.start("RAG検索全体")
        
        start_time = time.perf_counter()
        
        # モデルロード確認（初回のみ計測）
        if timer and not self.model_loaded:
            timer.start("モデルロード確認")
            self.model_loaded = True
            timer.end()
        
        # ベクトル化
        if timer:
            timer.start("クエリのベクトル化")
        q_emb = self.model.encode([query], normalize_embeddings=True)
        if timer:
            timer.end(f"次元数: {len(q_emb[0])}")
        
        # HNSW検索
        if timer:
            timer.start("HNSWインデックス検索")
        ids, distances = self.index.knn_query(q_emb, k=self.limit)
        if timer:
            timer.end(f"{len(ids[0])}件取得")
        
        # チャンク取得
        if timer:
            timer.start("データベースからチャンク取得")
        
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        
        chunks = []
        total_len = 0
        
        for i, dist in zip(ids[0], distances[0]):
            cur.execute("SELECT content FROM chunks WHERE id=?", (int(i),))
            row = cur.fetchone()
            if not row:
                continue
            
            text = row[0]
            similarity = 1.0 - dist  # コサイン類似度に変換
            
            if total_len + len(text) > self.max_context_chars:
                break
            
            chunks.append({
                "id": int(i),
                "content": text,
                "similarity": float(similarity),
                "length": len(text)
            })
            total_len += len(text)
        
        conn.close()
        
        if timer:
            timer.end(f"{len(chunks)}チャンク")
        
        elapsed_time = time.perf_counter() - start_time
        
        if timer:
            timer.end()  # RAG検索全体
        
        return {
            "source": "rag",
            "chunks": chunks,
            "context": "\n".join([c["content"] for c in chunks]),
            "total_length": total_len,
            "elapsed_time": elapsed_time
        }


# ====== Web検索クラス ======
# ====== Brave Web検索クラス ======
class BraveWebSearcher:
    """Brave Search API を使用したWeb検索"""
    
    def __init__(self, api_key=None, max_results=5, country="JP",
                 search_lang="jp", ui_lang="ja-JP", max_retries=3, retry_delay=2):
        self.api_key = api_key or os.getenv("BRAVE_API_KEY")
        self.max_results = max_results
        self.country = country
        self.search_lang = search_lang
        self.ui_lang = ui_lang
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.url = "https://api.search.brave.com/res/v1/web/search"
    
    def search(self, query, freshness=None, timer=None):
        """Brave Search APIで検索（リトライ機能付き、タイミング計測付き）"""
        if timer:
            timer.start("Brave Web検索全体")
        
        if not self.api_key:
            if timer:
                timer.end("エラー: APIキー未設定")
            return {
                "source": "brave_web",
                "results": [],
                "count": 0,
                "error": "BRAVE_API_KEY が設定されていません",
                "elapsed_time": 0
            }
        
        start_time = time.perf_counter()
        last_error = None
        
        for attempt in range(self.max_retries):
            if timer:
                timer.start(f"Brave検索試行{attempt + 1}")
            
            try:
                # パラメータ設定
                params = {
                    "q": query,
                    "count": self.max_results,
                    "country": self.country,
                    "search_lang": self.search_lang,
                    "ui_lang": self.ui_lang,
                }
                
                if freshness:
                    params["freshness"] = freshness
                
                headers = {
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self.api_key
                }
                
                response = requests.get(self.url, headers=headers,
                                       params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # 結果を処理
                results = []
                if 'web' in data and 'results' in data['web']:
                    for item in data['web']['results']:
                        results.append({
                            "title": item.get('title', ''),
                            "body": item.get('description', ''),
                            "url": item.get('url', ''),
                            "age": item.get('age', ''),
                            "language": item.get('language', '')
                        })
                
                elapsed_time = time.perf_counter() - start_time
                
                # 結果が0件の場合は失敗とみなしてリトライ
                if len(results) == 0:
                    last_error = f"検索結果が0件でした（試行 {attempt + 1}/{self.max_retries}）"
                    if timer:
                        timer.end(f"0件")
                    print(f"警告: {last_error}")
                    if attempt < self.max_retries - 1:
                        print(f"{self.retry_delay}秒後にリトライします...")
                        time.sleep(self.retry_delay)
                        continue
                
                # 成功
                if timer:
                    timer.end(f"{len(results)}件取得")
                    timer.end()  # Brave Web検索全体
                
                return {
                    "source": "brave_web",
                    "results": results,
                    "count": len(results),
                    "context": "\n\n".join([f"【{r['title']}】\n{r['body']}" for r in results]),
                    "elapsed_time": elapsed_time,
                    "attempts": attempt + 1,
                    "query_info": data.get('query', {})
                }
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:
                    last_error = f"認証エラー: APIキーが無効です (試行 {attempt + 1}/{self.max_retries})"
                elif e.response.status_code == 422:
                    last_error = f"パラメータエラー: 指定されたパラメータが無効です (試行 {attempt + 1}/{self.max_retries})"
                elif e.response.status_code == 429:
                    last_error = f"レート制限エラー (試行 {attempt + 1}/{self.max_retries})"
                else:
                    last_error = f"HTTPエラー: {e.response.status_code} (試行 {attempt + 1}/{self.max_retries})"
                
                if timer:
                    timer.end(f"エラー: {e.response.status_code}")
                print(f"警告: {last_error}")
                
                if attempt < self.max_retries - 1:
                    print(f"{self.retry_delay}秒後にリトライします...")
                    time.sleep(self.retry_delay)
            
            except Exception as e:
                last_error = f"エラー: {str(e)} (試行 {attempt + 1}/{self.max_retries})"
                if timer:
                    timer.end(f"エラー: {str(e)}")
                print(f"警告: {last_error}")
                if attempt < self.max_retries - 1:
                    print(f"{self.retry_delay}秒後にリトライします...")
                    time.sleep(self.retry_delay)
        
        # すべてのリトライが失敗
        elapsed_time = time.perf_counter() - start_time
        if timer:
            timer.end()  # Brave Web検索全体
        
        return {
            "source": "brave_web",
            "results": [],
            "count": 0,
            "error": last_error or "不明なエラー",
            "elapsed_time": elapsed_time,
            "attempts": self.max_retries
        }


# ====== 品質評価クラス ======
class QualityEvaluator:
    def evaluate(self, rag_result, query):
        """
        RAG結果の品質を評価
        4つの指標:
        1. 類似度スコア (40%)
        2. チャンク数 (20%)
        3. コンテンツ長 (20%)
        4. キーワード一致 (20%)
        """
        similarity_score = self._calc_similarity(rag_result)
        chunk_score = self._calc_chunk_score(rag_result)
        content_score = self._calc_content_score(rag_result)
        keyword_score = self._calc_keyword_score(rag_result, query)
        
        total_score = (
            similarity_score * 0.4 +
            chunk_score * 0.2 +
            content_score * 0.2 +
            keyword_score * 0.2
        )
        
        return {
            "total_score": total_score,
            "similarity_score": similarity_score,
            "chunk_score": chunk_score,
            "content_score": content_score,
            "keyword_score": keyword_score
        }
    
    def _calc_similarity(self, result):
        """類似度スコアの計算"""
        chunks = result.get("chunks", [])
        if not chunks:
            return 0.0
        max_sim = max(chunk["similarity"] for chunk in chunks)
        return max_sim
    
    def _calc_chunk_score(self, result):
        """チャンク数スコアの計算"""
        chunk_count = len(result.get("chunks", []))
        return min(chunk_count / 3.0, 1.0)
    
    def _calc_content_score(self, result):
        """コンテンツ長スコアの計算"""
        total_length = result.get("total_length", 0)
        return min(total_length / 1000.0, 1.0)
    
    def _calc_keyword_score(self, result, query):
        """キーワード一致スコアの計算"""
        query_keywords = set(query.lower().split())
        content = result.get("context", "")
        content_words = set(content.lower().split())
        
        if not query_keywords:
            return 0.0
        
        match_count = len(query_keywords & content_words)
        return match_count / len(query_keywords)


# ====== RAG + Web統合システム ======
class RAGWebSystem:
    def __init__(self, args, rag_searcher, web_searcher, evaluator):
        self.args = args
        self.rag = rag_searcher
        self.web = web_searcher
        self.evaluator = evaluator
    
    def mode_selection(self, query, search_type, timer=None):
        """選択モード: ユーザーが指定したモードで検索（タイミング計測付き）"""
        if timer:
            timer.start("選択モード全体")
        
        if search_type == "rag":
            result = self._rag_only(query, timer)
        elif search_type == "web":
            result = self._web_only(query, timer)
        elif search_type == "hybrid":
            result = self._hybrid_search(query, timer)
        
        if timer:
            timer.end()
            # タイミング情報を結果に追加
            result["timing"] = timer.get_report_section()
            # サマリーを出力
            print(timer.get_summary())
        
        return result
    
    def mode_fallback(self, query, timer=None):
        """フォールバックモード: RAG結果を評価し、必要に応じてWeb検索（タイミング計測付き）"""
        if timer:
            timer.start("フォールバックモード全体")
        
        # RAG検索
        rag_result = self.rag.search(query, timer)
        
        # 品質評価
        if timer:
            timer.start("品質評価")
        quality = self.evaluator.evaluate(rag_result, query)
        if timer:
            timer.end(f"スコア: {quality['total_score']:.3f}")
        
        if self.args.debug:
            print(f"\n[DEBUG] 品質スコア: {quality['total_score']:.3f}")
            print(f"  - 類似度: {quality['similarity_score']:.3f}")
            print(f"  - チャンク数: {quality['chunk_score']:.3f}")
            print(f"  - コンテンツ長: {quality['content_score']:.3f}")
            print(f"  - キーワード一致: {quality['keyword_score']:.3f}")
        
        # 閾値判定
        if quality["total_score"] < self.args.quality_threshold:
            if self.args.debug:
                print(f"[DEBUG] 品質不足 → Web検索を追加")
            
            # Web検索を追加
            web_result = self.web.search(query, timer)
            
            # LLM生成（RAG + Web統合）
            combined_context = f"【内部情報】\n{rag_result['context']}\n\n【Web情報】\n{web_result.get('context', '')}"
            prompt = f"以下の情報を参考に質問に答えてください。\n\n{combined_context}\n\n質問: {query}\n\n回答:"
            response = query_ollama(prompt, self.args.ollama_model, self.args.endpoint,
                                   self.args.temperature, self.args.top_p,
                                   self.args.num_ctx, self.args.num_predict, timer)
            
            if timer:
                timer.end()
                # サマリーを出力
                print(timer.get_summary())
            
            result = {
                "mode": "fallback",
                "decision": "web_added",
                "rag_result": rag_result,
                "web_result": web_result,
                "quality": quality,
                "response": response
            }
            
            if timer:
                result["timing"] = timer.get_report_section()
            
            return result
        else:
            if self.args.debug:
                print(f"[DEBUG] 品質十分 → RAGのみで回答")
            
            # LLM生成（RAGのみ）
            prompt = f"以下の情報を参考に質問に答えてください。\n\n{rag_result['context']}\n\n質問: {query}\n\n回答:"
            response = query_ollama(prompt, self.args.ollama_model, self.args.endpoint,
                                   self.args.temperature, self.args.top_p,
                                   self.args.num_ctx, self.args.num_predict, timer)
            
            if timer:
                timer.end()
                # サマリーを出力
                print(timer.get_summary())
            
            result = {
                "mode": "fallback",
                "decision": "rag_only",
                "rag_result": rag_result,
                "quality": quality,
                "response": response
            }
            
            if timer:
                result["timing"] = timer.get_report_section()
            
            return result
    
    def mode_hybrid(self, query, timer=None):
        """ハイブリッドモード: RAGとWeb検索を順次実行して統合（タイミング計測付き）"""
        if timer:
            timer.start("ハイブリッドモード全体")
            timer.start("順次検索（RAG + Web）")
        
        # 並行実行を避けて順次実行に変更（PyTorchモデルの互換性問題を回避）
        rag_result = self.rag.search(query, timer)
        web_result = self.web.search(query, timer)
        
        if timer:
            timer.end(f"RAG: {rag_result.get('elapsed_time', 0):.3f}秒, Web: {web_result.get('elapsed_time', 0):.3f}秒")
        
        if timer:
            timer.start("品質評価")
        quality = self.evaluator.evaluate(rag_result, query)
        if timer:
            timer.end(f"スコア: {quality['total_score']:.3f}")
        
        # コンテキスト統合（RAG 60% : Web 40%）
        combined_context = f"【内部情報】\n{rag_result['context']}\n\n【Web情報】\n{web_result.get('context', '')}"
        
        # LLM生成
        prompt = f"以下の情報を参考に質問に答えてください。内部情報を重視しつつ、Web情報も活用してください。\n\n{combined_context}\n\n質問: {query}\n\n回答:"
        response = query_ollama(prompt, self.args.ollama_model, self.args.endpoint,
                               self.args.temperature, self.args.top_p,
                               self.args.num_ctx, self.args.num_predict, timer)
        
        if timer:
            timer.end()
            # サマリーを出力
            print(timer.get_summary())
        
        result = {
            "mode": "hybrid",
            "rag_result": rag_result,
            "web_result": web_result,
            "quality": quality,
            "response": response
        }
        
        if timer:
            result["timing"] = timer.get_report_section()
        
        return result
    
    def mode_comparison(self, query, timer=None):
        """比較モード: 3つの方式すべてを実行して比較（タイミング計測付き）"""
        if timer:
            timer.start("比較モード全体")
        
        rag_result = self._rag_only(query, timer)
        web_result = self._web_only(query, timer)
        hybrid_result = self._hybrid_search(query, timer)
        
        if timer:
            timer.end()
            # サマリーを出力
            print(timer.get_summary())
        
        result = {
            "mode": "comparison",
            "rag_only": rag_result,
            "web_only": web_result,
            "hybrid": hybrid_result
        }
        
        if timer:
            result["timing"] = timer.get_report_section()
        
        return result
    
    def _rag_only(self, query, timer=None):
        """RAGのみで検索（タイミング計測付き）"""
        rag_result = self.rag.search(query, timer)
        
        if timer:
            timer.start("品質評価")
        quality = self.evaluator.evaluate(rag_result, query)
        if timer:
            timer.end(f"スコア: {quality['total_score']:.3f}")
        
        # LLM生成
        prompt = f"以下の情報を参考に質問に答えてください。\n\n{rag_result['context']}\n\n質問: {query}\n\n回答:"
        response = query_ollama(prompt, self.args.ollama_model, self.args.endpoint,
                               self.args.temperature, self.args.top_p,
                               self.args.num_ctx, self.args.num_predict, timer)
        
        return {
            "mode": "rag_only",
            "rag_result": rag_result,
            "quality": quality,
            "response": response
        }
    
    def _web_only(self, query, timer=None):
        """Webのみで検索（タイミング計測付き）"""
        web_result = self.web.search(query, timer)
        
        if web_result.get("error"):
            return {
                "mode": "web_only",
                "web_result": web_result,
                "response": f"Web検索エラー: {web_result['error']}"
            }
        
        # LLM生成
        prompt = f"以下のWeb検索結果を参考に質問に答えてください。\n\n{web_result['context']}\n\n質問: {query}\n\n回答:"
        response = query_ollama(prompt, self.args.ollama_model, self.args.endpoint,
                               self.args.temperature, self.args.top_p,
                               self.args.num_ctx, self.args.num_predict, timer)
        
        return {
            "mode": "web_only",
            "web_result": web_result,
            "response": response
        }
    
    def _hybrid_search(self, query, timer=None):
        """ハイブリッド検索（順次実行、タイミング計測付き）"""
        if timer:
            timer.start("順次検索（RAG + Web）")
        
        # 並行実行を避けて順次実行に変更（PyTorchモデルの互換性問題を回避）
        rag_result = self.rag.search(query, timer)
        web_result = self.web.search(query, timer)
        
        if timer:
            timer.end(f"RAG: {rag_result.get('elapsed_time', 0):.3f}秒, Web: {web_result.get('elapsed_time', 0):.3f}秒")
        
        if timer:
            timer.start("品質評価")
        quality = self.evaluator.evaluate(rag_result, query)
        if timer:
            timer.end(f"スコア: {quality['total_score']:.3f}")
        
        # コンテキスト統合（RAG 60% : Web 40%）
        combined_context = f"【内部情報】\n{rag_result['context']}\n\n【Web情報】\n{web_result.get('context', '')}"
        
        # LLM生成
        prompt = f"以下の情報を参考に質問に答えてください。内部情報を重視しつつ、Web情報も活用してください。\n\n{combined_context}\n\n質問: {query}\n\n回答:"
        response = query_ollama(prompt, self.args.ollama_model, self.args.endpoint,
                               self.args.temperature, self.args.top_p,
                               self.args.num_ctx, self.args.num_predict, timer)
        
        return {
            "mode": "hybrid",
            "rag_result": rag_result,
            "web_result": web_result,
            "quality": quality,
            "response": response
        }
    
    def _merge_results(self, rag_result, web_result, quality=None):
        """RAGとWeb結果を統合"""
        if quality is None:
            quality = self.evaluator.evaluate(rag_result, "")
        
        combined_context = f"【内部情報】\n{rag_result['context']}\n\n【Web情報】\n{web_result.get('context', '')}"
        
        return {
            "mode": "merged",
            "rag_result": rag_result,
            "web_result": web_result,
            "quality": quality,
            "combined_context": combined_context
        }


# ====== レポート生成 ======
def save_report(query, result, args, log_file=None):
    """結果をMarkdownレポートとして保存（追記モード）"""
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # ログファイル名を指定されていない場合は日付ベースで生成
    if log_file is None:
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = report_dir / f"four_modes_log_{date_str}.md"
    else:
        # log_fileがすでにパスを含んでいる場合はそのまま使用
        log_file = Path(log_file)
        if not log_file.is_absolute() and log_file.parts[0] != "reports":
            log_file = report_dir / log_file
    
    # 新規ファイルの場合はヘッダーを追加
    is_new_file = not log_file.exists()
    
    with open(log_file, "a", encoding="utf-8") as f:
        if is_new_file:
            f.write(f"# 4つのモード検証ログ\n\n")
            f.write(f"**作成日:** {datetime.now().strftime('%Y-%m-%d')}\n\n")
            f.write(f"---\n\n")
        
        # 各テストの区切り
        f.write(f"\n## テスト実行 - {datetime.now().strftime('%H:%M:%S')}\n\n")
        f.write(f"**モード:** {args.mode}\n\n")
        f.write(f"**質問:** {query}\n\n")
        
        # モード別の出力
        if args.mode == "comparison":
            _write_comparison_report(f, result)
        elif args.mode == "fallback":
            _write_fallback_report(f, result)
        else:
            _write_standard_report(f, result)
        
        f.write(f"\n---\n")
    
    print(f"\nレポートを追記しました: {log_file}\n")
    return log_file


def _write_standard_report(f, result):
    """標準レポート出力（タイミング情報付き）"""
    f.write(f"### 実行結果\n\n")
    
    if "rag_result" in result:
        rag = result["rag_result"]
        f.write(f"#### RAG検索結果\n\n")
        f.write(f"- チャンク数: {len(rag['chunks'])}\n")
        f.write(f"- 処理時間: {rag['elapsed_time']:.3f}秒\n")
        if "quality" in result:
            q = result["quality"]
            f.write(f"- 品質スコア: {q['total_score']:.3f}\n")
        f.write(f"\n")
    
    if "web_result" in result:
        web = result["web_result"]
        f.write(f"#### Web検索結果\n\n")
        f.write(f"- 結果数: {web['count']}\n")
        f.write(f"- 処理時間: {web.get('elapsed_time', 0):.3f}秒\n")
        
        # リトライ回数を表示
        if "attempts" in web:
            f.write(f"- 試行回数: {web['attempts']}\n")
        
        # エラーがある場合は詳細に表示
        if "error" in web:
            f.write(f"\n**⚠️ エラー詳細:**\n")
            f.write(f"```\n{web['error']}\n```\n")
        
        # 結果が0件の場合は警告と対処法
        if web['count'] == 0:
            f.write(f"\n**⚠️ 警告**: Web検索結果が0件でした。\n\n")
            f.write(f"**考えられる原因:**\n")
            f.write(f"- DuckDuckGo APIのレート制限\n")
            f.write(f"- ネットワーク接続の問題\n")
            f.write(f"- 検索クエリが適切でない\n")
            f.write(f"- 一時的なサービス障害\n\n")
            f.write(f"**対処法:**\n")
            f.write(f"- 数分待ってから再試行\n")
            f.write(f"- 検索クエリを変更\n")
            f.write(f"- VPNを使用\n")
            f.write(f"- 別の検索エンジンAPIを検討\n\n")
    
    if "response" in result:
        f.write(f"#### 回答\n\n{result['response']}\n\n")
    
    # タイミング情報を追加
    if "timing" in result:
        f.write(result["timing"])


def _write_fallback_report(f, result):
    """フォールバックレポート出力"""
    f.write(f"### フォールバック判定\n\n")
    
    if "quality" in result:
        q = result["quality"]
        f.write(f"#### 品質評価\n\n")
        f.write(f"- 総合スコア: {q['total_score']:.3f}\n")
        f.write(f"- 類似度: {q['similarity_score']:.3f}\n")
        f.write(f"- チャンク数: {q['chunk_score']:.3f}\n")
        f.write(f"- コンテンツ長: {q['content_score']:.3f}\n")
        f.write(f"- キーワード一致: {q['keyword_score']:.3f}\n\n")
    
    decision = result.get("decision", "merged")
    if decision == "rag_only":
        f.write(f"#### 判定結果\n\n")
        f.write(f"✅ RAGのみで十分な品質\n\n")
    else:
        f.write(f"#### 判定結果\n\n")
        f.write(f"❌ RAG結果が不十分 → Web検索を追加\n\n")
        
        # Web検索結果のエラー情報も表示
        if "web_result" in result:
            web = result["web_result"]
            if "error" in web:
                f.write(f"**⚠️ Web検索エラー:**\n")
                f.write(f"```\n{web['error']}\n```\n\n")
    
    # 回答を追加
    if "response" in result:
        f.write(f"#### 回答\n\n{result['response']}\n\n")


def _write_comparison_report(f, result):
    """比較レポート出力"""
    f.write(f"### 3つの方式の比較\n\n")
    
    for mode_name, mode_result in [("RAGのみ", result["rag_only"]),
                                     ("Webのみ", result["web_only"]),
                                     ("ハイブリッド", result["hybrid"])]:
        f.write(f"#### {mode_name}\n\n")
        f.write(f"**回答:**\n\n{mode_result.get('response', 'N/A')}\n\n")
        
        if "rag_result" in mode_result:
            rag = mode_result["rag_result"]
            f.write(f"- RAG処理時間: {rag['elapsed_time']:.3f}秒\n")
        
        if "web_result" in mode_result:
            web = mode_result["web_result"]
            f.write(f"- Web処理時間: {web.get('elapsed_time', 0):.3f}秒\n")
            f.write(f"- Web結果数: {web.get('count', 0)}\n")
            
            # エラー情報を表示
            if "error" in web:
                f.write(f"\n**⚠️ エラー:**\n```\n{web['error']}\n```\n")
            
            # リトライ情報を表示
            if "attempts" in web and web["attempts"] > 1:
                f.write(f"- 試行回数: {web['attempts']}\n")
        
        f.write(f"\n---\n\n")


# ====== メイン処理 ======
def main():
    args = parse_args()
    
    # Ollamaモデル存在確認
    check_ollama_model_exists(args.ollama_model)
    
    # ログ抑止
    warnings.filterwarnings("ignore")
    hf_logging.set_verbosity_error()
    
    # モデルロード
    print("モデルをロード中...")
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(devnull):
        model = SentenceTransformer(args.model, trust_remote_code=True, device='cpu')
    
    # インデックスロード
    index = hnswlib.Index(space='cosine', dim=model.get_sentence_embedding_dimension())
    index.load_index(args.index)
    
    # 各コンポーネント初期化
    rag_searcher = RAGSearcher(model, index, args.db, args.limit, args.max_context_chars)
    web_searcher = BraveWebSearcher(max_results=args.web_max_results)
    evaluator = QualityEvaluator()
    system = RAGWebSystem(args, rag_searcher, web_searcher, evaluator)
    
    print(f"✅ 初期化完了")
    print(f"モード: {args.mode}")
    if args.mode == "selection":
        print(f"検索タイプ: {args.search_type}")
    if args.debug:
        print(f"デバッグモード: ON（タイミングログ有効）")
    print()
    
    # 単一クエリモード
    if args.query:
        query = args.query
        print(f"質問: {query}\n")
        
        # タイミングロガー初期化
        timer = TimingLogger(enabled=args.debug)
        
        # モード実行
        if args.mode == "selection":
            result = system.mode_selection(query, args.search_type, timer)
        elif args.mode == "fallback":
            result = system.mode_fallback(query, timer)
        elif args.mode == "hybrid":
            result = system.mode_hybrid(query, timer)
        elif args.mode == "comparison":
            result = system.mode_comparison(query, timer)
        
        # 結果表示
        if args.mode == "comparison":
            print("\n=== RAGのみ ===")
            print(result["rag_only"].get("response", "N/A"))
            print("\n=== Webのみ ===")
            print(result["web_only"].get("response", "N/A"))
            print("\n=== ハイブリッド ===")
            print(result["hybrid"].get("response", "N/A"))
        else:
            print(result.get("response", "N/A"))
        
        # レポート保存
        if args.save_report:
            save_report(query, result, args, log_file=args.log_file)
        
        return
    
    # 対話モード
    print("質問を入力してください。(終了するには Ctrl+C)\n")
    
    while True:
        try:
            query = input("> ").strip()
            if not query:
                continue
            
            # タイミングロガー初期化
            timer = TimingLogger(enabled=args.debug)
            
            # モード実行
            if args.mode == "selection":
                result = system.mode_selection(query, args.search_type, timer)
            elif args.mode == "fallback":
                result = system.mode_fallback(query, timer)
            elif args.mode == "hybrid":
                result = system.mode_hybrid(query, timer)
            elif args.mode == "comparison":
                result = system.mode_comparison(query, timer)
            
            # 結果表示
            if args.mode == "comparison":
                print("\n=== RAGのみ ===")
                print(result["rag_only"].get("response", "N/A"))
                print("\n=== Webのみ ===")
                print(result["web_only"].get("response", "N/A"))
                print("\n=== ハイブリッド ===")
                print(result["hybrid"].get("response", "N/A"))
            else:
                print(f"\n{result.get('response', 'N/A')}\n")
            
            # レポート保存
            if args.save_report:
                save_report(query, result, args, log_file=args.log_file)
        
        except KeyboardInterrupt:
            print("\n終了します。")
            break
        except Exception as e:
            print(f"\nエラー: {e}\n")
            if args.debug:
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    main()