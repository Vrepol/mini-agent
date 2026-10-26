"""Chapter 01 loop + Chapter 02 session; deliberately without a framework."""

from __future__ import annotations

from collections.abc import Callable

from .state import JsonSessionStore, Session
from .tools import WorkspaceTools


class PendingToolCallsError(RuntimeError):
    pass


class AgentRuntime:
    def __init__(
        self,
        model,
        tools: WorkspaceTools,
        store: JsonSessionStore,
        *,
        max_steps: int = 8,
    ):
        if max_steps < 1:
            raise ValueError("max_steps must be positive")
        self.model = model
        self.tools = tools
        self.store = store
        self.max_steps = max_steps

    async def run_turn(
        self,
        session: Session,
        task: str,
        *,
        on_event: Callable[[str], None] | None = None,
    ) -> str:
        if session.pending_tool_calls:
            raise PendingToolCallsError(
                "Previous tool call may have executed before interruption. "
                "Inspect .sessions and workspace; automatic replay is disabled."
            )
        if not task.strip():
            raise ValueError("Empty user task")

        session.messages.append({"role": "user", "content": task})
        session.status = "running"
        self.store.save(session)

        try:
            for _ in range(self.max_steps):
                assistant = await self.model.complete(
                    session.messages, self.tools.definitions()
                )
                if assistant.get("role") != "assistant":
                    raise ValueError("Adapter must return an assistant message")

                calls = assistant.get("tool_calls") or []
                session.messages.append(assistant)
                session.total_steps += 1
                session.pending_tool_calls = list(calls)
                # Save assistant action BEFORE invoking a side-effecting tool.
                self.store.save(session)

                if not calls:
                    session.status = "idle"
                    self.store.save(session)
                    return assistant.get("content") or "(empty final response)"

                for call in calls:
                    function = call["function"]
                    if on_event:
                        on_event(f"tool: {function['name']}")
                    result = self.tools.invoke(
                        function["name"], function.get("arguments", "{}")
                    )
                    session.messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": call["id"],
                            "content": result,
                        }
                    )
                    session.pending_tool_calls.pop(0)
                    self.store.save(session)

            session.status = "paused"
            self.store.save(session)
            return (
                f"Paused after {self.max_steps} model steps. "
                "Send 'continue' for another turn."
            )
        except Exception:
            session.status = "interrupted"
            self.store.save(session)
            raise

    # TODO(DIY-02): support reviewing/reconciling unresolved tool calls.
    # TODO(DIY-03): design a ContextBuilder instead of sending all messages.
