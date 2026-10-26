# 第 02 章：Session & State — 代码映射

## 为什么需要 Session

一个 Turn 包含多次模型调用；多轮 Turn 需要共享历史。如果状态只在函数局部变量中，程序退出就失去上下文。

## 当前实现

```text
Session
  id                 会话 UUID
  workspace          工作目录（Environment 位置引用）
  messages           Conversation State
  status             Execution State：idle / running / paused / interrupted
  total_steps        模型调用次数
  pending_tool_calls 尚未确认完成的工具调用（Execution State）

JsonSessionStore
  save()    序列化 JSON，先写临时文件再替换
  load()    恢复 Session；running 被标记为 interrupted
  list_sessions() 给 CLI /sessions 使用
```

源代码：[mini_agent/state.py](../mini_agent/state.py) 和 [mini_agent/runtime.py](../mini_agent/runtime.py)。

- 新 Session：在 CLI 输入 `/new`
- 查看已保存会话：`/sessions`
- 恢复会话：`/resume <UUID>` 或启动参数 `--resume <UUID>`
- 在工具执行前，Runtime 先保存 pending；完成后再保存结果。
- **没有完成标记的工具不能自动重放。** 例如程序断电时文件可能已经写入，但完成事件还没持久化。
- 当前版本只针对单进程、本地学习。没有锁、数据库事务、幂等性机制或成熟的崩溃恢复。

## Session 和 Context 的区别

现在直接把 `session.messages` 全部发送模型。它是**当前最小实现的限制**，而非最佳实践。第 03 章将加入 ContextBuilder，用于选择和裁剪模型可见的信息。

## DIY

- 实现 `updated_at` 并让 `/sessions` 按最后更新时间排序。
- 给 pending 工具实现人工检查 / 人工修复机制，切勿不经核实直接重复执行。
- 把 JsonSessionStore 改成 SQLite，并设计并发与事务语义。
