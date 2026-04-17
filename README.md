<div align="center">

# 🤖 Nano-Code

**渐进式 AI 智能体框架 | 从单循环到自主协作团队**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Anthropic](https://img.shields.io/badge/Claude-API-orange?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)](https://github.com)

**12 个渐进模块 × 4 个技能系统 × 无限协作可能**

</div>

---

## 📖 目录

- [🌟 项目简介](#-项目简介)
- [🧠 核心架构](#-核心架构)
- [✨ 功能特性](#-功能特性)
- [🚀 快速开始](#-快速开始)
- [⚙️ 配置说明](#️-配置说明)
- [📚 模块详解](#-模块详解)
- [💡 使用示例](#-使用示例)
- [📁 项目结构](#-项目结构)
- [🔧 技术实现](#-技术实现)
- [🤝 贡献指南](#-贡献指南)

---

## 🌟 项目简介

**Nano-Code** 是一个**渐进式构建**的 AI 智能体开发框架，从最基础的 Agent Loop 到完整的多智能体协作系统，每个模块都是独立可运行的演进版本。

> 💡 **核心理念**: "每个模块都是一次迭代的思考结晶"

### 设计哲学

```
┌─────────────────────────────────────────────────────────────┐
│                    演进式架构设计                            │
├─────────────────────────────────────────────────────────────┤
│  s01 ──► s02 ──► s03 ──► s04 ──► s05 ──► s06                │
│  Loop   Tools   Todo   Sub    Skill  Compact                │
│                                                              │
│  s07 ──► s09 ──► s10 ──► s11 ──► s12                        │
│  Tasks  Teams  Protocol Auto   Worktree                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 核心架构

### 整体系统架构

```
                        ┌─────────────────────────────────┐
                        │         用户请求入口            │
                        └─────────────┬───────────────────┘
                                      │
                        ┌─────────────▼───────────────────┐
                        │       Team Lead Agent           │
                        │    (协调 + 任务分配 + 审批)      │
                        └─────────────┬───────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
    ┌─────────▼─────────┐   ┌─────────▼─────────┐   ┌─────────▼─────────┐
    │   Coder Agent     │   │   Reviewer Agent  │   │   Tester Agent    │
    │  (实现 + 调试)     │   │   (审查 + 反馈)    │   │   (测试 + 验证)   │
    └─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
              │                       │                       │
              └───────────────────────┼───────────────────────┘
                                      │
                        ┌─────────────▼───────────────────┐
                        │       任务系统 + Worktree        │
                        │    (持久化 + 隔离 + 依赖图)      │
                        └─────────────┬───────────────────┘
                                      │
                        ┌─────────────▼───────────────────┐
                        │      Skill Loading System       │
                        │    (按需加载 + 两层注入)         │
                        └─────────────┬───────────────────┘
                                      │
                        ┌─────────────▼───────────────────┐
                        │     Context Compact Pipeline     │
                        │   (三层压缩 + 无限运行)          │
                        └─────────────────────────────────┘
```

### Agent Loop 核心模式

```python
while stop_reason == "tool_use":
    response = LLM(messages, tools)
    execute tools
    append results
```

这是整个系统的核心循环：**工具结果反馈给模型，直到模型决定停止**。

---

## ✨ 功能特性

### 🔥 核心功能

| 功能 | 模块 | 描述 |
|------|------|------|
| 🔄 **Agent Loop** | s01 | 基础 LLM 循环，工具调用反馈机制 |
| 🛠️ **工具系统** | s02 | Bash、Read、Write、Edit 等核心工具 |
| 📋 **任务跟踪** | s03 | TodoManager 实时进度追踪 + 提醒 |
| 🧪 **子智能体** | s04 | 独立上下文的子任务委托执行 |
| 📚 **技能加载** | s05 | 两层注入，按需加载技能模块 |
| 🗜️ **三层压缩** | s06 | Micro + Auto + Compact 三级压缩管道 |
| 📦 **任务系统** | s07 | 持久化任务 + 依赖图 + 后台执行 |
| 👥 **团队协作** | s09 | 持久化命名 Agent + JSONL 收件箱通信 |
| 📜 **团队协议** | s10 | Shutdown 协议 + Plan Approval 协议 |
| 🤖 **自主智能体** | s11 | 空闲轮询 + 自动认领 + 身份重注入 |
| 🌳 **Worktree 隔离** | s12 | 目录级任务隔离 + Git Worktree |

### 🎯 技能系统

| 技能 | 描述 |
|------|------|
| 🎨 **frontend-react** | React + Next.js 开发指南 |
| 🖼️ **frontend-vue** | Vue 3 + Nuxt 开发指南 |
| ⚡ **frontend-svelte** | Svelte + SvelteKit 开发指南 |
| 🗃️ **database-design** | 数据库设计 + 查询优化 + 分片策略 |

---

## 🚀 快速开始

### 1️⃣ 环境准备

```bash
# 克隆项目
git clone https://github.com/your-org/nano-code.git
cd nano-code

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2️⃣ 配置 API Key

```bash
# 复制配置模板
cp .env.sample .env

# 编辑 .env 文件
ANTHROPIC_AUTH_TOKEN=your-api-key-here
ANTHROPIC_MODEL=claude-3-opus-20240229
# 或使用兼容 API
ANTHROPIC_BASE_URL=https://your-api-endpoint
MODEL_ID=your-model-id
```

### 3️⃣ 运行模块

```bash
# 运行基础循环
python agents/agent_loop.py

# 运行完整智能体
python agents/autonomous_agents.py

# 运行团队协作
python agents/worktree_task_isolation.py
```

---

## ⚙️ 配置说明

### 环境变量

| 变量 | 必填 | 描述 |
|------|------|------|
| `ANTHROPIC_AUTH_TOKEN` | ✅ | Anthropic API 密钥 |
| `ANTHROPIC_MODEL` / `MODEL_ID` | ✅ | 模型 ID |
| `ANTHROPIC_BASE_URL` | ❌ | 自定义 API 端点 |

### 核心参数

```python
# 压缩阈值
THRESHOLD = 50000       # 触发 Auto Compact 的 token 数
KEEP_RECENT = 3         # Micro Compact 保留最近消息数

# 自主轮询
POLL_INTERVAL = 5       # 收件箱轮询间隔（秒）
IDLE_TIMEOUT = 60       # 空闲超时（秒）

# 目录结构
TASKS_DIR = ".tasks"    # 任务持久化目录
TEAM_DIR = ".team"      # 团队配置目录
INBOX_DIR = ".inbox"    # 收件箱目录
```

---

## 📚 模块详解

### 📊 模块演进图

```
┌──────────────────────────────────────────────────────────────────────┐
│                         12 个渐进模块                                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │  s01    │───►│  s02    │───►│  s03    │───►│  s04    │            │
│  │  Loop   │    │  Tools  │    │  Todo   │    │  Sub    │            │
│  │         │    │         │    │         │    │         │            │
│  │  while  │    │  bash   │    │  track  │    │  fresh  │            │
│  │  tool   │    │  read   │    │  state  │    │  context│            │
│  │  loop   │    │  write  │    │         │    │         │            │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘            │
│       │              │              │              │                  │
│       └──────────────┴──────────────┴──────────────┘                  │
│                                                                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │  s05    │───►│  s06    │───►│  s07    │───►│  s08    │            │
│  │  Skill  │    │ Compact │    │  Task   │    │(reserved)│            │
│  │         │    │         │    │         │    │         │            │
│  │  lazy   │    │ 3-layer │    │ persist │    │         │            │
│  │  load   │    │ compress│    │  deps   │    │         │            │
│  │         │    │ forever │    │         │    │         │            │
│  └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘            │
│       │              │              │              │                  │
│       └──────────────┴──────────────┴──────────────┘                  │
│                                                                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐            │
│  │  s09    │───►│  s10    │───►│  s11    │───►│  s12    │            │
│  │  Team   │    │Protocol │    │  Auto   │    │Worktree │            │
│  │         │    │         │    │         │    │         │            │
│  │ named   │    │shutdown │    │  poll   │    │ isolate │            │
│  │ inbox   │    │ approve │    │  claim  │    │ by dir  │            │
│  │ thread  │    │ request │    │  identity│   │ parallel│            │
│  └────┴────┘    └────┴────┘    └────┴────┘    └────┴────┘            │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### 🔬 各模块详解

#### s01 - Agent Loop (基础循环)

```python
# 核心模式
while stop_reason == "tool_use":
    response = LLM(messages, tools)
    execute tools
    append results

# 关键洞察
"The entire secret of an AI coding agent in one pattern"
```

#### s02 - Tool Use (工具扩展)

```python
# 工具处理器
TOOL_HANDLERS = {
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(...),
}

# 关键洞察
"The loop didn't change at all. I just added tools."
```

#### s03 - Todo Write (任务跟踪)

```python
# 状态管理
TodoManager:
    items: [{"id": 1, "text": "...", "status": "pending|in_progress|completed"}]
    
    update(items) -> validates + injects reminder

# 关键洞察
"The agent can track its own progress -- and I can see it."
```

#### s04 - Sub Agent (子智能体)

```python
# 子智能体模式
Parent Agent          Subagent
messages=[...]        messages=[]  <-- fresh context

dispatch(prompt)  ──► execute
return summary    ◄── discard context

# 关键洞察
"Process isolation gives context isolation for free."
```

#### s05 - Skill Loading (技能加载)

```python
# 两层注入
Layer 1: skill names in system prompt (~100 tokens/skill)
Layer 2: full skill body in tool_result (on demand)

skills/
    pdf/SKILL.md       <-- frontmatter + body
    code-review/SKILL.md

# 关键洞察
"Don't put everything in the system prompt. Load on demand."
```

#### s06 - Context Compact (三层压缩)

```python
# 压缩管道
Layer 1: micro_compact  (silent, every turn)
    Replace old tool_results with "[Previous: used {tool_name}]"

Layer 2: auto_compact   (when tokens > 50000)
    Save transcript -> LLM summarize -> Replace messages

Layer 3: compact tool   (manual trigger)
    Same as auto, user-initiated

# 关键洞察
"The agent can forget strategically and keep working forever."
```

#### s07 - Task System (任务系统)

```python
# 持久化任务
.tasks/
    task_1.json  {"id":1, "subject":"...", "status":"completed"}
    task_2.json  {"blockedBy":[1], "status":"pending"}

# 依赖图解析
task_1 (complete) --> task_2 (blocked) --> task_3 (blocked)
     completing task_1 removes it from task_2's blockedBy

# 关键洞察
"State that survives compression -- because it's outside the conversation."
```

#### s09 - Agent Teams (智能体团队)

```python
# 团队结构
.team/config.json          .team/.inbox/
+------------------+       +------------------+
| {"members": [    |       | alice.jsonl      |
|   {"name":"alice"|       | bob.jsonl        |
|    "role":"coder"|       +------------------+
|  }]}            |        send_message("alice", "fix bug"):
+------------------+         open("alice.jsonl", "a").write(msg)

# 每个队友独立线程
Thread: alice              Thread: bob
+------------------+       +------------------+
| agent_loop       |       | agent_loop       |
| status: working  |       | status: idle     |
+------------------+       +------------------+

# 关键洞察
"Teammates that can talk to each other."
```

#### s10 - Team Protocols (团队协议)

```python
# Shutdown 协议 (request_id correlation)
Lead                          Teammate
shutdown_request ──────────► receives request
                              decides: approve?
shutdown_response ◄────────── shutdown_response

# Plan Approval 协议
Teammate                      Lead
plan_approval.submit ──────► reviews plan
plan_approval_resp ◄───────── plan_approval.review

# 关键洞察
"Same request_id correlation pattern, two domains."
```

#### s11 - Autonomous Agents (自主智能体)

```python
# 队友生命周期
spawn
   │
   ▼
WORK  ◄──►  LLM (tool_use)
   │
   │ stop_reason != tool_use
   ▼
IDLE  ──► poll every 5s for 60s
   │
   ├──► check inbox -> message? -> resume WORK
   ├──► scan .tasks/ -> unclaimed? -> claim -> WORK
   └──► timeout -> shutdown

# 身份重注入 (after compression)
messages = [identity_block, ...remaining...]
"You are 'coder', role:backend, team:my-team"

# 关键洞察
"The agent finds work itself."
```

#### s12 - Worktree Task Isolation (任务隔离)

```python
# 目录级隔离
.tasks/task_12.json         .worktrees/index.json
+------------------+        +------------------+
| {"id": 12,       |        | {"worktrees": [{ |
|  "worktree":     |        |   "name": "...", |
|  "auth-refactor"}|        |   "task_id": 12} |
+------------------+        +------------------+

# 控制平面 vs 执行平面
Tasks: control plane (协调)
Worktrees: execution plane (隔离执行)

# 关键洞察
"Isolate by directory, coordinate by task id."
```

---

## 💡 使用示例

### 🎬 基础使用

```python
# s01 - 最简单的 Agent Loop
from agents.agent_loop import agent_loop

agent_loop(
    prompt="List all Python files in the current directory",
    system="You are a coding agent. Use bash to solve tasks."
)
```

### 🎬 子智能体委托

```python
# s04 - 委托复杂任务
from agents.sub_agent import dispatch_subagent

# 主智能体保持干净上下文
result = dispatch_subagent(
    prompt="Explore the codebase and find all API endpoints",
    description="Find all REST API endpoints in the project"
)
# result 是摘要，子智能体上下文被丢弃
```

### 🎬 团队协作

```python
# s09 - 创建团队
from agents.agent_teams import spawn_teammate, send_message

# 启动队友
spawn_teammate("alice", "coder", system_prompt)
spawn_teammate("bob", "reviewer", system_prompt)
spawn_teammate("lead", "coordinator", system_prompt)

# 发送消息
send_message("alice", {"type": "message", "content": "Implement auth module"})
```

### 🎬 自主智能体

```python
# s11 - 自主智能体自动认领任务
from agents.autonomous_agents import AutonomousAgent

agent = AutonomousAgent(
    name="coder",
    role="backend",
    team="my-team"
)

# 智能体自动:
# - 轮询收件箱检查新消息
# - 扫描 .tasks/ 目录认领未认领任务
# - 身份重注入保持角色认知
```

---

## 📁 项目结构

```
nano-code/
├── 📂 agents/                 # 核心智能体模块
│   ├── 📄 agent_loop.py           # s01: 基础循环
│   ├── 📄 tool_use.py             # s02: 工具扩展
│   ├── 📄 todo_write.py           # s03: 任务跟踪
│   ├── 📄 sub_agent.py            # s04: 子智能体
│   ├── 📄 skill_loading.py        # s05: 技能加载
│   ├── 📄 context_compact.py      # s06: 三层压缩
│   ├── 📄 task_system.py          # s07: 任务系统
│   ├── 📄 backgroup_tasks.py      # s07: 后台任务
│   ├── 📄 agent_teams.py          # s09: 智能体团队
│   ├── 📄 team_protocols.py       # s10: 团队协议
│   ├── 📄 autonomous_agents.py    # s11: 自主智能体
│   ├── 📄 worktree_task_isolation.py  # s12: Worktree 隔离
│   │
│   └── 📂 skills/               # 技能模块
│       ├── 📂 frontend-react/
│       ├── 📂 frontend-vue/
│       ├── 📂 frontend-svelte/
│       └── 📂 database-design/
│
├── 📄 requirements.txt         # Python 依赖
├── 📄 .env.sample              # 配置模板
├── 📄 .gitignore               # Git 忽略规则
│
└── 📂 .tasks/                  # 任务持久化目录
    └── task_*.json

└── 📂 .team/                   # 团队配置目录
    ├── config.json
    └── 📂 .inbox/
        ├── alice.jsonl
        └── bob.jsonl

└── 📂 .transcripts/            # 压缩 transcripts
└── 📂 .worktrees/              # Git Worktree 隔离
```

---

## 🔧 技术实现

### 🔒 安全措施

```python
# 命令过滤
dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
if any(d in command for d in dangerous):
    return "Error: Dangerous command blocked"

# 路径验证
def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path
```

### 📊 Token 估算

```python
def estimate_tokens(messages: list) -> int:
    """Rough token count: ~4char per token."""
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        if isinstance(content, str):
            total += len(content) // 4
        elif isinstance(content, list):
            for block in content:
                if block.get("type") == "text":
                    total += len(block.get("text", "")) // 4
    return total
```

### 📦 消息类型

```python
VALID_MESSAGE_TYPES = [
    "message",              # 普通消息
    "broadcast",            # 广播消息
    "shutdown_request",     # 关闭请求
    "shutdown_response",    # 关闭响应
    "plan_approval_response",  # 计划审批响应
]
```

---

## 🤝 贡献指南

### 🌿 开发流程

```bash
# 1. Fork 并克隆
git clone https://github.com/your-fork/nano-code.git

# 2. 创建特性分支
git checkout -b feature/your-feature

# 3. 开发并测试
python agents/your_module.py

# 4. 提交代码
git commit -m "Add: your feature description"

# 5. 推送并创建 PR
git push origin feature/your-feature
```

### 📝 模块命名规范

```
s{序号}_{功能名}.py

示例:
s01_agent_loop.py
s02_tool_use.py
s03_todo_write.py
```

### 🎯 代码风格

- 每个模块顶部必须有清晰的文档注释
- 包含 ASCII 图解说明核心概念
- 最后一行是 "Key Insight" 总结
- 使用类型注解和清晰的变量命名

---

<div align="center">

## 📜 许可证

MIT License © 2024

---

**Made with ❤️ by Nano-Code Team**

[⬆ 返回顶部](#-robot-nano-code)

</div>