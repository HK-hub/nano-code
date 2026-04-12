#!/usr/bin/env python3
"""
s07_background_tasks.py - Background Tasks

Run commands in background threads. A notification queue is drained
before each LLM call delivery results

    Main thread                Background thread
    +-----------------+        +-----------------+
    | agent loop      |        | task executes   |
    | ...             |        | ...             |
    | [LLM call] <---+------- | enqueue(result) |
    |  ^drain queue   |        +-----------------+
    +-----------------+

    Timeline:
    Agent ----[spawn A]----[spawn B]----[other work]----
                 |              |
                 v              v
              [A runs]      [B runs]        (parallel)
                 |              |
                 +-- notification queue --> [results injected]



Key insight: "Fire and forget -- the agent dosen't block while the command runs."
"""
import json
import os
import re
import subprocess
import threading
import uuid
import time
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
PROJECT_ROOT = Path(__file__).resolve().parent.parent
env_path = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# 读取配置
ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN")
if not ANTHROPIC_AUTH_TOKEN:
    raise ValueError(
        "ANTHROPIC_AUTH_TOKEN is not set. Please copy .env.sample to .env and fill in your API key."
    )

# 创建客户端
client = Anthropic(
    base_url=os.getenv("ANTHROPIC_BASE_URL") or None, api_key=ANTHROPIC_AUTH_TOKEN
)
MODEL: str = os.getenv("ANTHROPIC_MODEL") or os.getenv("MODEL_ID")
if not MODEL:
    raise ValueError(
        "ANTHROPIC_MODEL or MODEL_ID is not set. Please set it in your .env file."
    )

# 工作目录
WORKDIR = Path.cwd()

# 任务目录
TASKS_DIR = WORKDIR / ".tasks"

# Auto-Compact 阈值
THRESHOLD = 50000
# 触发第二层压缩Auto Compact时，会话持久化保存位置
TRANSCRIPT_DIR = WORKDIR / ".transcripts"
# 触发第一层压缩:Micro Compact时，保留最近的会话数量不进行压缩
KEEP_RECENT = 3

# Skill目录
SKILL_DIR = WORKDIR / "skills"


# -- BackgroundManager: threaded execution + quque notification --
class BackgroundManager:
    def __init__(self):
        # task_id -> {status, result, comman}
        self.tasks = {}
        # completed task results
        self._notification_queue = []
        self._lock = threading.Lock()

    def run(self, command: str) -> str:
        """Start a background thread, return task_id immediately."""
        task_id = str(uuid.uuid4())[:8]
        self.tasks[task_id] = {"status": "running", "result": None, "command": command}
        thread = threading.Thread(target=self._execute, args=(task_id, command), daemon=True)
        thread.start()
        return f"Background task {task_id} started: {command}"

    def _execute(self, task_id: str, command: str):
        """Thread target: run subprocess, capture out, push to queue."""
        try:
            r = subprocess.run(command, shell=True, capture_output=True, cwd=WORKDIR, text=True, timeout=300)
            output = (r.stdout + r.stderr).strip()[:50000]
            status = "completed"
        except subprocess.TimeoutExpired:
            output = "Timeout: 300s"
            status = "timeout"
        except Exception as e:
            output = f"Error: {e}"
            status = "error"

        self.tasks[task_id]["status"] = status
        self.tasks[task_id]["result"] = output or "(no output)"

        with self._lock:
            self._notification_queue.append({
                "task_id": task_id,
                "status": status,
                "command": command[:80],
                "result": (output or "(no output)")[:500]
            })

    def check(self, task_id: str = None) -> str:
        """Check status of one task or list all."""
        if task_id:
            t = self.tasks.get(task_id)
            if not t:
                return f"Error: Unknown task {task_id}"
            return f"[{t['status']} {t['command'][:60]} {t.get('result') or '(running)'}]"

        lines = []
        for tid, t in self.tasks.items():
            lines.append(f"{tid}: [{t['status']}], {t['command'][:60]}")
        return "\n".join(lines) if lines else "No background tasks"

    def drain_notifications(self) -> list:
        """Return and clear all pending completion notifications."""
        with self._lock:
            notifs = list(self._notification_queue)
            self._notification_queue.clear()
        return notifs


BG = BackgroundManager()


# -- TaskManager: CRUD with dependency graph and persisted as JSON file --
class TaskManager:
    def __init__(self, task_dir: Path):
        self.dir = task_dir
        self.dir.mkdir(exist_ok=True)
        self._next_id = self._max_id() + 1

    def _max_id(self) -> int:
        ids = [int(f.stem.split("_")[1]) for f in self.dir.glob("task_*.json")]
        return max(ids) if ids else 0

    def _load(self, task_id: int) -> dict:
        path = self.dir / f"task_{task_id}.json"
        if not path.exists():
            raise ValueError(f"Task {task_id} does not exist")
        return json.loads(path.read_text())

    def _save(self, task: dict):
        path = self.dir / f"task_{task['id']}.json"
        path.write_text(json.dumps(task, indent=2), encoding="utf-8")

    def create(self, subject: str, description: str = "") -> str:
        task = {
            "id": self._next_id,
            "subject": subject,
            "description": description,
            "status": "pending",
            "blockedBy": [],
            "blocks": [],
            "owner": [],
        }
        self._save(task)
        self._next_id += 1
        return json.dumps(task, indent=2)

    def get(self, task_id: int) -> str:
        return json.dumps(self._load(task_id), indent=2)


    def update(self, task_id: int, status: str = None, add_blocked_by: list = None, add_blocks: list = None) -> str:
        task = self._load(task_id)
        if status:
            if status not in ["pending", "in_progress", "completed"]:
                raise ValueError(f"Invalid status: {status}")
            task["status"] = status
            # when a task completed, remove it from all others task blockedBy
            if status == "completed":
                self._clear_dependency(task_id)

        if add_blocked_by:
            task["blockedBy"] = list(set(task["blockedBy"] + add_blocked_by))

        if add_blocks:
            task["blocks"] = list(set(task["blocks"] + add_blocks))
            # Bidirectional: also update the blocked task's blockedBy list
            for blocked_id in add_blocks:
                try:
                    blocked  = self._load(blocked_id)
                    if task_id not in blocked["blockedBy"]:
                        blocked["blockedBy"].append(task_id)
                        self._save(blocked)
                except ValueError:
                    pass
        self._save(task)
        return json.dumps(task, indent=2)


    def _clear_dependency(self, completed_id: int):
        """Remove completed_id from all other tasks' blockedBy lists."""
        for f in self.dir.glob("task_*.json"):
            task = json.loads(f.read_text())
            if completed_id in task.get("blockedBy", []):
                task["blockedBy"].remove(completed_id)
                self._save(task)

    def list_all(self) -> str:
        tasks = []
        for f in sorted(self.dir.glob("task_*.json")):
            task = json.loads(f.read_text())
            tasks.append(task)

        if not tasks:
            return "Not tasks."
        lines = []
        for t in tasks:
            marker = {"pending": "[ ]", "in_progress": "[>]", "completed": "[x]"}.get(t["status"], "[?]")
            blocked = f"(blocked by: {t['blockedBy']})" if t["blockedBy"] else ""
            lines.append(f"{marker} #{t['id']}: {t['subject']} {blocked}")
        return "\n".join(lines)


TASKS = TaskManager(TASKS_DIR)


def estimate_tokens(messages: list) -> int:
    """Rough token count: ~4char per token."""
    return len(str(messages)) // 4

# -- Layer 1: micro_compact - replace old tool results with placeholders --
def micro_compact(messages: list) -> list:
    # Collect(message_index, part_index, tool_result_dict) for all tool_result_entries
    tool_results = []
    for message_index, message in enumerate(messages):
        if message["role"] == "user" and isinstance(message.get("content"), list):
            for part_index, part in enumerate(message["content"]):
                if isinstance(part, dict) and part.get("type") == "tool_result":
                    tool_results.append((message_index, part_index, part))

    if len(tool_results) <= KEEP_RECENT:
        return messages

    # find tool_name for each result by matching tool_use_id in prior assistant messages
    tool_name_map = {}
    for message in messages:
        if message["role"] == "assistant":
            content = message.get("content", [])
            if isinstance(content, list):
                for block in content:
                    if hasattr(block, "type") and block.type == "tool_use":
                        tool_name_map[block.id] = block.name
    # Clear old results, keep last KEEP_RECENT
    to_clear = tool_results[:-KEEP_RECENT]
    for _, _, result in to_clear:
        if isinstance(result.get("content"), str) and len(result["content"]) > 100:
            tool_id = result.get("tool_use_id", "")
            tool_name = tool_name_map.get(tool_id, "unknown")
            result["content"] = f"[Previous: used {tool_name}]"
    return messages


# -- Layer 2: auto_compact - save transcript, summarize, replace messages --
def auto_compact(messages: list) -> list:
    # save full transcript to disk
    TRANSCRIPT_DIR.mkdir(exist_ok=True)
    transcript_path = TRANSCRIPT_DIR / f"transcript_{int(time.time())}.jsonl"

    with open(transcript_path, "w") as f:
        for msg in messages:
            f.write(json.dumps(msg, default=str) + "\n")
    print(f"[Transcript saved: {transcript_path}]")

    # Ask LLM to summarize
    conversation_text = json.dumps(messages, default=str)[:80000]
    response = client.messages.create(
        model=MODEL,
        messages=[{"role": "user", "content":
            "Summarize this conversation for continuity. Include: "
            "1) What was accomplished, 2) Current state, 3) Key decisions made. "
            "Be concise but preserve critical details.\n\n" + conversation_text}],
        max_tokens=2000,
    )

    summaries = []
    for item in response.content:
        if item.text:
            summaries.append(item.text)
    summary = "\n".join(summaries)
    print(f"[> Auto-compact: {summary}]")

    # replace all messages with compressed summary
    return [
        {"role": "user", "content": f"[Conversation compressed. Transcript: {transcript_path}\n\n{summary}]"},
        {"role": "assistant", "content": "Understood. I have the context from summary. Continuing."}
    ]



# -- SkillLoader: scan skills/<name>/SKILL.md with YAML frontmatter --
class SkillLoader:
    def __init__(self, skill_dir: Path):
        self.skill_dir = skill_dir
        self.skills = {}
        self._load_all()

    def _load_all(self):
        if not self.skill_dir.exists():
            return
        for skill in sorted(self.skill_dir.rglob("SKILL.md")):
            text = skill.read_text(encoding="utf-8", errors="ignore")
            meta, body = self._parse_frontmatter(text)
            name = meta.get("name", skill.parent.name)
            self.skills[name] = {
                "meta": meta,
                "body": body,
                "path": str(skill),
            }

    def _parse_frontmatter(self, text: str) -> tuple:
        """Parse YAML frontmatter between --- delimiters."""
        match = re.match(r"^---\n(.*?)\n---\n(.*)", text, re.DOTALL)
        if not match:
            return {}, text
        meta = {}
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
        return meta, match.group(2).strip()

    def get_description(self) -> str:
        """Layer 1: short description for the system prompt."""
        if not self.skills:
            return "(no available skills)"
        lines = []
        for name, skill in self.skills.items():
            desc = skill["meta"].get("description", "no description")
            tags = skill["meta"].get("tags", "")
            line = f"  - {name}: {desc}"
            if tags:
                line += f" [{tags}]"
            lines.append(line)
        return "\n".join(lines)

    def get_content(self, name: str) -> str:
        """Layer 2: full skill body returned in tool_result"""
        skill = self.skills.get(name)
        if not skill:
            return f"Error: Unknown skill: '{name}'. Available skills: {', '.join(self.skills.keys())}"
        return f"<skill name={name}>\n{skill['body']}\n</skill>"


SKILL_LOADER = SkillLoader(SKILL_DIR)


# -- TodoManager: structured state the LLM writes to --
class TodoManager:
    def __init__(self):
        self.items = []

    def update(self, items: list) -> str:
        if len(items) > 20:
            raise ValueError("Max 20 todos allowed")
        validated = []
        in_progress_count = 0
        for i, item in enumerate(items):
            text = str(item.get("text", "")).strip()
            status = str(item.get("status", "pending")).strip().lower()
            item_id = str(item.get("id", {i + 1}))

            if not text:
                raise ValueError(f"Item: {item_id}: text required")
            if not status in ["pending", "in_progress", "completed"]:
                raise ValueError(f"Item: {item_id}: invalid status:{status}")
            if status == "in_progress":
                in_progress_count += 1

            # 添加校验合法的todoItem
            validated.append({
                "id": item_id,
                "text": text,
                "status": status,
            })

        if in_progress_count > 1:
            raise ValueError("Only one todo task can be in progress at a time")
        self.items = validated
        return self.render()

    def render(self) -> str:
        if not self.items:
            return "No todos."

        lines = []
        for item in self.items:
            # 确定每个task执行状态
            marker = {
                "pending": "[ ]",
                "in_progress": "[>]",
                "completed": "[x]",
            }[item["status"]]
            lines.append(f"{marker} #{item['id']}: {item['text']}")
        done = sum(1 for t in self.items if t["status"] == "completed")
        lines.append(f"\n{done} of {len(self.items)} tasks done")
        todos = "\n".join(lines)
        print(todos)
        return todos

TODO = TodoManager()


# 系统提示词
## Layer 1: skill metadata inject into prompt
SYSTEM = f"""You are a coding agent at {WORKDIR}. Use background_run for long-running commands.

Skills available:
{SKILL_LOADER.get_description()}
"""
SUBAGENT_SYSTEM = f"""You are a coding subagent at {WORKDIR}. Use background_run for long-running commands."""

TOOL_HANDLERS = {
    "bash":       lambda **kw: run_bash(kw["command"]),
    "read_file":  lambda **kw: run_read(kw["path"], kw.get("limit")),
    "write_file": lambda **kw: run_write(kw["path"], kw["content"]),
    "edit_file":  lambda **kw: run_edit(kw["path"], kw["old_text"], kw["new_text"]),
    "load_skill": lambda **kw: SKILL_LOADER.get_content(kw["name"]),
    "compact": lambda **kw: "Manual compression requested",
    "task_create": lambda **kw: TASKS.create(kw["subject"], kw.get("description", "")),
    "task_update": lambda **kw: TASKS.update(kw["task_id"], kw.get("status"), kw.get("addBlockedBy"), kw.get("addBlocks")),
    "task_list":   lambda **kw: TASKS.list_all(),
    "task_get":    lambda **kw: TASKS.get(kw["task_id"]),
    "background_run": lambda **kw: BG.run(kw["command"]),
    "check_background": lambda **kw: BG.check(kw.get("task_id")),
}

# child gets all base tools except task (no recursive spawning)
CHILD_TOOLS:list = [
    {"name": "bash", "description": "Run a shell command.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file contents.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "limit": {"type": "integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace exact text in file.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "old_text": {"type": "string"}, "new_text": {"type": "string"}}, "required": ["path", "old_text", "new_text"]}},
    {"name": "load_skill", "description": "Load specialized knowledge by name.",
     "input_schema": {"type": "object", "properties": {"name": {"type": "string", "description": "Skill name to load"}}, "required": ["name"]}},
    {"name": "compact", "description": "Trigger manual conversation compression",
     "input_schema": {"type": "object", "properties": {"focus": {"type": "string", "description": "What to preserve in the summary"}}}},
    {"name": "task_create", "description": "Create a new task.",
     "input_schema": {"type": "object", "properties": {"subject": {"type": "string"}, "description": {"type": "string"}}, "required": ["subject"]}},
    {"name": "task_update", "description": "Update a task's status or dependencies.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}, "status": {"type": "string", "enum": ["pending", "in_progress", "completed"]}, "addBlockedBy": {"type": "array", "items": {"type": "integer"}}, "addBlocks": {"type": "array", "items": {"type": "integer"}}}, "required": ["task_id"]}},
    {"name": "task_list", "description": "List all tasks with status summary.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "task_get", "description": "Get full details of a task by ID.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "integer"}}, "required": ["task_id"]}},
    {"name": "background_run", "description": "Run command in background thread. Returns task_id immediately.",
     "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]}},
    {"name": "check_background", "description": "Check background task status. Omit task_id to list all.",
     "input_schema": {"type": "object", "properties": {"task_id": {"type": "string"}}}},
]


# -- Tool implementations shared by parent and child --
def safe_path(p: str) -> Path:
    path = (WORKDIR / p).resolve()
    if not path.is_relative_to(WORKDIR):
        raise ValueError(f"Path escapes workspace: {p}")
    return path


# 运行 bash 命令
def run_bash(command: str) -> str:
    print(f"$ {command}")
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        r = subprocess.run(
            command,
            shell=True,
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',  # 忽略掉所有解不开的字节（比如那个 0xbe）
            timeout=120,
        )
        out = (r.stdout + r.stderr).strip()
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


def run_read(path: str, limit: int = None) -> str:
    try:
        text = safe_path(path).read_text()
        lines = text.splitlines()
        if limit and limit < len(lines):
            lines = lines[:limit] + [f"... ({len(lines) - limit} more lines)"]
        return "\n".join(lines)[:50000]
    except Exception as e:
        return f"Error: {e}"


def run_write(path: str, content: str) -> str:
    try:
        fp = safe_path(path)
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
        return f"Wrote {len(content)} bytes to {path}"
    except Exception as e:
        return f"Error: {e}"


def run_edit(path: str, old_text: str, new_text: str) -> str:
    try:
        fp = safe_path(path)
        content = fp.read_text()
        if old_text not in content:
            return f"Error: Text not found in {path}"
        fp.write_text(content.replace(old_text, new_text, 1))
        return f"Edited {path}"
    except Exception as e:
        return f"Error: {e}"


# -- Subagent: fresh context, filtered tools, summary-only return --
def run_subagent(prompt: str) -> str:
    # refresh context
    sub_messages:list = [{"role": "user", "content": prompt}]

    # subagent循环，最多30轮的安全限制
    for _ in range(30):
        response = client.messages.create(model=MODEL, system=SUBAGENT_SYSTEM, messages=sub_messages,
                               tools=CHILD_TOOLS, max_tokens=8000)
        sub_messages.append({"role": "assistant", "content": response.content})
        if response.stop_reason != "tool_use":
            break
        results = []
        for block in response.content:
            if block.type == "tool_use":
                handler = TOOL_HANDLERS.get(block.name)
                output = handler(**block.input) if handler else f"Unknown tool:{block.name}"
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)[:50000]})

        sub_messages.append({"role": "user", "content": results})
    # Only the final text returns to the parent, child context is discarded
    return "".join(b.text for b in response.content if hasattr(b, "text")) or "(no summary)"


# -- Parent tools: base tools + task dispatcher --
PARENT_TOOLS: list = CHILD_TOOLS + [
    {
        "name": "task",
        "description": "Spawn a subagent with fresh context. It shares the filesystem but not conversation history.",
        "input_schema": {"type": "object", "properties": {"prompt": {"type": "string"}, "description": {"type": "string", "description": "Short description of the task"}, "required": ["prompt"]}},
    }
]


# -- The core pattern: a while loop that calls tools until the model stops --
def agent_loop(messages: list):
    rounds_since_todo = 0
    while True:

        # layer 1: micro compact each LLM call
        micro_compact(messages)

        # layer 2: auto compact if token estimate exceeds threshold
        if estimate_tokens(messages) > THRESHOLD:
            print("[> Auto-compact triggered]")
            messages[:] = auto_compact(messages)

        # Drain background notification and inject as system message before LLM call
        notifs = BG.drain_notifications()
        if notifs and messages:
            notif_text = "\n".join(
                f"[bg:{n['task_id']}] {n['status']}: {n['result']}" for n in notifs
            )
            messages.append({"role": "user", "content": f"<background-results>\n{notif_text}\n</background-results>"})
            messages.append({"role": "assistant", "content": "Noted background results."})

        response = client.messages.create(
            model=MODEL,
            system=SYSTEM,
            messages=messages,
            tools=PARENT_TOOLS,
            max_tokens=8000,
        )
        # Append assistant turn
        messages.append({"role": "assistant", "content": response.content})
        # If the model didn't call a tool, we're done
        if response.stop_reason != "tool_use":
            return

        # Execute each tool call, collect results
        results = []
        used_todo = False
        manual_compact = False
        for block in response.content:
            if block.type == "tool_use":
                if block.name == "compact":
                    manual_compact = True
                    output = "Compressing..."
                elif block.name == "task":
                    desc = block.input.get("description", "subtask")
                    print(f"> task ({desc}): {block.input['prompt']}")
                    output = run_subagent(str(block.input["prompt"]))
                else:
                    handler = TOOL_HANDLERS.get(block.name)
                    try:
                        output = handler(**block.input) if handler else f"Unknown tool: {block.name}"
                    except Exception as e:
                        output = f"Error: {e}"

                print(f"> {block.name}: {str(output)[:200]}")
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(output)})
                if block.name == "todo":
                    used_todo = True

        messages.append({"role": "user", "content": results})

        # Layer 3: manual compact triggered by the compact tool
        if manual_compact:
            print("[> Manual compact triggered]")
            messages[:] = auto_compact(messages)

        rounds_since_todo = 0 if used_todo else rounds_since_todo + 1
        # 如果经历了3轮没有使用todo，则提示使用todo
        if rounds_since_todo >= 3:
            results.insert(0, {"type": "text", "text": "<reminder>Update your todos.</reminder>"})
        # Append tool results to the message history


if __name__ == "__main__":
    history = []
    while True:
        try:
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        if query.strip().lower() in ("q", "exit", ""):
            break
        history.append({"role": "user", "content": query})
        agent_loop(history)
        response_content = history[-1]["content"]
        if isinstance(response_content, list):
            for block in response_content:
                if hasattr(block, "text"):
                    print(block.text)
        print()
