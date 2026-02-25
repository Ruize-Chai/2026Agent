import json
from typing import Any, Union

from pydantic import ValidationError

from Schema.payload.node_payload import NodePayload
from Schema.payload.workflow_payload import WorkflowPayload
from Logger import (
	NodePayloadValidationError,
	WorkflowPayloadValidationError,
	NodeDictValidationError,
	WorkflowDictValidationError,
)

#安全转化dict
def _ensure_dict(data: Union[str, dict, Any]) -> dict:
	"""尝试把输入转为 dict,失败时抛出 ValueError。"""
	if isinstance(data, dict):
		return data
	if isinstance(data, str):
		try:
			parsed = json.loads(data)
			if isinstance(parsed, dict):
				return parsed
			raise ValueError("JSON does not represent an object")
		except Exception as e:
			raise ValueError(f"Invalid JSON: {e}")
	raise ValueError("Unsupported data type, expected dict or JSON string")

#校验node pydantic payload
def is_valid_node_payload(data: Union[str, dict, Any]) -> bool:
	"""验证 `NodePayload`，校验失败时抛出 `NodePayloadValidationError`。成功返回 True。"""
	try:
		d = _ensure_dict(data)
	except ValueError as e:
		raise NodePayloadValidationError(str(e))
	try:
		NodePayload(**d)
		return True
	except ValidationError as ve:
		raise NodePayloadValidationError(str(ve))
	except Exception as e:
		raise NodePayloadValidationError(str(e))

#校验workflow pydantic payload
def is_valid_workflow_payload(data: Union[str, dict, Any]) -> bool:
	"""验证 `WorkflowPayload`，校验失败时抛出 `WorkflowPayloadValidationError`。成功返回 True。"""
	try:
		d = _ensure_dict(data)
	except ValueError as e:
		raise WorkflowPayloadValidationError(str(e))
	try:
		WorkflowPayload(**d)
		return True
	except ValidationError as ve:
		raise WorkflowPayloadValidationError(str(ve))
	except Exception as e:
		raise WorkflowPayloadValidationError(str(e))

#校验node python dict
def is_valid_node_dict(d: Any) -> bool:
	"""针对已解析的 Python dict 做结构校验，校验失败时抛出 `NodeDictValidationError`。"""
	if not isinstance(d, dict):
		raise NodeDictValidationError("payload is not a dict")
	# 必需字段
	if "type" not in d or not isinstance(d["type"], str):
		raise NodeDictValidationError("`type` missing or invalid")
	# inputs
	inputs = d.get("inputs", [])
	if not isinstance(inputs, list) or not all(isinstance(i, int) for i in inputs):
		raise NodeDictValidationError("`inputs` missing or invalid")
	# outputs
	outputs = d.get("outputs", [])
	if not isinstance(outputs, list) or not all((isinstance(o, int) or o is None) for o in outputs):
		raise NodeDictValidationError("`outputs` missing or invalid")
	# params
	params = d.get("params", None)
	if not isinstance(params, dict):
		raise NodeDictValidationError("`params` missing or invalid")
	# listen
	listen = d.get("listen", [])
	if listen is not None and (not isinstance(listen, list) or not all(isinstance(i, int) for i in listen)):
		raise NodeDictValidationError("`listen` missing or invalid")
	return True

#校验workflow python dict
def is_valid_workflow_dict(d: Any) -> bool:
	"""针对已解析的 Python dict 做 workflow 结构校验，校验失败时抛出 `WorkflowDictValidationError`。"""
	if not isinstance(d, dict):
		raise WorkflowDictValidationError("payload is not a dict")
	if "workflow_id" not in d or not isinstance(d["workflow_id"], str) or len(d["workflow_id"]) == 0:
		raise WorkflowDictValidationError("`workflow_id` missing or invalid")
	if "entry" not in d or not isinstance(d["entry"], int):
		raise WorkflowDictValidationError("`entry` missing or invalid")
	nodes = d.get("nodes", None)
	if not isinstance(nodes, list) or len(nodes) < 1:
		raise WorkflowDictValidationError("`nodes` missing or invalid")
	for n in nodes:
		if not isinstance(n, dict):
			raise WorkflowDictValidationError("each node must be an object/dict")
		if "id" not in n or not isinstance(n.get("id"), int):
			raise WorkflowDictValidationError("node.id must be an integer")
		if "type" not in n or not isinstance(n.get("type"), str):
			raise WorkflowDictValidationError("node.type must be a string")
		# reuse node dict checks for node-like fields
		try:
			is_valid_node_dict({
				"type": n.get("type"),
				"inputs": n.get("inputs", []),
				"outputs": n.get("outputs", []),
				"params": n.get("params", {}),
				"listen": n.get("listen", []),
			})
		except NodeDictValidationError as nde:
			raise nde
	return True

