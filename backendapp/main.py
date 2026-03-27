"""FastAPI backend with LLM chat endpoint and Langfuse tracing."""

from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

from backendapp.llm_service import call_llm  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # Flush Langfuse events on shutdown
    from langfuse.decorators import langfuse_context

    langfuse_context.flush()


app = FastAPI(
    title="LLMOps Backend",
    description="FastAPI backend with multi-provider LLM support and Langfuse tracing",
    version="0.1.0",
    lifespan=lifespan,
)
app.openapi_version = "3.0.3"


# --- Health Check ---


@app.get("/health")
def health():
    return {"status": "ok"}


# --- Chat Endpoint ---


class ChatRequest(BaseModel):
    message: str
    model: str = "openai/gpt-4o"
    system: Optional[str] = None
    max_tokens: int = 1024


class ChatResponse(BaseModel):
    response: str
    model: str


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a message to an LLM and get a response.

    All calls are automatically traced in Langfuse.

    Supported model formats:
    - openai/gpt-4o
    - anthropic/claude-sonnet-4-20250514
    - azure/gpt-4o
    - gemini/gemini-pro
    """
    try:
        response_text = call_llm(
            prompt=request.message,
            model=request.model,
            system=request.system or "",
            max_tokens=request.max_tokens,
        )
        return ChatResponse(response=response_text, model=request.model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Item CRUD (in-memory, from execplan-fastapi-backend) ---

_items: dict[int, dict] = {}
_next_id = 1


class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tags: list[str] = []


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    tags: Optional[list[str]] = None


class Item(ItemBase):
    id: int


@app.get("/items", response_model=list[Item])
def list_items():
    return [Item(id=k, **v) for k, v in _items.items()]


@app.post("/items", response_model=Item, status_code=201)
def create_item(item: ItemCreate):
    global _next_id
    item_id = _next_id
    _next_id += 1
    _items[item_id] = item.model_dump()
    return Item(id=item_id, **_items[item_id])


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(id=item_id, **_items[item_id])


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemUpdate):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    update_data = item.model_dump(exclude_unset=True)
    _items[item_id].update(update_data)
    return Item(id=item_id, **_items[item_id])


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id not in _items:
        raise HTTPException(status_code=404, detail="Item not found")
    del _items[item_id]
    return {"status": "deleted", "id": item_id}
