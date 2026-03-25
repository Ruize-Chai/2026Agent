# Oriflow-Agent (Workflow Generator)

Oriflow-Agent 是一个强大的基于 TUI（终端用户界面）的工作流对话生成系统。它能够通过自然语言对话，自动生成符合规范（Schema）的可执行工作流 JSON 配置文件。

## 快速开始

### 1. 环境准备
确保已安装 Python 3.10+，并安装必要依赖：
```bash
pip install -r requirements.txt
```

### 2. 配置与启动
使用 `tools/textual_tui.py` 进入交互式生成界面：
```bash
python tools/textual_tui.py --setup
```
*   **API Key**: 输入你的 OpenAI 或七牛云 Minimax API Key。
*   **Endpoint**: 输入 API 地址（例如：`https://api.qnaigc.com/v1`）。

### 3. 生成工作流
一旦进入 TUI 界面，你可以直接与 AI 对话。
*   **普通对话**: 描述你的需求或询问插件功能。
*   **核心指令 `@G`**: 使用 `@G` 前缀让 AI 生成工作流 JSON。
    *   *示例*: `@G 生成一个分析 CSV 数据并绘制折线图的工作流`
*   **校验与保存**: 
    *   系统会自动根据 `OriflowPrompts/SchemaRulePrompts.md` 进行实时校验。
    -   工作流会自动保存到 `WorkflowBase/` 目录下。

## 核心特性
- **Schema 强约束**: 自动校验节点 ID、输入输出链路及参数合法性。
- **自动滚动锁定**: 聊天窗口持续自动锁定到最新回复。
- **美化展示**: 右侧预览窗口实时格式化展示生成的 JSON。
- **多端适配**: 完美兼容 OpenAI 及国内七牛云、Minimax 等主流 API 协议。

## 文档参考
- 节点规范：`Docs/nodes_contexts_v2.md`
- 规则配置：`OriflowPrompts/SchemaRulePrompts.md`
- 接口说明：`Docs/Server_API.md`
