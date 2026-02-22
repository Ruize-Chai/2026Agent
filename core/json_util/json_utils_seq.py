import json
from typing import Any, Dict

from core.json_util.json_utils_confirm import validate_skill, validate_workflow


def pack_json(data: Dict[str, Any]) -> str:
	'''
	序列化
	'''
	return json.dumps(data, ensure_ascii=True, separators=(",", ":"))


def unpack_json(text: str) -> Dict[str, Any]:
	'''
	反序列化
	'''
	return json.loads(text)


def pack_workflow(data: Dict[str, Any], validate: bool = True) -> str:
	'''
	校验后;序列化workflow
	'''
	if validate:
		validate_workflow(data, raise_on_error=True)
	return pack_json(data)


def pack_skill(data: Dict[str, Any], validate: bool = True) -> str:
	'''
	校验后;序列化skill
	'''
	if validate:
		validate_skill(data, raise_on_error=True)
	return pack_json(data)


def unpack_workflow(text: str, validate: bool = True) -> Dict[str, Any]:
	'''
	检验后反序列化workflow
	'''
	data = unpack_json(text)
	if validate:
		validate_workflow(data, raise_on_error=True)
	return data


def unpack_skill(text: str, validate: bool = True) -> Dict[str, Any]:
	'''
	校验后序列化workflow
	'''
	data = unpack_json(text)
	if validate:
		validate_skill(data, raise_on_error=True)
	return data
