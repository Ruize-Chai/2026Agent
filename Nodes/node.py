import asyncio
from abc import ABC, abstractmethod
from typing import Any, Optional

from Schema import BaseNode


class Node(BaseNode, ABC):
    """节点基类，继承 `BaseNode`。

    - 构造接收单个 dict(交给 `BaseNode` 处理)
    - `execute` 为抽象协程方法，插件实现具体逻辑
    - 内部使用 `asyncio.Event` 作为可重置触发器；`trigger()` 会 set event,listener 在 execute 完成后 clear event
    """

    def __init__(self, data: dict):
        super().__init__(data)
        self._event = asyncio.Event()
        self._lock = asyncio.Lock()
        self._listener_task: Optional[asyncio.Task] = None
        self._payload: Any = None

    @abstractmethod
    async def execute(self, payload: Any) -> Any:
        """插件需实现的核心逻辑（协程）。"""
        raise NotImplementedError

    async def _listener(self):
        try:
            while True:
                await self._event.wait()
                async with self._lock:
                    try:
                        await self.execute(self._payload)
                    except asyncio.CancelledError:
                        raise
                    except Exception:
                        # 插件内部错误应被上层捕获/记录；这里不阻止清理触发器
                        pass
                    finally:
                        # 执行完毕后重置触发器，准备下一次
                        try:
                            self._event.clear()
                        except Exception:
                            # ignore clearing errors
                            pass
        except asyncio.CancelledError:
            # 任务被取消，退出监听循环
            return

    def start_listener(self, payload: Any = None) -> None:
        """启动后台监听任务（非阻塞）。可多次调用，但只会创建必要的任务。"""
        if payload is not None:
            self._payload = payload
        if self._listener_task is None or self._listener_task.done():
            self._listener_task = asyncio.create_task(self._listener())

    def trigger(self, payload: Any = None) -> None:
        """触发一次执行；可携带 payload。"""
        if payload is not None:
            self._payload = payload
        self._event.set()

    def stop(self) -> None:
        """取消后台监听任务（如果存在）。"""
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
