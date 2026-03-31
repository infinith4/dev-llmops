# Ragas 評価デモ実行ガイド

## 概要

`backendapp/demo_ragas.py` は、Ragas 評価フレームワークを Langfuse と連携させるデモスクリプトである。`demo_trace.py` が作成したトレース・データセットに対して Ragas メトリクスで自動評価を実行し、結果を Langfuse にスコアとして書き戻す。

LLM の API キーがなくても Non-LLM メトリクス（文字列類似度、BLEU、ROUGE）で動作する。

---

## 前提条件

- Langfuse が起動済みであること
- `demo_trace.py` を事前に実行済みであること（トレースとデータセットが必要）

```bash
# Langfuse 起動確認
curl -s http://localhost:3600/api/public/health
# → {"status":"OK","version":"3.162.0"}

# トレース・データセット作成（未実行の場合）
python -m backendapp.demo_trace
```

---

## デモ実行手順

### 1. 依存パッケージのインストール

```bash
pip install -r backendapp/requirements.txt
```

Ragas と関連パッケージ（`rapidfuzz`, `sacrebleu`, `rouge-score` 等）がインストールされる。

### 2. デモスクリプトの実行

```bash
cd /workspaces/dev-llmops
python -m backendapp.demo_ragas
```

### 3. 実行結果（ターミナル出力）

#### Mode A: Non-LLM メトリクスのみ（API キーなし・デフォルト）

```
=== Ragas Evaluation Demo ===

Mode: Non-LLM metrics only
Langfuse Host: http://localhost:3600

1. Standalone Ragas evaluation...
  Metrics: non_llm_string_similarity, bleu_score, rouge_score
  Samples: 4

  [1] LangfuseとLangSmithの違いを比較して、それぞれの料金体系も教えて...
      non_llm_string_similarity=0.353  bleu_score=0.000  rouge_score=0.235
  [2] Pythonのリスト内包表記とは？...
      non_llm_string_similarity=1.000  bleu_score=0.000  rouge_score=1.000
  [3] RESTとGraphQLの違いは？...
      non_llm_string_similarity=1.000  bleu_score=0.000  rouge_score=1.000
  [4] Docker Composeの用途は？...
      non_llm_string_similarity=1.000  bleu_score=0.000  rouge_score=1.000

2. Score existing Langfuse traces...
  Scored 3 traces with 3 metrics each (9 scores total)
3. Langfuse experiment with Ragas evaluators...
  Experiment completed: 12 items evaluated
  Evaluators: non_llm_string_similarity, bleu_score, rouge_score

Flushing to Langfuse...

Done! Check Langfuse UI: http://localhost:3600
  - Traces with ragas-* scores
  - Datasets > qa-evaluation-set > Runs > ragas-evaluation
```

#### Mode B: Full 評価（`OPENAI_API_KEY` 設定時）

`backendapp/.env` に `OPENAI_API_KEY` を設定すると、LLM ベースメトリクスが追加される。

```
Mode: Full (LLM + Non-LLM)
...
  Metrics: non_llm_string_similarity, bleu_score, rouge_score, faithfulness, answer_relevancy, answer_correctness
```

---

## デモの構成

スクリプトは 3 つのデモで構成される。

### Demo 1: Standalone Ragas 評価

Ragas を単独で実行し、コンソールに結果を出力する。Langfuse には送信しない。

- `demo_trace.py` で使用したモックデータ（RAG パイプラインの質問・コンテキスト・回答・正解）を使用
- `SingleTurnSample` を構成し、各メトリクスの `ascore()` を実行
- response と reference が完全一致するサンプルではスコアが 1.0 になり、異なるサンプルでは低い値になることが確認できる

### Demo 2: 既存 Langfuse トレースへのスコア書き戻し

Langfuse に記録済みの `dataset-run` トレースに対して Ragas 評価を実行し、結果をスコアとしてアタッチする。

- Langfuse REST API で `dataset-run` トレースを取得
- Ragas メトリクスで評価
- `langfuse.create_score()` で `ragas-*` スコアを書き込み
- Langfuse UI のトレース詳細 > Scores タブで確認できる

### Demo 3: Langfuse Experiment 連携

Langfuse v4 の `run_experiment()` API を使用し、データセット評価を一括実行する。

- `qa-evaluation-set` データセットの全アイテムに対して実行
- `task` 関数: dataset item の `expected_output` をモデル出力として返す（モック）
- `evaluators`: Ragas メトリクスを async Langfuse EvaluatorFunction にラップ
- 結果は Langfuse の **Datasets > qa-evaluation-set > Runs** に `ragas-evaluation` として記録される

---

## Langfuse UI での確認

### トレースのスコア確認

**Tracing > Traces** から `dataset-run` トレースを開き、**Scores** タブを確認する。`ragas-*` プレフィックスのスコアが追加されている。

```
┌─ Scores ──────────────────────────────────────────────────────────────────┐
│ Name                          │ Value │ Comment                           │
├───────────────────────────────┼───────┼───────────────────────────────────┤
│ ragas-non_llm_string_similarity│ 1.000 │ Ragas non_llm_string_similarity  │
│ ragas-bleu_score              │ 0.000 │ Ragas bleu_score evaluation       │
│ ragas-rouge_score             │ 1.000 │ Ragas rouge_score evaluation      │
│ correctness                   │ 1.000 │ 期待出力と一致（demo_trace.py）     │
└───────────────────────────────┴───────┴───────────────────────────────────┘
```

### データセット Experiment 確認

**Datasets > qa-evaluation-set** を開き、**Runs** タブから `ragas-evaluation` を選択する。各アイテムに対する Ragas メトリクスのスコアが一覧表示される。

---

## 評価メトリクス一覧

### Non-LLM メトリクス（API キー不要）

| メトリクス | スコア名 | 範囲 | 説明 |
|-----------|---------|------|------|
| NonLLMStringSimilarity | `ragas-non_llm_string_similarity` | 0.0〜1.0 | 編集距離ベースの文字列類似度 |
| BleuScore | `ragas-bleu_score` | 0.0〜1.0 | BLEU スコア（n-gram 精度） |
| RougeScore | `ragas-rouge_score` | 0.0〜1.0 | ROUGE スコア（n-gram 再現率） |

### LLM メトリクス（`OPENAI_API_KEY` 必要）

| メトリクス | スコア名 | 範囲 | 説明 |
|-----------|---------|------|------|
| Faithfulness | `ragas-faithfulness` | 0.0〜1.0 | コンテキストに対する事実整合性 |
| AnswerRelevancy | `ragas-answer_relevancy` | 0.0〜1.0 | 質問に対する回答の関連性 |
| AnswerCorrectness | `ragas-answer_correctness` | 0.0〜1.0 | 正解に対する回答の正確性 |

---

## データフロー

```
demo_trace.py                    demo_ragas.py
─────────────                    ──────────────
Creates traces ──────────┐
Creates dataset items ───┤
Creates mock scores ─────┘
                                 ┌─ Reads dataset from Langfuse
                                 ├─ Constructs evaluation samples
                                 ├─ Runs Ragas metrics (non-LLM or full)
                                 ├─ Writes ragas-* scores to existing traces
                                 └─ Runs langfuse.run_experiment()
                                          │
                                          ▼
                                 Langfuse UI:
                                   - Traces に ragas-* スコア追加
                                   - Datasets > Runs に ragas-evaluation 結果
```

---

## トラブルシューティング

### `ModuleNotFoundError: No module named 'rapidfuzz'`

Ragas の Non-LLM メトリクスに必要な依存パッケージが不足している。

```bash
pip install rapidfuzz sacrebleu rouge-score
```

### `Dataset 'qa-evaluation-set' not found`

`demo_trace.py` を先に実行する必要がある。

```bash
python -m backendapp.demo_trace
python -m backendapp.demo_ragas
```

### `No dataset-run traces found`

同上。`demo_trace.py` がデータセット評価のトレースを作成する。

### LLM メトリクスを使いたい

`backendapp/.env` に `OPENAI_API_KEY` を設定する。

```bash
# backendapp/.env に追加
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx
```

設定後に `demo_ragas.py` を再実行すると、Mode B（Full 評価）で動作する。
