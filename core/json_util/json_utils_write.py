import json
from pathlib import Path
from typing import Any, Dict

from core.json_util.json_utils_confirm import validate_skill, validate_workflow


def read_json_file(file_path: str) -> Dict[str, Any]:
	"""
	通用读取json文件
	"""
	with open(file_path, "r", encoding="utf-8") as file:
		return json.load(file)


def write_json_file(data: Dict[str, Any], file_path: str) -> None:
	"""
	通用写入json文件
	"""
	path = Path(file_path)
	path.parent.mkdir(parents=True, exist_ok=True)
	with path.open("w", encoding="utf-8") as file:
		json.dump(data, file, ensure_ascii=True, indent=2)


def read_workflow_file(file_path: str, validate: bool = True) -> Dict[str, Any]:
	"""
	读取workflow文件(可选校验)
	"""
	data = read_json_file(file_path)
	if validate:
		validate_workflow(data, raise_on_error=True)
	return data


def write_workflow_file(data: Dict[str, Any], file_path: str, validate: bool = True) -> None:
	"""
	写入workflow文件(可选校验)
	"""
	if validate:
		validate_workflow(data, raise_on_error=True)
	write_json_file(data, file_path)


def read_skill_file(file_path: str, validate: bool = True) -> Dict[str, Any]:
	"""
	读取skill文件(可选校验)
	"""
	data = read_json_file(file_path)
	if validate:
		validate_skill(data, raise_on_error=True)
	return data


def write_skill_file(data: Dict[str, Any], file_path: str, validate: bool = True) -> None:
	"""
	写入skill文件(可选校验)
	"""
	if validate:
		validate_skill(data, raise_on_error=True)
	write_json_file(data, file_path)
