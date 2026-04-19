#!/bin/bash
# 最適化パラメータでの4つのモード検証スクリプト
# granite3.3:2b vs gemma3:270M 比較用

set -e

# 引数チェック
if [ $# -lt 1 ]; then
    echo "使用方法: $0 <model_name> [log_dir]"
    echo "例: $0 granite3.3:2b"
    echo "例: $0 gemma3:270M reports/brave_four_models_20260417_153000"
    exit 1
fi

# モデル設定
MODEL=$1
LOG_DIR=${2:-"reports"}  # 第2引数がなければreportsディレクトリを使用
QUALITY_THRESHOLD=0.9
DEBUG_MODE="--debug"

# 最適化パラメータ
NUM_PREDICT=512
MAX_CONTEXT_CHARS=1500
TEMPERATURE=0.3

# ログファイル名
MODEL_SAFE=$(echo ${MODEL} | tr ':' '_' | tr '.' '_')
LOG_FILE="${LOG_DIR}/${MODEL_SAFE}.md"

echo "=========================================="
echo "4つのモード検証テスト（最適化版）"
echo "=========================================="
echo ""
echo "実行日時: $(date '+%Y-%m-%d %H:%M:%S')"
echo "モデル: ${MODEL}"
echo "ログファイル: ${LOG_FILE}"
echo ""
echo "最適化パラメータ:"
echo "  - 品質閾値: ${QUALITY_THRESHOLD}"
echo "  - 最大トークン数: ${NUM_PREDICT} (以前: 1024)"
echo "  - 最大コンテキスト: ${MAX_CONTEXT_CHARS}文字 (以前: 3000)"
echo "  - Temperature: ${TEMPERATURE} (以前: 0.7)"
echo "  - タイミングログ: 有効"
echo ""

# 依存パッケージのチェック
echo "依存パッケージをチェック中..."
python3 -c "import sentence_transformers" 2>/dev/null || {
    echo "エラー: sentence-transformers がインストールされていません"
    echo "インストール: pip install sentence-transformers"
    exit 1
}

python3 -c "import hnswlib" 2>/dev/null || {
    echo "エラー: hnswlib がインストールされていません"
    echo "インストール: pip install hnswlib"
    exit 1
}

python3 -c "import duckduckgo_search" 2>/dev/null || python3 -c "import ddgs" 2>/dev/null || {
    echo "警告: ddgs (旧: duckduckgo-search) がインストールされていません"
    echo "Web検索機能を使用するには: pip install ddgs"
    echo ""
}

echo "✅ 依存パッケージOK"
echo ""

# Ollamaサービスのチェック
echo "Ollamaサービスをチェック中..."
if ! command -v ollama &> /dev/null; then
    echo "エラー: Ollama がインストールされていません"
    echo "https://ollama.ai/download からインストールしてください"
    exit 1
fi

if ! ollama list &> /dev/null; then
    echo "エラー: Ollamaサービスが起動していません"
    echo "起動: ollama serve"
    exit 1
fi

# モデルの存在確認
if ! ollama list | grep -q "${MODEL}"; then
    echo "エラー: ${MODEL} モデルが見つかりません"
    echo "次のコマンドでモデルを取得してください："
    echo "  ollama pull ${MODEL}"
    exit 1
fi

echo "✅ OllamaサービスOK"
echo "✅ ${MODEL} モデルOK"
echo ""

# レポートディレクトリの作成
mkdir -p reports

echo "=========================================="
echo "Phase 1: 選択モード（RAGのみ）"
echo "=========================================="
echo ""

# 1-1. CPU仕様
echo "1-1. CPU仕様"
echo "質問: Raspberry Pi 5のCPU仕様は？"
python3 rag_web_four_modes_with_timing.py \
  --mode selection \
  --search_type rag \
  --query "Raspberry Pi 5のCPU仕様は？" \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

# 1-2. 最新ニュース（Webのみ）
echo "1-2. 最新ニュース"
echo "質問: Raspberry Pi 5の最新ニュースは？"
python3 rag_web_four_modes_with_timing.py \
  --mode selection \
  --search_type web \
  --query "Raspberry Pi 5の最新ニュースは？" \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

echo "=========================================="
echo "Phase 2: フォールバックモード"
echo "=========================================="
echo ""

# 2-1. Docker使用方法
echo "2-1. Docker使用方法"
echo "質問: Raspberry Pi 5でDockerを使用するには？"
python3 rag_web_four_modes_with_timing.py \
  --mode fallback \
  --query "Raspberry Pi 5でDockerを使用するには？" \
  --quality_threshold ${QUALITY_THRESHOLD} \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

# 2-2. GPU性能
echo "2-2. GPU性能"
echo "質問: Raspberry Pi 5のGPU性能は？"
python3 rag_web_four_modes_with_timing.py \
  --mode fallback \
  --query "Raspberry Pi 5のGPU性能は？" \
  --quality_threshold ${QUALITY_THRESHOLD} \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

# 2-3. Kubernetes
echo "2-3. Kubernetes"
echo "質問: Raspberry Pi 5でKubernetesを動かすには？"
python3 rag_web_four_modes_with_timing.py \
  --mode fallback \
  --query "Raspberry Pi 5でKubernetesを動かすには？" \
  --quality_threshold ${QUALITY_THRESHOLD} \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

# 2-4. 消費電力
echo "2-4. 消費電力"
echo "質問: Raspberry Pi 5の消費電力は？"
python3 rag_web_four_modes_with_timing.py \
  --mode fallback \
  --query "Raspberry Pi 5の消費電力は？" \
  --quality_threshold ${QUALITY_THRESHOLD} \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

echo "=========================================="
echo "Phase 3: ハイブリッドモード"
echo "=========================================="
echo ""

# 3-1. OpenVPN構築
echo "3-1. OpenVPN構築"
echo "質問: Raspberry Pi 5でOpenVPNサーバーを構築するには？"
python3 rag_web_four_modes_with_timing.py \
  --mode hybrid \
  --query "Raspberry Pi 5でOpenVPNサーバーを構築するには？" \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

# 3-2. ホームサーバー構築
echo "3-2. ホームサーバー構築"
echo "質問: Raspberry Pi 5でホームサーバーを構築するには？"
python3 rag_web_four_modes_with_timing.py \
  --mode hybrid \
  --query "Raspberry Pi 5でホームサーバーを構築するには？" \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

echo "=========================================="
echo "Phase 4: 比較モード"
echo "=========================================="
echo ""

# 4-1. オーバークロック性能
echo "4-1. オーバークロック性能"
echo "質問: Raspberry Pi 5のオーバークロック性能は？"
python3 rag_web_four_modes_with_timing.py \
  --mode comparison \
  --query "Raspberry Pi 5のオーバークロック性能は？" \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

# 4-2. メモリ性能
echo "4-2. メモリ性能"
echo "質問: Raspberry Pi 5のメモリ性能は？"
python3 rag_web_four_modes_with_timing.py \
  --mode comparison \
  --query "Raspberry Pi 5のメモリ性能は？" \
  --ollama_model ${MODEL} \
  --num_predict ${NUM_PREDICT} \
  --max_context_chars ${MAX_CONTEXT_CHARS} \
  --temperature ${TEMPERATURE} \
  --log_file ${LOG_FILE} \
  --save_report \
  ${DEBUG_MODE}

echo ""
echo "---"
echo ""

echo "=========================================="
echo "全テスト完了！"
echo "=========================================="
echo ""
echo "ログファイル: ${LOG_FILE}"
echo ""
echo "次のステップ:"
echo "1. ログファイルを確認"
echo "   cat ${LOG_FILE}"
echo ""
echo "2. 他のモデルと比較"
if [ "${MODEL}" = "granite3.3:2b" ]; then
    echo "   ./run_four_modes_test_optimized.sh gemma3:270M"
else
    echo "   ./run_four_modes_test_optimized.sh granite3.3:2b"
fi
echo ""
echo "3. 最適化効果を評価"
echo "   - 処理時間の短縮"
echo "   - 回答品質の維持/向上"
echo "   - 無限ループの解消（gemma3:270M）"
echo ""