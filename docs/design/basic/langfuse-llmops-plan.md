# Langfuse LLMOps 環境構築計画

## Context

LLM アプリケーションの開発・運用において、トレーシング・プロンプト管理・評価・コスト追跡などの LLMOps 機能が必要。Langfuse（オープンソース LLM エンジニアリングプラットフォーム v3）をセルフホストで導入し、Python FastAPI バックエンドと統合する。

**LLM プロバイダー**: 未定（OpenAI / Anthropic / Azure OpenAI 等を複数併用する可能性あり）。そのため、特定プロバイダーに依存しない設計とする。

**今回の実装範囲**: Phase 1（サーバー構築）+ Phase 2（Python トレーシング統合）

---

## Phase 1: Langfuse サーバー構築（Docker Compose）

### 1-1. DevContainer に Docker-in-Docker 機能を追加

**対象ファイル**: `.devcontainer/devcontainer.json`

```jsonc
// features に追加
"ghcr.io/devcontainers/features/docker-in-docker:2": {}
```

これにより devcontainer 内で `docker` / `docker compose` コマンドが使用可能になる。

### 1-2. Langfuse Docker Compose 定義を作成

**新規作成**: `langfuse/docker-compose.yml`

Langfuse v3 に必要なサービス:

| サービス | イメージ | ポート | 役割 |
|---------|---------|--------|------|
| langfuse-web | langfuse/langfuse | 3000 | Web UI + API |
| langfuse-worker | langfuse/langfuse-worker | - | 非同期イベント処理 |
| postgres | postgres:17 | 5432 | ユーザー・設定データ |
| clickhouse | clickhouse/clickhouse-server | 8123 | トレーシングデータ・分析 |
| redis | redis:7 | 6379 | イベントキュー・キャッシュ |
| minio | chainguard/minio | 9090/9091 | Blob ストレージ |

**新規作成**: `langfuse/.env`（gitignore 対象）+ `langfuse/.env.example`

### 1-3. gitignore・設定ファイル更新

**変更ファイル**:
- `.claude/settings.json` — `Bash(docker compose*)` を allow に追加

### 1-4. セットアップドキュメント作成

**新規作成**: `docs/design/basic/langfuse-setup.md`
- 起動手順、初期ユーザー作成、トラブルシューティング

### Phase 1 検証

```bash
cd langfuse && docker compose up -d
# http://localhost:3000 にアクセス
# 初期ユーザーを作成し、プロジェクト・API キーを発行
```

---

## Phase 2: Python FastAPI + マルチ LLM トレーシング統合

### 設計方針

LLM プロバイダーは未定で複数併用の可能性があるため、**LiteLLM** を採用する。LiteLLM は OpenAI / Anthropic / Azure OpenAI / Google Gemini 等 100+ プロバイダーを統一インターフェースで呼び出せるプロキシライブラリであり、Langfuse との統合もネイティブサポートされている。

| プロバイダー | Langfuse 統合方式 |
|-------------|------------------|
| OpenAI | `langfuse.openai` で自動インストルメンテーション |
| Anthropic | `@observe` デコレータによる手動トレーシング |
| Azure OpenAI | `langfuse.openai` で自動インストルメンテーション |
| LiteLLM 経由（全プロバイダー統一） | LiteLLM コールバックで自動トレーシング |

→ **LiteLLM + Langfuse コールバック** を使えば、プロバイダーを問わず統一的にトレーシングできる。

### 2-1. FastAPI バックエンド作成

**新規作成**:
- `backendapp/__init__.py`
- `backendapp/main.py` — FastAPI アプリ（ヘルスチェック + Item CRUD + LLM チャット）
- `backendapp/requirements.txt` — 依存関係

### 2-2. Langfuse SDK + LiteLLM 統合

**依存関係** (`backendapp/requirements.txt`):

```
fastapi>=0.110.0
uvicorn[standard]
pydantic
litellm
langfuse
python-dotenv
pytest
httpx
```

**新規作成**: `backendapp/llm_service.py` — マルチ LLM 呼び出し + Langfuse トレーシング

```python
import litellm
from litellm import completion
from langfuse.decorators import observe

# Langfuse コールバックを設定（全 LLM 呼び出しを自動トレース）
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]

@observe()
def call_llm(
    prompt: str,
    model: str = "openai/gpt-4o",
    system: str = "",
    max_tokens: int = 1024,
) -> str:
    """マルチ LLM 呼び出し + Langfuse 自動トレーシング

    model の例:
      - "openai/gpt-4o"
      - "anthropic/claude-sonnet-4-20250514"
      - "azure/gpt-4o"
      - "gemini/gemini-pro"
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = completion(model=model, messages=messages, max_tokens=max_tokens)
    return response.choices[0].message.content
```

### 2-3. LLM エンドポイント

- `POST /chat` — 指定モデルにメッセージを送信し、レスポンスを返す
- リクエストで `model` パラメータを指定可能（デフォルト: `openai/gpt-4o`）
- Langfuse で自動的にトレース・トークン数・コストが記録される（プロバイダー問わず）

### 2-4. 環境変数設定

**新規作成**: `backendapp/.env.example`

```
# Langfuse 接続情報
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_HOST=http://localhost:3000

# LLM プロバイダー API キー（使用するものだけ設定）
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
AZURE_API_KEY=xxx
AZURE_API_BASE=https://xxx.openai.azure.com/
GEMINI_API_KEY=xxx
```

### Phase 2 検証

```bash
# FastAPI 起動
cd /workspaces/dev-langfuse
pip install -r backendapp/requirements.txt
uvicorn backendapp.main:app --reload

# OpenAI モデルで呼び出し
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "model": "openai/gpt-4o"}'

# Anthropic モデルで呼び出し
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "model": "anthropic/claude-sonnet-4-20250514"}'

# Langfuse UI (http://localhost:3000) で確認:
# - トレース一覧に各リクエストが表示される
# - Generation にモデル名・入出力・トークン数が記録されている
# - プロバイダー別のコストが自動計算されている
```

---

## 作成・変更ファイル一覧

| ファイル | 操作 | Phase |
|---------|------|-------|
| `.devcontainer/devcontainer.json` | 変更（Docker-in-Docker 追加） | 1 |
| `langfuse/docker-compose.yml` | 新規 | 1 |
| `langfuse/.env` | 新規（gitignore 対象） | 1 |
| `langfuse/.env.example` | 新規 | 1 |
| `.claude/settings.json` | 変更（docker compose 許可追加） | 1 |
| `docs/design/basic/langfuse-setup.md` | 新規 | 1 |
| `backendapp/__init__.py` | 新規 | 2 |
| `backendapp/main.py` | 新規 | 2 |
| `backendapp/llm_service.py` | 新規（LiteLLM + Langfuse 統合） | 2 |
| `backendapp/requirements.txt` | 新規（litellm, langfuse 等） | 2 |
| `backendapp/.env.example` | 新規（マルチプロバイダー API キー） | 2 |

---

## 将来フェーズ（今回は実装しない）

| Phase | 内容 | 概要 |
|-------|------|------|
| 3 | プロンプト管理 | Langfuse でプロンプトをバージョン管理、コード変更なしで更新 |
| 4 | 評価パイプライン | LLM-as-a-Judge、ユーザーフィードバック、データセット管理 |
| 5 | TypeScript SDK 統合 | フロントエンド/Node.js からのトレーシング |
| 6 | ダッシュボード・運用 | カスタムダッシュボード、アラート設定 |
