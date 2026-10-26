"""CLI: python -m mini_agent.cli (or the 'mini-agent' command)."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from dotenv import load_dotenv

from .model import DeepSeekAdapter
from .runtime import AgentRuntime, PendingToolCallsError
from .state import JsonSessionStore, Session
from .tools import WorkspaceTools


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Mini Agent Lab")
    parser.add_argument("--workspace", default="examples/calculator")
    parser.add_argument("--state-dir", default=".sessions")
    parser.add_argument("--resume", metavar="SESSION_ID")
    parser.add_argument("--allow-write", action="store_true")
    parser.add_argument("--max-steps", type=int, default=8)
    parser.add_argument("--prompt", help="Run one user turn and exit")
    args = parser.parse_args()

    store = JsonSessionStore(args.state_dir)
    workspace = str(Path(args.workspace).resolve())
    session = store.load(args.resume) if args.resume else Session(workspace=workspace)
    store.save(session)

    model = DeepSeekAdapter()

    def run(task: str) -> None:
        tools = WorkspaceTools(session.workspace, allow_write=args.allow_write)
        runtime = AgentRuntime(model, tools, store, max_steps=args.max_steps)
        try:
            result = asyncio.run(
                runtime.run_turn(session, task, on_event=lambda event: print(f"[{event}]"))
            )
            print(f"\nAgent: {result}\n")
        except PendingToolCallsError as exc:
            print(f"Cannot resume safely: {exc}")
        except Exception as exc:
            print(f"Agent error: {type(exc).__name__}: {exc}")

    print(f"Session: {session.id}")
    print(f"Workspace: {session.workspace}")
    print("Commands: /sessions, /resume <id>, /new, /exit")
    print("File writes:", "enabled" if args.allow_write else "disabled")
    if args.prompt is not None:
        run(args.prompt)
        return

    while True:
        try:
            task = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not task:
            continue
        if task == "/exit":
            break
        if task == "/sessions":
            for item in store.list_sessions():
                print(f"  {item.id}  {item.status:12}  steps={item.total_steps}")
            continue
        if task == "/new":
            session = Session(workspace=workspace)
            store.save(session)
            print(f"New session: {session.id}")
            continue
        if task.startswith("/resume "):
            try:
                session = store.load(task.split(maxsplit=1)[1])
                print(f"Resumed: {session.id} ({session.status})")
            except (ValueError, OSError) as exc:
                print(f"Unable to load session: {exc}")
            continue
        run(task)


if __name__ == "__main__":
    main()
