# Oriflow-Agent (Workflow Generator)

Oriflow-Agent is a specialized TUI (Terminal User Interface) based generation system that transforms natural language into schema-compliant, executable workflow JSON files.

## Quick Start

### 1. Prerequisites
Ensure Python 3.10+ is installed, then install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure & Launch
Start the interactive generator using `tools/textual_tui.py`:
```bash
python tools/textual_tui.py --setup
```
*   **API Key**: Enter your OpenAI or Qiniu Minimax API key.
*   **Endpoint**: Set the API base URL (e.g., `https://api.qnaigc.com/v1`).

### 3. Generate Workflows
Interact directly with the AI in the TUI interface.
*   **Free Chat**: Describe your requirements or ask about plugin capabilities.
*   **Core Command `@G`**: Use the `@G` prefix to trigger workflow generation.
    *   *Example*: `@G generate a workflow to analyze CSV data and plot a line chart`
*   **Validate & Save**: 
    *   The system performs real-time validation against `OriflowPrompts/SchemaRulePrompts.md`.
    -   Generated workflows are automatically saved to the `WorkflowBase/` directory.

## Core Features
- **Strict Schema Enforcement**: Validates node IDs, I/O links, and parameter integrity automatically.
- **Sticky Scroll Lock**: The chat window stays locked to the bottom for the latest messages.
- **Formatted Preview**: Real-time, pretty-printed JSON preview in the right panel.
- **Provider Agnostic**: Fully compatible with OpenAI, Qiniu, Minimax, and other standard API protocols.

## Documentation Reference
- Node Contexts: `Docs/nodes_contexts_v2.md`
- Generation Rules: `OriflowPrompts/SchemaRulePrompts.md`
- API Reference: `Docs/Server_API.md`
