Plugin Lists Reference (English) — supplemental to Plugins/pluginLists.json

For each plugin name in `Plugins/pluginLists.json`, provide a short description and the minimal interface expected by the workflow system.

Format for each entry:
- Name: <plugin name>
- Description: 1-2 lines
- Minimal params: { field: type (required|optional) }
- Inputs/Outputs: brief semantics (how inputs/outputs are used)
- Notes: limitations, common failure modes, retry suggestions

Examples (short):
- HttpRequest:
  - Description: Perform an HTTP request to a URL and emit success/fail outputs.
  - Minimal params: { method: string (required), url: string (required), timeout: int (optional) }
  - Inputs/Outputs: single input; outputs: [success_index, failure_index] (by convention)
  - Notes: network failures should be handled by retry or failure branch.

- DelayTimer:
  - Description: Wait for a specified number of seconds, then continue.
  - Minimal params: { seconds: int (required) }
  - Inputs/Outputs: no special semantics; acts as a pass-through delay.

Usage guidance:
- Models generating or repairing workflows should consult this file to pick reasonable default params and to avoid inventing unsupported capabilities.
