"""Offline tests: no DeepSeek API key is needed."""

import json
import tempfile
import unittest
from pathlib import Path

from mini_agent import AgentRuntime, JsonSessionStore, PendingToolCallsError, Session
from mini_agent.tools import WorkspaceTools


def tool_call(call_id, name, arguments):
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


class ScriptedModel:
    """Fake the model, but exercise the real Harness and Tool Executor."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.inputs = []

    async def complete(self, messages, tools):
        self.inputs.append(list(messages))
        if not self.replies:
            raise RuntimeError("Scripted model ran out of replies")
        return self.replies.pop(0)


class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        (self.workspace / "note.txt").write_text("hello from file", encoding="utf-8")
        self.store = JsonSessionStore(self.root / "sessions")
        self.session = Session(workspace=str(self.workspace))
        self.tools = WorkspaceTools(self.workspace)

    async def test_tool_loop_persists_complete_conversation(self):
        model = ScriptedModel(
            {"role": "assistant", "content": None, "tool_calls": [
                tool_call("call-1", "read_file", {"path": "note.txt"})
            ]},
            {"role": "assistant", "content": "The file says hello from file."},
        )
        runtime = AgentRuntime(model, self.tools, self.store)
        answer = await runtime.run_turn(self.session, "Read note.txt")
        self.assertIn("hello from file", answer)
        self.assertEqual(self.session.total_steps, 2)
        self.assertEqual(self.session.status, "idle")
        self.assertEqual([m["role"] for m in self.session.messages],
                         ["user", "assistant", "tool", "assistant"])
        self.assertEqual(self.session.messages[2]["tool_call_id"], "call-1")
        restored = self.store.load(self.session.id)
        self.assertEqual(restored.messages, self.session.messages)
        self.assertEqual(restored.pending_tool_calls, [])

    async def test_multiple_tools_execute_in_order(self):
        (self.workspace / "tests").mkdir()
        (self.workspace / "calculator.py").write_text(
            "def add(a, b):\n    return a - b\n", encoding="utf-8"
        )
        (self.workspace / "tests" / "test_calculator.py").write_text(
            "import unittest\nfrom calculator import add\n"
            "class TestAdd(unittest.TestCase):\n"
            "    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n",
            encoding="utf-8",
        )
        model = ScriptedModel(
            {"role": "assistant", "content": None, "tool_calls": [
                tool_call("call-a", "write_file", {
                    "path": "calculator.py",
                    "content": "def add(a, b):\n    return a + b\n",
                }),
                tool_call("call-b", "run_tests", {}),
            ]},
            {"role": "assistant", "content": "Fixed and tests passed."},
        )
        runtime = AgentRuntime(
            model, WorkspaceTools(self.workspace, allow_write=True), self.store
        )
        result = await runtime.run_turn(self.session, "Fix calculator and test")
        self.assertIn("passed", result)
        tools = [m for m in self.session.messages if m["role"] == "tool"]
        self.assertEqual([m["tool_call_id"] for m in tools], ["call-a", "call-b"])
        self.assertIn("exit_code=0", tools[1]["content"])
        self.assertEqual(self.session.pending_tool_calls, [])

    async def test_limit_pauses_without_dangling_tool_calls(self):
        model = ScriptedModel(
            {"role": "assistant", "content": None, "tool_calls": [
                tool_call("call-1", "read_file", {"path": "note.txt"})
            ]}
        )
        runtime = AgentRuntime(model, self.tools, self.store, max_steps=1)
        answer = await runtime.run_turn(self.session, "Read")
        self.assertIn("Paused", answer)
        self.assertEqual(self.session.status, "paused")
        self.assertEqual(self.session.pending_tool_calls, [])

    async def test_error_state_is_persisted(self):
        model = ScriptedModel()
        runtime = AgentRuntime(model, self.tools, self.store)
        with self.assertRaises(RuntimeError):
            await runtime.run_turn(self.session, "Do something")
        self.assertEqual(self.store.load(self.session.id).status, "interrupted")

    async def test_does_not_replay_pending_tool_call(self):
        self.session.pending_tool_calls = [
            tool_call("maybe-ran", "write_file", {"path": "note.txt", "content": "X"})
        ]
        self.store.save(self.session)
        runtime = AgentRuntime(ScriptedModel(), self.tools, self.store)
        with self.assertRaises(PendingToolCallsError):
            await runtime.run_turn(self.store.load(self.session.id), "Continue")

    async def test_workspace_guards(self):
        self.assertIn("permission denied", self.tools.invoke(
            "write_file", json.dumps({"path": "note.txt", "content": "changed"})
        ).lower())
        self.assertIn("escapes workspace", self.tools.invoke(
            "read_file", json.dumps({"path": "../outside.txt"})
        ))
        self.assertEqual((self.workspace / "note.txt").read_text(), "hello from file")
