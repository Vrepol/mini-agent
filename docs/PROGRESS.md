# 学习进度与代码状态（持续维护）

更新于：2026-10-26

## 理论进度

- [x] 第 01 章 Agent Loop：为什么需要 Harness、Tool Call 如何驱动循环。
- [x] 第 02 章 Session & State：Session、Turn、Execution State、Environment State 和恢复风险。
- [ ] 第 03 章 Context Engineering：**下一章**。
- [ ] 第 04–12 章：按 [COURSE.md](COURSE.md) 依次推进。

## Mini Agent 实现进度

- [x] Python 包结构和 DeepSeek 模型适配器（当前仅 Chat Completions 非思考模式）。
- [x] AgentRuntime：逐轮模型推理、工具调用、工具反馈、最终回答与步骤上限。
- [x] Session + JsonSessionStore：会话 UUID、消息历史、状态、pending_tool_calls、磁盘持久化。
- [x] CLI：/sessions、/resume、/new、/exit，以及工作区、步数和文件写入参数。
- [x] WorkspaceTools：列出文件、读文件、显式授权后写文件、预设 unittest 命令。
- [x] ScriptedModel 离线测试和有 Bug 的 Calculator 工作区。
- [ ] ContextBuilder 和 Compaction（第 03 章）。
- [ ] Anthropic Messages / OpenAI Responses 适配器（第 04 章）。
- [ ] 生产级沙箱、权限系统、幂等恢复、Tracing、多 Agent（第 05–11 章）。

## 验证等级（务必区分）

- **代码提交**：GitHub 中已有完整代码、示例、离线单元测试及 CI 工作流。
- **离线单元测试**：由 GitHub Actions 执行；查看 Actions 页面确认每次提交是否通过。
- **DeepSeek 真实 API**：未使用用户密钥验证；需用户在本地填写 .env 并实际运行。
- **恢复边界**：pending 工具调用只标记风险并阻止自动重放，不提供自动调和；JSON 文件不保证事务恢复。

## 下一步课程

第 03 章 Context Engineering：为什么 `Session.messages` ≠ 模型真正需要的 Context？设计 ContextBuilder，逐步实现消息选择、Prompt 规则和长上下文管理。第 04 章再增加厂商特定的 Tool Call 协议 Adapter。

## 跨会话学习说明

新会话首先阅读 README.md、docs/COURSE.md、docs/PROGRESS.md、docs/RESUME.md；从标记的下一章继续。聊天中的额外技术讨论不自动改变章节进度；代码实现与理论进度单独维护。
