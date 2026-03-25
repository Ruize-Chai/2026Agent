from typing import Any, List, Optional, Dict
import asyncio

from Nodes.node import Node


class Self_Node(Node):
    """LLM_Answer 节点：使用大模型根据指定的上下文生成回答。

    行为：
    - 通过 `params.context_slot` 指定要采集的上下文（list of {id:int,key:str}）。
    - 将采集到的上下文合并为 prompt（可通过 `params.param_config.prompt_template` 自定义模板）。
    - 使用全局 `Workflow.llm_config.get_llm_api()` 的 `api_key` / `endpoint`（或通过构造函数传入的 `llm_config` 覆盖）作为默认凭证。
    - 调用 `openai`（若可用且配置正确）生成响应，将结果写入节点 `context`（键由 `params.param_config.key` 指定，默认 `answer`），并把输出缓存到 `ex_hub` 以供前端读取。

    Context Outputs:
    - `answer` (str): LLM 生成的文本回答（默认键，可由 `param_config.key` 覆盖）。
    """

    def __init__(self, data: dict, llm_config=None, **kwargs) -> None:
        super().__init__(data, **kwargs)
        # llm_config 可以是 Workflow.llm_config 模块或 None
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

            # 本节点
            if sid == self.node_id:
                if isinstance(self.context, dict) and key in self.context:
                    results.append(str(self.context.get(key)))
                    continue
                for c in (self.contexts or []):
                    if isinstance(c, dict) and key in c:
                        results.append(str(c.get(key)))
                        continue

            # 其它节点
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

    async def execute(self) -> List[int]:
        params = self.params or {}
        cfg = params.get("param_config", {}) or {}
        key = cfg.get("key", "answer")
        model = cfg.get("model", "text-davinci-003")
        prompt_template = cfg.get("prompt_template")

        contents = self._gather_contexts()
        if prompt_template:
            # 简单模板替换 {context}
            prompt = prompt_template.replace("{context}", "\n".join(contents))
        else:
            prompt = "\n".join(contents)

        listener = getattr(self, "listener", None)
        if listener is not None:
            try:
                listener.set_state(self.node_id, "ACTIVE")
            except Exception:
                pass

        # 获取全局或注入的 llm 配置
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

        # Use the central LLM client wrapper to handle compatibility with different openai versions
        result_text = ""
        try:
            from LLM import create_client

            client = create_client(backend="openai", api_key=api_key, endpoint=endpoint)
            # Synchronous generate is fine inside async when executed in thread by client
            # Use asyncio.to_thread via client.generate_async to avoid blocking
            try:
                result_text = await client.generate_async(prompt, model=model, max_tokens=cfg.get("max_tokens", 256))
            except Exception:
                # fallback to sync generate in thread
                result_text = await client.generate_async(prompt, model=model, max_tokens=cfg.get("max_tokens", 256))
        except Exception as e:
            result_text = f"LLM client unavailable: {e}"

        # 写入节点 context
        try:
            if not isinstance(self.context, dict):
                self.context = {}
            self.context[key] = result_text
        except Exception:
            pass

        # 缓存到 ex_hub 供前端读取
        ex_hub = getattr(self, "ex_hub", None)
        if ex_hub is not None:
            try:
                ex_hub.cache(self.node_id, {key: result_text})
            except Exception:
                pass

        if listener is not None:
            try:
                listener.set_state(self.node_id, "OUTPUT")
            except Exception:
                pass

        return list(range(len(self.outputs or [])))
