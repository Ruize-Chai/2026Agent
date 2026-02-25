"""Simple printer utility for formatted console output with optional colors.

Features:
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Timestamped output
- Optional colorized output if `Logger.LOGGER.color` is available
- Thread-safe simple print using a lock
"""
from __future__ import annotations

import sys
import threading
from datetime import datetime
from typing import Optional

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Printer:
	"""
	Console printer that formats messages with level and timestamp.
	打印器，支持等级与时间戳
	"""

	def __init__(self, out_stream=None):
		self.out = out_stream or sys.stdout
		self._lock = threading.Lock()

	def _format(self, message: str, level: str) -> str:
		now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")#获取时间戳
		if level:
			lvl = level.upper()
		else:
			lvl = "INFO"
		return f"[{now}] [{lvl}] {message}"

	def print(self, message: str, level: str = "INFO", end: str = "\n") -> str:
		"""
		Print a formatted message. Returns the raw formatted string.
		"""
		if level:
			lvl = level.upper()
		else:
			lvl = "INFO"
		if lvl not in LEVELS:
			lvl = "INFO"

		text = self._format(message, lvl)

		with self._lock:
			try:
				self.out.write(text + end)
				self.out.flush()
			except Exception:
				# best-effort: ignore write/flush errors
				pass

		return text

#默认打印器
_default_printer = Printer()


def print_msg(message: str, level: str = "INFO") -> str:
	"""Convenient Printer with Default Print

	快捷输出函数,调用默认打印器,行为同 `Printer.print`。
	"""
	return _default_printer.print(message, level=level)


__all__ = ["Printer", "print_msg"]

