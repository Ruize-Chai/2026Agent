"""JSON Lines writer for log records.

功能：
- 将字典记录作为单行 JSON 追加到文件(NDJSON/JSONL)。
- 自动补 timestamp(UTC ISO8601)和 level(默认 INFO)字段（若缺失）。
- 线程安全，写入后 flush 并 fsync 保证落盘。

用法示例：
    writer = JSONLineWriter()
    writer.write({"level":"ERROR","message":"失败","code":901})
"""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional


def _default_log_path() -> str:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    return os.path.join(base, 'Logs', 'logs.jsonl')


class JSONLineWriter:
    """Thread-safe JSONL writer.

    Params:
        path: 输出文件路径，默认 `Logs/logs.jsonl` 相对于仓库根。
        ensure_dir: 若目标目录不存在则创建(默认 True)。
    """

    def __init__(self, path: Optional[str] = None, ensure_dir: bool = True):
        self.path = path or _default_log_path()
        self._lock = threading.Lock()
        if ensure_dir:
            d = os.path.dirname(self.path)
            if d and not os.path.exists(d):
                os.makedirs(d, exist_ok=True)

    def _prepare_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        # copy to avoid mutating caller dict
        r = dict(record)
        if 'timestamp' not in r:
            # use UTC ISO8601 with millisecond precision and Z
            r['timestamp'] = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
        if 'level' not in r:
            r['level'] = 'INFO'
        return r

    def write(self, record: Dict[str, Any]) -> str:
        """Write a record (dict) as one JSON line. Returns the written line string.

        Raises `TypeError` if the record is not JSON-serializable.
        """
        if not isinstance(record, dict):
            raise TypeError('record must be a dict')

        r = self._prepare_record(record)

        # Serialize to a single-line JSON string
        try:
            line = json.dumps(r, ensure_ascii=False, separators=(',', ':'))
        except TypeError as e:
            # attempt to provide a helpful message
            raise TypeError(f'record is not JSON serializable: {e}') from e

        # Append newline
        line_to_write = line + '\n'

        # Thread-safe append with flush + fsync
        with self._lock:
            # open in append and binary to ensure fsync works predictably
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
                    # platform may not support fsync on some streams; ignore
                    pass

        return line


def default_writer() -> JSONLineWriter:
    return JSONLineWriter()


__all__ = ["JSONLineWriter", "default_writer"]
LOG_PATH = ""