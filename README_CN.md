# Oriflow Smith (Workflow Generator)

Oriflow Smith 是一个强大的基于 TUI（终端用户界面）的工作流对话生成系统。它能够通过自然语言对话，自动生成符合规范（Schema）的可执行工作流 JSON 配置文件。

## 快速开始

### 1. 环境准备
确保已安装 Python 3.10+，并安装必要依赖：
```bash
pip install -r requirements.txt
```

### 2. 配置与启动
使用 `tools/textual_tui.py` 进入 Oriflow Smith 实验室：
```bash
python tools/textual_tui.py --setup
```
*   **API Key**: 输入你的 OpenAI 或七牛云 Minimax API Key。
*   **Endpoint**: 输入 API 地址（例如：`https://api.qnaigc.com/v1`）。

### 3. 工作流指令 (Oriflow Smith 实验室)
一旦进入 TUI 界面，使用以下命令与 AI 协作：
*   **`@G <描述>`**: **从零生成** 工作流。示例：`@G 生成一个提取文章摘要的工作流`。
*   **`@Ud <修改>`**: **局部更新** 已有工作流。示例：`@Ud 把 workflow_name 改为翻译助手`。
*   **`@It <反馈>`**: **逻辑迭代**。示例：`@It 在节点 2 后面加一个 3 秒延迟的 DelayTimer`。

## 核心特性
- **Schema 自动纠错**: 如果 AI 输出格式有误，系统会自动拦截并报错回传给 AI 重新尝试（限3次），确保最终输出 100% 正解。
- **插件白名单约束**: 强制 AI 只能使用现有的节点类型（如 `CHATbox`, `LLM_QA`, `DelayTimer` 等），杜绝幻觉。
- **美化展示**: 实时 Pretty-Print 渲染 JSON 对话，确保可读性。
- **本地持久化**: 所有成功校验的文件自动保存到 `WorkflowBase/` 目录下（已在 .gitignore 中忽略）。
- **多端适配**: 完美兼容 OpenAI 及国内七牛云、Minimax 等主流 API 协议。

## 文档参考
- 节点规范：`Docs/nodes_contexts_v2.md`
- 规则配置：`OriflowPrompts/SchemaRulePrompts.md`
- 接口说明：`Docs/Server_API.md`
