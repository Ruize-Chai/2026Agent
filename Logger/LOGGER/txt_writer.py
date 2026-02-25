"""Plain-text log writer.

Writes simple human-readable log lines to a text file (default Logs/logs.txt).
Each line contains timestamp, level and message; optional `code` and `ctx`
will be appended in compact form.

Example line:
  2026-02-26T16:00:00.123Z [INFO] Started process code=100 ctx={"pid":1234}
"""
from __future__ import annotations

import os
import threading
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _default_txt_path() -> str:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base, 'Logs', 'logs.txt')


class TextWriter:
    """Thread-safe plain-text writer.

    Parameters:
        path: output file path (default Logs/logs.txt)
        ensure_dir: create parent dir if missing
    """

    def __init__(self, path: Optional[str] = None, ensure_dir: bool = True):
        self.path = path or _default_txt_path()
        self._lock = threading.Lock()
        if ensure_dir:
            d = os.path.dirname(self.path)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec='milliseconds')

    def _format(self, record: Dict[str, Any]) -> str:
        ts = record.get('timestamp') or self._now_iso()
        lvl = record.get('level') or 'INFO'
        msg = record.get('message') or ''
        parts = [f"{ts} [{lvl}] {msg}"]
        if 'code' in record:
            parts.append(f"code={record['code']}")
        if 'ctx' in record:
            try:
                ctxs = json.dumps(record['ctx'], ensure_ascii=False, separators=(',', ':'))
            except Exception:
                ctxs = str(record['ctx'])
            parts.append(f"ctx={ctxs}")
        return ' '.join(parts)

    def write(self, record: Dict[str, Any]) -> str:
        """Append a formatted line for `record` to the text log file.

        Returns the written line (without trailing newline).
        """
        if not isinstance(record, dict):
            raise TypeError('record must be a dict')

        line = self._format(record)

        line_to_write = line + '\n'

        with self._lock:
            with open(self.path, 'a', encoding='utf-8') as f:
                f.write(line_to_write)
                try:
                    f.flush()
                except Exception:
                    pass
                try:
                    fd = f.fileno()
                    os.fsync(fd)
                except Exception:
                    pass

        return line


def default_writer() -> TextWriter:
    return TextWriter()


__all__ = ["TextWriter", "default_writer"]
