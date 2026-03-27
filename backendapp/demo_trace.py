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


@observe(name="rag-pipeline")
def demo_multi_step_trace():
    """Create a multi-step RAG pipeline trace."""
    # Step 1: Query rewriting
    rewrite_span = langfuse.start_observation(
        name="query-rewrite",
        as_type="span",
        input={"original_query": "Langfuseとは何ですか？"},
    )

    rewrite_gen = rewrite_span.start_observation(
        name="rewrite-llm",
        as_type="generation",
        model="openai/gpt-4o-mini",
        input=[{"role": "user", "content": "Rephrase: Langfuseとは何ですか？"}],
        output={
            "role": "assistant",
            "content": "What is Langfuse? Explain its features for LLM observability.",
        },
        usage_details={"input": 20, "output": 15},
    )
    rewrite_gen.end()

    rewrite_span.update(
        output={"rewritten_query": "What is Langfuse? LLM observability"}
    )
    rewrite_span.end()

    # Step 2: Vector search
    search_span = langfuse.start_observation(
        name="vector-search",
        as_type="retriever",
        input={"query": "What is Langfuse? LLM observability"},
        metadata={"index": "docs-v2", "top_k": 3},
    )
    search_span.update(
        output={
            "documents": [
                "Langfuse is an open-source LLM engineering platform.",
                "Langfuse provides tracing, prompt management, and evaluation.",
                "Langfuse supports OpenAI, Anthropic, and other providers.",
            ]
        }
    )
    search_span.end()

    # Step 3: Answer generation
    answer_gen = langfuse.start_observation(
        name="answer-generation",
        as_type="generation",
        model="anthropic/claude-sonnet-4-20250514",
        model_parameters={"temperature": 0.3, "max_tokens": 512},
        input=[
            {
                "role": "system",
                "content": "コンテキストに基づいて日本語で回答してください。",
            },
            {
                "role": "user",
                "content": (
                    "質問: Langfuseとは何ですか？\n\n"
                    "コンテキスト:\n"
                    "- Langfuse is an open-source LLM engineering platform.\n"
                    "- Langfuse provides tracing, prompt management, and evaluation.\n"
                    "- Langfuse supports OpenAI, Anthropic, and other providers."
                ),
            },
        ],
        output={
            "role": "assistant",
            "content": (
                "Langfuseは、オープンソースのLLMエンジニアリングプラットフォームです。"
                "主な機能として、トレーシング、プロンプト管理、評価機能を提供しています。"
                "OpenAI、Anthropicなど複数のLLMプロバイダーをサポートしています。"
            ),
        },
        usage_details={"input": 150, "output": 80},
    )
    answer_gen.end()

    trace_id = langfuse.get_current_trace_id()
    print(f"  [rag-pipeline] trace_id={trace_id}")
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
