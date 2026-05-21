#!/bin/bash
# 4つのモデルでの比較テストスクリプト（Brave Search API版）
# Granite3.3:2b, Gemma3:1b, Qwen3:0.6b, Gemma3:270M

set -e

# 仮想環境を有効化
if [ -d "$HOME/venvv" ]; then
    source "$HOME/venvv/bin/activate"
    echo "✅ 仮想環境を有効化しました: $VIRTUAL_ENV"
else
    echo "⚠️  警告: 仮想環境が見つかりません ($HOME/venvv)"
fi

# .envファイルから環境変数を読み込む
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ .envファイルを読み込みました"
else
    echo "⚠️  警告: .envファイルが見つかりません"
fi

# モデルリスト
MODELS=(
    "Granite3.3:2b"
    "gemma3:1b"
    "qwen3:0.6b"
    "gemma3:270M"
)

# 最適化パラメータ
NUM_PREDICT=512
MAX_CONTEXT_CHARS=1500
TEMPERATURE=0.3
QUALITY_THRESHOLD=0.9

# ログディレクトリ
LOG_DATE=$(date '+%Y%m%d_%H%M%S')
LOG_DIR="reports/brave_four_models_${LOG_DATE}"
mkdir -p ${LOG_DIR}

echo "=========================================="
echo "4モデル比較テスト（Brave Search API版）"
echo "=========================================="
echo ""
echo "実行日時: $(date '+%Y-%m-%d %H:%M:%S')"
echo "ログディレクトリ: ${LOG_DIR}"
echo ""
echo "対象モデル:"
for model in "${MODELS[@]}"; do
    echo "  - ${model}"
done
echo ""
echo "最適化パラメータ:"
echo "  - 品質閾値: ${QUALITY_THRESHOLD}"
echo "  - 最大トークン数: ${NUM_PREDICT}"
echo "  - 最大コンテキスト: ${MAX_CONTEXT_CHARS}文字"
echo "  - Temperature: ${TEMPERATURE}"
echo ""

# Brave API キーのチェック
if [ -z "${BRAVE_API_KEY}" ]; then
    echo "⚠️  警告: BRAVE_API_KEY 環境変数が設定されていません"
    echo "   DuckDuckGo検索にフォールバックします"
    echo ""
fi

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

echo "✅ OllamaサービスOK"
echo ""

# 各モデルでテスト実行
SUCCESS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

for model in "${MODELS[@]}"; do
    echo "=========================================="
    echo "モデル: ${model}"
    echo "=========================================="
    echo ""
    
    MODEL_SAFE=$(echo ${model} | tr ':' '_' | tr '.' '_')
    LOG_FILE="${LOG_DIR}/${MODEL_SAFE}.md"
    
    # モデルの存在確認
    if ! ollama list | grep -q "${model}"; then
        echo "⚠️  ${model} が見つかりません。スキップします。"
        echo "   インストール: ollama pull ${model}"
        echo ""
        SKIP_COUNT=$((SKIP_COUNT + 1))
        
        # スキップ情報をログに記録
        echo "# ${model} - スキップ" > ${LOG_FILE}
        echo "" >> ${LOG_FILE}
        echo "モデルが見つかりませんでした。" >> ${LOG_FILE}
        echo "" >> ${LOG_FILE}
        echo "インストール方法:" >> ${LOG_FILE}
        echo "\`\`\`bash" >> ${LOG_FILE}
        echo "ollama pull ${model}" >> ${LOG_FILE}
        echo "\`\`\`" >> ${LOG_FILE}
        
        continue
    fi
    
    echo "📝 ログファイル: ${LOG_FILE}"
    echo ""
    
    # テスト実行（ログディレクトリを渡す）
    if ./run_four_modes_test_optimized.sh ${model} ${LOG_DIR}; then
        echo ""
        echo "✅ ${model} 完了"
        echo ""
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo ""
        echo "❌ ${model} 失敗"
        echo ""
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
    
    # 少し待機（システムリソースの回復）
    echo "システムリソース回復のため5秒待機..."
    sleep 5
    echo ""
done

echo "=========================================="
echo "全モデルのテスト完了！"
echo "=========================================="
echo ""
echo "結果サマリー:"
echo "  ✅ 成功: ${SUCCESS_COUNT}モデル"
echo "  ❌ 失敗: ${FAIL_COUNT}モデル"
echo "  ⏭️  スキップ: ${SKIP_COUNT}モデル"
echo ""
echo "ログディレクトリ: ${LOG_DIR}"
echo ""

# 結果ファイルのリスト
echo "生成されたログファイル:"
for log in ${LOG_DIR}/*.md; do
    if [ -f "$log" ]; then
        SIZE=$(wc -l < "$log")
        echo "  - $(basename $log) (${SIZE}行)"
    fi
done
echo ""

echo "次のステップ:"
echo "1. 結果の比較"
echo "   python3 analyze_four_models_results.py ${LOG_DIR}"
echo ""
echo "2. 個別のログを確認"
echo "   cat ${LOG_DIR}/granite3_3_2b.md"
echo "   cat ${LOG_DIR}/gemma3_1b.md"
echo "   cat ${LOG_DIR}/qwen3_0_6b.md"
echo "   cat ${LOG_DIR}/gemma3_270M.md"
echo ""
echo "3. 比較レポートの生成"
echo "   python3 generate_comparison_report.py ${LOG_DIR}"
echo ""

# 成功したモデル数に応じて終了コード
if [ ${SUCCESS_COUNT} -eq 0 ]; then
    echo "⚠️  警告: すべてのモデルが失敗またはスキップされました"
    exit 1
elif [ ${FAIL_COUNT} -gt 0 ]; then
    echo "⚠️  警告: 一部のモデルが失敗しました"
    exit 2
else
    echo "🎉 すべてのモデルが正常に完了しました！"
    exit 0
fi