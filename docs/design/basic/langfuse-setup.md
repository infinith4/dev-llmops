# Langfuse セルフホスト セットアップガイド

## 前提条件

- Docker & Docker Compose が利用可能であること
- DevContainer を再ビルド済みであること（Docker-in-Docker feature が必要）

## クイックスタート

### 1. DevContainer の再ビルド

`.devcontainer/devcontainer.json` に `docker-in-docker` feature を追加済み。
VS Code で `Dev Containers: Rebuild Container` を実行する。

### 2. Langfuse 起動

```bash
cd /workspaces/dev-llmops/langfuse
docker compose up -d
```

初回起動には 2〜3 分かかる（イメージのダウンロード + マイグレーション）。

起動時に以下が自動作成される（`docker-compose.yml` の `LANGFUSE_INIT_*` で定義）:
- 管理者ユーザー: `admin@example.com`
- Organization: `DevOrg`
- Project: `LLMOps`（ID: `my-project`）
- API キー: `pk-lf-dev-local` / `sk-lf-dev-local`

### 3. 起動確認

```bash
# 全サービスが healthy か確認
docker compose ps

# Web UI のヘルスチェック
curl -s http://localhost:3600/api/public/health
```

### 4. 初期セットアップ

自動初期化を使用する場合（推奨）:

1. ブラウザで http://localhost:3600 にアクセス
2. `admin@example.com` でログイン（パスワードは `docker-compose.yml` の `LANGFUSE_INIT_USER_PASSWORD` で設定）
3. `backendapp/.env` に API キーが設定済みであることを確認

手動セットアップの場合:

1. ブラウザで http://localhost:3600 にアクセス
2. 「Sign Up」で管理者アカウントを作成
3. Organization → Project を作成
4. Settings → API Keys で公開キー・秘密キーを発行
5. 発行したキーを `backendapp/.env` に設定

```bash
# backendapp/.env の例
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_HOST=http://localhost:3600
```

## デモスクリプトの実行

### トレーシング & LLM-as-a-Judge デモ

LLM の API キー不要で、Langfuse にモックデータを流し込むデモスクリプトを用意している。

```bash
cd /workspaces/dev-llmops

# 依存パッケージのインストール
pip install -r backendapp/requirements.txt

# デモ実行
python -m backendapp.demo_trace
```

実行すると以下の4種類のデータが Langfuse に送信される:

| デモ | 内容 |
|------|------|
| Basic Trace | LLM 生成（フィボナッチ）+ ユーザーフィードバックスコア |
| RAG Pipeline | クエリ書き換え → ベクトル検索 → 回答生成の多段トレース |
| LLM-as-a-Judge | relevance / faithfulness / helpfulness / toxicity の4評価スコア |
| Dataset Evaluation | Q&A テストケース3件のデータセット作成 + 評価実行 |

実行後、Langfuse UI で確認:
- トレース一覧: http://localhost:3600/project/my-project/traces
- データセット: http://localhost:3600/project/my-project/datasets

### FastAPI サーバー起動

実際の LLM を呼び出す場合は、LLM プロバイダーの API キーを `backendapp/.env` に追加してサーバーを起動する。

```bash
# backendapp/.env に LLM プロバイダーの API キーを追加
# OPENAI_API_KEY=sk-xxx
# ANTHROPIC_API_KEY=sk-ant-xxx

# FastAPI 起動
uvicorn backendapp.main:app --reload
```

チャットエンドポイントの呼び出し:

```bash
# OpenAI モデル
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "model": "openai/gpt-4o"}'

# Anthropic モデル
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello!", "model": "anthropic/claude-sonnet-4-20250514"}'
```

すべてのリクエストは Langfuse に自動トレースされる（モデル名・入出力・トークン数・コスト）。

## サービス構成

| サービス | ポート | URL |
|---------|--------|-----|
| Langfuse Web UI | 3600 | http://localhost:3600 |
| Langfuse Worker | 3030 (localhost only) | - |
| PostgreSQL | 5432 (localhost only) | - |
| ClickHouse | 8123 (localhost only) | - |
| MinIO (S3) | 9090 (API) / 9091 (Console) | http://localhost:9091 |
| Redis | 6379 (localhost only) | - |

## よく使うコマンド

```bash
# 起動
cd langfuse && docker compose up -d

# 停止
cd langfuse && docker compose down

# ログ確認
cd langfuse && docker compose logs -f langfuse-web

# 完全リセット（データも削除）
cd langfuse && docker compose down -v
```

## トラブルシューティング

### Docker が使えない

DevContainer に Docker-in-Docker feature が追加されているか確認:
```bash
docker --version
```

表示されない場合は DevContainer を再ビルドする。

### ポートが競合する

他のサービスがポート 3600, 5432, 9090 等を使用している場合、
`langfuse/docker-compose.yml` のポートマッピングを変更するか、競合するサービスを停止する。

### ClickHouse のヘルスチェックが失敗する

メモリ不足の可能性がある。Langfuse v3 は最低 16GiB RAM を推奨。
```bash
free -h
```

### Langfuse にデータが届かない

1. Langfuse が起動しているか確認:
   ```bash
   curl -s http://localhost:3600/api/public/health
   ```
2. `backendapp/.env` の `LANGFUSE_HOST`、`LANGFUSE_PUBLIC_KEY`、`LANGFUSE_SECRET_KEY` が正しいか確認
3. API キーの認証テスト:
   ```bash
   curl -s -u "pk-lf-xxx:sk-lf-xxx" http://localhost:3600/api/public/traces?limit=1
   ```
