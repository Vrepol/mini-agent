# Agent 架构学习目录 v1.0

## 学习目标

从第一性原理理解 Coding Agent 的运行机制，最终独立设计出一个具备多轮工作能力、工具执行、上下文管理、权限与观察性的 Mini Codex。

**主参考**：[Codex 开源代码](https://github.com/openai/codex)；**对照**：[Claude Code 文档](https://code.claude.com/docs/en/overview)。这份目录是教学抽象，不代表两种产品内部模块一一对应。

## 阶段 A：单 Agent 核心运行机制

### 01. Agent Loop — 理论已完成
- 为什么 LLM 不能独自完成涉及环境的任务
- LLM 输出工具调用请求，Harness 执行并把反馈回传
- Loop 终止、步骤限制与最小抽象伪代码

### 02. Session & State — 理论已完成
- Session / Thread、Turn、Step、State 的区别
- Conversation / Execution / Environment State 的边界
- Session Manager、State Store、持久化、恢复语义
- 工具调用中断、Unknown 状态和幂等性
- DIY：列出会话 / resume；中断工具调用提示

### 03. Context Engineering — 下一章
- Session 保存的数据 ≠ 每次发送给模型的 Context
- System / Developer / User / Assistant / Tool 消息如何组织
- Prompt 构建、文件与工具结果选择、token 预算
- 长上下文、截断、摘要 / Compaction、模型差异
- Codex / Claude Code 的真实上下文管理思路

### 04. Tool System
- Tool Schema、Tool Call 与 Result 协议
- Registry、Dispatcher、Executor、错误处理
- 单轮多工具、异步工具调用、接口规范化
- DeepSeek Chat Completions vs Anthropic Messages vs OpenAI Responses

## 阶段 B：真实环境执行与可靠性

### 05. Environment & Sandbox
- Workspace、文件系统、Shell、子进程
- 沙箱、工作目录、环境状态与权限边界

### 06. Task Planning & Verification
- 任务拆解、动态规划、测试验证、停止条件
- 防止“模型宣布完成但任务没完成”

### 07. Permission & Control
- Approval、危险操作授权、取消与超时
- 失败恢复、重试与幂等性

## 阶段 C：高级机制

### 08. Skills / MCP / Hooks
- 动态能力装载、外部工具协议、确定性事件钩子
- 可插拔能力与职责分工

### 09. Multi-Agent
- 主 Agent / 子 Agent、任务委派、上下文隔离
- 并行执行、汇总与协调成本

### 10. Event & Lifecycle
- Run / Turn 生命周期、事件流、暂停和恢复
- CLI / IDE 如何与 Runtime 通信

## 阶段 D：工程化与整合

### 11. Observability & Evaluation
- Trace、日志、成本、延迟、成功率、可重复评测
- 从失败样本改进 Harness 与模型接口

### 12. 架构整合与实战
- 完成并运行 Mini Codex
- 端到端示范登录 Bug 的修复
- 模块间契约、源码阅读和工程扩展

## 每章固定讲解模板

1. **第一性原理**：如果没有这个模块会发生什么？
2. **抽象设计**：职责、接口和生命周期。
3. **伪代码 + 运行轨迹**：真正理解数据和控制流。
4. **Codex / Claude Code 对照**：可验证的真实机制与设计取舍。
5. **增量代码 + DIY**：修改同一份 Mini Agent，提交并更新进度。

**路线管理**：遇到额外议题可以讨论，但要标注为“路线外讨论”，不自动更改下一章。下一章始终按照进度文件推进。
