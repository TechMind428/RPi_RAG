#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rag_web_auto_mode.py - RAG + Web検索 自動モード選択システム
---------------------------------------------------------------------------
10月号で解説する最適化機能:
1. クエリ分類による自動モード選択
2. 動的な品質閾値調整
3. パラメータプロファイル（fast/balanced/quality）
4. 詳細なパフォーマンス計測

ベースシステム: rag_web_four_modes_brave.py
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
import json
from datetime import datetime
from pathlib import Path
from sentence_transformers import SentenceTransformer
from transformers import logging as hf_logging

# .envファイルから環境変数を読み込む
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
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    os.environ[key] = value
    except Exception as e:
        print(f"警告: .envファイルの読み込みに失敗しました: {e}")

load_env_file()


# ====== クエリ分類器 ======
class QueryClassifier:
    """
    クエリを分類して最適なモードと閾値を選択
    10月号 セクション10-1で解説
    """
    
    # クエリタイプ別のキーワード
    TEMPORAL_KEYWORDS = [
        "最新", "今", "現在", "ニュース", "価格", 
        "発売", "販売", "いつ", "何時", "最近"
    ]
    
    SPEC_KEYWORDS = [
        "仕様", "スペック", "構成", "性能", "アーキテクチャ",
        "CPU", "GPU", "メモリ", "ストレージ", "電源",
        "周波数", "コア", "帯域幅"
    ]
    
    HOWTO_KEYWORDS = [
        "使い方", "構築", "設定", "インストール", "方法",
        "やり方", "手順", "導入", "セットアップ", "には"
    ]
    
    @classmethod
    def classify(cls, query):
        """
        クエリを分類してモードと閾値を返す
        
        Args:
            query: ユーザーのクエリ文字列
            
        Returns:
            dict: {
                "mode": "rag" | "web" | "fallback",
                "query_type": "spec" | "news" | "howto",
                "threshold": float,
                "reason": str
            }
        """
        # 時間依存の情報 → Web検索優先
        if any(kw in query for kw in cls.TEMPORAL_KEYWORDS):
            return {
                "mode": "web",
                "query_type": "news",
                "threshold": 0.95,  # Web検索なので高い閾値
                "reason": "時間依存の情報を求めるクエリ"
            }
        
        # 仕様・スペック → RAG優先
        if any(kw in query for kw in cls.SPEC_KEYWORDS):
            return {
                "mode": "rag",
                "query_type": "spec",
                "threshold": 0.85,  # RAGで十分な情報が期待される
                "reason": "仕様・スペック情報を求めるクエリ"
            }
        
        # 使い方・構築方法 → Fallback（RAG→Web）
        if any(kw in query for kw in cls.HOWTO_KEYWORDS):
            return {
                "mode": "fallback",
                "query_type": "howto",
                "threshold": 0.90,  # 高品質な情報を求める
                "reason": "使い方・構築方法を求めるクエリ"
            }
        
        # デフォルト: Fallback（中程度の閾値）
        return {
            "mode": "fallback",
            "query_type": "general",
            "threshold": 0.85,
            "reason": "一般的なクエリ"
        }


# ====== パラメータプロファイル ======
class ParameterProfile:
    """
    LLMパラメータのプロファイル管理
    10月号 セクション10-6で解説
    """
    
    PROFILES = {
        "fast": {
            "num_predict": 128,
            "max_context_chars": 2000,
            "temperature": 0.5,
            "top_p": 0.7,
            "description": "高速応答優先（モバイル・リアルタイム用）"
        },
        "balanced": {
            "num_predict": 256,
            "max_context_chars": 3000,
            "temperature": 0.7,
            "top_p": 0.8,
            "description": "バランス型（デフォルト推奨）"
        },
        "quality": {
            "num_predict": 512,
            "max_context_chars": 4000,
            "temperature": 0.8,
            "top_p": 0.9,
            "description": "高品質応答優先（詳細な分析用）"
        }
    }
    
    @classmethod
    def get_profile(cls, profile_name):
        """プロファイルを取得"""
        return cls.PROFILES.get(profile_name, cls.PROFILES["balanced"])
    
    @classmethod
    def list_profiles(cls):
        """利用可能なプロファイル一覧を表示"""
        print("\n利用可能なパラメータプロファイル:")
        print("=" * 70)
        for name, profile in cls.PROFILES.items():
            print(f"\n【{name}】")
            print(f"  説明: {profile['description']}")
            print(f"  num_predict: {profile['num_predict']}")
            print(f"  max_context_chars: {profile['max_context_chars']}")
            print(f"  temperature: {profile['temperature']}")
            print(f"  top_p: {profile['top_p']}")
        print("=" * 70)


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
    
    def get_metrics(self):
        """メトリクスを辞書形式で取得"""
        if not self.timings:
            return {}
        
        total = sum(t["elapsed"] for t in self.timings)
        metrics = {
            "total_time": total,
            "sections": []
        }
        
        for t in self.timings:
            percentage = (t["elapsed"] / total * 100) if total > 0 else 0
            metrics["sections"].append({
                "name": t["section"],
                "elapsed": t["elapsed"],
                "percentage": percentage,
                "details": t["details"]
            })
        
        return metrics


# ====== 引数定義 ======
def parse_args():
    p = argparse.ArgumentParser(
        description="RAG + Web検索 自動モード選択システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # 自動モード選択（デフォルト）
  python rag_web_auto_mode.py --query "Raspberry Pi 5のCPU仕様は？"
  
  # パラメータプロファイル指定
  python rag_web_auto_mode.py --profile fast --query "Raspberry Pi 5のGPU性能は？"
  
  # 手動モード指定（自動選択を無効化）
  python rag_web_auto_mode.py --manual_mode rag --query "Raspberry Pi 5のメモリ仕様は？"
  
  # プロファイル一覧表示
  python rag_web_auto_mode.py --list_profiles
        """
    )
    
    # 基本設定
    p.add_argument("--model", default="Alibaba-NLP/gte-multilingual-base", 
                   help="ベクトル化モデル")
    p.add_argument("--ollama_model", default="granite3.3:2b", 
                   help="Ollamaモデル")
    p.add_argument("--db", default="output/chunks.sqlite", 
                   help="チャンクデータベース")
    p.add_argument("--index", default="output/hnsw_index.bin", 
                   help="HNSWインデックス")
    p.add_argument("--endpoint", default="http://localhost:11434", 
                   help="Ollama APIエンドポイント")
    
    # パラメータプロファイル
    p.add_argument("--profile", choices=["fast", "balanced", "quality"], 
                   default="balanced", help="パラメータプロファイル")
    p.add_argument("--list_profiles", action="store_true", 
                   help="利用可能なプロファイル一覧を表示")
    
    # 自動モード選択
    p.add_argument("--auto_mode", action="store_true", default=True,
                   help="自動モード選択を有効化（デフォルト）")
    p.add_argument("--manual_mode", choices=["rag", "web", "fallback", "hybrid"], 
                   help="手動でモードを指定（自動選択を無効化）")
    
    # RAG設定
    p.add_argument("--limit", type=int, default=5, 
                   help="取得するチャンク数")
    
    # Web検索設定
    p.add_argument("--web_max_results", type=int, default=5, 
                   help="Web検索の最大結果数")
    
    # 出力設定
    p.add_argument("--query", type=str, 
                   help="質問（指定しない場合は対話モード）")
    p.add_argument("--save_report", action="store_true", 
                   help="結果をMarkdownレポートとして保存")
    p.add_argument("--output_dir", default="reports/auto_mode_tests",
                   help="レポート出力ディレクトリ")
    p.add_argument("--debug", action="store_true", 
                   help="デバッグ情報を表示")
    
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
def query_ollama(prompt, model, endpoint, temperature=0.7, top_p=0.8, 
                 num_ctx=None, num_predict=256, timer=None):
    """Ollama APIを呼び出してLLM応答を取得"""
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
    
    try:
        r = requests.post(url, json=payload, timeout=600)
    except requests.exceptions.ConnectionError:
        if timer:
            timer.end("エラー: 接続失敗")
        print("\nエラー: Ollamaサーバーに接続できません。\n")
        return ""
    
    if not r.ok:
        if timer:
            timer.end()
        print(f"\nOllama APIエラー: {r.status_code} - {r.text}\n")
        return ""
    
    data = r.json()
    response = data.get("response", "").strip()
    
    if timer:
        timer.end(f"{len(response)}文字")
    
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
        """RAG検索を実行"""
        if timer:
            timer.start("RAG検索全体")
        
        start_time = time.perf_counter()
        
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
            similarity = 1.0 - dist
            
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
            timer.end()
        
        return {
            "source": "rag",
            "chunks": chunks,
            "context": "\n".join([c["content"] for c in chunks]),
            "total_length": total_len,
            "elapsed_time": elapsed_time
        }


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
        """Brave Search APIで検索"""
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
            try:
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
                
                if len(results) == 0:
                    last_error = f"検索結果が0件でした（試行 {attempt + 1}/{self.max_retries}）"
                    print(f"警告: {last_error}")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                
                if timer:
                    timer.end(f"{len(results)}件取得")
                
                return {
                    "source": "brave_web",
                    "results": results,
                    "count": len(results),
                    "context": "\n\n".join([f"【{r['title']}】\n{r['body']}" for r in results]),
                    "elapsed_time": elapsed_time,
                    "attempts": attempt + 1
                }
                
            except Exception as e:
                last_error = f"エラー: {str(e)} (試行 {attempt + 1}/{self.max_retries})"
                print(f"警告: {last_error}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        
        elapsed_time = time.perf_counter() - start_time
        if timer:
            timer.end()
        
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
        10月号 セクション10-2で解説
        """
        chunks = rag_result.get("chunks", [])
        
        if not chunks:
            return {
                "score": 0.0,
                "details": {
                    "similarity_score": 0.0,
                    "chunk_count_score": 0.0,
                    "content_length_score": 0.0,
                    "keyword_match_score": 0.0
                },
                "reason": "チャンクが見つかりませんでした"
            }
        
        # 1. 類似度スコア (40%)
        avg_similarity = sum(c["similarity"] for c in chunks) / len(chunks)
        similarity_score = min(avg_similarity / 0.9, 1.0) * 0.4
        
        # 2. チャンク数スコア (20%)
        chunk_count_score = min(len(chunks) / 5, 1.0) * 0.2
        
        # 3. コンテンツ長スコア (20%)
        total_length = sum(c["length"] for c in chunks)
        content_length_score = min(total_length / 2000, 1.0) * 0.2
        
        # 4. キーワード一致スコア (20%)
        query_words = set(query.lower().split())
        context = rag_result.get("context", "").lower()
        matched_words = sum(1 for word in query_words if word in context)
        keyword_match_score = (matched_words / len(query_words) if query_words else 0) * 0.2
        
        total_score = similarity_score + chunk_count_score + content_length_score + keyword_match_score
        
        return {
            "score": total_score,
            "details": {
                "similarity_score": similarity_score,
                "chunk_count_score": chunk_count_score,
                "content_length_score": content_length_score,
                "keyword_match_score": keyword_match_score,
                "avg_similarity": avg_similarity,
                "chunk_count": len(chunks),
                "total_length": total_length,
                "matched_words": matched_words
            },
            "reason": self._get_quality_reason(total_score)
        }
    
    def _get_quality_reason(self, score):
        """スコアに基づいて理由を返す"""
        if score >= 0.8:
            return "高品質: RAGで十分な情報が得られました"
        elif score >= 0.6:
            return "中品質: 基本情報はありますが、追加情報が有用です"
        elif score >= 0.4:
            return "低品質: RAGの情報が不十分です"
        else:
            return "非常に低品質: RAGでは情報が得られませんでした"


# ====== メイン処理 ======
def main():
    args = parse_args()
    
    # プロファイル一覧表示
    if args.list_profiles:
        ParameterProfile.list_profiles()
        return
    
    # パラメータプロファイルを適用
    profile = ParameterProfile.get_profile(args.profile)
    print(f"\n使用するパラメータプロファイル: {args.profile}")
    print(f"説明: {profile['description']}")
    print(f"num_predict={profile['num_predict']}, "
          f"max_context_chars={profile['max_context_chars']}, "
          f"temperature={profile['temperature']}, "
          f"top_p={profile['top_p']}\n")
    
    # Ollamaモデルチェック
    check_ollama_model_exists(args.ollama_model)
    
    # 警告を抑制
    warnings.filterwarnings("ignore")
    hf_logging.set_verbosity_error()
    
    # タイミングロガー初期化
    timer = TimingLogger(enabled=True)
    
    # モデルとインデックスのロード
    print("システムを初期化しています...")
    timer.start("システム初期化")
    
    with contextlib.redirect_stdout(open(os.devnull, 'w')):
        embedding_model = SentenceTransformer(args.model, trust_remote_code=True)
    
    hnsw_index = hnswlib.Index(space='cosine', dim=768)
    hnsw_index.load_index(args.index)
    
    timer.end()
    
    # 検索エンジン初期化
    rag_searcher = RAGSearcher(
        embedding_model, hnsw_index, args.db,
        limit=args.limit,
        max_context_chars=profile['max_context_chars']
    )
    
    web_searcher = BraveWebSearcher(max_results=args.web_max_results)
    evaluator = QualityEvaluator()
    
    # クエリ処理
    if args.query:
        process_query(args.query, args, rag_searcher, web_searcher, 
                     evaluator, profile, timer)
    else:
        # 対話モード
        print("\n対話モードを開始します（終了するには 'exit' または 'quit' を入力）")
        while True:
            try:
                query = input("\n質問を入力してください: ").strip()
                if query.lower() in ['exit', 'quit', 'q']:
                    break
                if not query:
                    continue
                
                timer = TimingLogger(enabled=True)
                process_query(query, args, rag_searcher, web_searcher,
                            evaluator, profile, timer)
                
            except KeyboardInterrupt:
                print("\n\n終了します。")
                break


def process_query(query, args, rag_searcher, web_searcher, evaluator, profile, timer):
    """クエリを処理"""
    print(f"\n{'='*70}")
    print(f"質問: {query}")
    print(f"{'='*70}")
    
    # クエリ分類
    if args.manual_mode:
        classification = {
            "mode": args.manual_mode,
            "query_type": "manual",
            "threshold": 0.85,
            "reason": "手動モード指定"
        }
        print(f"\n[モード] 手動指定: {args.manual_mode}")
    else:
        timer.start("クエリ分類")
        classification = QueryClassifier.classify(query)
        timer.end()
        
        print(f"\n[自動分類結果]")
        print(f"  モード: {classification['mode']}")
        print(f"  クエリタイプ: {classification['query_type']}")
        print(f"  品質閾値: {classification['threshold']}")
        print(f"  理由: {classification['reason']}")
    
    # モードに応じて処理
    mode = classification["mode"]
    threshold = classification["threshold"]
    
    if mode == "rag":
        # RAGのみ
        rag_result = rag_searcher.search(query, timer)
        quality = evaluator.evaluate(rag_result, query)
        
        print(f"\n[RAG検索結果]")
        print(f"  チャンク数: {len(rag_result['chunks'])}")
        print(f"  品質スコア: {quality['score']:.3f}")
        print(f"  処理時間: {rag_result['elapsed_time']:.3f}秒")
        
        # LLM生成
        prompt = f"""以下の情報を参考に、質問に答えてください。

質問: {query}

参考情報:
{rag_result['context']}

回答:"""
        
        response = query_ollama(
            prompt, args.ollama_model, args.endpoint,
            temperature=profile['temperature'],
            top_p=profile['top_p'],
            num_predict=profile['num_predict'],
            timer=timer
        )
        
        print(f"\n[回答]")
        print(response)
        
    elif mode == "web":
        # Web検索のみ
        web_result = web_searcher.search(query, timer=timer)
        
        print(f"\n[Web検索結果]")
        print(f"  結果数: {web_result['count']}")
        print(f"  処理時間: {web_result['elapsed_time']:.3f}秒")
        
        if web_result['count'] > 0:
            prompt = f"""以下のWeb検索結果を参考に、質問に答えてください。

質問: {query}

Web検索結果:
{web_result['context']}

回答:"""
            
            response = query_ollama(
                prompt, args.ollama_model, args.endpoint,
                temperature=profile['temperature'],
                top_p=profile['top_p'],
                num_predict=profile['num_predict'],
                timer=timer
            )
            
            print(f"\n[回答]")
            print(response)
        else:
            print("\nWeb検索結果が得られませんでした。")
    
    elif mode == "fallback":
        # Fallbackモード: RAG → 品質評価 → 必要ならWeb
        rag_result = rag_searcher.search(query, timer)
        quality = evaluator.evaluate(rag_result, query)
        
        print(f"\n[RAG検索結果]")
        print(f"  チャンク数: {len(rag_result['chunks'])}")
        print(f"  品質スコア: {quality['score']:.3f}")
        print(f"  閾値: {threshold}")
        print(f"  処理時間: {rag_result['elapsed_time']:.3f}秒")
        
        if quality['score'] >= threshold:
            print(f"  判定: RAGで十分 ✓")
            
            prompt = f"""以下の情報を参考に、質問に答えてください。

質問: {query}

参考情報:
{rag_result['context']}

回答:"""
            
            response = query_ollama(
                prompt, args.ollama_model, args.endpoint,
                temperature=profile['temperature'],
                top_p=profile['top_p'],
                num_predict=profile['num_predict'],
                timer=timer
            )
            
            print(f"\n[回答（RAGのみ）]")
            print(response)
        else:
            print(f"  判定: Web検索を追加 →")
            
            web_result = web_searcher.search(query, timer=timer)
            
            print(f"\n[Web検索結果]")
            print(f"  結果数: {web_result['count']}")
            print(f"  処理時間: {web_result['elapsed_time']:.3f}秒")
            
            if web_result['count'] > 0:
                prompt = f"""以下の情報を参考に、質問に答えてください。

質問: {query}

RAG情報:
{rag_result['context']}

Web検索結果:
{web_result['context']}

回答:"""
                
                response = query_ollama(
                    prompt, args.ollama_model, args.endpoint,
                    temperature=profile['temperature'],
                    top_p=profile['top_p'],
                    num_predict=profile['num_predict'],
                    timer=timer
                )
                
                print(f"\n[回答（RAG + Web）]")
                print(response)
            else:
                print("\nWeb検索結果が得られませんでした。RAGの情報のみで回答します。")
                
                prompt = f"""以下の情報を参考に、質問に答えてください。

質問: {query}

参考情報:
{rag_result['context']}

回答:"""
                
                response = query_ollama(
                    prompt, args.ollama_model, args.endpoint,
                    temperature=profile['temperature'],
                    top_p=profile['top_p'],
                    num_predict=profile['num_predict'],
                    timer=timer
                )
                
                print(f"\n[回答（RAGのみ）]")
                print(response)
    
    elif mode == "hybrid":
        # Hybridモード: RAGとWebを並行実行
        print("\n[並行実行中...]")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            rag_future = executor.submit(rag_searcher.search, query, None)
            web_future = executor.submit(web_searcher.search, query, None, None)
            
            rag_result = rag_future.result()
            web_result = web_future.result()
        
        quality = evaluator.evaluate(rag_result, query)
        
        print(f"\n[RAG検索結果]")
        print(f"  チャンク数: {len(rag_result['chunks'])}")
        print(f"  品質スコア: {quality['score']:.3f}")
        print(f"  処理時間: {rag_result['elapsed_time']:.3f}秒")
        
        print(f"\n[Web検索結果]")
        print(f"  結果数: {web_result['count']}")
        print(f"  処理時間: {web_result['elapsed_time']:.3f}秒")
        
        if web_result['count'] > 0:
            prompt = f"""以下の情報を参考に、質問に答えてください。

質問: {query}

RAG情報:
{rag_result['context']}

Web検索結果:
{web_result['context']}

回答:"""
            
            response = query_ollama(
                prompt, args.ollama_model, args.endpoint,
                temperature=profile['temperature'],
                top_p=profile['top_p'],
                num_predict=profile['num_predict'],
                timer=timer
            )
            
            print(f"\n[回答（Hybrid）]")
            print(response)
        else:
            print("\nWeb検索結果が得られませんでした。RAGの情報のみで回答します。")
            
            prompt = f"""以下の情報を参考に、質問に答えてください。

質問: {query}

参考情報:
{rag_result['context']}

回答:"""
            
            response = query_ollama(
                prompt, args.ollama_model, args.endpoint,
                temperature=profile['temperature'],
                top_p=profile['top_p'],
                num_predict=profile['num_predict'],
                timer=timer
            )
            
            print(f"\n[回答（RAGのみ）]")
            print(response)
    
    # タイミングサマリー
    print(timer.get_summary())
    
    # レポート保存
    if args.save_report:
        save_report(query, classification, rag_result if 'rag_result' in locals() else None,
                   web_result if 'web_result' in locals() else None,
                   quality if 'quality' in locals() else None,
                   response if 'response' in locals() else "",
                   timer, args)


def save_report(query, classification, rag_result, web_result, quality, response, timer, args):
    """レポートを保存"""
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"auto_mode_test_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 自動モード選択テスト結果\n\n")
        f.write(f"- 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- モデル: {args.ollama_model}\n")
        f.write(f"- プロファイル: {args.profile}\n\n")
        
        f.write(f"## 質問\n\n{query}\n\n")
        
        f.write(f"## 自動分類結果\n\n")
        f.write(f"- モード: {classification['mode']}\n")
        f.write(f"- クエリタイプ: {classification['query_type']}\n")
        f.write(f"- 品質閾値: {classification['threshold']}\n")
        f.write(f"- 理由: {classification['reason']}\n\n")
        
        if rag_result:
            f.write(f"## RAG検索結果\n\n")
            f.write(f"- チャンク数: {len(rag_result['chunks'])}\n")
            if quality:
                f.write(f"- 品質スコア: {quality['score']:.3f}\n")
            f.write(f"- 処理時間: {rag_result['elapsed_time']:.3f}秒\n\n")
        
        if web_result:
            f.write(f"## Web検索結果\n\n")
            f.write(f"- 結果数: {web_result['count']}\n")
            f.write(f"- 処理時間: {web_result['elapsed_time']:.3f}秒\n\n")
        
        f.write(f"## 回答\n\n{response}\n\n")
        
        f.write(f"## パフォーマンス\n\n")
        metrics = timer.get_metrics()
        if metrics:
            f.write(f"- 合計処理時間: {metrics['total_time']:.3f}秒\n\n")
            f.write("### 詳細\n\n")
            for section in metrics['sections']:
                f.write(f"- {section['name']}: {section['elapsed']:.3f}秒 ({section['percentage']:.1f}%)\n")
    
    print(f"\nレポートを保存しました: {filename}")


if __name__ == "__main__":
    main()

# Made with Bob
