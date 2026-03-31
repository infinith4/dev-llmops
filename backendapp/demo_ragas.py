"""Demo script to run Ragas evaluation and report scores to Langfuse.

Usage:
    python -m backendapp.demo_ragas

Prerequisite:
    python -m backendapp.demo_trace  (creates traces and dataset in Langfuse)

Mode A (default): Non-LLM metrics only (no API key required)
Mode B: Set OPENAI_API_KEY for LLM-based metrics (Faithfulness, etc.)
"""

import asyncio
import os
import time

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from langfuse import Evaluation, Langfuse
from ragas.metrics.collections import BleuScore, NonLLMStringSimilarity, RougeScore

langfuse = Langfuse()

# ── Evaluation data (mirrors demo_trace.py mock data) ──

RAG_EVAL_DATA = [
    {
        "user_input": "LangfuseとLangSmithの違いを比較して、それぞれの料金体系も教えて",
        "retrieved_contexts": [
            "Langfuse is an open-source LLM engineering platform with tracing, prompt management, and evaluation.",
            "LangSmith is LangChain's platform for debugging, testing, evaluating, and monitoring LLM applications.",
            "Langfuse offers a free self-hosted option and a cloud plan starting at $59/month.",
            "LangSmith pricing starts with a free Developer plan, Plus at $39/seat/month.",
            "Key difference: Langfuse is open-source (MIT license), while LangSmith is proprietary.",
        ],
        "response": (
            "Langfuseは、オープンソースのLLMエンジニアリングプラットフォームです。"
            "主な機能として、トレーシング、プロンプト管理、評価機能を提供しています。"
            "OpenAI、Anthropicなど複数のLLMプロバイダーをサポートしています。"
        ),
        "reference": (
            "Langfuseはオープンソース(MIT)のLLMエンジニアリングプラットフォームで、"
            "トレーシング、プロンプト管理、評価機能を提供する。"
            "料金はセルフホスト無料、Cloud Hobby無料、Pro $59/月。"
            "LangSmithはLangChainのプロプライエタリプラットフォームで、"
            "Developer無料、Plus $39/席/月。"
        ),
    },
    {
        "user_input": "Pythonのリスト内包表記とは？",
        "retrieved_contexts": [],
        "response": "リスト内包表記は、forループを1行で書ける構文です。",
        "reference": "リスト内包表記は、forループを1行で書ける構文です。",
    },
    {
        "user_input": "RESTとGraphQLの違いは？",
        "retrieved_contexts": [],
        "response": "RESTはリソースごとにエンドポイントを持ち、GraphQLは単一エンドポイントでクエリを柔軟に記述できます。",
        "reference": "RESTはリソースごとにエンドポイントを持ち、GraphQLは単一エンドポイントでクエリを柔軟に記述できます。",
    },
    {
        "user_input": "Docker Composeの用途は？",
        "retrieved_contexts": [],
        "response": "複数のDockerコンテナを定義・管理し、一括で起動・停止できるツールです。",
        "reference": "複数のDockerコンテナを定義・管理し、一括で起動・停止できるツールです。",
    },
]


def has_llm_api_key() -> bool:
    """Check if an LLM API key is available for Ragas LLM-based metrics."""
    key = os.getenv("OPENAI_API_KEY", "")
    return bool(key) and key != "sk-xxx"


def get_non_llm_metrics():
    return [NonLLMStringSimilarity(), BleuScore(), RougeScore()]


def get_llm_metrics():
    from ragas.metrics.collections import (
        AnswerCorrectness,
        AnswerRelevancy,
        Faithfulness,
    )

    return [Faithfulness(), AnswerRelevancy(), AnswerCorrectness()]


def get_metrics():
    metrics = get_non_llm_metrics()
    if has_llm_api_key():
        metrics += get_llm_metrics()
    return metrics


# ── Demo 1: Standalone Ragas evaluation ──


def demo_standalone():
    """Run Ragas metrics on local data and print results."""
    metrics = get_metrics()
    metric_names = [m.name for m in metrics]

    print(f"  Metrics: {', '.join(metric_names)}")
    print(f"  Samples: {len(RAG_EVAL_DATA)}")
    print()

    for i, data in enumerate(RAG_EVAL_DATA):
        scores = {}
        for metric in metrics:
            result = asyncio.run(
                metric.ascore(reference=data["reference"], response=data["response"])
            )
            scores[metric.name] = float(result)

        question = data["user_input"][:40]
        score_str = "  ".join(f"{k}={v:.3f}" for k, v in scores.items())
        print(f"  [{i + 1}] {question}...")
        print(f"      {score_str}")

    print()


# ── Demo 2: Score existing Langfuse traces ──


def _fetch_traces_by_name(name: str, limit: int = 10) -> list[dict]:
    """Fetch traces from Langfuse REST API by name."""
    import httpx

    host = os.getenv("LANGFUSE_HOST", "http://localhost:3600")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")

    resp = httpx.get(
        f"{host}/api/public/traces",
        params={"name": name, "limit": limit},
        auth=(public_key, secret_key),
    )
    resp.raise_for_status()
    return resp.json()["data"]


def demo_score_existing_traces():
    """Fetch dataset-run traces from Langfuse, evaluate with Ragas, write scores back."""
    metrics = get_non_llm_metrics()

    traces = _fetch_traces_by_name("dataset-run", limit=3)
    if not traces:
        print("  No dataset-run traces found. Run demo_trace.py first.")
        return

    qa_data = RAG_EVAL_DATA[1:4]  # The 3 QA items

    scored = 0
    for trace, data in zip(traces, qa_data):
        for metric in metrics:
            result = asyncio.run(
                metric.ascore(reference=data["reference"], response=data["response"])
            )
            langfuse.create_score(
                trace_id=trace["id"],
                name=f"ragas-{metric.name}",
                value=float(result),
                data_type="NUMERIC",
                comment=f"Ragas {metric.name} evaluation",
            )
        scored += 1

    print(
        f"  Scored {scored} traces with {len(metrics)} metrics each "
        f"({scored * len(metrics)} scores total)"
    )


# ── Demo 3: Langfuse run_experiment with Ragas evaluators ──


def _make_ragas_evaluator(metric):
    """Wrap a Ragas metric as a Langfuse async EvaluatorFunction."""

    async def evaluator(*, output, expected_output=None, **kwargs):
        response = str(output) if output else ""
        reference = str(expected_output) if expected_output else ""
        result = await metric.ascore(reference=reference, response=response)
        return Evaluation(
            name=f"ragas-{metric.name}",
            value=float(result),
            comment=f"Ragas {metric.name}",
        )

    return evaluator


def demo_run_experiment():
    """Run a Langfuse experiment with Ragas metrics as evaluators."""
    try:
        dataset = langfuse.get_dataset("qa-evaluation-set")
    except Exception:
        print("  Dataset 'qa-evaluation-set' not found. Run demo_trace.py first.")
        return

    if not dataset.items:
        print("  Dataset has no items. Run demo_trace.py first.")
        return

    metrics = get_non_llm_metrics()
    evaluators = [_make_ragas_evaluator(m) for m in metrics]

    def task(*, item, **kwargs):
        """Mock task: return expected_output as model response."""
        return item.expected_output

    result = langfuse.run_experiment(
        name="qa-evaluation-set",
        run_name="ragas-evaluation",
        description="Ragas non-LLM metrics evaluation",
        data=dataset.items,
        task=task,
        evaluators=evaluators,
    )

    print(f"  Experiment completed: {len(dataset.items)} items evaluated")
    print(f"  Evaluators: {', '.join(m.name for m in metrics)}")


def main():
    print("=== Ragas Evaluation Demo ===\n")
    mode = "Full (LLM + Non-LLM)" if has_llm_api_key() else "Non-LLM metrics only"
    print(f"Mode: {mode}")
    print(f"Langfuse Host: {os.getenv('LANGFUSE_HOST', 'not set')}")
    print()

    print("1. Standalone Ragas evaluation...")
    demo_standalone()

    print("2. Score existing Langfuse traces...")
    demo_score_existing_traces()

    print("3. Langfuse experiment with Ragas evaluators...")
    demo_run_experiment()

    print("\nFlushing to Langfuse...")
    langfuse.flush()
    time.sleep(2)

    print("\nDone! Check Langfuse UI: http://localhost:3600")
    print("  - Traces with ragas-* scores")
    print("  - Datasets > qa-evaluation-set > Runs > ragas-evaluation")


if __name__ == "__main__":
    main()
