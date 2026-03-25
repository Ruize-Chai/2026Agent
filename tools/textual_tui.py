"""隔离的 Textual 聊天 TUI（独立于主程序）。

用法：
    python tools/textual_tui.py [--backend openai]

默认使用 `openai` 后端。要使用真实 LLM，请安装 `openai` 并通过
`--backend openai`（默认）启动，同时通过 `LLM.set_llm_api(...)` 或 `Workflow.llm_config` 设置凭证。
"""
from __future__ import annotations

import argparse
import asyncio
from typing import Optional, Any
import json
import os
import uuid
from datetime import datetime, timezone

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Input, Button, Static

import sys
from pathlib import Path

# Ensure repository root is on sys.path so top-level packages (e.g. LLM, Workflow)
# can be imported when running this script from the `tools/` directory.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from LLM import create_client, set_llm_api, clear_llm_api, get_llm_api
from types import SimpleNamespace
from Json_Utils.json_validate import is_valid_workflow_dict, is_valid_workflow_payload

def load_generation_context(current_workflow: Optional[str] = None) -> tuple[str, list[str]]:
    """加载生成工作流所需的上下文信息（Prompt、插件列表等）。"""
    try:
        # 1. 加载 Schema Rules
        schema_path = REPO_ROOT / "OriflowPrompts" / "SchemaRulePrompts.md"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_rules = f.read()
        
        # 2. 加载插件列表
        plugins_path = REPO_ROOT / "Plugins" / "pluginLists.json"
        with open(plugins_path, "r", encoding="utf-8") as f:
            plugins = json.load(f)
        
        all_plugins = plugins.get("basic_plugins", []) + plugins.get("llm_plugins", [])
        
        context = f"### SCHEMA RULES:\n{schema_rules}\n\n"
        context += f"### AVAILABLE PLUGINS (ONLY USE THESE IN 'type' FIELD):\n{', '.join(all_plugins)}\n\n"
        
        if current_workflow:
            context += f"### CURRENT WORKFLOW (STAGED):\n{current_workflow}\n\n"
            context += "### TASK: Modify or Iterate the CURRENT WORKFLOW based on user instructions.\n"
            context += "CRITICAL: You MUST maintain the existing logic unless asked to change it. Output EVERY required field (id, type, params, inputs, outputs) for EVERY node, even if unchanged.\n"
        
        return context, all_plugins
    except Exception as e:
        return f"Context loading failed: {e}", []

class ChatBubble(Static):
    def __init__(self, who: str, text: str, **kwargs):
        # Use simple inline formatting to avoid relying on CSS
        if who.upper() == "USER":
            display = f"YOU: {text}"
        elif who.upper() == "ASSISTANT":
            display = f"ASSISTANT: {text}"
        else:
            display = f"{who}: {text}"
        super().__init__(display, **kwargs)


class TextualChatApp(App):
    TITLE = "Oriflow Smith"
    BINDINGS = [("ctrl+c", "quit", "Quit")]
    
    # 增加 CSS 样式以确保聊天区域可滚动且不溢出
    CSS = """
    #messages {
        height: 1fr;
        overflow-y: scroll;
        scrollbar-gutter: stable;
        padding: 1;
    }
    .user {
        background: $primary-darken-3;
        margin: 1 0;
        padding: 0 1;
    }
    .assistant {
        background: $secondary-darken-3;
        margin: 1 0;
        padding: 0 1;
    }
    .system {
        color: $warning;
        text-style: italic;
    }
    """

    def __init__(self, backend: str = "openai", api_key: Optional[str] = None, endpoint: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.backend = backend
        self.api_key = api_key
        self.endpoint = endpoint
        self.client = create_client(backend=self.backend, api_key=self.api_key, endpoint=self.endpoint)
        

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        # Main area: left = chat messages, right = preview
        with Horizontal(id="main"):
            with Vertical(id="left_col"):
                yield Static("Chat", id="chat_title")
                yield Vertical(id="messages")
            with Vertical(id="right_col"):
                yield Static("Preview", id="preview_title")
                yield Static("", id="preview")

        with Horizontal(id="controls"):
            yield Input(placeholder="用自然语言描述要生成的工作流", id="input")
            yield Button("生成", id="send")
            yield Button("保存 JSON", id="save")
        # help / command hints under input
        yield Static("Commands: @G <instruction> — gen | @Ud <instruction> — update | @It <feedback> — iterate", id="help")

        yield Footer()

    async def on_mount(self) -> None:
        # messages container (mount ChatBubble widgets here)
        self.messages = self.query_one("#messages", Vertical)
        self.preview = self.query_one("#preview", Static)
        self.input = self.query_one("#input", Input)
        self.input.focus()
        self.last_generated: Optional[str] = None
        self._msg_lines: list[str] = []

    async def action_quit(self) -> None:
        # Use App.exit() to stop the application (compatible across versions).
        # If unavailable, raise SystemExit to terminate.
        try:
            self.exit()
        except Exception:
            raise SystemExit

    async def append_message(self, who: str, text: str) -> None:
        # mount a ChatBubble widget into messages container
        bubble = ChatBubble(who, text)
        # add role class for styling
        role = "user" if who.upper() == "USER" else "assistant" if who.upper() == "ASSISTANT" else "system"
        try:
            await self.messages.mount(bubble, classes=role)
            # 持续锁定到最下端
            self.messages.scroll_end(animate=False)
            bubble.scroll_visible()
        except Exception:
            # fallback if mount doesn't accept classes param
            try:
                bubble.classes = role
                await self.messages.mount(bubble)
                self.messages.scroll_end(animate=False)
                bubble.scroll_visible()
            except Exception:
                # as a last resort, update preview of concatenated text
                self._msg_lines.append(f"[{who}]: {text}")
                try:
                    self.preview.update("\n".join(self._msg_lines))
                except Exception:
                    pass

    async def on_input_submitted(self, event: Any) -> None:
        # Accept any event-like object with a `value` attribute for compatibility
        text = (getattr(event, "value", "") or "").strip()
        if not text:
            return
        await self.append_message("USER", text)
        # clear input
        self.input.value = ""
        

        # --- ALPHA FEATURE: Workflow Workspace Controls ---
        # @G: Create New
        # @Ud: Update (Change fields, rename, etc.)
        # @It: Iterate (Logic change, add nodes, logic fix)
        
        is_workflow_cmd = any(text.startswith(prefix) for prefix in ["@G", "@Ud", "@It"])

        if is_workflow_cmd:
            cmd = text[:3].strip() # handles @G, @Ud, @It
            remainder = text[len(cmd):].strip()

            # 准备上下文
            # 如果是 @Ud 或 @It，注入 self.last_generated 作为 Current Workflow
            staged_workflow = None
            if cmd in ["@Ud", "@It"] and self.last_generated:
                staged_workflow = self.last_generated

            gen_context, all_plugins = load_generation_context(current_workflow=staged_workflow)
            
            if cmd == "@G":
                msg = "开始按 Schema 生成工作流..."
                prompt = (
                    f"SYSTEM ROLE: You are a Workflow Creator. Output ONLY JSON.\n\n"
                    f"CRITICAL FORMAT RULES:\n"
                    f"1. Root object must be {{ \"workflow_id\": \"...\", \"entry\": 1, \"nodes\": [...] }}\n"
                    f"2. Every node must have: \"id\" (int), \"type\" (string), \"params\" (obj), \"inputs\" (list), \"outputs\" (list).\n\n"
                    f"STRICT PLUGIN RULES:\n"
                    f"1. You MUST ONLY use node types from the 'ALLOWED_PLUGINS' list below.\n"
                    f"2. DO NOT hallucinate or invent new node types (like 'delay', 'action', etc.).\n"
                    f"3. Logic must be mapped to these specific available tools.\n\n"
                    f"ALLOWED_PLUGINS:\n{all_plugins}\n\n"
                    f"STRICT LOGIC RULES:\n"
                    f"1. NO internal code/scripts in params.\n"
                    f"2. ALL logic via Nodes and Connections.\n\n"
                    f"{gen_context}\n\nUSER REQUEST: {remainder}\n\nGENERATE NEW JSON:"
                )
            elif cmd == "@Ud":
                msg = "正在局部更新/重命名工作流..."
                prompt = (
                    f"SYSTEM ROLE: You are a Workflow Editor. Modify ONLY specific fields requested. Output ONLY JSON.\n\n"
                    f"CRITICAL FORMAT RULES:\n"
                    f"1. Root object must be {{ \"workflow_id\": \"...\", \"entry\": 1, \"nodes\": [...] }}\n"
                    f"2. Every node must have: \"id\" (int), \"type\" (string), \"params\" (obj), \"inputs\" (list), \"outputs\" (list).\n\n"
                    f"STRICT PLUGIN RULES:\n"
                    f"1. You MUST ONLY use node types from the 'ALLOWED_PLUGINS' list below.\n"
                    f"2. ALLOWED_PLUGINS:\n{all_plugins}\n\n"
                    f"{gen_context}\n\nUSER REQUEST: {remainder}\n\nRETURN UPDATED JSON:"
                )
            else: # @It
                msg = "正在根据逻辑迭代工作流..."
                prompt = (
                    f"SYSTEM ROLE: You are a Workflow Optimization Expert. Improve logic via Nodes and Connections. Output ONLY JSON.\n\n"
                    f"CRITICAL FORMAT RULES:\n"
                    f"1. Root object must be {{ \"workflow_id\": \"...\", \"entry\": 1, \"nodes\": [...] }}\n"
                    f"2. Every node must have: \"id\" (int), \"type\" (string), \"params\" (obj), \"inputs\" (list), \"outputs\" (list).\n\n"
                    f"STRICT PLUGIN RULES:\n"
                    f"1. You MUST ONLY use node types from the 'ALLOWED_PLUGINS' list below.\n"
                    f"2. DO NOT invent node types. Mapping logic to existing plugins is mandatory.\n\n"
                    f"ALLOWED_PLUGINS:\n{all_plugins}\n\n"
                    f"{gen_context}\n\nUSER FEEDBACK: {remainder}\n\nRETURN IMPROVED JSON:"
                )
            # 提高 tokens 到 2048 处理复杂更新
            await self.append_message("SYSTEM", msg)
            
            # --- 核心修复：Schema 校验重试机制 (限3次) ---
            max_retries = 3
            current_try = 0
            raw_content = ""
            parsed = None
            as_json = False
            last_error = ""

            # 复用 prompt，但在重试时注入错误信息
            active_prompt = prompt

            while current_try < max_retries:
                current_try += 1
                try:
                    # 针对迭代任务，稍微提高 temperature 到 0.2 以允许更好的逻辑联想，但保持结构严谨
                    temp = 0.0 if cmd == "@Ud" else 0.2
                    generated = await self.client.generate_async(active_prompt, model="minimax/minimax-m2.5", max_tokens=2048, temperature=temp)
                except Exception as e:
                    generated = f"LLM call failed: {e}"
                    break # 网络或接口错误直接跳出

                # 提取 JSON (防止 LLM 输出 Markdown 代码块)
                raw_content = generated.strip()
                if "```json" in raw_content:
                    raw_content = raw_content.split("```json")[1]
                    if "```" in raw_content: raw_content = raw_content.split("```")[0].strip()
                elif "```" in raw_content:
                    raw_content = raw_content.split("```")[1]
                    if "```" in raw_content: raw_content = raw_content.split("```")[0].strip()
                raw_content = raw_content.strip()

                try:
                    parsed = json.loads(raw_content)
                    
                    # --- 自动解包逻辑：如果模型嵌套了 "workflow": { ... }，尝试自动修复 ---
                    if "workflow" in parsed and "nodes" in parsed["workflow"]:
                        parsed = parsed["workflow"]
                    elif "data" in parsed and "nodes" in parsed["data"]:
                        parsed = parsed["data"]

                    # 组合校验：先基础结构校验，再 Pydantic 深度校验
                    is_valid_workflow_dict(parsed)
                    is_valid_workflow_payload(parsed)

                    # --- 新增：禁止在 params 中嵌入代码的启发式校验 ---
                    for node in parsed.get("nodes", []):
                        # 1. 代码黑名单检查
                        params_str = json.dumps(node.get("params", {}))
                        forbidden_patterns = ["def ", "import ", "lambda ", "class ", "return ", "print("]
                        if any(p in params_str for p in forbidden_patterns):
                            raise Exception(f"Node {node.get('id')} contains forbidden code patterns in params!")
                        
                        # 2. 严格插件名检查 (核心修复：防止模型幻觉)
                        allowed_types = all_plugins # all_plugins 已经是字符串列表了
                        curr_type = node.get("type")
                        if curr_type not in allowed_types:
                            raise Exception(f"Invalid Plugin Type: '{curr_type}'. You MUST use one of: {allowed_types}")
                    
                    as_json = True
                    await self.append_message("SYSTEM", f"✅ 第 {current_try} 次尝试: Schema 校验通过！")
                    break # 校验成功，跳出循环
                except Exception as ve:
                    last_error = str(ve)
                    # 简化错误信息，只传给模型核心部分
                    error_msg = last_error.split("\n")[0] if "\n" in last_error else last_error
                    await self.append_message("SYSTEM", f"⚠️ 第 {current_try} 次尝试校验失败: {error_msg}")
                    # 构造后续尝试的 Prompt
                    active_prompt = f"{prompt}\n\nPREVIOUS ERROR: {last_error}\n\nPlease fix the JSON according to the error above. Ensure all required fields like 'id', 'type', 'inputs', 'outputs', 'params' are present for EVERY node. Use the exact Schema structure provided in the context."

            # 最终展示逻辑
            if as_json and parsed:
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                await self.append_message("ASSISTANT", pretty)
            else:
                # 即使失败了，也要把最后一次的结果丢出来看看
                await self.append_message("ASSISTANT", raw_content)
                await self.append_message("SYSTEM", f"❌ 达到最大重试次数 ({max_retries})，最后一次错误: {last_error}")
                pretty = raw_content

            self.last_generated = pretty
            try:
                self.preview.update(pretty)
            except Exception:
                pass

            # 核心修复：确保在此处进行保存
            try:
                base_dir = REPO_ROOT / "WorkflowBase"
                os.makedirs(base_dir, exist_ok=True)
                
                # 确定 ID 和文件名
                if as_json and isinstance(parsed, dict) and parsed.get("workflow_id"):
                    wid = parsed["workflow_id"]
                else:
                    wid = f"gen-{uuid.uuid4().hex[:8]}"
                
                filename = f"{wid}.json"
                save_path = base_dir / filename
                
                # 写入文件
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(pretty)

                # 同步更新索引 workflowlists.json
                lists_path = base_dir / "workflowlists.json"
                lists = []
                if lists_path.exists():
                    try:
                        with open(lists_path, "r", encoding="utf-8") as f:
                            lists = json.load(f)
                            if not isinstance(lists, list):
                                lists = []
                    except:
                        lists = []
                
                # 更新或添加索引
                if not any(item.get("id") == wid for item in lists):
                    lists.append({"id": wid, "filename": filename})
                    with open(lists_path, "w", encoding="utf-8") as f:
                        json.dump(lists, f, ensure_ascii=False, indent=2)

                await self.append_message("SYSTEM", f"💾 工作流已持久化至: {filename}")
            except Exception as e:
                await self.append_message("SYSTEM", f"⚠️ 本地保存失败: {e}")

            return

        # Otherwise, normal chat behavior: call LLM asynchronously - expect JSON workflow output (or plain text)
        try:
            resp = await self.client.generate_async(text)
        except Exception as e:
            resp = f"[error] {e}"

        await self.append_message("ASSISTANT", resp)

        # try to parse as JSON and pretty-print into preview
        pretty = None
        try:
            parsed = json.loads(resp)
            pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
        except Exception:
            # not JSON, show raw text
            pretty = resp

        self.last_generated = pretty
        # set preview text
        try:
            self.preview.update(pretty)
        except Exception:
            try:
                setattr(self.preview, "text", pretty)
            except Exception:
                pass

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send":
            # create a simple event-like object containing `value`
            submitted = SimpleNamespace(value=self.input.value)
            await self.on_input_submitted(submitted)

        if event.button.id == "save":
            # only save the last generated content (do not run)
            if not self.last_generated:
                await self.append_message("SYSTEM", "没有可保存的生成内容")
                return
            # ensure directory
            outdir = os.path.join(os.getcwd(), "WorkflowBase")
            os.makedirs(outdir, exist_ok=True)
            # use timezone-aware UTC timestamp
            fname = f"generated-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}.json"
            path = os.path.join(outdir, fname)
            try:
                # if it's valid JSON string, save as-is; otherwise save as text
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.last_generated)
                await self.append_message("SYSTEM", f"已保存: {path}")
            except Exception as e:
                await self.append_message("SYSTEM", f"保存失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="Run Textual chat TUI")
    parser.add_argument("--backend", choices=["openai"], default="openai")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--setup", action="store_true", help="Interactively configure LLM API before launching TUI")
    args = parser.parse_args()

    # Interactive pre-TUI setup
    if args.setup:
        print("== LLM API Setup ==")
        backend = input(f"Backend (openai) [{args.backend}]: ").strip() or args.backend
        api_key = input("API key (enter to skip): ").strip() or None
        endpoint = input("Endpoint / API base (enter to skip): ").strip() or None
        # allow arbitrary backend string
        args.backend = backend
        args.api_key = api_key
        args.endpoint = endpoint
        try:
            if api_key is None and endpoint is None:
                clear_llm_api()
            else:
                set_llm_api(api_key=api_key, endpoint=endpoint)
            print("LLM configuration saved.")
        except Exception as e:
            print(f"Failed to save LLM config: {e}")

    # If user provided API key via CLI, set global config (optional)
    if args.api_key:
        set_llm_api(api_key=args.api_key, endpoint=args.endpoint)

    # Enforce pre-TUI API key for openai backend: prompt if missing
    if args.backend == "openai":
        try:
            cfg = get_llm_api() or {}
        except Exception:
            cfg = {}
        if not args.api_key and not cfg.get("api_key"):
            print("OpenAI backend selected but no API key configured.")
            key = input("Enter API key (or leave empty to cancel): ").strip()
            if not key:
                print("API key required for openai backend. Aborting.")
                return
            args.api_key = key
            try:
                set_llm_api(api_key=args.api_key, endpoint=args.endpoint)
                print("LLM configuration saved.")
            except Exception as e:
                print(f"Failed to save LLM config: {e}")
                return

    # launch TUI with configured backend
    app = TextualChatApp(backend=args.backend, api_key=args.api_key, endpoint=args.endpoint)
    app.run()


if __name__ == "__main__":
    main()
