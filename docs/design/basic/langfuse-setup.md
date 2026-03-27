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
cd /workspaces/dev-langfuse/langfuse
docker compose up -d
```

初回起動には 2〜3 分かかる（イメージのダウンロード + マイグレーション）。

### 3. 起動確認

```bash
# 全サービスが healthy か確認
docker compose ps

# Web UI のヘルスチェック
curl -s http://localhost:3000/api/public/health
```

### 4. 初期セットアップ

1. ブラウザで `http://localhost:3000` にアクセス
2. 「Sign Up」で管理者アカウントを作成
3. Organization → Project を作成
4. Settings → API Keys で公開キー・秘密キーを発行
5. 発行したキーを `backendapp/.env` に設定

## サービス構成

| サービス | ポート | URL |
|---------|--------|-----|
| Langfuse Web UI | 3000 | http://localhost:3000 |
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

他のサービスがポート 3000, 5432, 9090 等を使用している場合、
`langfuse/.env` でポートマッピングを変更するか、競合するサービスを停止する。

### ClickHouse のヘルスチェックが失敗する

メモリ不足の可能性がある。Langfuse v3 は最低 16GiB RAM を推奨。
```bash
free -h
```
