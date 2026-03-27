# Codex Instructions

このファイルはCodex CLIがこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

AI駆動開発プロジェクトです。GitHub Copilot、Codex、Claude Codeを使用して効率的なソフトウェア開発を行います。

## エージェント

12のエージェントが利用可能です（詳細は`agents/`ディレクトリ参照）:

### 要件・設計フェーズ
| エージェント | ファイル | 用途 |
|-------------|----------|------|
| requirements-agent | `requirements-agent.md` | PRD、ユースケース、ユーザーストーリー |
| ui-spec-agent | `ui-spec-agent.md` | 画面仕様書 |
| basic-design-agent | `basic-design-agent.md` | 基本設計書 |
| detailed-design-agent | `detailed-design-agent.md` | 詳細設計書 |
| api-spec-agent | `api-spec-agent.md` | API仕様書（OpenAPI） |

### 実装フェーズ
| エージェント | ファイル | 用途 |
|-------------|----------|------|
| implementation-agent-typescript | `implementation-agent.typescript.md` | TypeScript実装 |
| implementation-agent-python | `implementation-agent.python.md` | Python実装 |
| implementation-agent-csharp | `implementation-agent.csharp.md` | C#実装 |
| implementation-agent-java | `implementation-agent.java.md` | Java実装 |

### テスト・レビューフェーズ
| エージェント | ファイル | 用途 |
|-------------|----------|------|
| unit-test-agent | `unit-test-agent.md` | 単体テスト |
| e2e-test-agent | `e2e-test-agent.md` | E2Eテスト |
| code-review-agent | `code-review-agent.md` | コードレビュー |

## 開発フロー

```
要件定義 → 設計（画面/基本/詳細/API） → 実装 → テスト → レビュー → マージ
```

## 対応言語・プロジェクト構成

| 言語 | ディレクトリ | フレームワーク |
|------|-------------|---------------|
| TypeScript | `frontend/` | React, Vite |
| Python | `backendapp/` | FastAPI |
| C# | `csharp-backend/` | .NET 9, Web API |
| C# | `batch-csharp/` | .NET 9, Console |
| Java | `java-backend/` | Spring Boot, Maven |

## コマンド

### フロントエンド (TypeScript/React)
```bash
cd frontend
npm install
npm run dev      # 開発サーバー
npm run build    # ビルド
npm test         # テスト
npm run lint     # リント
```

### バックエンド (Python/FastAPI)
```bash
pip install -r backendapp/requirements.txt
uvicorn backendapp.main:app --reload  # 開発サーバー
pytest tests/                          # テスト
ruff check .                           # リント
```

### C# Backend/Batch
```bash
dotnet build
dotnet run --project csharp-backend/
dotnet test csharp-backend.Tests/
dotnet test batch-csharp.Tests/
```

### Java Backend
```bash
cd java-backend
mvn compile
mvn spring-boot:run  # 開発サーバー
mvn test             # テスト
```

### E2Eテスト
```bash
npx playwright test
npx playwright test --ui  # インタラクティブモード
```

## ドキュメント出力先

| ドキュメント種別 | 配置先 |
|----------------|--------|
| 要件定義書 | `docs/requirements/` |
| 基本設計書 | `docs/design/basic/` |
| 詳細設計書 | `docs/design/detailed/` |
| API仕様書 | `docs/api/` |
| 画面仕様書 | `docs/ui-specs/` |

## ExecPlans

複雑な機能実装やリファクタリングでは、`.agent/PLANS.md`に従ってExecPlanを作成してください。

### ExecPlan作成時のポイント
- 自己完結型のドキュメントを作成
- 明確なマイルストーンを設定
- 検証可能な成果物を定義
- Progressセクションを常に更新

## セキュリティ

- 機密情報（.env, credentials等）をコミットしない
- 入力値のバリデーションを行う
- OWASP Top 10を考慮する
- SQLインジェクション、XSS対策を実装

## Codex実行モード

```bash
# 読み取り専用モード（レビュー用）
codex exec --sandbox read-only "<prompt>"

# 書き込み可能モード（実装用）
codex exec --sandbox workspace-write "<prompt>"
```

## Claude Code連携

重要なマイルストーンではClaude Codeと連携してレビューを実施：
- Codex: read-onlyでレビュー（監査役）
- Claude Code: 修正担当
- `ok: true`になるまで反復
