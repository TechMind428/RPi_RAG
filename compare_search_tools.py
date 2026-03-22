#!/usr/bin/env python3
"""
4つの検索ツール比較スクリプト
DuckDuckGo, Tavily, Brave, SerpAPI を統一的に比較

使い方:
  1. インタラクティブモード:
     python compare_search_tools.py

  2. シングルクエリ:
     python compare_search_tools.py "検索クエリ"

  3. バッチモード:
     python compare_search_tools.py --batch queries.txt

  4. 特定ツールのみ:
     python compare_search_tools.py "検索クエリ" --tools duckduckgo,brave

環境変数:
  TAVILY_API_KEY  - Tavily APIキー
  BRAVE_API_KEY   - Brave Search APIキー
  SERPAPI_KEY     - SerpAPI キー
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# .envファイルのサポート（オプション）
try:
    from dotenv import load_dotenv
    load_dotenv()  # .envファイルから環境変数を読み込み
except ImportError:
    pass  # python-dotenvがインストールされていない場合はスキップ

# 新しいパッケージ名（ddgs）を優先、古いパッケージ名（duckduckgo_search）にフォールバック
try:
    from ddgs import DDGS
except ImportError:
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("⚠️  警告: ddgs がインストールされていません")
        print("インストール: pip install ddgs")
        print("（旧パッケージ名: pip install duckduckgo-search）")
        DDGS = None


# ============================================================================
# 定数
# ============================================================================

# 検索結果のdescriptionの長さ制限
MAX_DESCRIPTION_LENGTH = 500  # 最大文字数（複雑な質問に対応）
MIN_DESCRIPTION_LENGTH = 100  # 最小文字数（情報不足を防ぐ）


# ============================================================================
# データクラス
# ============================================================================

@dataclass
class SearchResult:
    """検索結果の統一データ構造"""
    title: str
    url: str
    description: str
    source: str
    timestamp: str
    response_time: float
    extra_data: Optional[Dict[str, Any]] = None

    def to_dict(self):
        """辞書形式に変換"""
        result = asdict(self)
        # extra_dataがNoneの場合は空の辞書に変換
        if result['extra_data'] is None:
            result['extra_data'] = {}
        return result


@dataclass
class EvaluationScore:
    """自動評価スコア"""
    response_time_score: int
    result_count_score: int
    success_score: int
    url_uniqueness_score: int
    title_quality_score: int
    total_score: float

    def to_dict(self):
        """辞書形式に変換"""
        return asdict(self)


@dataclass
class ManualEvaluation:
    """手動評価"""
    relevance: int  # 1-5
    quality: int    # 1-5
    freshness: int  # 1-5
    japanese_quality: int  # 1-5
    overall: int    # 1-5
    comment: str = ""

    def to_dict(self):
        """辞書形式に変換"""
        return asdict(self)


# ============================================================================
# 検索エンジンクラス
# ============================================================================

class SearchEngine(ABC):
    """検索エンジンの抽象基底クラス"""
    
    def __init__(self, name: str, timeout: int = 30):
        self.name = name
        self.timeout = timeout
    
    @abstractmethod
    def search(self, query: str, max_results: int = 5) -> tuple[List[SearchResult], float, Optional[str]]:
        """
        検索を実行
        
        Returns:
            tuple: (検索結果リスト, 応答時間, エラーメッセージ)
        """
        pass
    
    def _format_result(self, title: str, url: str, description: str,
                      response_time: float, extra_data: Optional[Dict] = None) -> SearchResult:
        """検索結果を統一フォーマットに変換"""
        
        # descriptionの長さを制限
        if len(description) > MAX_DESCRIPTION_LENGTH:
            description = description[:MAX_DESCRIPTION_LENGTH] + "..."
        
        # 短すぎる場合は警告（デバッグ用）
        if len(description) < MIN_DESCRIPTION_LENGTH:
            # 注: 短い場合でもそのまま使用（タイトルなどで補完しない）
            pass
        
        return SearchResult(
            title=title,
            url=url,
            description=description,
            source=self.name,
            timestamp=datetime.now().isoformat(),
            response_time=response_time,
            extra_data=extra_data
        )


class DuckDuckGoSearch(SearchEngine):
    """DuckDuckGo検索"""
    
    def __init__(self, timeout: int = 30):
        super().__init__("duckduckgo", timeout)
    
    def search(self, query: str, max_results: int = 5) -> tuple[List[SearchResult], float, Optional[str]]:
        """DuckDuckGo検索を実行"""
        if DDGS is None:
            return [], 0.0, "ddgs がインストールされていません（pip install ddgs）"
        
        try:
            start_time = datetime.now()
            
            with DDGS() as ddgs:
                raw_results = list(ddgs.text(
                    query,
                    max_results=max_results,
                    region='jp-jp',
                    safesearch='off',
                    timelimit=None
                ))
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            results = []
            for item in raw_results:
                result = self._format_result(
                    title=item.get('title', 'N/A'),
                    url=item.get('href', 'N/A'),
                    description=item.get('body', 'N/A'),
                    response_time=elapsed,
                    extra_data=None
                )
                results.append(result)
            
            return results, elapsed, None
            
        except Exception as e:
            return [], 0.0, str(e)


class TavilySearch(SearchEngine):
    """Tavily検索"""
    
    def __init__(self, timeout: int = 30):
        super().__init__("tavily", timeout)
        self.api_key = os.getenv("TAVILY_API_KEY")
    
    def search(self, query: str, max_results: int = 5) -> tuple[List[SearchResult], float, Optional[str]]:
        """Tavily検索を実行"""
        if not self.api_key:
            return [], 0.0, "TAVILY_API_KEY 環境変数が設定されていません"
        
        try:
            start_time = datetime.now()
            
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.api_key,
                    "query": query,
                    "max_results": max_results,
                    "include_answer": True,
                    "search_depth": "basic",
                    "include_domains": [".jp"],
                    "exclude_domains": [".cn", ".tw"]
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            results = []
            ai_answer = data.get('answer', '')
            
            for item in data.get('results', []):
                extra_data = {'ai_answer': ai_answer} if ai_answer else None
                result = self._format_result(
                    title=item.get('title', 'N/A'),
                    url=item.get('url', 'N/A'),
                    description=item.get('content', 'N/A'),
                    response_time=elapsed,
                    extra_data=extra_data
                )
                results.append(result)
            
            return results, elapsed, None
            
        except requests.exceptions.Timeout:
            return [], 0.0, f"タイムアウト（{self.timeout}秒）"
        except requests.exceptions.HTTPError as e:
            return [], 0.0, f"HTTPエラー: {e}"
        except Exception as e:
            return [], 0.0, str(e)


class BraveSearch(SearchEngine):
    """Brave検索"""
    
    def __init__(self, timeout: int = 30):
        super().__init__("brave", timeout)
        self.api_key = os.getenv("BRAVE_API_KEY")
    
    def search(self, query: str, max_results: int = 5) -> tuple[List[SearchResult], float, Optional[str]]:
        """Brave検索を実行"""
        if not self.api_key:
            return [], 0.0, "BRAVE_API_KEY 環境変数が設定されていません"
        
        try:
            start_time = datetime.now()
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "X-Subscription-Token": self.api_key
            }
            
            params = {
                "q": query,
                "count": max_results,
                "country": "JP",
                "search_lang": "jp",
                "ui_lang": "ja-JP"
            }
            
            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers=headers,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            results = []
            for item in data.get('web', {}).get('results', []):
                extra_data = {}
                if 'age' in item:
                    extra_data['age'] = item['age']
                if 'language' in item:
                    extra_data['language'] = item['language']
                
                result = self._format_result(
                    title=item.get('title', 'N/A'),
                    url=item.get('url', 'N/A'),
                    description=item.get('description', 'N/A'),
                    response_time=elapsed,
                    extra_data=extra_data if extra_data else None
                )
                results.append(result)
            
            return results, elapsed, None
            
        except requests.exceptions.Timeout:
            return [], 0.0, f"タイムアウト（{self.timeout}秒）"
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTPエラー: {e}"
            if hasattr(e, 'response') and e.response is not None:
                if e.response.status_code == 401:
                    error_msg = "APIキーが無効です"
                elif e.response.status_code == 429:
                    error_msg = "レート制限に達しました"
            return [], 0.0, error_msg
        except Exception as e:
            return [], 0.0, str(e)


class SerpAPISearch(SearchEngine):
    """SerpAPI検索"""
    
    def __init__(self, timeout: int = 30):
        super().__init__("serpapi", timeout)
        self.api_key = os.getenv("SERPAPI_KEY")
    
    def search(self, query: str, max_results: int = 5) -> tuple[List[SearchResult], float, Optional[str]]:
        """SerpAPI検索を実行"""
        if not self.api_key:
            return [], 0.0, "SERPAPI_KEY 環境変数が設定されていません"
        
        try:
            start_time = datetime.now()
            
            params = {
                "q": query,
                "api_key": self.api_key,
                "num": max_results,
                "hl": "ja",
                "gl": "jp"
            }
            
            response = requests.get(
                "https://serpapi.com/search",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            results = []
            for item in data.get('organic_results', [])[:max_results]:
                extra_data = None
                if 'position' in item:
                    extra_data = {'position': item['position']}
                
                result = self._format_result(
                    title=item.get('title', 'N/A'),
                    url=item.get('link', 'N/A'),
                    description=item.get('snippet', 'N/A'),
                    response_time=elapsed,
                    extra_data=extra_data
                )
                results.append(result)
            
            return results, elapsed, None
            
        except requests.exceptions.Timeout:
            return [], 0.0, f"タイムアウト（{self.timeout}秒）"
        except requests.exceptions.HTTPError as e:
            return [], 0.0, f"HTTPエラー: {e}"
        except Exception as e:
            return [], 0.0, str(e)


# ============================================================================
# 評価クラス
# ============================================================================

class AutoEvaluator:
    """自動評価"""
    
    def evaluate(self, tool_name: str, results: List[SearchResult], 
                 response_time: float, success: bool, 
                 all_results: Dict[str, List[SearchResult]]) -> EvaluationScore:
        """自動評価を実行"""
        
        # 応答時間スコア (0-100)
        if response_time <= 0.5:
            time_score = 100
        elif response_time <= 1.0:
            time_score = 80
        elif response_time <= 2.0:
            time_score = 60
        else:
            time_score = max(40, int(100 - (response_time - 2.0) * 10))
        
        # 結果数スコア (0-100)
        result_count = len(results)
        if result_count >= 10:
            count_score = 100
        elif result_count >= 5:
            count_score = 80
        elif result_count >= 3:
            count_score = 60
        else:
            count_score = max(40, result_count * 20)
        
        # 成功スコア (0-100)
        success_score = 100 if success else 0
        
        # URL独自性スコア (0-100)
        uniqueness_score = self._calculate_url_uniqueness(tool_name, results, all_results)
        
        # タイトル品質スコア (0-100)
        quality_score = self._calculate_title_quality(results)
        
        # 総合スコア（加重平均）
        total = (
            time_score * 0.25 +
            count_score * 0.20 +
            success_score * 0.25 +
            uniqueness_score * 0.15 +
            quality_score * 0.15
        )
        
        return EvaluationScore(
            response_time_score=time_score,
            result_count_score=count_score,
            success_score=success_score,
            url_uniqueness_score=uniqueness_score,
            title_quality_score=quality_score,
            total_score=round(total, 1)
        )
    
    def _calculate_url_uniqueness(self, tool_name: str, results: List[SearchResult],
                                  all_results: Dict[str, List[SearchResult]]) -> int:
        """URL独自性を計算"""
        if not results:
            return 0
        
        my_urls = set(r.url for r in results)
        other_urls = set()
        
        for name, other_results in all_results.items():
            if name != tool_name:
                other_urls.update(r.url for r in other_results)
        
        if not my_urls:
            return 0
        
        unique_count = len(my_urls - other_urls)
        uniqueness_ratio = unique_count / len(my_urls)
        
        return int(uniqueness_ratio * 100)
    
    def _calculate_title_quality(self, results: List[SearchResult]) -> int:
        """タイトル品質を計算"""
        if not results:
            return 0
        
        scores = []
        for result in results:
            title_len = len(result.title)
            if 20 <= title_len <= 100:
                scores.append(100)
            elif 10 <= title_len < 20 or 100 < title_len <= 150:
                scores.append(80)
            elif title_len < 10 or title_len > 150:
                scores.append(60)
            else:
                scores.append(40)
        
        return int(sum(scores) / len(scores)) if scores else 0


class ManualEvaluator:
    """手動評価（対話式）"""
    
    def evaluate(self, tool_name: str, results: List[SearchResult]) -> Optional[ManualEvaluation]:
        """手動評価を実行"""
        if not results:
            print(f"\n{tool_name}: 結果がないため評価をスキップします")
            return None
        
        print(f"\n{'='*70}")
        print(f"【{tool_name}】の手動評価")
        print(f"{'='*70}")
        
        # 結果を表示
        for i, result in enumerate(results[:3], 1):  # 最初の3件のみ表示
            print(f"\n[{i}] {result.title}")
            print(f"    URL: {result.url}")
            print(f"    概要: {result.description[:100]}...")
        
        print(f"\n以下の項目を1-5で評価してください（1=最低、5=最高）:")
        
        try:
            relevance = self._get_score("関連性（検索クエリとの関連度）")
            quality = self._get_score("情報の質（有用性）")
            freshness = self._get_score("鮮度（情報の新しさ）")
            japanese_quality = self._get_score("日本語品質（自然さ）")
            overall = self._get_score("総合評価")
            
            comment = input("\nコメント（任意、Enterでスキップ）: ").strip()
            
            return ManualEvaluation(
                relevance=relevance,
                quality=quality,
                freshness=freshness,
                japanese_quality=japanese_quality,
                overall=overall,
                comment=comment
            )
            
        except KeyboardInterrupt:
            print("\n\n評価をスキップしました")
            return None
    
    def _get_score(self, prompt: str) -> int:
        """スコア入力を取得"""
        while True:
            try:
                score = input(f"  {prompt} (1-5): ").strip()
                score = int(score)
                if 1 <= score <= 5:
                    return score
                print("    ⚠️  1-5の範囲で入力してください")
            except ValueError:
                print("    ⚠️  数値を入力してください")


# ============================================================================
# ログクラス
# ============================================================================

class Logger:
    """ログ記録"""
    
    def __init__(self, log_dir: str = "./search_logs"):
        self.log_dir = log_dir
        self._ensure_log_dir()
    
    def _ensure_log_dir(self):
        """ログディレクトリを作成"""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def save_json(self, data: dict, filename: Optional[str] = None) -> str:
        """JSON形式で保存"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_{timestamp}.json"
        
        filepath = os.path.join(self.log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def save_markdown(self, data: dict, filename: Optional[str] = None) -> str:
        """Markdown形式で保存"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_{timestamp}.md"
        
        filepath = os.path.join(self.log_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self._format_markdown(data))
        
        return filepath
    
    def _format_markdown(self, data: dict) -> str:
        """Markdown形式にフォーマット"""
        md = []
        
        # ヘッダー
        md.append("# 検索ツール比較レポート\n")
        md.append("## 検索情報\n")
        md.append(f"- **クエリ**: {data['query']}")
        md.append(f"- **実行時刻**: {data['timestamp']}")
        md.append(f"- **使用ツール**: {', '.join(data['config']['tools'])}")
        md.append(f"- **最大結果数**: {data['config']['max_results']}件")
        md.append(f"- **評価モード**: {data['config']['eval_mode']}\n")
        
        # 各ツールの結果
        md.append("## 検索結果\n")
        
        for tool_name, tool_data in data['results'].items():
            md.append(f"### {tool_name.upper()}\n")
            md.append(f"- **応答時間**: {tool_data['response_time']:.2f}秒")
            md.append(f"- **結果数**: {tool_data['result_count']}件")
            md.append(f"- **ステータス**: {'✅ 成功' if tool_data['status'] == 'success' else '❌ 失敗'}")
            
            if tool_data.get('error'):
                md.append(f"- **エラー**: {tool_data['error']}")
            
            # 自動評価
            if 'auto_evaluation' in tool_data:
                eval_data = tool_data['auto_evaluation']
                md.append(f"- **自動評価スコア**: {eval_data['total_score']}/100")
            
            # 手動評価
            if 'manual_evaluation' in tool_data:
                manual = tool_data['manual_evaluation']
                md.append(f"- **手動評価**: 総合 {manual['overall']}/5")
            
            md.append("")
            
            # AI要約（Tavilyの場合）
            if tool_name == 'tavily' and tool_data['results']:
                first_result = tool_data['results'][0]
                if 'extra_data' in first_result and first_result['extra_data'] is not None and 'ai_answer' in first_result['extra_data']:
                    md.append(f"**🤖 AI要約**:\n{first_result['extra_data']['ai_answer']}\n")
            
            # 検索結果
            if tool_data['results']:
                md.append("#### 検索結果\n")
                for i, result in enumerate(tool_data['results'], 1):
                    md.append(f"{i}. **{result['title']}**")
                    md.append(f"   - URL: {result['url']}")
                    # descriptionは既に500文字に制限されているので、そのまま表示
                    md.append(f"   - 概要: {result['description']}")
                    md.append("")
            
            md.append("")
        
        # 比較分析
        if 'comparison' in data:
            md.append("## 比較分析\n")
            comp = data['comparison']
            
            md.append("| 項目 | 結果 |")
            md.append("|------|------|")
            
            if 'fastest' in comp:
                md.append(f"| ⚡ 最速 | {comp['fastest']['tool']} ({comp['fastest']['time']:.2f}秒) |")
            
            if 'slowest' in comp:
                md.append(f"| 🐌 最遅 | {comp['slowest']['tool']} ({comp['slowest']['time']:.2f}秒) |")
            
            if 'most_results' in comp:
                md.append(f"| 📈 最多結果 | {comp['most_results']['tool']} ({comp['most_results']['count']}件) |")
            
            if 'least_results' in comp:
                md.append(f"| 📉 最少結果 | {comp['least_results']['tool']} ({comp['least_results']['count']}件) |")
            
            if 'success_rate' in comp:
                md.append(f"| ✅ 成功率 | {comp['success_count']}/{comp['total_count']} ({comp['success_rate']*100:.0f}%) |")
            
            if 'highest_score' in comp:
                md.append(f"| 🎯 最高評価 | {comp['highest_score']['tool']} ({comp['highest_score']['score']}点) |")
            
            md.append("")
        
        return "\n".join(md)


# ============================================================================
# メインクラス
# ============================================================================

class SearchComparator:
    """検索比較メインクラス"""
    
    def __init__(self, tools: List[str], max_results: int = 5,
                 timeout: int = 30, log_dir: str = "./search_logs"):
        self.max_results = max_results
        self.timeout = timeout
        self.engines = self._init_engines(tools)
        self.auto_evaluator = AutoEvaluator()
        self.manual_evaluator = ManualEvaluator()
        self.logger = Logger(log_dir)
        
        # APIキーの状態をチェック
        self._check_api_keys(tools)
    
    def _init_engines(self, tools: List[str]) -> Dict[str, SearchEngine]:
        """検索エンジンを初期化"""
        engine_map = {
            'duckduckgo': DuckDuckGoSearch,
            'tavily': TavilySearch,
            'brave': BraveSearch,
            'serpapi': SerpAPISearch
        }
        
        engines = {}
        for tool in tools:
            tool = tool.lower().strip()
            if tool in engine_map:
                engines[tool] = engine_map[tool](self.timeout)
        
        return engines
    
    def _check_api_keys(self, tools: List[str]):
        """APIキーの状態をチェックして表示"""
        print(f"\n{'='*80}")
        print("🔑 APIキー設定状況")
        print(f"{'='*80}\n")
        
        api_key_status = {
            'duckduckgo': {
                'required': False,
                'key': None,
                'env_var': None,
                'status': '✅ APIキー不要'
            },
            'tavily': {
                'required': True,
                'key': os.getenv("TAVILY_API_KEY"),
                'env_var': 'TAVILY_API_KEY',
                'status': None
            },
            'brave': {
                'required': True,
                'key': os.getenv("BRAVE_API_KEY"),
                'env_var': 'BRAVE_API_KEY',
                'status': None
            },
            'serpapi': {
                'required': True,
                'key': os.getenv("SERPAPI_KEY"),
                'env_var': 'SERPAPI_KEY',
                'status': None
            }
        }
        
        has_missing_keys = False
        
        for tool in tools:
            tool = tool.lower().strip()
            if tool not in api_key_status:
                continue
            
            info = api_key_status[tool]
            
            if not info['required']:
                # DuckDuckGo
                print(f"  {tool.upper():<12} : {info['status']}")
            else:
                # APIキーが必要なツール
                if info['key']:
                    # APIキーが設定されている
                    masked_key = info['key'][:10] + "..." + info['key'][-4:] if len(info['key']) > 14 else info['key'][:6] + "..."
                    print(f"  {tool.upper():<12} : ✅ 設定済み ({masked_key})")
                else:
                    # APIキーが設定されていない
                    print(f"  {tool.upper():<12} : ⚠️  未設定 (環境変数: {info['env_var']})")
                    has_missing_keys = True
        
        print(f"\n{'='*80}\n")
        
        # 未設定のAPIキーがある場合は警告を表示
        if has_missing_keys:
            print("⚠️  警告: 一部のツールでAPIキーが設定されていません")
            print("\n設定方法:")
            print("  方法1: .envファイルを使用（推奨）")
            print("    1. cp .env.example .env")
            print("    2. .env ファイルを編集してAPIキーを設定")
            print("    3. pip install python-dotenv")
            print("\n  方法2: 環境変数を直接設定")
            
            for tool in tools:
                tool = tool.lower().strip()
                if tool in api_key_status and api_key_status[tool]['required'] and not api_key_status[tool]['key']:
                    print(f"    export {api_key_status[tool]['env_var']}='your-api-key'")
            
            print("\n詳細は SEARCH_TOOLS_COMPARISON_SETUP.md を参照してください")
            print(f"{'='*80}\n")
    
    def _wrap_text(self, text: str, width: int) -> List[str]:
        """テキストを指定幅で折り返す（日本語対応）
        
        Args:
            text: 折り返すテキスト
            width: 最大文字幅（半角文字基準）
        
        Returns:
            折り返されたテキストの行リスト
        """
        if not text:
            return [""]
        
        lines = []
        current_line = ""
        current_width = 0
        
        for char in text:
            # 文字幅を計算
            # 日本語（全角）: 2
            # 英数字（半角）: 1
            # 絵文字など: 2
            if ord(char) > 127:
                # 全角文字
                char_width = 2
            else:
                # 半角文字
                char_width = 1
            
            # 幅を超える場合は改行
            if current_width + char_width > width:
                if current_line:  # 空行を避ける
                    lines.append(current_line)
                current_line = char
                current_width = char_width
            else:
                current_line += char
                current_width += char_width
        
        # 最後の行を追加
        if current_line:
            lines.append(current_line)
        
        return lines if lines else [""]
    
    def compare(self, query: str, eval_mode: str = 'auto',
                save_log: bool = True, log_format: str = 'both') -> dict:
        """検索比較を実行"""
        
        print(f"\n{'='*80}")
        print(f"🔍 検索クエリ: {query}")
        print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # 検索実行
        all_results = {}
        all_times = {}
        all_errors = {}
        
        for i, (tool_name, engine) in enumerate(self.engines.items(), 1):
            print(f"【{i}/{len(self.engines)}】{tool_name.upper()} 検索中...")
            
            results, response_time, error = engine.search(query, self.max_results)
            
            all_results[tool_name] = results
            all_times[tool_name] = response_time
            all_errors[tool_name] = error
            
            if error:
                print(f"❌ 失敗 | エラー: {error}")
            else:
                print(f"✅ 成功 | ⏱️  {response_time:.2f}秒 | 📊 {len(results)}件")
                
                # Tavilyの場合、AI要約を表示
                if tool_name == 'tavily' and results and results[0].extra_data and results[0].extra_data.get('ai_answer'):
                    print(f"🤖 AI要約あり")
            
            print()
        
        # 結果表示
        self._display_results(query, all_results, all_times, all_errors)
        
        # 評価実行
        evaluations = {}
        manual_evaluations = {}
        
        if eval_mode == 'auto':
            print(f"\n{'='*80}")
            print("📊 自動評価を実行中...")
            print(f"{'='*80}\n")
            
            for tool_name, results in all_results.items():
                success = all_errors[tool_name] is None
                eval_score = self.auto_evaluator.evaluate(
                    tool_name, results, all_times[tool_name], success, all_results
                )
                evaluations[tool_name] = eval_score
                print(f"{tool_name.upper()}: {eval_score.total_score}/100")
        
        elif eval_mode == 'manual':
            print(f"\n{'='*80}")
            print("👤 手動評価モード")
            print(f"{'='*80}")
            
            for tool_name, results in all_results.items():
                manual_eval = self.manual_evaluator.evaluate(tool_name, results)
                if manual_eval:
                    manual_evaluations[tool_name] = manual_eval
        
        # 比較分析
        comparison = self._analyze_comparison(all_results, all_times, all_errors, evaluations)
        
        # 比較結果表示
        self._display_comparison(comparison)
        
        # データ構造作成
        data = self._create_data_structure(
            query, all_results, all_times, all_errors, 
            evaluations, manual_evaluations, comparison, eval_mode
        )
        
        # ログ保存
        if save_log:
            self._save_logs(data, log_format)
        
        return data
    
    def _display_results(self, query: str, all_results: Dict, 
                        all_times: Dict, all_errors: Dict):
        """検索結果を表示"""
        print(f"{'='*80}")
        print("📊 検索結果詳細")
        print(f"{'='*80}\n")
        
        for tool_name, results in all_results.items():
            print(f"┌{'─'*78}┐")
            print(f"│ {tool_name.upper():<76} │")
            print(f"├{'─'*78}┤")
            print(f"│ ⏱️  応答時間: {all_times[tool_name]:.2f}秒{' '*60}│")
            print(f"│ 📊 結果数: {len(results)}件{' '*66}│")
            
            if all_errors[tool_name]:
                print(f"│ ❌ ステータス: 失敗{' '*62}│")
                print(f"│ エラー: {all_errors[tool_name]:<68}│")
            else:
                print(f"│ ✅ ステータス: 成功{' '*62}│")
            
            print(f"├{'─'*78}┤")
            
            if results:
                for i, result in enumerate(results[:3], 1):  # 最初の3件のみ表示
                    # タイトルを複数行で表示（切り詰めない）
                    title_lines = self._wrap_text(result.title, 73)
                    for idx, line in enumerate(title_lines):
                        if idx == 0:
                            print(f"│ [{i}] {line:<73}│")
                        else:
                            print(f"│     {line:<73}│")
                    
                    # URLを複数行で表示
                    url_lines = self._wrap_text(result.url, 70)
                    for line in url_lines:
                        print(f"│     🔗 {line:<70}│")
                    
                    # 説明を複数行で表示（切り詰めない）
                    desc_lines = self._wrap_text(result.description, 70)
                    for line in desc_lines:
                        print(f"│     📝 {line:<70}│")
                    
                    # Tavilyの場合、AI要約を表示
                    if tool_name == 'tavily' and i == 1 and result.extra_data and result.extra_data.get('ai_answer'):
                        ai_answer_lines = self._wrap_text(result.extra_data['ai_answer'], 60)
                        for idx, line in enumerate(ai_answer_lines):
                            if idx == 0:
                                print(f"│     🤖 AI要約: {line:<60}│")
                            else:
                                print(f"│            {line:<60}│")
                    
                    if i < min(len(results), 3):
                        print(f"│{' '*78}│")
            else:
                print(f"│ 結果なし{' '*70}│")
            
            print(f"└{'─'*78}┘\n")
    
    def _analyze_comparison(self, all_results: Dict, all_times: Dict, 
                           all_errors: Dict, evaluations: Dict) -> dict:
        """比較分析を実行"""
        comparison = {}
        
        # 最速/最遅
        valid_times = {k: v for k, v in all_times.items() if v > 0}
        if valid_times:
            fastest = min(valid_times.items(), key=lambda x: x[1])
            slowest = max(valid_times.items(), key=lambda x: x[1])
            comparison['fastest'] = {'tool': fastest[0], 'time': fastest[1]}
            comparison['slowest'] = {'tool': slowest[0], 'time': slowest[1]}
        
        # 最多/最少結果
        result_counts = {k: len(v) for k, v in all_results.items()}
        if result_counts:
            most = max(result_counts.items(), key=lambda x: x[1])
            least = min(result_counts.items(), key=lambda x: x[1])
            comparison['most_results'] = {'tool': most[0], 'count': most[1]}
            comparison['least_results'] = {'tool': least[0], 'count': least[1]}
        
        # 成功率
        success_count = sum(1 for error in all_errors.values() if error is None)
        total_count = len(all_errors)
        comparison['success_count'] = success_count
        comparison['total_count'] = total_count
        comparison['success_rate'] = success_count / total_count if total_count > 0 else 0
        
        # 最高評価
        if evaluations:
            highest = max(evaluations.items(), key=lambda x: x[1].total_score)
            comparison['highest_score'] = {
                'tool': highest[0],
                'score': highest[1].total_score
            }
        
        return comparison
    
    def _display_comparison(self, comparison: dict):
        """比較結果を表示"""
        print(f"\n{'='*80}")
        print("📊 比較分析")
        print(f"{'='*80}\n")
        
        if 'fastest' in comparison:
            print(f"⚡ 最速: {comparison['fastest']['tool'].upper()} ({comparison['fastest']['time']:.2f}秒)")
        
        if 'slowest' in comparison:
            print(f"🐌 最遅: {comparison['slowest']['tool'].upper()} ({comparison['slowest']['time']:.2f}秒)")
        
        if 'most_results' in comparison:
            print(f"📈 最多結果: {comparison['most_results']['tool'].upper()} ({comparison['most_results']['count']}件)")
        
        if 'least_results' in comparison:
            print(f"📉 最少結果: {comparison['least_results']['tool'].upper()} ({comparison['least_results']['count']}件)")
        
        if 'success_rate' in comparison:
            print(f"✅ 成功率: {comparison['success_count']}/{comparison['total_count']} ({comparison['success_rate']*100:.0f}%)")
        
        if 'highest_score' in comparison:
            print(f"🎯 最高評価: {comparison['highest_score']['tool'].upper()} ({comparison['highest_score']['score']}点)")
        
        print(f"\n{'='*80}\n")
    
    def _create_data_structure(self, query: str, all_results: Dict, 
                              all_times: Dict, all_errors: Dict,
                              evaluations: Dict, manual_evaluations: Dict,
                              comparison: dict, eval_mode: str) -> dict:
        """データ構造を作成"""
        data = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'config': {
                'tools': list(self.engines.keys()),
                'max_results': self.max_results,
                'timeout': self.timeout,
                'eval_mode': eval_mode
            },
            'results': {},
            'comparison': comparison
        }
        
        for tool_name in self.engines.keys():
            tool_data = {
                'status': 'success' if all_errors[tool_name] is None else 'failed',
                'response_time': all_times[tool_name],
                'result_count': len(all_results[tool_name]),
                'error': all_errors[tool_name],
                'results': [r.to_dict() for r in all_results[tool_name]]
            }
            
            if tool_name in evaluations:
                tool_data['auto_evaluation'] = evaluations[tool_name].to_dict()
            
            if tool_name in manual_evaluations:
                tool_data['manual_evaluation'] = manual_evaluations[tool_name].to_dict()
            
            data['results'][tool_name] = tool_data
        
        return data
    
    def _save_logs(self, data: dict, log_format: str):
        """ログを保存"""
        print("💾 ログ保存中...")
        
        saved_files = []
        errors = []
        
        try:
            if log_format in ['json', 'both']:
                json_path = self.logger.save_json(data)
                saved_files.append(f"JSON: {json_path}")
        except Exception as e:
            errors.append(f"JSON保存エラー: {e}")
        
        try:
            if log_format in ['markdown', 'both']:
                md_path = self.logger.save_markdown(data)
                saved_files.append(f"Markdown: {md_path}")
        except Exception as e:
            errors.append(f"Markdown保存エラー: {e}")
        
        if saved_files:
            print("✅ ログ保存完了:")
            for file in saved_files:
                print(f"   - {file}")
        
        if errors:
            print("⚠️  ログ保存時の警告:")
            for error in errors:
                print(f"   - {error}")
    
    def interactive_mode(self, eval_mode: str = 'auto', 
                        save_log: bool = True, log_format: str = 'both'):
        """インタラクティブモード"""
        print(f"{'='*80}")
        print("🔍 検索ツール比較 - インタラクティブモード")
        print(f"{'='*80}")
        print(f"\n使用ツール: {', '.join(self.engines.keys())}")
        print(f"評価モード: {eval_mode}")
        print("\nコマンド:")
        print("  - 検索クエリを入力して Enter")
        print("  - 'quit', 'exit', 'q' で終了")
        print(f"{'='*80}\n")
        
        while True:
            try:
                # readline を使用して日本語入力を改善
                import sys
                if sys.stdin.isatty():
                    # ターミナルの場合、readlineを使用
                    try:
                        import readline
                        query = input("🔍 検索クエリ > ").strip()
                    except ImportError:
                        # readlineが利用できない場合は通常のinput
                        query = input("🔍 検索クエリ > ").strip()
                else:
                    # パイプやリダイレクトの場合は通常のinput
                    query = input("🔍 検索クエリ > ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 終了します。")
                    break
                
                self.compare(query, eval_mode, save_log, log_format)
                
            except KeyboardInterrupt:
                print("\n\n👋 終了します。")
                break
            except Exception as e:
                print(f"\n❌ エラー: {e}\n")
    
    def batch_mode(self, queries_file: str, eval_mode: str = 'auto',
                   save_log: bool = True, log_format: str = 'both'):
        """バッチモード"""
        print(f"{'='*80}")
        print("📦 バッチモード")
        print(f"{'='*80}\n")
        
        try:
            with open(queries_file, 'r', encoding='utf-8') as f:
                queries = [line.strip() for line in f if line.strip()]
            
            print(f"📄 クエリファイル: {queries_file}")
            print(f"📊 クエリ数: {len(queries)}件\n")
            
            for i, query in enumerate(queries, 1):
                print(f"\n{'='*80}")
                print(f"クエリ {i}/{len(queries)}")
                print(f"{'='*80}")
                
                self.compare(query, eval_mode, save_log, log_format)
                
                if i < len(queries):
                    print("\n⏸️  次のクエリまで3秒待機...")
                    import time
                    time.sleep(3)
            
            print(f"\n{'='*80}")
            print("✅ バッチ処理完了")
            print(f"{'='*80}\n")
            
        except FileNotFoundError:
            print(f"❌ エラー: ファイルが見つかりません: {queries_file}")
        except Exception as e:
            print(f"❌ エラー: {e}")


# ============================================================================
# CLI処理
# ============================================================================

def parse_args():
    """コマンドライン引数を解析"""
    parser = argparse.ArgumentParser(
        description='4つの検索ツール（DuckDuckGo, Tavily, Brave, SerpAPI）を比較',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # インタラクティブモード
  python compare_search_tools.py

  # シングルクエリ
  python compare_search_tools.py "Raspberry Pi 5 ニュース"

  # 手動評価モード
  python compare_search_tools.py "Python チュートリアル" --manual-eval

  # 特定ツールのみ
  python compare_search_tools.py "AI ニュース" --tools duckduckgo,brave

  # バッチモード
  python compare_search_tools.py --batch queries.txt

環境変数:
  TAVILY_API_KEY  - Tavily APIキー
  BRAVE_API_KEY   - Brave Search APIキー
  SERPAPI_KEY     - SerpAPI キー
        """
    )
    
    parser.add_argument(
        'query',
        nargs='?',
        help='検索クエリ（省略時はインタラクティブモード）'
    )
    
    parser.add_argument(
        '--tools',
        default='duckduckgo,tavily,brave,serpapi',
        help='使用するツール（カンマ区切り、デフォルト: すべて）'
    )
    
    parser.add_argument(
        '--max-results',
        type=int,
        default=5,
        help='最大結果数（デフォルト: 5）'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='タイムアウト秒数（デフォルト: 30）'
    )
    
    parser.add_argument(
        '--log-dir',
        default='./search_logs',
        help='ログ保存ディレクトリ（デフォルト: ./search_logs）'
    )
    
    parser.add_argument(
        '--no-log',
        action='store_true',
        help='ログを保存しない'
    )
    
    parser.add_argument(
        '--format',
        choices=['json', 'markdown', 'both'],
        default='both',
        help='ログフォーマット（デフォルト: both）'
    )
    
    parser.add_argument(
        '--manual-eval',
        action='store_true',
        help='手動評価モードを有効化'
    )
    
    parser.add_argument(
        '--no-eval',
        action='store_true',
        help='評価を実行しない（検索結果のみ）'
    )
    
    parser.add_argument(
        '--batch',
        help='バッチモード: クエリファイルを指定'
    )
    
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_args()
    
    # ツールリストを解析
    tools = [t.strip() for t in args.tools.split(',')]
    
    # 評価モードを決定
    if args.no_eval:
        eval_mode = 'none'
    elif args.manual_eval:
        eval_mode = 'manual'
    else:
        eval_mode = 'auto'
    
    # SearchComparatorを初期化
    comparator = SearchComparator(
        tools=tools,
        max_results=args.max_results,
        timeout=args.timeout,
        log_dir=args.log_dir
    )
    
    # モードに応じて実行
    if args.batch:
        # バッチモード
        comparator.batch_mode(
            args.batch,
            eval_mode=eval_mode,
            save_log=not args.no_log,
            log_format=args.format
        )
    elif args.query:
        # シングルクエリモード
        comparator.compare(
            args.query,
            eval_mode=eval_mode,
            save_log=not args.no_log,
            log_format=args.format
        )
    else:
        # インタラクティブモード
        comparator.interactive_mode(
            eval_mode=eval_mode,
            save_log=not args.no_log,
            log_format=args.format
        )


if __name__ == "__main__":
    main()