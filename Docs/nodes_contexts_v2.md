```markdown
# Node Context Outputs Reference (updated)

本文件列出各节点类型向 `context` 中写入或向前端 `ex_hub` 缓存的数据字段和类型，供前端开发者参考。

- Start
  - Context Outputs: 无

- End
  - Context Outputs: 无

- TextInput
  - Context Outputs: `<key>` (str) — 用户输入的文本，键名由 `params.param_config.key` 指定，默认 `text`。

- NumberInput
  - Context Outputs: `<key>` (int|float) — 用户输入的数字，键名由 `params.param_config.key` 指定，默认 `number`。

- Chatbox / CHATbox
  - Context Outputs: `message` (str) — 合并后的聊天消息文本，键名可通过 `param_config.message_key` 覆盖。
  - Exposed via `ex_hub.cache(node_id, {message_key: message})`。

- Checkbox
  - Context Outputs: `selection` (list[str] or list[int]) — 用户最终选择的项（前端在用户确认后 POST 回来并由后端写入节点 `context`）。
  - Options exposed via `ex_hub.cache(node_id, {"options": [...]})`。

- DelayTimer
  - Context Outputs: 无

- IfCondition
  - Context Outputs: 无（基于其它节点 `context` 中的布尔字段进行分支，不写入新的 context）

- LLM_Answer
  - Context Outputs: `answer` (str) — LLM 生成的文本回复，默认键为 `answer`，可通过 `params.param_config.key` 覆盖。
  - Exposed via `ex_hub.cache(node_id, {key: answer})`。


如需新增节点类型或修改字段，请同步更新本文件以及相应插件模块头部的说明。

<!-- LLM_GenerateWorkflow 已移除：生成/存储工作流由工具链或前端交互处理 -->

- LLM_FileProduction
  - Context Outputs: `file_id` (str) — 生成的文件唯一 id（文件名，不含扩展名）。
  - Context Outputs: `path` (str) — 文件系统路径，例：`FileBase/{file_id}.txt`。
  - Exposed via `ex_hub.cache(node_id, {"file_id": file_id, "path": path})`。

```
