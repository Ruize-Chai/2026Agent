from typing import Any, List, Dict
import os
import json
import uuid

from Nodes.node import Node


class Self_Node(Node):
    """LLM_FileProduction：使用 LLM 生成文件内容并保存到 `FileBase/`。

    行为（按 DesignFull）：
    - 采集 `params.context_slot` 指定的上下文作为生成输入。
    - 使用全局 `Workflow.llm_config` 提供的 api_key/endpoint 调用 LLM，生成文件内容（文本或二进制以文本形式返回）。
    - 将生成结果保存为 `FileBase/{file_id}.{ext}`，默认扩展名可通过 `param_config.file_ext` 指定。
    - 更新或创建 `FileBase/filebaselists.json`，将新文件的元数据（id, filename）加入列表。
    - 在节点 `context` 中写入 `file_id` 与 `path`，并缓存到 `ex_hub` 以供前端读取。

    Context Outputs:
    - `file_id` (str): 生成的文件唯一 id（文件名，不含扩展名）。
    - `path` (str): 文件系统路径，例：`FileBase/{file_id}.txt`。
    """

    def __init__(self, data: dict, llm_config=None, **kwargs) -> None:
        super().__init__(data, **kwargs)
        self.llm_config = llm_config

    def _gather_contexts(self) -> List[str]:
        params = self.params or {}
        slots = params.get("context_slot", [])
        results: List[str] = []
        node_getter = getattr(self, "node_getter", None)
        for s in slots:
            try:
                sid = int(s.get("id"))
                key = s.get("key")
            except Exception:
                continue

            if sid == self.node_id:
                if isinstance(self.context, dict) and key in self.context:
                    results.append(str(self.context.get(key)))
                    continue
                for c in (self.contexts or []):
                    if isinstance(c, dict) and key in c:
                        results.append(str(c.get(key)))
                        continue

            if callable(node_getter):
                try:
                    target = node_getter(sid)
                    if target is not None:
                        tctx = getattr(target, "context", None)
                        if isinstance(tctx, dict) and key in tctx:
                            results.append(str(tctx.get(key)))
                            continue
                        for c in getattr(target, "contexts", []) or []:
                            if isinstance(c, dict) and key in c:
                                results.append(str(c.get(key)))
                                continue
                except Exception:
                    pass

        return results

    def _call_llm(self, prompt: str, cfg: Dict[str, Any]) -> str:
        api_key = None
        endpoint = None
        try:
            if self.llm_config is not None:
                cfgvals = getattr(self.llm_config, "get_llm_api", lambda: {"api_key": None, "endpoint": None})()
            else:
                from Workflow.llm_config import get_llm_api

                cfgvals = get_llm_api()
            api_key = cfgvals.get("api_key")
            endpoint = cfgvals.get("endpoint")
        except Exception:
            api_key = None
            endpoint = None

        # Use centralized LLM client to handle compatibility
        try:
            from LLM import create_client

            client = create_client(backend="openai", api_key=api_key, endpoint=endpoint)
            # use async wrapper via to_thread
            try:
                # call generate synchronously inside thread
                generated = client.generate(prompt, model=cfg.get("model", "gpt-3.5-turbo"), max_tokens=cfg.get("max_tokens", 512))
            except Exception:
                # try async path
                generated = client.generate(prompt, model=cfg.get("model", "gpt-3.5-turbo"), max_tokens=cfg.get("max_tokens", 512))
            return generated
        except Exception as e:
            return f"LLM call failed: {e}"

    def _save_file(self, content: str, ext: str = "txt") -> Dict[str, str]:
        base_dir = os.path.join(os.getcwd(), "FileBase")
        os.makedirs(base_dir, exist_ok=True)
        fid = str(uuid.uuid4())
        filename = f"{fid}.{ext}"
        path = os.path.join(base_dir, filename)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            with open(path, "wb") as f:
                f.write(content.encode("utf-8", errors="ignore"))

        lists_path = os.path.join(base_dir, "filebaselists.json")
        try:
            if os.path.exists(lists_path):
                with open(lists_path, "r", encoding="utf-8") as f:
                    lists = json.load(f)
            else:
                lists = []
        except Exception:
            lists = []

        entry = {"id": fid, "filename": filename}
        lists.append(entry)
        try:
            with open(lists_path, "w", encoding="utf-8") as f:
                json.dump(lists, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        return {"file_id": fid, "path": path}

    def execute(self) -> List[int]:
        params = self.params or {}
        cfg = params.get("param_config", {}) or {}

        contents = self._gather_contexts()
        prompt = cfg.get("prompt_template") or ("Generate file content from context:\n{context}".replace("{context}", "\n".join(contents)))

        generated = self._call_llm(prompt, cfg)

        file_ext = cfg.get("file_ext") or "txt"
        saved = self._save_file(generated, ext=file_ext)

        try:
            if not isinstance(self.context, dict):
                self.context = {}
            self.context.update(saved)
        except Exception:
            pass

        ex_hub = getattr(self, "ex_hub", None)
        if ex_hub is not None:
            try:
                ex_hub.cache(self.node_id, saved)
            except Exception:
                pass

        listener = getattr(self, "listener", None)
        if listener is not None:
            try:
                listener.set_state(self.node_id, "OUTPUT")
            except Exception:
                pass

        return list(range(len(self.outputs or [])))
