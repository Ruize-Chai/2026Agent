"""Simple printer utility for formatted console output with optional colors.

Features:
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Timestamped output
- Colorized output using `console_color` when enabled
- Thread-safe simple print using a lock
"""
from __future__ import annotations

import sys
import threading
from datetime import datetime
from typing import Optional, Dict

from .console_color import color, GET_COLOR

LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Printer:
    """
    Console printer that formats messages with level and timestamp.
    打印器，支持等级与时间戳，支持可选颜色映射
    """

    def __init__(self, out_stream=None, colorize: bool = True, color_map: Optional[Dict[str, str]] = None):
        self.out = out_stream or sys.stdout
        self._lock = threading.Lock()
        self.colorize = colorize
        # default color mapping per level
        default_map = {
            "DEBUG": GET_COLOR.BRIGHT_BLUE,
            "INFO": GET_COLOR.GREEN,
            "WARNING": GET_COLOR.YELLOW,
            "ERROR": GET_COLOR.RED,
            "CRITICAL": GET_COLOR.BRIGHT_RED,
        }
        self.color_map = {**default_map, **(color_map or {})}

    def _format(self, message: str, level: str) -> str:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lvl = level.upper() if level else "INFO"
        return f"[{now}] [{lvl}] {message}"

    def print(self, message: str, level: str = "INFO", end: str = "\n") -> str:
        """
        Print a formatted message. Returns the raw formatted string (without ANSI colors).
        """
        lvl = level.upper() if level else "INFO"
        if lvl not in LEVELS:
            lvl = "INFO"

        # Raw text (returned, without ANSI color codes)
        text = self._format(message, lvl)

        # Build colored output for the stream, but keep returned `text` unmodified
        with self._lock:
            try:
                if self.colorize:
                    color_code = self.color_map.get(lvl)
                    if color_code:
                        # Only color the level bracket, e.g. [INFO]
                        level_token = f"[{lvl}]"
                        colored_level = color(level_token, color_code)
                        # Replace the first occurrence of the level token in the formatted text
                        colored_text = text.replace(level_token, colored_level, 1)
                        self.out.write(colored_text + end)
                    else:
                        self.out.write(text + end)
                else:
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

