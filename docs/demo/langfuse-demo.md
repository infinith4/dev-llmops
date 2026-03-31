# Langfuse デモ実行ガイド

## 概要

`backendapp/demo_trace.py` は、LLM の API キーなしで Langfuse にトレーシング・評価データを送信するデモスクリプトである。実際の LLM 呼び出しは行わず、モックデータを使用して Langfuse の各機能を体験できる。

---

## 前提条件

- Langfuse が起動済みであること
- `backendapp/.env` に Langfuse の接続情報が設定済みであること

```bash
# Langfuse 起動
cd /workspaces/dev-llmops/langfuse
docker compose up -d

# ヘルスチェック
curl -s http://localhost:3600/api/public/health
# → {"status":"OK","version":"3.162.0"}
```

---

## デモ実行手順

### 1. 依存パッケージのインストール

```bash
pip install -r backendapp/requirements.txt
```

### 2. デモスクリプトの実行

```bash
cd /workspaces/dev-llmops
python -m backendapp.demo_trace
```

### 3. 実行結果（ターミナル出力）

以下のような出力が表示される。

```
=== Langfuse Demo: Tracing & LLM-as-a-Judge ===

Langfuse Host: http://localhost:3600

1. Basic trace with generation and score...
  [basic-trace] trace_id=b80262dd1bb2...
2. Multi-step RAG pipeline trace...
  [agentic-rag] trace_id=d48f71fc1ceb...
3. LLM-as-a-Judge evaluation...
  [llm-as-judge] Attached 4 scores to trace_id=d48f71fc1ceb...
4. Dataset evaluation run...
  [dataset] Created dataset with 3 items

Flushing to Langfuse...

Done! Check Langfuse UI: http://localhost:3600
  - Traces: http://localhost:3600/project/my-project/traces
  - Datasets: http://localhost:3600/project/my-project/datasets
```

実行完了後、ブラウザで http://localhost:3600 を開いて結果を確認する。

---

## Langfuse UI での確認

### ログイン

| 項目 | 値 |
|------|-----|
| URL | http://localhost:3600 |
| メール | `admin@example.com` |
| パスワード | `password` |

ログイン後、左メニューから **Tracing > Traces** を選択する。

---

### トレース一覧画面

**Tracing > Traces** を開くと、デモで作成された全トレースが一覧表示される。

![トレース一覧画面](attachements/Pasted%20image%2020260331152031.png)

左ペインにトレース名の一覧、右ペインに各トレースの Observations ツリーと Scores が表示される。`agentic-rag-pipeline` には複数の Evaluator スコアが付与されていることが確認できる。

デモは以下の 4 種類・計 6 トレースを生成する。

| トレース名 | 件数 | 内容 |
|-----------|------|------|
| `demo-chat` | 1 | 基本的な LLM 呼び出し + ユーザーフィードバック |
| `agentic-rag-pipeline` | 1 | 9 ステップ・24 オブザベーションの複雑なパイプライン |
| `llm-as-judge` | 1 | 評価 LLM の推論トレース |
| `dataset-run` | 3 | データセット評価の各テストケース実行 |

---

### Demo 1: Basic Trace（`demo-chat`）

シンプルな LLM チャットのトレースである。トレース名 `demo-chat` をクリックして詳細を開く。

![demo-chat トレース詳細](attachements/Pasted%20image%2020260331152153.png)

左ペインに `demo-chat` → `context-retrieval` → `llm-response` のツリーが表示され、右ペインで選択したオブザベーションの Input/Output・メタデータが確認できる。

![demo-chat フローチャート表示](attachements/Pasted%20image%2020260331154000.png)

Timeline ビューではフローチャート形式で `demo-chat` → `context-retrieval` → `llm-response` の実行順序が視覚的に表示される。

#### トレース構造

```
demo-chat
├── context-retrieval    (retriever)  ─ 検索クエリ「フィボナッチ数列 Python」
└── llm-response         (generation) ─ openai/gpt-4o, 45+120 tokens
```

#### 観測ポイント

- **Generation パネル**: `llm-response` をクリックすると、Input（system + user メッセージ）と Output（フィボナッチのコード）が表示される
- **Scores タブ**: `user-feedback = 1.0`（コメント:「正確なコードだった」）が記録されている

```
┌─ Scores ─────────────────────────────────────────┐
│ Name            │ Value │ Comment                 │
├─────────────────┼───────┼─────────────────────────┤
│ user-feedback   │  1.0  │ 正確なコードだった        │
└─────────────────┴───────┴─────────────────────────┘
```

---

### Demo 2: Agentic RAG Pipeline（`agentic-rag-pipeline`）

最も複雑なトレースである。エージェント型 RAG パイプラインの全ステップが 24 オブザベーションとして記録されている。トレース名 `agentic-rag-pipeline` をクリックして詳細を開く。

![agentic-rag-pipeline トレース詳細](attachements/Pasted%20image%2020260331152134.png)

左ペインのツリービューで `agentic-rag-pipeline` 配下の全オブザベーションが階層表示される。`input-guardrail` → `moderation-check` のようにネストされた構造が視覚的に確認できる。右ペインには選択したオブザベーションの Output やメタデータが表示される。

#### ユーザークエリ

> LangfuseとLangSmithの違いを比較して、それぞれの料金体系も教えて

#### トレース構造（24 observations）

Langfuse UI の左ペインに以下のツリーが表示される。

```
agentic-rag-pipeline                              (span)
│
├── input-guardrail                                (guardrail)
│   └── moderation-check                           (generation) openai/gpt-4o-mini  35→18 tokens
│
├── intent-classification                          (span)
│   └── classify-llm                               (generation) openai/gpt-4o-mini  50→25 tokens
│
├── query-decomposition                            (span)
│   └── decompose-llm                              (generation) openai/gpt-4o       55→60 tokens
│
├── parallel-retrieval                             (span)
│   ├── vector-search                              (retriever)
│   │   └── embedding                              (embedding)  text-embedding-3-small  85 tokens
│   ├── keyword-search                             (retriever)  BM25/Elasticsearch
│   └── web-search                                 (tool)       Tavily
│
├── rerank-and-fuse                                (span)
│   └── rerank-llm                                 (generation) openai/gpt-4o-mini  320→30 tokens
│
├── context-compression                            (span)
│   └── compress-llm                               (generation) openai/gpt-4o-mini  480→120 tokens
│
├── answer-generation                              (chain)
│   ├── draft-answer                               (generation) claude-sonnet-4      280→65 tokens
│   ├── tool-call-execution                        (tool)
│   │   └── code-interpreter                       (span)       比較表 Markdown 生成
│   └── final-answer                               (generation) claude-sonnet-4      450→280 tokens
│
├── output-guardrail                               (guardrail)
│   └── safety-check                               (generation) openai/gpt-4o-mini  300→20 tokens
│
└── response-formatting                            (span)
```

#### Observations タブ（全オブザベーション一覧）

Observations タブを開くと、24 件すべてのオブザベーションがテーブル形式で一覧表示される。各行にオブザベーションの型（GENERATION / RETRIEVER / TOOL 等）、モデル名、トークン数、スコアが表示される。

![agentic-rag-pipeline Observations 一覧](attachements/Pasted%20image%2020260331153904.png)

#### 各ステップの詳細

| # | ステップ | 種別 | モデル | 内容 |
|---|---------|------|--------|------|
| 1 | input-guardrail | guardrail | gpt-4o-mini | 入力の安全性チェック。`safe: true` を返す |
| 2 | intent-classification | span | gpt-4o-mini | 意図分類。`comparison` + `pricing` を検出 |
| 3 | query-decomposition | span | gpt-4o | クエリを 5 つのサブクエリに分解 |
| 4 | parallel-retrieval | span | - | 3 ソース並列検索（ベクトル / キーワード / Web） |
| 4a | └ vector-search | retriever | embedding-3-small | pgvector で 5 件取得。embedding 子スパンあり |
| 4b | └ keyword-search | retriever | - | Elasticsearch BM25 で 3 件取得 |
| 4c | └ web-search | tool | - | Tavily で料金ページ等 3 件取得 |
| 5 | rerank-and-fuse | span | gpt-4o-mini | RRF + LLM リランクで 11→6 件に絞り込み |
| 6 | context-compression | span | gpt-4o-mini | 6 件を圧縮率 25% で要約 |
| 7 | answer-generation | chain | claude-sonnet-4 | ドラフト→ツール呼び出し→最終回答の 3 段階 |
| 7a | └ draft-answer | generation | claude-sonnet-4 | 比較表作成ツールを呼び出す tool_call を返す |
| 7b | └ tool-call-execution | tool | - | code-interpreter で Markdown 比較表を生成 |
| 7c | └ final-answer | generation | claude-sonnet-4 | ツール結果を組み込んだ最終回答を生成 |
| 8 | output-guardrail | guardrail | gpt-4o-mini | 事実性・バイアス・PII チェック。すべて pass |
| 9 | response-formatting | span | - | Markdown 形式に整形 |

#### Scores（LLM-as-a-Judge による評価）

Demo 3 の `llm-as-judge` がこのトレースに対して 4 つのスコアをアタッチする。Scores タブで確認できる。

```
┌─ Scores ──────────────────────────────────────────────────────────────────┐
│ Name          │ Value │ Comment                                           │
├───────────────┼───────┼───────────────────────────────────────────────────┤
│ relevance     │  0.90 │ 回答は質問に対して高い関連性がある                     │
│ faithfulness  │  0.85 │ コンテキストに忠実だが、一部補足情報が追加されている        │
│ helpfulness   │  1.00 │ ユーザーの質問に十分に答えている                       │
│ toxicity      │  0.00 │ 有害なコンテンツは含まれていない                        │
└───────────────┴───────┴───────────────────────────────────────────────────┘
```

#### UI での確認ポイント

1. **ツリービュー（左ペイン）**: 各ノードをクリックすると右ペインに Input/Output が表示される
2. **Generation の詳細**: `draft-answer` をクリックすると `tool_calls` を含む出力が確認できる
3. **ネストの深さ**: `parallel-retrieval > vector-search > embedding` のように 3 階層のネストがある
4. **型の多様性**: span / generation / retriever / embedding / tool / chain / guardrail の 7 種類が使われている

---

### Demo 3: LLM-as-a-Judge（`llm-as-judge`）

評価用 LLM の推論プロセス自体をトレースしたものである。

#### トレース構造

```
llm-as-judge
└── judge-reasoning    (generation) openai/gpt-4o, 100→60 tokens
```

#### 動作の説明

このトレースは「評価する側」の LLM 呼び出しを記録している。評価結果（スコア）は、評価対象である `agentic-rag-pipeline` トレースの Scores にアタッチされる。

```
agentic-rag-pipeline  ←── relevance: 0.9, faithfulness: 0.85, ...（スコアが付与される）
        ↑
llm-as-judge          ←── judge-reasoning で評価理由を生成（こちらはトレースのみ）
```

この分離により、「何を評価したか」と「どう評価したか」が独立して追跡可能である。

---

### Demo 4: Dataset Evaluation（`dataset-run` × 3）

Q&A テストケースのデータセット評価である。

![dataset-run トレース詳細](attachements/Pasted%20image%2020260331152059.png)

`dataset-run` トレースをクリックすると、各テストケースの generation とスコアが確認できる。右ペインの Scores タブに `correctness = 1.0` が表示される。

#### データセット

**Datasets** メニュー（左メニュー > Datasets）から `qa-evaluation-set` を開くと、3 件のテストケースが表示される。

![qa-evaluation-set データセットアイテム一覧](attachements/Pasted%20image%2020260331154112.png)

各アイテムの Input（質問文）と Expected Output（期待される回答）が一覧で確認できる。Status 列でアイテムの状態も管理される。

#### 各テストケースのトレース構造

```
dataset-run
└── answer    (generation) openai/gpt-4o, 30→40 tokens
```

各 `dataset-run` トレースには `correctness = 1.0` のスコアが付与されている。

![dataset-run 個別アイテム詳細](attachements/Pasted%20image%2020260331152543.png)

個別の `dataset-run` トレースを開くと、Input の質問文と Expected Output が右ペインに表示される。generation の出力と期待値が一致していることが確認できる。

![dataset-run スコア詳細](attachements/Pasted%20image%2020260331154251.png)

Scores タブを開くと、各テストケースに付与された `correctness` スコアや Evaluator による自動評価結果が一覧表示される。コメント欄に評価理由が記録されている。

---

## 補足: デモで生成されるデータの全体像

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         Langfuse に記録されるデータ                        │
├──────────────────┬───────────────────────────────────────────────────────┤
│ Traces           │ 6 件（demo-chat, agentic-rag-pipeline, llm-as-judge, │
│                  │       dataset-run ×3）                                │
├──────────────────┼───────────────────────────────────────────────────────┤
│ Observations     │ 計 33 件                                              │
│                  │   - demo-chat: 3                                      │
│                  │   - agentic-rag-pipeline: 24                          │
│                  │   - llm-as-judge: 2                                   │
│                  │   - dataset-run: 各 2 × 3 = 6 ※トレース自体含めず       │
├──────────────────┼───────────────────────────────────────────────────────┤
│ Scores           │ 計 8 件                                               │
│                  │   - demo-chat: user-feedback (1.0)                    │
│                  │   - agentic-rag-pipeline: relevance (0.9),            │
│                  │     faithfulness (0.85), helpfulness (1.0),           │
│                  │     toxicity (0.0)                                    │
│                  │   - dataset-run: correctness (1.0) × 3               │
├──────────────────┼───────────────────────────────────────────────────────┤
│ Datasets         │ 1 件（qa-evaluation-set, 3 items）                    │
├──────────────────┼───────────────────────────────────────────────────────┤
│ Models referenced│ openai/gpt-4o, openai/gpt-4o-mini,                   │
│                  │ openai/text-embedding-3-small,                        │
│                  │ anthropic/claude-sonnet-4-20250514                    │
├──────────────────┼───────────────────────────────────────────────────────┤
│ Observation types│ span, generation, retriever, embedding, tool,         │
│                  │ chain, guardrail                                      │
└──────────────────┴───────────────────────────────────────────────────────┘
```

---

## トラブルシューティング

### デモ実行時にエラーが出る

```bash
# Langfuse の起動確認
curl -s http://localhost:3600/api/public/health

# .env の確認
cat backendapp/.env
# LANGFUSE_PUBLIC_KEY と LANGFUSE_SECRET_KEY が正しいか確認する
```

### トレースが Langfuse UI に表示されない

スクリプト実行後、Langfuse への送信には数秒かかる。`Flushing to Langfuse...` の後 2 秒待機するが、表示されない場合はブラウザをリロードする。

### データセットが重複する

デモを複数回実行すると `qa-evaluation-set` の作成で既存データセットが返される。テストケースのアイテムは追加されるため、重複が気になる場合は Langfuse UI から手動削除するか、以下でリセットする。

```bash
cd langfuse && docker compose down -v && docker compose up -d
```
