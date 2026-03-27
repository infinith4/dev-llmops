# Copilot Custom Instructions

このファイルはGitHub Copilotがこのリポジトリで作業する際のグローバルなガイダンスを提供します。

## プロジェクト概要

AI駆動開発プロジェクトです。GitHub Copilot、Codex、Claude Codeを使用して効率的なソフトウェア開発を行います。

## 対応言語・プロジェクト構成

| 言語 | ディレクトリ | フレームワーク |
|------|-------------|---------------|
| TypeScript | `frontend/` | React, Vite |
| Python | `backendapp/` | FastAPI |
| C# | `csharp-backend/` | .NET 9, Web API |
| C# | `batch-csharp/` | .NET 9, Console |
| Java | `java-backend/` | Spring Boot, Maven |

## 基本ルール

### コーディング規約
- クリーンコードの原則に従う
- 適切なエラーハンドリングを実装
- セキュリティを考慮した実装（OWASP Top 10）
- テスト可能な設計を心がける
- 純粋関数と予測可能な副作用を優先

### 作業スタイル
- リポジトリ標準に従う: ASCII、必要時のみコメント
- 小さなdiff、明確な理由、検証手順を示す
- APIを推測しない: 既存ファイルを先に読む
- 実行コマンドを明示する

## ドキュメント出力先

| ドキュメント種別 | 配置先 |
|----------------|--------|
| 要件定義書 | `docs/requirements/` |
| 基本設計書 | `docs/design/basic/` |
| 詳細設計書 | `docs/design/detailed/` |
| API仕様書 | `docs/api/` |
| 画面仕様書 | `docs/ui-specs/` |
| PM成果物 | `docs/pm/` |

## 主要ファイル

| ファイル | 説明 |
|---------|------|
| `backendapp/main.py` | FastAPI バックエンド |
| `frontend/src/App.tsx` | React フロントエンド |
| `frontend/src/api.ts` | API クライアント |
| `csharp-backend/Program.cs` | C# Web API エントリ |
| `batch-csharp/Program.cs` | C# バッチ処理 |
| `java-backend/src/main/` | Java Spring Boot |

## セキュリティ

- 機密情報（.env, credentials等）をコミットしない
- 入力値のバリデーションを行う
- SQLインジェクション、XSS対策を実装
- 認証・認可の適切な実装

## 環境変数

| 変数 | 説明 |
|------|------|
| `VITE_API_BASE` | フロントエンドのAPI基点URL |
| `DATABASE_URL` | データベース接続文字列 |
| `JWT_SECRET` | JWT署名キー |

## エージェント定義

共通エージェント定義は `AGENTS.md` を参照してください。
13のエージェント（開発9種 + PM4種）が定義されています。
