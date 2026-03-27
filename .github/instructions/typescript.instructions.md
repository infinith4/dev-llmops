---
applyTo: "**/*.ts,**/*.tsx"
description: TypeScript/React コーディング規約
---

# TypeScript/React Instructions

## コーディング規約

- ESLint + Prettierの規約に準拠
- 厳格な型定義（`strict: true`）
- async/awaitパターンを使用
- Reactコンポーネントは関数コンポーネントを優先

## 型定義

```typescript
// 明示的な型定義を使用
interface User {
  id: string;
  name: string;
  email: string;
}

// 型推論が明確な場合は省略可
const items = ['a', 'b', 'c'];
```

## React コンポーネント

```typescript
// 関数コンポーネントを使用
interface Props {
  title: string;
  onClick: () => void;
}

export const Button: React.FC<Props> = ({ title, onClick }) => {
  return <button onClick={onClick}>{title}</button>;
};
```

## 非同期処理

```typescript
// async/await を優先
async function fetchData(): Promise<Data> {
  const response = await fetch('/api/data');
  return response.json();
}
```

## エラーハンドリング

```typescript
try {
  await riskyOperation();
} catch (error) {
  if (error instanceof CustomError) {
    // 型安全なエラー処理
  }
  throw error;
}
```

## テスト

- Jest / Vitest を使用
- テストファイルは `*.test.ts` または `*.spec.ts`
- AAA パターン (Arrange-Act-Assert)

## コマンド

```bash
cd frontend
npm install       # 依存関係インストール
npm run dev       # 開発サーバー
npm run build     # ビルド
npm test          # テスト
npm run lint      # リント
```
