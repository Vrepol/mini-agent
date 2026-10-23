# 学习进度与代码状态（持续维护）

## 当前定位

- **理论学习**：第 01 章 Agent Loop 和第 02 章 Session & State 已完成。
- **下一章**：03. Context Engineering。
- **代码仓库**：2026-10-23 初始化教学文档；Mini Agent 可运行代码尚未提交，不能声称已通过真实模型 API 验证。
- **贯穿项目**：用 Python 构建 Mini Codex；DeepSeek API 默认运行；Claude Opus / OpenAI Responses 的模型 Adapter 为教学对照；私密密钥仅使用本地 .env。

## 已理解的重要结论

### 第 01 章 Agent Loop
- LLM 生成文本或结构化 Tool Call，不直接执行本地动作。
- Harness 驱动“请求模型 → 解释响应 → 执行工具 → 回填结果 → 再请求模型”循环。
- Agent 最小循环要区分 final、tool_call、失败和步骤上限。

### 第 02 章 Session & State
- Session / Thread 代表持续会话；一个 Turn 可包含多次模型 Step 和工具调用。
- Conversation State、Execution State、Environment State 是三种不同的状态；记录工具成功 ≠ 外部世界必然保持原样。
- JsonSessionStore 可以用于理解持久化，但不是生产级数据库 / 事务恢复。
- 工具执行后的崩溃可能让操作处于 Unknown；不能无脑重放有副作用的工具。
- DIY：`/sessions` 和 `/resume`；中断工具调用提示。

## 尚未完成的实现

- [ ] Mini Agent Python 包与项目配置
- [ ] Agent Loop 最小可运行版本
- [ ] Session/State & JsonSessionStore
- [ ] DeepSeek ModelAdapter 与本地 .env.example
- [ ] Tool Registry 与安全的基础工具
- [ ] 单元测试、示例工作区及运行指南
- [ ] Anthropic / OpenAI Adapter 对照
- [ ] 其余各章模块

## 下一章（03）要回答

**Session 存储的信息不等于给模型发送的上下文。Context Builder 如何决定每次模型看到什么？** 由此展开消息历史、指令层、工具结果、上下文预算与压缩策略；保持同一个登录 Bug 示例。

## 继续教学的约束

- 不跳章。用户明确要求旁支讨论的例外，只答当下议题，不视为课程推进。
- 每次解释都包含原理、模块接口、抽象代码、真实案例、DIY。
- 代码提交以后再把对应任务勾选；以 GitHub 中可检查到的内容为准。
