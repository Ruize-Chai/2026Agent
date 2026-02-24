import asyncio
import json
import os
from typing import Any, List


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_TABLE_PATH = os.path.join(BASE_DIR, "userlist.json")


async def read_user_table(path: str = USER_TABLE_PATH) -> List[dict[str, Any]]:
	def _read() -> List[dict[str, Any]]:
		if not os.path.exists(path):
			return []
		with open(path, "r", encoding="utf-8") as handle:
			data = json.load(handle)
		if not isinstance(data, list):
			raise ValueError("User table must be a JSON array")
		return data

	return await asyncio.to_thread(_read)


async def write_user_table(
	rows: List[dict[str, Any]],
	path: str = USER_TABLE_PATH,
) -> None:
	def _write() -> None:
		os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
		with open(path, "w", encoding="utf-8") as handle:
			json.dump(rows, handle, ensure_ascii=True, indent=2)

	await asyncio.to_thread(_write)
