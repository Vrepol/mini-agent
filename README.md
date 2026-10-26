# Mini Agent Lab

从第一性原理学习 Coding Agent：一边拆解 Codex / Claude Code 的 Harness 架构，一边构建可以自己运行和修改的 Python Mini Agent。

**当前进度：第 01 章 Agent Loop + 第 02 章 Session & State 的最小实现已提交；第 03 章 Context Engineering 尚未开始。**

## 快速运行（DeepSeek）

需要 Python 3.11+ 和自己的 DeepSeek API Key。

```bash
git clone https://github.com/Vrepol/mini-agent.git
cd mini-agent
python -m venv .venv
source .venv/bin/activate             # Windows: .venv\Scripts\activate
python -m pip install -e .
cp .env.example .env                  # Windows: copy .env.example .env
```

编辑本地 `.env`，将 `DEEPSEEK_API_KEY` 换成自己的密钥。**不要提交 .env。**

```bash
mini-agent
```

默认示例项目在 `examples/calculator`，其中 `add(2, 3)` 故意返回错误结果。初次运行只允许读文件和执行预设测试。需要模型修改代码时：

```bash
mini-agent --allow-write --workspace examples/calculator
```

示例任务：

```text
请先查看文件和测试，找出 add 函数的 bug，修改后运行测试，报告结果。
```

CLI 命令：`/sessions` 查看会话，`/resume <session-id>` 恢复会话，`/new` 创建新会话，`/exit` 退出。程序启动时也可使用 `--resume <session-id>`。使用 `--prompt "请读取 calculator.py"` 可只运行一个 Turn。

**注意**：`--allow-write` 允许模型写入工作区文件；`run_tests` 会执行该工作区中的 Python 测试代码。只对你信任的测试项目使用，不要把它当作安全沙箱。建议使用 Git 工作区并在实验后查看 diff。

## 离线测试（不需要 API Key）

```bash
python -m unittest discover -s tests -v
```

测试中的 `ScriptedModel` 代替 DeepSeek，验证真实 Harness 的工具调用、消息历史、持久化、步数上限、写入权限与中断行为。**离线通过不能证明 DeepSeek 实际联网调用已验证**；后者需要你本地配置 API Key。

## 已实现的目录

```text
mini_agent/
  runtime.py     # Agent Loop / Turn 运行
  model.py       # DeepSeek Chat Completions 适配器
  tools.py       # list_files/read_file/write_file/run_tests
  state.py       # Session + JsonSessionStore
  cli.py         # 交互命令 /sessions, /resume, /new
tests/
  test_runtime.py   # 离线 Fake Model 测试
examples/calculator/ # 可观察修复效果的错误代码与测试
docs/
  COURSE.md          # 固定的 12 章教学目录
  PROGRESS.md        # 理论 / 代码 / 真实验证区分
  RESUME.md          # 换会话继续学习
  CH01_AGENT_LOOP.md
  CH02_SESSION_STATE.md
```

## 每个模块属于哪一章？

| 当前源码 | 对应章节 | 之后如何升级 |
|---|---|---|
| `runtime.py` | 01 Agent Loop | 06 规划验证；10 事件生命周期 |
| `state.py` | 02 Session & State | 07 更可靠的恢复机制 |
| `model.py` | 01 最小模型调用 | 04 Model Adapter；Claude Opus / OpenAI Responses |
| `tools.py` | 01 演示用最小工具 | 04 Tool Registry；05 Sandbox |
| `cli.py` | 02 Session 操作界面 | 10 Event / Lifecycle |
| ContextBuilder | 03 **尚未实现** | Prompt 构建与上下文压缩 |

DeepSeek 默认使用官方目前推荐的 `deepseek-flash` 和 `https://api.deepseek.com`，并显式关闭思考模式来简化工具调用示例。不同厂商的协议转换会在第 04 章展开：[DeepSeek Tool Calls 文档](https://api-docs.deepseek.com/guides/tool_calls/)。

**学习方法**：每章先解释第一性原理，再理解抽象设计和代码运行轨迹，最后对照真实 Codex/Claude Code 机制。留有 `TODO(DIY-XX)` 供自己扩展。完整课程见 [docs/COURSE.md](docs/COURSE.md)。

> 本仓库是教学实验系统，不是生产级 Coding Agent。当前没有任意 Shell 工具、完整 Sandbox、并发 Session 锁、上下文压缩或通用工具权限系统。
