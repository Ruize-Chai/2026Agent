import json
from pathlib import Path
from typing import Any, Dict, List

try:
	from jsonschema import Draft7Validator
except ImportError:  # pragma: no cover - optional dependency
	Draft7Validator = None

_CORE_DIR = Path(__file__).resolve().parents[1]
_WORKFLOW_SCHEMA_PATH = _CORE_DIR / "workflow" / "workflow_schema.json"
_SKILL_SCHEMA_PATH = _CORE_DIR / "skill" / "plugin_manifest_schema.json"


def _load_schema(schema_path: Path) -> Dict[str, Any]:
	"""
	从Path加载schema
	"""
	with schema_path.open("r", encoding="utf-8") as file:
		return json.load(file)


def _validate_with_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
	"""
	通用schema校验
	"""
	if Draft7Validator is None:
		raise ImportError("jsonschema is required for schema validation")

	validator = Draft7Validator(schema)
	errors = sorted(validator.iter_errors(data), key=lambda err: list(err.path))
	messages: List[str] = []
	for err in errors:
		if err.path:
			path = "/".join(map(str, err.path))
			messages.append(f"{path}: {err.message}")
		else:
			messages.append(err.message)
	return messages


def validate_workflow(data: Dict[str, Any], raise_on_error: bool = True) -> List[str]:
	"""
	workflow类型数据校验
	"""
	schema = _load_schema(_WORKFLOW_SCHEMA_PATH)
	errors = _validate_with_schema(data, schema)
	if errors and raise_on_error:
		raise ValueError("Workflow schema validation failed: " + "; ".join(errors))
	return errors


def validate_skill(data: Dict[str, Any], raise_on_error: bool = True) -> List[str]:
	"""
	skill类型数据校验
	"""
	schema = _load_schema(_SKILL_SCHEMA_PATH)
	errors = _validate_with_schema(data, schema)
	if errors and raise_on_error:
		raise ValueError("Skill schema validation failed: " + "; ".join(errors))
	return errors
