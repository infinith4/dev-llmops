# Ragas × Langfuse 連携 実装プラン

## Context

既存の `backendapp/demo_trace.py` が Langfuse にモックトレース・データセット・スコアを送信する仕組みは構築済みである。しかし評価は手動のハードコード値であり、自動評価フレームワークが存在しない。Ragas を導入し、Langfuse に記録済みのトレース・データセットに対して自動評価メトリクスを実行し、結果を Langfuse にスコアとして書き戻す仕組みを構築する。

---

## 方針

### デュアルモード設計

- **Mode A（API キー不要・デフォルト）**: Ragas の Non-LLM メトリクス（`NonLLMStringSimilarity`, `BleuScore`, `RougeScore`）のみ使用。外部 API 呼び出しなしで動作する。
- **Mode B（`OPENAI_API_KEY` 設定時）**: LLM ベースメトリクス（`Faithfulness`, `AnswerRelevancy`, `AnswerCorrectness`）を追加実行。

### 実行順序の依存関係

```
1. Langfuse 起動済み（docker compose up -d）
2. pip install -r backendapp/requirements.txt
3. python -m backendapp.demo_trace        ← トレース・データセット作成
4. python -m backendapp.demo_ragas        ← Ragas 評価実行（本プランの対象）
```

---

## 変更対象ファイル

### 1. `backendapp/requirements.txt`（変更）

`ragas>=0.4.0` を追加する。

### 2. `backendapp/demo_ragas.py`（新規作成）

メインのデモスクリプト。以下の 3 つのデモを含む。

#### Demo 1: Standalone Ragas 評価

- `demo_trace.py` の agentic-rag-pipeline で使用したモックデータ（question / context / response / reference）から `SingleTurnSample` を構成
- `ragas.evaluate()` で Non-LLM メトリクスを実行
- 結果をコンソールに表示（Langfuse には送信しない）

#### Demo 2: 既存 Langfuse データセットの Ragas 評価 → スコア書き戻し

- `langfuse.get_dataset("qa-evaluation-set")` でデータセットを取得
- 各アイテムの `input["question"]` と `expected_output` から `SingleTurnSample` を構成
- Ragas で評価し、`langfuse.create_score(trace_id=..., name="ragas-{metric}", value=...)` でスコアをアタッチ
- 注: dataset item にはリンクされた trace_id がないため、`demo_trace.py` のデータセット実行で生成された trace を name="dataset-run" でフィルタして紐付ける

#### Demo 3: `langfuse.run_experiment()` で Ragas Evaluator を統合実行

- Langfuse v4 の `run_experiment()` API を使用
- `task` 関数: dataset item の expected_output をそのまま返す（モック）
- `evaluators`: Ragas メトリクスを `Langfuse Evaluation` を返す callable にラップ
- 結果は Langfuse の Datasets > Runs に自動記録される

#### スクリプト構造

```python
# backendapp/demo_ragas.py

# 共通データ
RAG_EVAL_DATA = [
    {
        "user_input": "LangfuseとLangSmithの違いを比較して...",
        "retrieved_contexts": ["Langfuse is an open-source...", ...],
        "response": "Langfuseは、オープンソースの...",
        "reference": "Langfuseはオープンソースの...",
    },
    # + qa-evaluation-set の 3 件
]

# メトリクス選択
def get_metrics() -> list:
    metrics = [NonLLMStringSimilarity(), BleuScore(), RougeScore()]
    if has_llm_api_key():
        metrics += [Faithfulness(), AnswerRelevancy(), AnswerCorrectness()]
    return metrics

# Demo 1: standalone
# Demo 2: score existing traces
# Demo 3: run_experiment with Ragas evaluators

def main():
    print("=== Ragas Evaluation Demo ===")
    print(f"Mode: {'Full (LLM + Non-LLM)' if has_llm_api_key() else 'Non-LLM only'}")
    demo_standalone()
    demo_score_existing_traces()
    demo_run_experiment()
    langfuse.flush()
```

### 3. `backendapp/.env.example`（変更）

Ragas 用のコメントブロックを追加:

```
# Ragas evaluation (optional - non-LLM metrics work without API key)
# OPENAI_API_KEY=sk-xxx
```

### 4. `docs/demo/ragas-evaluation-demo.md`（新規作成）

`langfuse-demo.md` と同じスタイル（である調・日本語）で作成:

- 概要
- 前提条件（Langfuse 起動 + demo_trace.py 実行済み）
- 実行手順
- ターミナル出力例（Mode A / Mode B）
- Langfuse UI での確認方法
- メトリクス一覧表
- トラブルシューティング

---

## スコア命名規則

Ragas スコアは既存スコアと区別するため `ragas-` プレフィックスを付ける:

| メトリクス | スコア名 | モード | 説明 |
|-----------|---------|-------|------|
| NonLLMStringSimilarity | `ragas-NonLLMStringSimilarity` | A (デフォルト) | 文字列類似度 |
| BleuScore | `ragas-BleuScore` | A (デフォルト) | BLEU スコア（n-gram 精度） |
| RougeScore | `ragas-RougeScore` | A (デフォルト) | ROUGE スコア（n-gram 再現率） |
| Faithfulness | `ragas-Faithfulness` | B (API キー必要) | コンテキストに対する事実整合性 |
| AnswerRelevancy | `ragas-AnswerRelevancy` | B (API キー必要) | 質問に対する回答の関連性 |
| AnswerCorrectness | `ragas-AnswerCorrectness` | B (API キー必要) | 正解に対する回答の正確性 |

---

## データフロー

```
demo_trace.py                    demo_ragas.py
─────────────                    ──────────────
Creates traces ──────────┐
Creates dataset items ───┤
Creates mock scores ─────┘
                                 ┌─ Reads dataset from Langfuse
                                 ├─ Constructs SingleTurnSample objects
                                 ├─ Runs ragas.evaluate() (non-LLM or full)
                                 ├─ Writes ragas-* scores to Langfuse traces
                                 └─ Runs langfuse.run_experiment() with Ragas evaluators
                                          │
                                          ▼
                                 Langfuse UI shows:
                                   - ragas-* scores on traces
                                   - Dataset run with per-item Ragas scores
                                   - Experiment results in Datasets > Runs
```

---

## 検証手順

```bash
# 1. 依存パッケージインストール
pip install -r backendapp/requirements.txt

# 2. トレース・データセット作成（未実行の場合）
python -m backendapp.demo_trace

# 3. Ragas 評価実行
python -m backendapp.demo_ragas

# 4. Langfuse UI で確認
#    - Traces: ragas-* スコアが付与されているか
#    - Datasets > qa-evaluation-set > Runs: 実験結果があるか
```
