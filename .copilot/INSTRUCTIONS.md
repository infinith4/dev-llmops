# Copilot Workspace Instructions

このファイルはGitHub Copilotがこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

AI駆動開発プロジェクトです。GitHub Copilot、Codex、Claude Codeを使用して効率的なソフトウェア開発を行います。

## エージェント（プロンプト）

14のエージェントプロンプトが利用可能です（`prompts/`ディレクトリ参照）:

### 要件・設計フェーズ
| プロンプト | ファイル | 用途 |
|-----------|----------|------|
| 要件定義 | `prompts/requirements.md` | PRD、ユースケース、ユーザーストーリー |
| 画面仕様 | `prompts/ui-spec.md` | 画面仕様書作成 |
| 基本設計 | `prompts/basic-design.md` | アーキテクチャ設計 |
| 詳細設計 | `prompts/detailed-design.md` | クラス設計、DB設計 |
| API仕様 | `prompts/api-spec.md` | OpenAPI仕様作成 |

### 実装・テスト・レビューフェーズ
| プロンプト | ファイル | 用途 |
|-----------|----------|------|
| 実装 | `prompts/implement.md` | 機能実装 |
| テスト | `prompts/tests.md` | 単体テスト作成 |
| E2E | `prompts/e2e.md` | E2Eテスト作成 |
| レビュー | `prompts/review.md` | コードレビュー |

### PMフェーズ
| プロンプト | ファイル | 用途 |
|-----------|----------|------|
| WBS | `prompts/pm-wbs.md` | 作業分解構造 |
| スケジュール | `prompts/pm-schedule.md` | ガントチャート/マイルストーン |
| リソース | `prompts/pm-resource.md` | リソース計画 |
| リスク | `prompts/pm-risk.md` | リスク管理 |
| 業務フロー | `prompts/pm-business-flow.md` | 業務フロー作成 |

## 開発フロー

```
要件定義 → 設計（画面/基本/詳細/API） → 実装 → テスト → レビュー → マージ
```

## 基本ルール

- リポジトリ標準に従う: ASCII、必要時のみコメント
- ExecPlan作成時は`.agent/PLANS.md`に従う
- 実行コマンドを明示する
- 小さなdiff、明確な理由、検証手順を示す
- レビューではリスク・バグ・リグレッションを最初に指摘
- APIを推測しない: 既存ファイルを先に読む
- 純粋関数と予測可能な副作用を優先

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

## 主要ファイル

| ファイル | 説明 |
|---------|------|
| `backendapp/main.py` | FastAPI バックエンド |
| `frontend/src/App.tsx` | React フロントエンド |
| `frontend/src/api.ts` | API クライアント |
| `csharp-backend/Program.cs` | C# Web API エントリ |
| `batch-csharp/Program.cs` | C# バッチ処理 |
| `java-backend/src/main/` | Java Spring Boot |

## ドキュメント出力先

| ドキュメント種別 | 配置先 |
|----------------|--------|
| 要件定義書 | `docs/requirements/` |
| 基本設計書 | `docs/design/basic/` |
| 詳細設計書 | `docs/design/detailed/` |
| API仕様書 | `docs/api/` |
| 画面仕様書 | `docs/ui-specs/` |

## 環境変数

| 変数 | 説明 |
|------|------|
| `VITE_API_BASE` | フロントエンドのAPI基点URL |
| `DATABASE_URL` | データベース接続文字列 |
| `JWT_SECRET` | JWT署名キー |

## セキュリティ

- 機密情報（.env, credentials等）をコミットしない
- 入力値のバリデーションを行う
- OWASP Top 10を考慮する
- SQLインジェクション、XSS対策を実装

## Claude Code/Codex連携

このプロジェクトはClaude CodeおよびCodexと連携できます：
- 共通エージェント定義: `AGENTS.md`
- Claude Code設定: `.claude/skills/`
- Codex設定: `.codex/agents/`
