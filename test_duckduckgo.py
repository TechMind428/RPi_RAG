# test_duckduckgo.py
from ddgs import DDGS
import json

def simple_search(query, max_results=3):
    """シンプルなWeb検索"""
    print(f"検索クエリ: {query}")
    print("-" * 50)
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(
                keywords=query,
                max_results=max_results,
                region='jp-jp'  # 日本語の結果を優先
            ))
        
        print(f"✅ 検索成功: {len(results)}件の結果")
        print()
        
        for i, result in enumerate(results, 1):
            print(f"【結果 {i}】")
            print(f"タイトル: {result.get('title', 'N/A')}")
            print(f"URL: {result.get('href', 'N/A')}")
            print(f"概要: {result.get('body', 'N/A')[:100]}...")
            print()
        
        return results
    
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return []

if __name__ == "__main__":
    # テスト検索
    simple_search("Python プログラミング 入門")
