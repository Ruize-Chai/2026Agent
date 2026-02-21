import json
from typing import Any, Dict
import openai

def parse_json_to_api_params(json_str: str) -> Dict[str, Any]:
	"""
	将JSON字符串解析为API参数字典。
	:param json_str: JSON格式的字符串
	:return: 参数字典
	"""
	try:
		params = json.loads(json_str)
		if not isinstance(params, dict):
			raise ValueError("JSON内容必须为对象类型")
		return params
	except Exception as e:
		raise ValueError(f"解析JSON失败: {e}")



def call_chat_completion(params: Dict[str, Any]) -> Any:
	"""
	调用OpenAI兼容的Chat Completion接口。
	params中可包含api_key和base_url字段用于动态指定API信息。
	:param params: API参数字典,支持api_key、base_url、model、messages等
	:return: OpenAI接口返回结果
	"""
	api_key = params.pop("api_key", None)
	base_url = params.pop("base_url", None)
	if not api_key or not base_url:
		raise ValueError("params中必须包含api_key和base_url字段")
	client = openai.OpenAI(api_key=api_key, base_url=base_url)
	try:
		response = client.chat.completions.create(**params)
		return response
	except Exception as e:
		raise RuntimeError(f"调用OpenAI接口失败: {e}")





