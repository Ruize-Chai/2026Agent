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
from Json_Utils.json_validate import is_valid_workflow_dict

def load_generation_context() -> str:
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
        context += "### EXAMPLE VALID STRUCTURE (FOLLOW THIS STRICTLY):\n"
        context += """
{
  "workflow_id": "example_id",
  "entry": 1,
  "nodes": [
    {
      "id": 1,
      "type": "Start",
      "params": {},
      "inputs": [],
      "outputs": [2]
    }
  ]
}
"""
        context += "\n### OUTPUT REQUIREMENT:\nReturn ONLY a valid JSON object. Ensure EVERY node has 'id', 'type', 'params', 'inputs', and 'outputs' (use [] if empty). No conversational filler."
        return context
    except Exception as e:
        return f"Context loading failed: {e}"

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
        yield Static("Commands: @G <instruction> — generate workflow", id="help")

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
        

        # If user input begins with @G, run the fixed GenerateWorkflow flow
        if text.startswith("@G"):
            # collect context from previous messages (simple concatenation)
            ctx_lines = []
            for line in self._msg_lines:
                ctx_lines.append(line)

            # also include remainder after @G as instruction
            remainder = text[2:].strip()
            if remainder:
                ctx_lines.append(f"INSTRUCTION: {remainder}")

            # 获取包含 Schema Rules 和 Plugin 列表的上下文
            gen_context = load_generation_context()
            prompt = f"{gen_context}\n\nUSER REQUEST: {remainder}\n\nGENERATE WORKFLOW JSON NOW:\n"

            await self.append_message("SYSTEM", "开始按 Schema 生成工作流...")
            try:
                generated = await self.client.generate_async(prompt, model="minimax/minimax-m2.5", max_tokens=1024)
            except Exception as e:
                generated = f"LLM call failed: {e}"

            # 提取 JSON (防止 LLM 输出 Markdown 代码块)
            raw_content = generated.strip()
            if raw_content.startswith("```json"):
                raw_content = raw_content[7:]
            if raw_content.strip().endswith("```"):
                # 处理末尾可能有的 ``` 标号
                idx = raw_content.rfind("```")
                if idx != -1:
                    raw_content = raw_content[:idx]
            raw_content = raw_content.strip()

            await self.append_message("ASSISTANT", raw_content)

            # 校验与展示逻辑
            pretty = raw_content
            as_json = False
            try:
                parsed = json.loads(raw_content)
                as_json = True
                try:
                    is_valid_workflow_dict(parsed)
                    await self.append_message("SYSTEM", "✅ Schema 校验通过！")
                except Exception as ve:
                    await self.append_message("SYSTEM", f"❌ Schema 校验失败: {ve}")
                
                # 美化显示
                pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
            except Exception as e:
                await self.append_message("SYSTEM", f"JSON 解析失败: {e}")
                pretty = generated

            self.last_generated = pretty
            try:
                self.preview.update(pretty)
            except Exception:
                pass

            # auto-save behavior
            try:
                base_dir = os.path.join(os.getcwd(), "WorkflowBase")
                os.makedirs(base_dir, exist_ok=True)
                
                # 优先使用 JSON 中的 workflow_id 作为文件名
                if as_json and isinstance(parsed, dict) and parsed.get("workflow_id"):
                    filename = f"{parsed['workflow_id']}.json"
                    wid = parsed["workflow_id"]
                else:
                    wid = str(uuid.uuid4())
                    filename = f"{wid}.json"
                
                path = os.path.join(base_dir, filename)
                
                # 写入文件
                with open(path, "w", encoding="utf-8") as f:
                    f.write(pretty)

                # 更新 workflowlists.json 索引
                lists_path = os.path.join(base_dir, "workflowlists.json")
                lists = []
                try:
                    if os.path.exists(lists_path):
                        with open(lists_path, "r", encoding="utf-8") as f:
                            lists = json.load(f)
                        if not isinstance(lists, list):
                            lists = []
                except Exception:
                    lists = []
                
                # 避免重复添加同一个 ID
                if not any(item.get("id") == wid for item in lists):
                    lists.append({"id": wid, "filename": filename})
                
                with open(lists_path, "w", encoding="utf-8") as f:
                    json.dump(lists, f, ensure_ascii=False, indent=2)

                await self.append_message("SYSTEM", f"工作流已同步至本地: {filename}")
            except Exception as e:
                await self.append_message("SYSTEM", f"本地同步失败: {e}")

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
