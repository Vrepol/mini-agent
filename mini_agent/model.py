"""Model boundary: currently only DeepSeek's non-thinking Chat Completions."""

from __future__ import annotations

import os


class DeepSeekAdapter:
    def __init__(self, *, api_key: str | None = None, model: str | None = None):
        key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise ValueError("Set DEEPSEEK_API_KEY in .env or the environment")
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(
            api_key=key,
            base_url=os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            timeout=90.0,
            max_retries=1,
        )
        self.model = model or os.environ.get("DEEPSEEK_MODEL", "deepseek-flash")

    async def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            # Keep the example simple. Thinking-mode tool calls need
            # reasoning_content forwarded across subsequent requests.
            extra_body={"thinking": {"type": "disabled"}},
        )
        message = response.choices[0].message
        output: dict = {"role": "assistant", "content": message.content}
        if message.tool_calls:
            output["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ]
        return output


# TODO(DIY-04): implement Anthropic Messages and OpenAI Responses adapters.
# Never pass provider-specific wire messages directly to another provider.
