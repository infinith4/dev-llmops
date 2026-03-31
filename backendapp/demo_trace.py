"""Demo script to send tracing and evaluation data to Langfuse.

Usage:
    python -m backendapp.demo_trace

No LLM API key required — uses mock data to demonstrate
Langfuse tracing, spans, generations, scores, and LLM-as-a-Judge evaluations.
"""

import os
import time

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from langfuse import Langfuse, observe

langfuse = Langfuse()


@observe(name="demo-chat")
def demo_basic_trace():
    """Create a basic trace with a generation and score."""
    # Simulate retrieval span
    retrieval_span = langfuse.start_observation(
        name="context-retrieval",
        as_type="retriever",
        input={"query": "フィボナッチ数列 Python"},
        metadata={"retriever": "mock"},
    )
    retrieval_span.update(
        output={"documents": ["フィボナッチ数列は前の2つの数を足して..."]},
        metadata={"num_results": 1},
    )
    retrieval_span.end()

    # Simulate LLM generation
    generation = langfuse.start_observation(
        name="llm-response",
        as_type="generation",
        model="openai/gpt-4o",
        model_parameters={"temperature": 0.7, "max_tokens": 1024},
        input=[
            {"role": "system", "content": "あなたは優秀なプログラマーです。"},
            {"role": "user", "content": "Pythonでフィボナッチ数列を書いて"},
        ],
        output={
            "role": "assistant",
            "content": (
                "def fibonacci(n):\n"
                "    if n <= 1:\n"
                "        return n\n"
                "    a, b = 0, 1\n"
                "    for _ in range(2, n + 1):\n"
                "        a, b = b, a + b\n"
                "    return b\n\n"
                "# 最初の10項を表示\n"
                "for i in range(10):\n"
                '    print(fibonacci(i))'
            ),
        },
        usage_details={"input": 45, "output": 120},
        metadata={"provider": "openai"},
    )
    generation.end()

    # User feedback score on current trace
    langfuse.score_current_trace(
        name="user-feedback", value=1.0, comment="正確なコードだった"
    )

    trace_id = langfuse.get_current_trace_id()
    print(f"  [basic-trace] trace_id={trace_id}")
    return trace_id


@observe(name="agentic-rag-pipeline")
def demo_multi_step_trace():
    """Create a complex agentic RAG pipeline trace.

    Trace structure:
    agentic-rag-pipeline
    ├── input-guardrail           (guardrail)
    │   └── moderation-check        (generation)
    ├── intent-classification     (span)
    │   └── classify-llm            (generation)
    ├── query-decomposition       (span)
    │   └── decompose-llm          (generation)
    ├── parallel-retrieval        (span)
    │   ├── vector-search           (retriever)
    │   │   └── embedding           (embedding)
    │   ├── keyword-search          (retriever)
    │   └── web-search              (tool)
    ├── rerank-and-fuse           (span)
    │   └── rerank-llm             (generation)
    ├── context-compression       (span)
    │   └── compress-llm           (generation)
    ├── answer-generation         (chain)
    │   ├── draft-answer            (generation)
    │   ├── tool-call-execution     (tool)
    │   │   └── code-interpreter      (span)
    │   └── final-answer            (generation)
    ├── output-guardrail          (guardrail)
    │   └── safety-check            (generation)
    └── response-formatting       (span)
    """
    user_query = "LangfuseとLangSmithの違いを比較して、それぞれの料金体系も教えて"

    # ── Step 1: Input Guardrail ──
    guardrail_in = langfuse.start_observation(
        name="input-guardrail",
        as_type="guardrail",
        input={"user_query": user_query},
        metadata={"policy": "content-safety-v2"},
    )
    moderation = guardrail_in.start_observation(
        name="moderation-check",
        as_type="generation",
        model="openai/gpt-4o-mini",
        model_parameters={"temperature": 0.0},
        input=[
            {"role": "system", "content": "Classify if the query is safe. Return JSON."},
            {"role": "user", "content": user_query},
        ],
        output={
            "role": "assistant",
            "content": '{"safe": true, "category": "technical_comparison", "confidence": 0.98}',
        },
        usage_details={"input": 35, "output": 18},
    )
    moderation.end()
    guardrail_in.update(output={"passed": True, "category": "technical_comparison"})
    guardrail_in.end()

    # ── Step 2: Intent Classification ──
    intent_span = langfuse.start_observation(
        name="intent-classification",
        as_type="span",
        input={"query": user_query},
    )
    intent_gen = intent_span.start_observation(
        name="classify-llm",
        as_type="generation",
        model="openai/gpt-4o-mini",
        model_parameters={"temperature": 0.0},
        input=[
            {
                "role": "system",
                "content": (
                    "Classify the user intent. Categories: "
                    "factual_qa, comparison, how_to, opinion, pricing, multi_intent"
                ),
            },
            {"role": "user", "content": user_query},
        ],
        output={
            "role": "assistant",
            "content": '{"primary": "comparison", "secondary": ["pricing"], "entities": ["Langfuse", "LangSmith"]}',
        },
        usage_details={"input": 50, "output": 25},
    )
    intent_gen.end()
    intent_span.update(
        output={"intent": "comparison", "sub_intents": ["pricing"], "entities": ["Langfuse", "LangSmith"]}
    )
    intent_span.end()

    # ── Step 3: Query Decomposition ──
    decomp_span = langfuse.start_observation(
        name="query-decomposition",
        as_type="span",
        input={"query": user_query, "intent": "comparison"},
    )
    decomp_gen = decomp_span.start_observation(
        name="decompose-llm",
        as_type="generation",
        model="openai/gpt-4o",
        model_parameters={"temperature": 0.2},
        input=[
            {
                "role": "system",
                "content": "Break down the user query into independent sub-queries for retrieval.",
            },
            {"role": "user", "content": user_query},
        ],
        output={
            "role": "assistant",
            "content": (
                '{"sub_queries": ['
                '"Langfuseの主な機能と特徴", '
                '"LangSmithの主な機能と特徴", '
                '"LangfuseとLangSmithの機能比較", '
                '"Langfuseの料金体系・プラン", '
                '"LangSmithの料金体系・プラン"'
                "]}"
            ),
        },
        usage_details={"input": 55, "output": 60},
    )
    decomp_gen.end()
    sub_queries = [
        "Langfuseの主な機能と特徴",
        "LangSmithの主な機能と特徴",
        "LangfuseとLangSmithの機能比較",
        "Langfuseの料金体系・プラン",
        "LangSmithの料金体系・プラン",
    ]
    decomp_span.update(output={"sub_queries": sub_queries})
    decomp_span.end()

    # ── Step 4: Parallel Retrieval (3 sources) ──
    retrieval_span = langfuse.start_observation(
        name="parallel-retrieval",
        as_type="span",
        input={"sub_queries": sub_queries},
        metadata={"strategy": "multi-source-fusion"},
    )

    # 4a. Vector search (with embedding sub-span)
    vec_search = retrieval_span.start_observation(
        name="vector-search",
        as_type="retriever",
        input={"queries": sub_queries, "top_k": 5},
        metadata={"index": "docs-v3", "provider": "pgvector"},
    )
    embedding = vec_search.start_observation(
        name="embedding",
        as_type="embedding",
        model="openai/text-embedding-3-small",
        input=sub_queries,
        usage_details={"input": 85},
        metadata={"dimensions": 1536},
    )
    embedding.end()
    vec_search.update(
        output={
            "documents": [
                {"id": "doc-001", "score": 0.94, "text": "Langfuse is an open-source LLM engineering platform with tracing, prompt management, and evaluation."},
                {"id": "doc-002", "score": 0.91, "text": "LangSmith is LangChain's platform for debugging, testing, evaluating, and monitoring LLM applications."},
                {"id": "doc-003", "score": 0.88, "text": "Langfuse offers a free self-hosted option and a cloud plan starting at $59/month."},
                {"id": "doc-004", "score": 0.85, "text": "LangSmith pricing starts with a free Developer plan, Plus at $39/seat/month."},
                {"id": "doc-005", "score": 0.82, "text": "Both platforms support OpenAI, Anthropic, and custom model integrations."},
            ]
        }
    )
    vec_search.end()

    # 4b. Keyword search (BM25)
    kw_search = retrieval_span.start_observation(
        name="keyword-search",
        as_type="retriever",
        input={"queries": sub_queries[:3], "method": "BM25"},
        metadata={"index": "docs-bm25", "provider": "elasticsearch"},
    )
    kw_search.update(
        output={
            "documents": [
                {"id": "doc-010", "score": 12.5, "text": "Langfuse provides native integrations with LangChain, LlamaIndex, OpenAI SDK, and custom frameworks."},
                {"id": "doc-011", "score": 11.2, "text": "LangSmith is tightly integrated with LangChain ecosystem but also supports non-LangChain applications."},
                {"id": "doc-012", "score": 9.8, "text": "Key difference: Langfuse is open-source (MIT license), while LangSmith is proprietary."},
            ]
        }
    )
    kw_search.end()

    # 4c. Web search (for up-to-date pricing)
    web_tool = retrieval_span.start_observation(
        name="web-search",
        as_type="tool",
        input={"query": "Langfuse vs LangSmith pricing 2026", "engine": "tavily"},
        metadata={"max_results": 3},
    )
    web_tool.update(
        output={
            "results": [
                {"url": "https://langfuse.com/pricing", "snippet": "Langfuse Cloud: Hobby (free, 50k observations/mo), Pro ($59/mo, 1M observations/mo), Team ($199/mo)."},
                {"url": "https://smith.langchain.com/pricing", "snippet": "LangSmith: Developer (free, 5k traces/mo), Plus ($39/seat/mo), Enterprise (custom)."},
                {"url": "https://example.com/comparison", "snippet": "2026 comparison: Langfuse self-hosted is free with unlimited data. LangSmith requires cloud for full features."},
            ]
        }
    )
    web_tool.end()

    retrieval_span.update(output={"total_documents": 11, "sources": ["vector", "keyword", "web"]})
    retrieval_span.end()

    # ── Step 5: Rerank & Fuse ──
    rerank_span = langfuse.start_observation(
        name="rerank-and-fuse",
        as_type="span",
        input={"num_candidates": 11, "target_k": 6},
        metadata={"algorithm": "reciprocal-rank-fusion + LLM-rerank"},
    )
    rerank_gen = rerank_span.start_observation(
        name="rerank-llm",
        as_type="generation",
        model="openai/gpt-4o-mini",
        model_parameters={"temperature": 0.0},
        input=[
            {
                "role": "system",
                "content": "Rerank the following documents by relevance to the query. Return top 6 doc IDs.",
            },
            {
                "role": "user",
                "content": f"Query: {user_query}\nDocuments: [doc-001..doc-012, web-001..web-003]",
            },
        ],
        output={
            "role": "assistant",
            "content": '{"ranked": ["doc-012", "doc-001", "doc-002", "web-001", "web-002", "doc-003"]}',
        },
        usage_details={"input": 320, "output": 30},
    )
    rerank_gen.end()
    rerank_span.update(
        output={
            "selected_docs": ["doc-012", "doc-001", "doc-002", "web-001", "web-002", "doc-003"],
            "rrf_scores": [0.95, 0.92, 0.89, 0.87, 0.84, 0.80],
        }
    )
    rerank_span.end()

    # ── Step 6: Context Compression ──
    compress_span = langfuse.start_observation(
        name="context-compression",
        as_type="span",
        input={"num_docs": 6, "total_tokens_before": 480},
        metadata={"method": "extractive-summary"},
    )
    compress_gen = compress_span.start_observation(
        name="compress-llm",
        as_type="generation",
        model="openai/gpt-4o-mini",
        model_parameters={"temperature": 0.0, "max_tokens": 300},
        input=[
            {
                "role": "system",
                "content": "Compress the following documents into a concise context, preserving all key facts.",
            },
            {
                "role": "user",
                "content": "[6 documents about Langfuse vs LangSmith features and pricing]",
            },
        ],
        output={
            "role": "assistant",
            "content": (
                "## Langfuse\n"
                "- OSS (MIT), self-hosted free, Cloud: Hobby(free)/Pro($59/mo)/Team($199/mo)\n"
                "- Tracing, prompt mgmt, evaluation, datasets\n"
                "- Integrations: LangChain, LlamaIndex, OpenAI SDK, custom\n\n"
                "## LangSmith\n"
                "- Proprietary, Developer(free)/Plus($39/seat/mo)/Enterprise\n"
                "- Debugging, testing, evaluation, monitoring\n"
                "- Deep LangChain integration, supports non-LangChain too\n\n"
                "## Key Difference\n"
                "- Langfuse: open-source, self-hostable, vendor-neutral\n"
                "- LangSmith: proprietary, LangChain-ecosystem-first"
            ),
        },
        usage_details={"input": 480, "output": 120},
    )
    compress_gen.end()
    compress_span.update(output={"total_tokens_after": 120, "compression_ratio": 0.25})
    compress_span.end()

    # ── Step 7: Answer Generation (multi-turn chain with tool call) ──
    answer_chain = langfuse.start_observation(
        name="answer-generation",
        as_type="chain",
        input={"query": user_query, "context_tokens": 120},
        metadata={"strategy": "chain-of-thought + tool-augmented"},
    )

    # 7a. Draft answer (with tool call request)
    draft_gen = answer_chain.start_observation(
        name="draft-answer",
        as_type="generation",
        model="anthropic/claude-sonnet-4-20250514",
        model_parameters={"temperature": 0.3, "max_tokens": 1024},
        input=[
            {
                "role": "system",
                "content": (
                    "あなたは技術比較の専門家です。コンテキストに基づいて正確な比較表を作成してください。"
                    "必要に応じてツールを使用できます。"
                ),
            },
            {"role": "user", "content": f"{user_query}\n\n[compressed context]"},
        ],
        output={
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "tc-001",
                    "type": "function",
                    "function": {
                        "name": "create_comparison_table",
                        "arguments": '{"products": ["Langfuse", "LangSmith"], "criteria": ["license", "pricing", "tracing", "evaluation", "integrations"]}',
                    },
                }
            ],
        },
        usage_details={"input": 280, "output": 65},
    )
    draft_gen.end()

    # 7b. Tool execution
    tool_exec = answer_chain.start_observation(
        name="tool-call-execution",
        as_type="tool",
        input={
            "tool": "create_comparison_table",
            "args": {"products": ["Langfuse", "LangSmith"], "criteria": ["license", "pricing", "tracing", "evaluation", "integrations"]},
        },
    )
    code_span = tool_exec.start_observation(
        name="code-interpreter",
        as_type="span",
        input={"code": "generate_markdown_table(products, criteria, data)"},
        metadata={"runtime": "python-sandbox"},
    )
    code_span.update(
        output={
            "table": (
                "| 観点 | Langfuse | LangSmith |\n"
                "|------|----------|----------|\n"
                "| ライセンス | MIT (OSS) | プロプライエタリ |\n"
                "| 料金 (無料枠) | 50k obs/月 | 5k traces/月 |\n"
                "| 料金 (有料) | $59/月~ | $39/席/月~ |\n"
                "| セルフホスト | 可 (無料・無制限) | 不可 |\n"
                "| トレーシング | 全プロバイダー対応 | LangChain最適化 |\n"
                "| 評価機能 | LLM-as-Judge, データセット | オンライン/オフライン評価 |\n"
                "| 連携 | LangChain, LlamaIndex, OpenAI SDK | LangChain中心, 他も対応 |"
            )
        }
    )
    code_span.end()
    tool_exec.update(output={"status": "success", "result_type": "markdown_table"})
    tool_exec.end()

    # 7c. Final answer (incorporating tool result)
    final_gen = answer_chain.start_observation(
        name="final-answer",
        as_type="generation",
        model="anthropic/claude-sonnet-4-20250514",
        model_parameters={"temperature": 0.3, "max_tokens": 1024},
        input=[
            {
                "role": "system",
                "content": "コンテキストとツール結果を使って最終回答を生成してください。",
            },
            {"role": "user", "content": user_query},
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [{"id": "tc-001", "type": "function", "function": {"name": "create_comparison_table"}}],
            },
            {
                "role": "tool",
                "tool_call_id": "tc-001",
                "content": "[comparison table markdown]",
            },
        ],
        output={
            "role": "assistant",
            "content": (
                "## LangfuseとLangSmithの比較\n\n"
                "どちらもLLMアプリケーションの開発・運用を支援するプラットフォームですが、"
                "設計思想と料金体系に大きな違いがあります。\n\n"
                "### 主な違い\n\n"
                "| 観点 | Langfuse | LangSmith |\n"
                "|------|----------|----------|\n"
                "| ライセンス | MIT (OSS) | プロプライエタリ |\n"
                "| 料金 (無料枠) | 50k obs/月 | 5k traces/月 |\n"
                "| 料金 (有料) | $59/月~ | $39/席/月~ |\n"
                "| セルフホスト | 可 (無料・無制限) | 不可 |\n\n"
                "### 料金体系\n\n"
                "**Langfuse**: Hobby(無料)→Pro($59/月, 1M obs)→Team($199/月)。"
                "セルフホストなら完全無料で制限なし。\n\n"
                "**LangSmith**: Developer(無料, 5k traces)→Plus($39/席/月)→Enterprise(要問合せ)。\n\n"
                "### まとめ\n\n"
                "ベンダーロックインを避けたい場合やセルフホストが必要な場合は **Langfuse**、"
                "LangChain エコシステムを中心に使っている場合は **LangSmith** が適しています。"
            ),
        },
        usage_details={"input": 450, "output": 280},
    )
    final_gen.end()
    answer_chain.update(output={"answer_tokens": 280, "tool_calls_count": 1})
    answer_chain.end()

    # ── Step 8: Output Guardrail ──
    guardrail_out = langfuse.start_observation(
        name="output-guardrail",
        as_type="guardrail",
        input={"answer_length": 280},
        metadata={"checks": ["factuality", "bias", "pii"]},
    )
    safety_gen = guardrail_out.start_observation(
        name="safety-check",
        as_type="generation",
        model="openai/gpt-4o-mini",
        model_parameters={"temperature": 0.0},
        input=[
            {
                "role": "system",
                "content": "Check the response for: factual errors, unfair bias, PII leakage. Return JSON.",
            },
            {"role": "user", "content": "[final answer text]"},
        ],
        output={
            "role": "assistant",
            "content": '{"factuality": "pass", "bias": "pass", "pii": "pass", "overall": "safe"}',
        },
        usage_details={"input": 300, "output": 20},
    )
    safety_gen.end()
    guardrail_out.update(output={"passed": True, "checks": {"factuality": "pass", "bias": "pass", "pii": "pass"}})
    guardrail_out.end()

    # ── Step 9: Response Formatting ──
    format_span = langfuse.start_observation(
        name="response-formatting",
        as_type="span",
        input={"format": "markdown", "locale": "ja"},
        metadata={"includes_table": True},
    )
    format_span.update(
        output={"formatted": True, "sections": ["comparison_table", "pricing", "summary"]}
    )
    format_span.end()

    trace_id = langfuse.get_current_trace_id()
    print(f"  [agentic-rag] trace_id={trace_id}")
    return trace_id


def demo_llm_as_judge(trace_id: str):
    """Simulate LLM-as-a-Judge evaluation and attach scores to an existing trace."""
    evaluations = [
        {
            "name": "relevance",
            "value": 0.9,
            "comment": "回答は質問に対して高い関連性がある",
        },
        {
            "name": "faithfulness",
            "value": 0.85,
            "comment": "コンテキストに忠実だが、一部補足情報が追加されている",
        },
        {
            "name": "helpfulness",
            "value": 1.0,
            "comment": "ユーザーの質問に十分に答えている",
        },
        {
            "name": "toxicity",
            "value": 0.0,
            "comment": "有害なコンテンツは含まれていない",
        },
    ]

    _run_judge(trace_id, evaluations)
    print(f"  [llm-as-judge] Attached {len(evaluations)} scores to trace_id={trace_id}")


@observe(name="llm-as-judge")
def _run_judge(target_trace_id: str, evaluations: list[dict]):
    """Run the LLM judge and record scores on the target trace."""
    judge_gen = langfuse.start_observation(
        name="judge-reasoning",
        as_type="generation",
        model="openai/gpt-4o",
        model_parameters={"temperature": 0.0},
        input=[
            {
                "role": "system",
                "content": (
                    "You are an evaluation judge. Score the following response "
                    "on relevance, faithfulness, helpfulness, and toxicity."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Question: Langfuseとは何ですか？\n"
                    "Response: Langfuseはオープンソースのプラットフォームです...\n"
                    "Context: Langfuse is an open-source LLM engineering platform."
                ),
            },
        ],
        output={
            "role": "assistant",
            "content": (
                "Evaluation:\n"
                "- Relevance: 0.9 — 回答は質問に対して高い関連性がある\n"
                "- Faithfulness: 0.85 — コンテキストに忠実\n"
                "- Helpfulness: 1.0 — 十分な回答\n"
                "- Toxicity: 0.0 — 有害コンテンツなし"
            ),
        },
        usage_details={"input": 100, "output": 60},
    )
    judge_gen.end()

    # Attach scores to the target trace (the one being evaluated)
    for ev in evaluations:
        langfuse.create_score(
            trace_id=target_trace_id,
            name=ev["name"],
            value=ev["value"],
            comment=ev["comment"],
            data_type="NUMERIC",
        )


def demo_dataset_evaluation():
    """Create a dataset with test cases and run evaluations."""
    langfuse.create_dataset(
        name="qa-evaluation-set",
        description="Q&Aの品質評価用データセット",
        metadata={"version": "1.0"},
    )

    test_cases = [
        {
            "input": {"question": "Pythonのリスト内包表記とは？"},
            "expected_output": "リスト内包表記は、forループを1行で書ける構文です。",
        },
        {
            "input": {"question": "RESTとGraphQLの違いは？"},
            "expected_output": "RESTはリソースごとにエンドポイントを持ち、GraphQLは単一エンドポイントでクエリを柔軟に記述できます。",
        },
        {
            "input": {"question": "Docker Composeの用途は？"},
            "expected_output": "複数のDockerコンテナを定義・管理し、一括で起動・停止できるツールです。",
        },
    ]

    for tc in test_cases:
        langfuse.create_dataset_item(
            dataset_name="qa-evaluation-set",
            input=tc["input"],
            expected_output=tc["expected_output"],
        )

    for tc in test_cases:
        _run_dataset_item(tc)

    print(f"  [dataset] Created dataset with {len(test_cases)} items")


@observe(name="dataset-run")
def _run_dataset_item(tc: dict):
    """Run a single dataset test case."""
    generation = langfuse.start_observation(
        name="answer",
        as_type="generation",
        model="openai/gpt-4o",
        input=[{"role": "user", "content": tc["input"]["question"]}],
        output={"role": "assistant", "content": tc["expected_output"]},
        usage_details={"input": 30, "output": 40},
    )
    generation.end()

    langfuse.score_current_trace(
        name="correctness", value=1.0, comment="期待出力と一致"
    )


def main():
    print("=== Langfuse Demo: Tracing & LLM-as-a-Judge ===\n")
    print(f"Langfuse Host: {os.getenv('LANGFUSE_HOST', 'not set')}")
    print()

    print("1. Basic trace with generation and score...")
    demo_basic_trace()

    print("2. Multi-step RAG pipeline trace...")
    rag_trace_id = demo_multi_step_trace()

    print("3. LLM-as-a-Judge evaluation...")
    demo_llm_as_judge(rag_trace_id)

    print("4. Dataset evaluation run...")
    demo_dataset_evaluation()

    print("\nFlushing to Langfuse...")
    langfuse.flush()
    time.sleep(2)

    print("\nDone! Check Langfuse UI: http://localhost:3600")
    print("  - Traces: http://localhost:3600/project/my-project/traces")
    print("  - Datasets: http://localhost:3600/project/my-project/datasets")


if __name__ == "__main__":
    main()
