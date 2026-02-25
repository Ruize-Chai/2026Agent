import json
from typing import Any, Dict

from .json_validate import is_valid_node_dict, is_valid_workflow_dict
from Logger import ReadFileNotFoundError


def read_json_file(path: str) -> Dict[str, Any]:
	"""从文件读取 JSON 并返回 dict。"""
	try:
		with open(path, "r", encoding="utf-8") as f:
			data = json.load(f)
	except FileNotFoundError as e:
		raise ReadFileNotFoundError(str(e))
	if not isinstance(data, dict):
		raise ValueError("JSON file does not contain an object at top level")
	return data


def read_node_json(path: str) -> Dict[str, Any]:
	"""读取 node JSON 文件并用 `is_valid_node_dict` 校验，校验失败会抛出错误。"""
	data = read_json_file(path)
	# is_valid_node_dict 会在失败时抛出 NodeDictValidationError
	is_valid_node_dict(data)
	return data


def read_workflow_json(path: str) -> Dict[str, Any]:
	"""读取 workflow JSON 文件并用 `is_valid_workflow_dict` 校验，校验失败会抛出错误。"""
	data = read_json_file(path)
	is_valid_workflow_dict(data)
	return data
