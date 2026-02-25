"""Central Logger that routes records to JSONL and TXT writers and console.

设计：接受任意日志或 `OriflowError`，标准化为 dict 记录并写入两个后端。
"""
from __future__ import annotations

import socket
import os
import traceback
from typing import Any, Dict, Optional

from .json_line_writer import JSONLineWriter
from .txt_writer import TextWriter
from .printer import Printer

try:
    # import OriflowError if available
    from Logger.errors.Errors import OriflowError
except Exception:
    OriflowError = None  # type: ignore


def _default_logger_name() -> str:
    return "Oriflow"


class Logger:
    """Simple logger facade routing to JSONL/TXT and optional console.

    Example:
        lg = Logger()
        lg.log('INFO', 'started')
        lg.error(my_exc)
    """

    def __init__(self,
                 name: Optional[str] = None,
                 json_path: Optional[str] = None,
                 txt_path: Optional[str] = None,
                 to_console: bool = True):
        self.name = name or _default_logger_name()
        self.json_writer = JSONLineWriter(path=json_path) if json_path is not None else JSONLineWriter()
        self.txt_writer = TextWriter(path=txt_path) if txt_path is not None else TextWriter()
        self.printer = Printer() if to_console else None
        self.host = socket.gethostname()
        self.pid = os.getpid()

    def _make_base_record(self, level: str, message: str, code: Optional[int] = None, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        rec: Dict[str, Any] = {
            'level': level.upper() if level else 'INFO',
            'message': message,
            'logger': self.name,
            'host': self.host,
            'pid': self.pid,
        }
        if code is not None:
            rec['code'] = code
        if ctx is not None:
            rec['ctx'] = ctx
        return rec

    def log(self, level: str, message: str, code: Optional[int] = None, ctx: Optional[Dict[str, Any]] = None) -> None:
        rec = self._make_base_record(level, message, code=code, ctx=ctx)
        # write to backends
        try:
            self.json_writer.write(rec)
        except Exception:
            # swallow write errors to avoid cascading failures
            pass
        try:
            self.txt_writer.write(rec)
        except Exception:
            pass

        if self.printer:
            try:
                self.printer.print(f"{rec['message']}", level=rec['level'])
            except Exception:
                pass

    def error(self, exc: Exception, ctx: Optional[Dict[str, Any]] = None) -> None:
        """Log an exception object. Supports OriflowError specially."""
        if OriflowError is not None and isinstance(exc, OriflowError):
            # extract fields from OriflowError
            level = exc.level.value if getattr(exc, 'level', None) is not None else 'ERROR'
            message = getattr(exc, 'message', str(exc))
            code = getattr(exc, 'code', None)
            rec = self._make_base_record(level, message, code=code, ctx=ctx)
            # include repr
            rec['error_type'] = exc.__class__.__name__
        else:
            # generic exception: include stack
            tb = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            rec = self._make_base_record('ERROR', str(exc), ctx=ctx)
            rec['stack'] = tb

        try:
            self.json_writer.write(rec)
        except Exception:
            pass
        try:
            self.txt_writer.write(rec)
        except Exception:
            pass

        if self.printer:
            try:
                # print message and optionally stack
                self.printer.print(rec.get('message', ''), level=rec.get('level', 'ERROR'))
                if 'stack' in rec:
                    self.printer.print(rec['stack'], level='ERROR')
            except Exception:
                pass

    def exception(self, message: str, ctx: Optional[Dict[str, Any]] = None) -> None:
        """Convenience to log current exception with a message (like logging.exception)."""
        try:
            raise
        except Exception as e:
            # attach message
            full_msg = f"{message}: {e}"
            self.error(e, ctx=ctx)


_default_logger = Logger()


def get_logger() -> Logger:
    return _default_logger


__all__ = ["Logger", "get_logger", "_default_logger"]
