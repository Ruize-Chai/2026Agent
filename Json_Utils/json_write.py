import json
from typing import Any, Dict, Optional

from .json_validate import is_valid_node_dict, is_valid_workflow_dict
from Logger import WriteFileNotFoundError


def write_json_file(path: str, data: Dict[str, Any], *, indent: Optional[int] = 2) -> None:
	"""将 dict 写入 JSON 文件。"""
	if not isinstance(data, dict):
		raise ValueError("data must be a dict")
	try:
		with open(path, "w", encoding="utf-8") as f:
			json.dump(data, f, ensure_ascii=False, indent=indent)
	except FileNotFoundError as e:
		raise WriteFileNotFoundError(str(e))


def write_node_json(path: str, data: Dict[str, Any], *, indent: Optional[int] = 2) -> None:
	"""在写入前用 `is_valid_node_dict` 校验，校验失败会抛出错误。"""
	is_valid_node_dict(data)
	write_json_file(path, data, indent=indent)


def write_workflow_json(path: str, data: Dict[str, Any], *, indent: Optional[int] = 2) -> None:
	"""在写入前用 `is_valid_workflow_dict` 校验，校验失败会抛出错误。"""
	is_valid_workflow_dict(data)
	write_json_file(path, data, indent=indent)
