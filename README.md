# Mini Agent Lab

一个从第一性原理出发、参考 Codex / Claude Code 架构、逐章实现的 Coding Agent 教学项目。

- **语言**：Python
- **实际使用模型**：DeepSeek API（API Key 仅放本地 .env）
- **架构对照**：Anthropic Messages（Claude Opus）、OpenAI Responses（OpenAI/Codex 系列模型）
- **原则**：不用 LangChain / LangGraph 隐藏核心机制；每章有抽象代码、真实运行链路、案例对照、可 DIY 的 TODO。
- **贯穿案例**：进入已有代码仓库，定位登录 Bug，修改代码，执行测试，失败后重试，最终总结。
- **状态**：第 01 章和第 02 章的**理论讲解已完成**，Mini Agent 的可运行代码**尚未提交**；下一章是第 03 章 Context Engineering。

## 教学文档（跨会话恢复）

1. [完整教学目录](docs/COURSE.md)：固定的 12 章学习路线及每章目标。
2. [当前学习状态](docs/PROGRESS.md)：学到哪里、哪些代码已经实现、后续从哪里继续。
3. [新对话续讲指南](docs/RESUME.md)：复制到新的 ChatGPT 对话中，快速恢复课程上下文。

## 目标架构（逻辑抽象，非 Codex / Claude Code 逐模块复刻）

```text
User / CLI / IDE
      |
      v
Agent Runtime / Harness
  |- Session Manager
  |- Context Manager
  |- Agent Loop
  |- Tool Registry / Dispatcher
  |- Task Controller
  |- Policy Manager
  |- Event / Trace
      |
      +--> Model Adapter (DeepSeek / Anthropic / OpenAI)
      +--> Tool Executor --> Workspace / Shell / Sandbox
      +--> State Store
```

## 后续实现约定

- 按章节渐进构建，不提前塞入完整框架。
- 模型调用实现 `ModelAdapter` 抽象，默认 DeepSeek；Anthropic / OpenAI 仅做 API 结构对照，实际运行不需要其密钥。
- 关键模块分别具备“接口说明、最小实现、单元测试、TODO(DIY)”。
- 每次新增代码后更新 [学习进度](docs/PROGRESS.md)；**理论讲过不等于代码已实现、代码已运行不等于真实 API 已验证**。
- 不提交密钥、.env、持久化会话、真实项目隐私数据。

> 本仓库是教学实验仓库，早期实现为了容易理解，会刻意保留部分工业级问题，在对应章节升级。
