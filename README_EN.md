# Oriflow Smith (Workflow Generator)

Oriflow Smith is a specialized TUI (Terminal User Interface) based generation system that transforms natural language into schema-compliant, executable workflow JSON files.

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

### 3. Workflow Commands (Oriflow Smith Laboratory)
Once inside the TUI, use these commands to collaborate with AI:
*   **`@G <description>`**: **Generate** a new workflow from scratch. Example: `@G Create a summarizer`.
*   **`@Ud <edit>`**: **Update** specific fields in the current workflow. Example: `@Ud rename 'summarizer' to 'translator'`.
*   **`@It <feedback>`**: **Iterate** and optimize the logic. Example: `@It add a 3s delay before the summary`.

## Core Features
- **Auto-Retry Validation**: If AI output fails schema checks, the system automatically redirects errors back to the AI for fixed output (up to 3 retries), ensuring 100% correct JSON.
- **Plugin Whitelist Enforcement**: Only allows existing node types (e.g., `CHATbox`, `LLM_QA`, `DelayTimer`), preventing hallucinated models.
- **Pretty Printing**: Real-time rendering of all generated JSON in the chat for the best readability.
- **Persistent Storage**: All validated files are automatically saved to the `WorkflowBase/` directory (ignored in .gitignore).
- **Provider Agnostic**: Fully compatible with OpenAI, Qiniu, Minimax, and other standard API protocols.

## Documentation Reference
- Node Contexts: `Docs/nodes_contexts_v2.md`
- Generation Rules: `OriflowPrompts/SchemaRulePrompts.md`
- API Reference: `Docs/Server_API.md`
