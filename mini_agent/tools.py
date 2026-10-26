"""Chapter 01: small, bounded tools. This is NOT a secure sandbox."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


class WorkspaceTools:
    """Files stay inside workspace; no arbitrary shell tool is exposed."""

    def __init__(self, workspace: str | Path, *, allow_write: bool = False):
        self.root = Path(workspace).resolve()
        if not self.root.is_dir():
            raise ValueError(f"Workspace does not exist: {self.root}")
        self.allow_write = allow_write

    def _safe_path(self, path: str) -> Path:
        target = (self.root / path).resolve()
        if not target.is_relative_to(self.root):
            raise ValueError("Path escapes workspace")
        if ".git" in target.relative_to(self.root).parts:
            raise ValueError("Editing Git internals is not allowed")
        return target

    def definitions(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "list_files",
                    "description": "List up to 100 files inside the workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read a UTF-8 text file from the workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {"path": {"type": "string"}},
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Replace a UTF-8 file inside the workspace. Requires CLI --allow-write.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "run_tests",
                    "description": "Run python -m unittest discover -s tests -v in workspace.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "additionalProperties": False,
                    },
                },
            },
        ]

    def invoke(self, name: str, raw_arguments: str) -> str:
        """Convert a tool failure into a model-visible observation."""
        try:
            arguments: Any = json.loads(raw_arguments or "{}")
            if not isinstance(arguments, dict):
                raise ValueError("Arguments must be a JSON object")
            if name == "list_files":
                result = self.list_files()
            elif name == "read_file":
                result = self.read_file(arguments["path"])
            elif name == "write_file":
                result = self.write_file(arguments["path"], arguments["content"])
            elif name == "run_tests":
                result = self.run_tests()
            else:
                raise ValueError(f"Unknown tool: {name}")
            return result
        except (ValueError, TypeError, KeyError, OSError, UnicodeError, subprocess.TimeoutExpired) as exc:
            return f"TOOL_ERROR: {type(exc).__name__}: {exc}"

    def list_files(self) -> str:
        paths: list[str] = []
        excluded = {".git", ".venv", ".sessions", "__pycache__", "node_modules"}
        for parent, dirs, filenames in os.walk(self.root, followlinks=False):
            dirs[:] = sorted(
                item for item in dirs
                if item not in excluded and not (Path(parent) / item).is_symlink()
            )
            for filename in sorted(filenames):
                path = Path(parent) / filename
                if not path.is_symlink():
                    paths.append(path.relative_to(self.root).as_posix())
                    if len(paths) >= 100:
                        return "\n".join(paths) + "\n... (truncated)"
        return "\n".join(paths) or "(workspace is empty)"

    def read_file(self, path: str) -> str:
        target = self._safe_path(path)
        if not target.is_file():
            raise ValueError(f"Not a file: {path}")
        with target.open("r", encoding="utf-8") as handle:
            return handle.read(16000) + ("\n... (truncated)" if handle.read(1) else "")

    def write_file(self, path: str, content: str) -> str:
        if not self.allow_write:
            raise ValueError("Write permission denied: restart CLI with --allow-write")
        target = self._safe_path(path)
        if target == self.root:
            raise ValueError("Cannot replace workspace root")
        if len(content) > 40000:
            raise ValueError("File content exceeds 40,000 characters")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"Wrote {target.relative_to(self.root).as_posix()}"

    def run_tests(self) -> str:
        command = [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]
        result = subprocess.run(
            command,
            cwd=self.root,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
            check=False,
        )
        return f"exit_code={result.returncode}\n{result.stdout[:12000]}"
