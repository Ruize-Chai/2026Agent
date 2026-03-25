# 参数配置参考（`param_config`）

本文档列出各节点可设置的 `params.param_config` 字段、含义与默认值，便于前端或工作流设计者配置节点行为。

- **TextInput**
  - `key` (str): 写入 `context` 的键名。默认 `text`。
  - `prompt` (str, optional): 缓存给前端的提示文本（通过 `ex_hub.cache(node_id, {"prompt": prompt})`）。

- **NumberInput**
  - `key` (str): 写入 `context` 的键名。默认 `number`。
  - `prompt` (str, optional): 缓存给前端的提示文本。

- **CHATbox / Chatbox**
  - `message_key` (str): 缓存到 `ex_hub` 的键名，默认 `message`。

- **Checkbox**
  - 前端/后端在交互时约定返回的 `selection` 字段名（无强制字段名，通常前端直接 POST 结构化选择结果，后端在收到后写入节点 `context` 的具体键）。

- **DelayTimer**
  - `duration` (number): 延时秒数，默认 `1`。

- **IfCondition**
  - 无统一 `param_config` 字段（条件判定依据由 `params.context_slot` 指定的上下文键决定）。

- **LLM_Answer**（及继承类如 `LLM_Summarize`, `LLM_QA`, `LLM_Translate`, `LLM_CodeGeneration`, `LLM_Conversation`）
  - `key` (str): 写入节点 `context` 的键名，默认 `answer`。
  - `model` (str): LLM 模型标识，默认 `text-davinci-003`（若使用 ChatCompletion 则可为 `gpt-3.5-turbo` 类模型）。
  - `prompt_template` (str, optional): 自定义模板，模板中可使用 `{context}` 占位符代表采集到的上下文文本。
  - `max_tokens` (int, optional): 生成最大 token 数，默认约 `256`（插件可读取并传递给 LLM 客户端）。
  - 特定继承插件额外字段：
    - `LLM_Translate`: `target_lang` (str) — 若提供则插件会填充默认 `prompt_template`。
    - `LLM_CodeGeneration`: `language` (str) — 指定目标编程语言，插件会填充默认 `prompt_template`。

<!-- LLM_GenerateWorkflow 已移除：相关生成功能由外部工具或 TUI 处理 -->

- **LLM_FileProduction**
  - `prompt_template` (str, optional): 指定用于生成文件内容的模板。
  - `file_ext` (str, optional): 生成文件的扩展名，默认 `txt`。
  - `model`, `max_tokens` 等同 `LLM_Answer` 的配置项。

示例 `params`:

```json
{
  "context_slot": [{"id": 1, "key": "text"}],
  "param_config": {
    "key": "answer",
    "prompt_template": "Summarize:\n{context}",
    "model": "gpt-3.5-turbo",
    "max_tokens": 300
  }
}
```

说明：所有节点实现从 `params` 中使用 `params.get("param_config", {})` 读取配置。若字段缺失，则使用插件内设定的默认值。LLM 系列插件会优先使用注入的 `llm_config`（若存在）或全局 `Workflow.llm_config.get_llm_api()` 返回的凭证调用模型。

如需补充某个节点的更多可配置项，告诉我我会把该节点的 `param_config` 字段补充到本文件中并更新 `Docs/nodes_contexts_v2.md`。
