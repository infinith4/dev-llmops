---
applyTo: "**/*.py"
description: Python/FastAPI コーディング規約
---

# Python/FastAPI Instructions

## コーディング規約

- PEP 8に準拠
- 型ヒント（Type Hints）を使用
- async/awaitパターンをサポート
- Black + Ruffでフォーマット

## 型ヒント

```python
from typing import Optional, List

def get_user(user_id: str) -> Optional[User]:
    """ユーザーを取得する"""
    ...

async def list_users(limit: int = 10) -> List[User]:
    """ユーザー一覧を取得する"""
    ...
```

## FastAPI エンドポイント

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: str

@router.post("/users", response_model=User)
async def create_user(data: UserCreate) -> User:
    """新規ユーザーを作成する"""
    ...
```

## エラーハンドリング

```python
from fastapi import HTTPException

if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

## 依存性注入

```python
from fastapi import Depends

async def get_db() -> AsyncGenerator[Session, None]:
    async with async_session() as session:
        yield session

@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    db: Session = Depends(get_db)
) -> User:
    ...
```

## テスト

- pytest を使用
- テストファイルは `test_*.py` または `*_test.py`
- フィクスチャを活用

```python
import pytest

@pytest.fixture
def client():
    return TestClient(app)

def test_create_user(client):
    response = client.post("/users", json={"name": "Test"})
    assert response.status_code == 200
```

## コマンド

```bash
pip install -r backendapp/requirements.txt
uvicorn backendapp.main:app --reload  # 開発サーバー
pytest tests/                          # テスト
ruff check .                           # リント
black .                                # フォーマット
```
