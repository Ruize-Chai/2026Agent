Schema Rule Prompts (Concise protocol and validator guidance)

Provide these rules to other models as a canonical compact reference describing how workflow schema maps to executable structure.

Key rules:
- Top-level `workflow` requirements: must include `workflow_id` (non-empty string), `entry` (node id integer), and `nodes` (array, at least 1 element).
- Node structure: each node must include `id` (int), `type` (string - must appear in plugin list), `params` (object or empty), `inputs` (array of ints or empty), `outputs` (array of ints or null), `listen` (optional array of ints).
- Plugin contract: nodes must communicate via `inputs`/`outputs` indexes and use only simple param primitives (string, number, bool, object). Plugins must not embed code or external script references in params.
- Validation focuses: required field presence, exact type matching, array element types, enum checks (node type in plugin list), and referential integrity (inputs/outputs reference existing node ids).
- Error report format: { "path": "<JSON Pointer>", "code": <optional code>, "message": "...", "suggested_fix": "..." }

Instruction to models using this prompt:
- For any automatic fix produce before/after diffs for auditability.
- Avoid changing semantics unless explicitly requested; when in doubt, add placeholders and surface the uncertainty in output.
