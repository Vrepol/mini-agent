# 第 01 章：Agent Loop — 代码映射

## 第一性原理

LLM 只是输出字符串 / 结构化工具调用，无法亲自读取、修改文件。Harness 必须执行工具并把观察结果返回模型，形成反馈闭环。

## 运行链路

```text
User task
  -> AgentRuntime.run_turn()
  -> DeepSeekAdapter.complete(history, tool_schema)
  -> assistant message: tool_calls
  -> persist assistant + pending tool calls
  -> WorkspaceTools.invoke(name, args)
  -> tool result (role=tool, tool_call_id=...)
  -> persist result, remove pending
  -> DeepSeekAdapter.complete(updated history, ...)
  -> assistant final answer
```

源码导航：

- 循环核心：[mini_agent/runtime.py](../mini_agent/runtime.py)
- 模型协议：[mini_agent/model.py](../mini_agent/model.py)
- 工具及 schema：[mini_agent/tools.py](../mini_agent/tools.py)
- 离线 ScriptedModel：[tests/test_runtime.py](../tests/test_runtime.py)

## 必须读懂的 4 行（概念化简）

```python
assistant = await model.complete(session.messages, tools.definitions())
session.messages.append(assistant)
result = tools.invoke(tool_name, arguments)
session.messages.append({"role": "tool", "tool_call_id": call_id, "content": result})
```

真实实现还会处理多工具调用、每步持久化、失败和步数上限。框架不会自动保证模型已经完成任务；“完成”是当前模型给出的判断。

## DIY

- 修改 max_steps，观察暂停行为。
- 给 list_files 工具增加 `extension` 筛选参数。
- 打开 tests/test_runtime.py，给 ScriptedModel 添加一次错误的工具调用，看 Harness 如何将错误反馈给模型。
