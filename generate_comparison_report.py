#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
4つのモデルの詳細な比較レポートを生成するスクリプト
Markdown形式で視覚的に見やすいレポートを作成
"""

import argparse
import re
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def parse_log_file(log_file):
    """ログファイルから結果を抽出"""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"警告: {log_file} の読み込みに失敗: {e}")
        return None
    
    # スキップされたモデルのチェック
    if "スキップ" in content or "が見つかりませんでした" in content:
        return {
            'skipped': True,
            'model_name': log_file.stem,
            'reason': 'モデルが見つかりません'
        }
    
    result = {
        'skipped': False,
        'model_name': log_file.stem,
        'timings': {},
        'quality_scores': [],
        'modes': defaultdict(dict),
        'total_time': 0,
        'query_count': 0,
        'rag_times': [],
        'web_times': [],
        'llm_times': []
    }
    
    # 合計処理時間を抽出
    total_time_pattern = r'\*\*合計処理時間\*\*:\s*(\d+\.\d+)秒'
    for match in re.finditer(total_time_pattern, content):
        time_sec = float(match.group(1))
        result['total_time'] += time_sec
        result['query_count'] += 1
    
    # RAG検索時間を抽出（RAG検索結果セクションのみ）
    rag_sections = re.findall(r'#### RAG検索結果.*?- 処理時間:\s*(\d+\.\d+)秒', content, re.DOTALL)
    for time_str in rag_sections:
        result['rag_times'].append(float(time_str))
    
    # Web検索時間を抽出（Web検索結果セクションのみ）
    web_sections = re.findall(r'#### Web検索結果.*?- 処理時間:\s*(\d+\.\d+)秒', content, re.DOTALL)
    for time_str in web_sections:
        result['web_times'].append(float(time_str))
    
    # API呼び出し時間（LLM生成）を抽出
    api_pattern = r'- \*\*API呼び出し\*\*:\s*(\d+\.\d+)秒'
    for match in re.finditer(api_pattern, content):
        time_sec = float(match.group(1))
        result['llm_times'].append(time_sec)
    
    # 品質スコアを抽出
    quality_pattern = r'品質スコア:\s*(\d+\.\d+)'
    for match in re.finditer(quality_pattern, content):
        score = float(match.group(1))
        result['quality_scores'].append(score)
    
    # モード別の情報を抽出
    mode_counts = {
        'selection': len(re.findall(r'\*\*モード:\*\* selection', content)),
        'fallback': len(re.findall(r'\*\*モード:\*\* fallback', content)),
        'hybrid': len(re.findall(r'\*\*モード:\*\* hybrid', content)),
        'comparison': len(re.findall(r'\*\*モード:\*\* comparison', content))
    }
    
    for mode_key, count in mode_counts.items():
        result['modes'][mode_key]['executed'] = count > 0
        result['modes'][mode_key]['query_count'] = count
    
    return result


def generate_markdown_report(results, output_file):
    """Markdown形式の詳細レポートを生成"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # ヘッダー
        f.write("# Brave Search API - 4モデル比較レポート\n\n")
        f.write(f"**生成日時:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # 目次
        f.write("## 📋 目次\n\n")
        f.write("1. [概要](#概要)\n")
        f.write("2. [基本統計](#基本統計)\n")
        f.write("3. [性能ランキング](#性能ランキング)\n")
        f.write("4. [詳細比較](#詳細比較)\n")
        f.write("5. [推奨モデル](#推奨モデル)\n")
        f.write("6. [結論](#結論)\n\n")
        f.write("---\n\n")
        
        # 概要
        f.write("## 概要\n\n")
        completed = len([r for r in results.values() if not r.get('skipped')])
        skipped = len([r for r in results.values() if r.get('skipped')])
        f.write(f"- **テスト対象モデル:** {len(results)}個\n")
        f.write(f"- **完了:** {completed}個 ✅\n")
        f.write(f"- **スキップ:** {skipped}個 ⏭️\n\n")
        
        # 基本統計
        f.write("## 基本統計\n\n")
        f.write("| モデル | 状態 | 合計時間 | クエリ数 | 平均品質 |\n")
        f.write("|--------|------|----------|----------|----------|\n")
        
        for model_name, data in sorted(results.items()):
            if data.get('skipped'):
                f.write(f"| {model_name} | ⏭️ スキップ | - | - | - |\n")
            else:
                avg_quality = f"{sum(data['quality_scores']) / len(data['quality_scores']):.3f}" if data['quality_scores'] else "-"
                f.write(f"| {model_name} | ✅ 完了 | {data['total_time']:.2f}秒 | {data['query_count']}件 | {avg_quality} |\n")
        
        f.write("\n")
        
        # モード別実行状況
        f.write("### モード別実行状況\n\n")
        f.write("| モデル | Selection | Fallback | Hybrid | Comparison |\n")
        f.write("|--------|-----------|----------|--------|------------|\n")
        
        for model_name, data in sorted(results.items()):
            if data.get('skipped'):
                f.write(f"| {model_name} | ⏭️ | ⏭️ | ⏭️ | ⏭️ |\n")
            else:
                selection = "✅" if data['modes']['selection']['executed'] else "❌"
                fallback = "✅" if data['modes']['fallback']['executed'] else "❌"
                hybrid = "✅" if data['modes']['hybrid']['executed'] else "❌"
                comparison = "✅" if data['modes']['comparison']['executed'] else "❌"
                f.write(f"| {model_name} | {selection} | {fallback} | {hybrid} | {comparison} |\n")
        
        f.write("\n---\n\n")
        
        # 性能ランキング
        f.write("## 性能ランキング\n\n")
        
        completed_models = {k: v for k, v in results.items() if not v.get('skipped')}
        
        if completed_models:
            # 処理時間ランキング
            f.write("### 🚀 処理時間ランキング（速い順）\n\n")
            time_ranking = sorted(completed_models.items(), key=lambda x: x[1]['total_time'])
            for i, (model_name, data) in enumerate(time_ranking, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                f.write(f"{medal} **{model_name}** - {data['total_time']:.2f}秒\n")
            f.write("\n")
            
            # 品質スコアランキング
            f.write("### 🏆 品質スコアランキング（高い順）\n\n")
            quality_ranking = sorted(
                [(k, v, sum(v['quality_scores']) / len(v['quality_scores']) if v['quality_scores'] else 0) 
                 for k, v in completed_models.items()],
                key=lambda x: x[2],
                reverse=True
            )
            for i, (model_name, data, avg_quality) in enumerate(quality_ranking, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                f.write(f"{medal} **{model_name}** - {avg_quality:.3f}\n")
            f.write("\n")
            
            # バランス型ランキング
            f.write("### ⚖️ バランス型ランキング（品質/時間比率）\n\n")
            balance_ranking = []
            for model_name, data in completed_models.items():
                if data['quality_scores'] and data['total_time'] > 0:
                    avg_quality = sum(data['quality_scores']) / len(data['quality_scores'])
                    balance_score = avg_quality / data['total_time']
                    balance_ranking.append((model_name, data, balance_score))
            
            balance_ranking.sort(key=lambda x: x[2], reverse=True)
            for i, (model_name, data, balance_score) in enumerate(balance_ranking, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                f.write(f"{medal} **{model_name}** - {balance_score:.5f} (品質/秒)\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        # 詳細比較
        f.write("## 詳細比較\n\n")
        
        for model_name, data in sorted(completed_models.items()):
            f.write(f"### {model_name}\n\n")
            
            # 基本情報
            f.write("**基本情報:**\n")
            f.write(f"- 合計処理時間: {data['total_time']:.2f}秒\n")
            f.write(f"- クエリ数: {data['query_count']}件\n")
            if data['quality_scores']:
                avg_quality = sum(data['quality_scores']) / len(data['quality_scores'])
                f.write(f"- 平均品質スコア: {avg_quality:.3f}\n")
            f.write("\n")
            
            # 処理時間の内訳
            if data['rag_times'] or data['web_times'] or data['llm_times']:
                f.write("**処理時間の内訳:**\n")
                if data['rag_times']:
                    avg_rag = sum(data['rag_times']) / len(data['rag_times'])
                    f.write(f"- RAG検索: 平均 {avg_rag:.2f}秒 ({len(data['rag_times'])}回)\n")
                if data['web_times']:
                    avg_web = sum(data['web_times']) / len(data['web_times'])
                    f.write(f"- Web検索: 平均 {avg_web:.2f}秒 ({len(data['web_times'])}回)\n")
                if data['llm_times']:
                    avg_llm = sum(data['llm_times']) / len(data['llm_times'])
                    f.write(f"- LLM生成: 平均 {avg_llm:.2f}秒 ({len(data['llm_times'])}回)\n")
                f.write("\n")
            
            f.write("---\n\n")
        
        # 推奨モデル
        f.write("## 推奨モデル\n\n")
        
        if completed_models:
            # 最速モデル
            fastest = min(completed_models.items(), key=lambda x: x[1]['total_time'])
            f.write(f"### 🚀 最速モデル: **{fastest[0]}**\n\n")
            f.write(f"- **処理時間:** {fastest[1]['total_time']:.2f}秒\n")
            f.write(f"- **推奨用途:** リアルタイム応答が必要な場合、インタラクティブなアプリケーション\n\n")
            
            # 最高品質モデル
            quality_models = [(k, v, sum(v['quality_scores']) / len(v['quality_scores']) if v['quality_scores'] else 0) 
                              for k, v in completed_models.items()]
            best_quality = max(quality_models, key=lambda x: x[2])
            f.write(f"### 🏆 最高品質モデル: **{best_quality[0]}**\n\n")
            f.write(f"- **平均品質スコア:** {best_quality[2]:.3f}\n")
            f.write(f"- **推奨用途:** 品質が最優先の場合、詳細な分析が必要な場合\n\n")
            
            # バランス型モデル
            balance_models = []
            for model_name, data in completed_models.items():
                if data['quality_scores'] and data['total_time'] > 0:
                    avg_quality = sum(data['quality_scores']) / len(data['quality_scores'])
                    balance_score = avg_quality / data['total_time']
                    balance_models.append((model_name, data, balance_score, avg_quality))
            
            if balance_models:
                best_balance = max(balance_models, key=lambda x: x[2])
                f.write(f"### ⚖️ バランス型モデル: **{best_balance[0]}**\n\n")
                f.write(f"- **バランススコア:** {best_balance[2]:.5f} (品質/秒)\n")
                f.write(f"- **平均品質:** {best_balance[3]:.3f}\n")
                f.write(f"- **処理時間:** {best_balance[1]['total_time']:.2f}秒\n")
                f.write(f"- **推奨用途:** 品質と速度のバランスが重要な場合、一般的な用途\n\n")
        
        f.write("---\n\n")
        
        # 結論
        f.write("## 結論\n\n")
        f.write("このレポートは、Brave Search APIを使用した4つのLLMモデルの性能比較結果をまとめたものです。\n\n")
        f.write("**主な発見:**\n\n")
        
        if completed_models:
            fastest = min(completed_models.items(), key=lambda x: x[1]['total_time'])
            quality_models = [(k, v, sum(v['quality_scores']) / len(v['quality_scores']) if v['quality_scores'] else 0) 
                              for k, v in completed_models.items()]
            best_quality = max(quality_models, key=lambda x: x[2])
            
            f.write(f"1. **最速:** {fastest[0]} ({fastest[1]['total_time']:.2f}秒)\n")
            f.write(f"2. **最高品質:** {best_quality[0]} (スコア: {best_quality[2]:.3f})\n")
            f.write(f"3. **テスト完了率:** {completed}/{len(results)} ({completed/len(results)*100:.1f}%)\n\n")
        
        f.write("**次のステップ:**\n\n")
        f.write("- 推奨モデルを本番環境でテスト\n")
        f.write("- ユースケースに応じたモデル選択\n")
        f.write("- パラメータの最適化\n\n")
        
        f.write("---\n\n")
        f.write(f"*レポート生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
    
    print(f"✅ Markdownレポート生成完了: {output_file}")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="4モデルの詳細な比較レポートを生成")
    parser.add_argument("log_dir", help="ログディレクトリ")
    parser.add_argument("--output", "-o", default=None, help="出力ファイル名（デフォルト: comparison_report.md）")
    parser.add_argument("--json", help="JSON出力ファイル名（オプション）")
    args = parser.parse_args()
    
    log_dir = Path(args.log_dir)
    
    if not log_dir.exists():
        print(f"❌ エラー: ディレクトリが見つかりません: {log_dir}")
        return 1
    
    print(f"\n📂 ログディレクトリ: {log_dir}")
    print(f"📅 分析日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ログファイルを解析
    results = {}
    for log_file in sorted(log_dir.glob('*.md')):
        print(f"📝 解析中: {log_file.name}")
        result = parse_log_file(log_file)
        if result:
            results[result['model_name']] = result
    
    if not results:
        print("\n❌ 解析可能なログファイルが見つかりませんでした。")
        return 1
    
    print(f"\n✅ {len(results)}個のログファイルを解析しました。\n")
    
    # Markdownレポートを生成
    output_file = args.output if args.output else log_dir / "comparison_report.md"
    generate_markdown_report(results, output_file)
    
    # JSON出力
    if args.json:
        summary = {
            'timestamp': datetime.now().isoformat(),
            'models': results,
            'statistics': {
                'total_models': len(results),
                'completed_models': len([r for r in results.values() if not r.get('skipped')]),
                'skipped_models': len([r for r in results.values() if r.get('skipped')])
            }
        }
        
        with open(args.json, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"✅ JSON サマリー保存: {args.json}")
    
    print("\n🎉 レポート生成完了！\n")
    
    return 0


if __name__ == "__main__":
    exit(main())

# Made with Bob
