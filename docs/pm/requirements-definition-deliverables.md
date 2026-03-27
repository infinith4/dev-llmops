# PM向け 要件定義フェーズ成果物一覧

## 目的
PMが要件定義を計画・実行・承認するために必要な成果物を一覧化する。

## 成果物一覧

| 区分 | 成果物名 | ファイルパス | 主担当 | 完了条件 |
|------|----------|--------------|--------|----------|
| 計画 | 要件定義計画書 | `docs/pm/requirements-plan/plan.md` | PM | スコープ、体制、進め方、完了基準が定義済み |
| 計画 | ステークホルダーマップ | `docs/pm/requirements-plan/stakeholder-map.md` | PM | 関係者、責任、意思決定者が明確化済み |
| 計画 | 要件定義タイムライン | `docs/pm/requirements-plan/timeline.md` | PM | マイルストーンと依存関係が定義済み |
| 計画 | コミュニケーション計画 | `docs/pm/requirements-plan/communication.md` | PM | 会議体、報告頻度、連絡手段が定義済み |
| 計画 | レビュー・承認計画 | `docs/pm/requirements-plan/review-and-approval.md` | PM | レビュー手順、承認者、ゲートが定義済み |
| 要件 | PRD（プロダクト要件定義書） | `docs/requirements/PRD.md` | PM/BA | 目的、スコープ、成功指標が合意済み |
| 要件 | 機能要件一覧 | `docs/requirements/functional/FR-XXX-*.md` | BA | 機能要件ID、優先度、受入基準が定義済み |
| 要件 | 非機能要件 | `docs/requirements/non-functional/NFR.md` | PM/Architect | 性能・可用性・セキュリティ要件が定義済み |
| 要件 | ユースケース | `docs/requirements/use-cases/UC-XXX-*.md` | BA | 基本フロー・代替フローが定義済み |
| 要件 | ユーザーストーリー | `docs/requirements/user-stories/US-XXX-*.md` | PO/BA | Gherkin形式の受入基準が定義済み |
| 要件 | トレーサビリティ | `docs/requirements/traceability.md` | PM/BA | 要件と成果物・テストの対応が追跡可能 |

## 運用ルール
- 優先度は `Must / Should / Could / Won't` を使用する。
- すべての成果物に作成日、更新日、版数、責任者を記載する。
- 承認済み成果物のみをベースライン化し、変更は変更履歴に残す。
