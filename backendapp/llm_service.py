"""LLM Service with multi-provider support via LiteLLM + Langfuse tracing."""

import litellm
from litellm import completion
from langfuse.decorators import observe

# Langfuse callback for automatic tracing of all LLM calls
litellm.success_callback = ["langfuse"]
litellm.failure_callback = ["langfuse"]


@observe()
def call_llm(
    prompt: str,
    model: str = "openai/gpt-4o",
    system: str = "",
    max_tokens: int = 1024,
) -> str:
    """Call any LLM provider via LiteLLM with automatic Langfuse tracing.

    Args:
        prompt: User message to send to the LLM.
        model: Provider/model identifier. Examples:
            - "openai/gpt-4o"
            - "anthropic/claude-sonnet-4-20250514"
            - "azure/gpt-4o"
            - "gemini/gemini-pro"
        system: Optional system prompt.
        max_tokens: Maximum tokens in the response.

    Returns:
        The LLM response text.
    """
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = completion(model=model, messages=messages, max_tokens=max_tokens)

    return response.choices[0].message.content
