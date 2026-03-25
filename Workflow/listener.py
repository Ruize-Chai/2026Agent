from threading import Lock
from typing import Dict, List, Any, Optional

from Logger import UnregisteredStateError


class FlowListener:
    """状态监视器总线:维护节点状态表并提供线程安全的读/写接口。

    仅暴露：
    - `set_state(node_id, state)`：写入节点状态（仅允许预定义状态）
    - `get_state(node_id)`：读取单个节点状态
    - `read()`：读取全部状态快照
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._state_table: Dict[int, str] = {}
        #静态状态集合
        self._allowed_states: List[str] = [
            "ACTIVE",
            "SILENT",
            "TEXT_INPUT",
            "NUMBER_INPUT",
            "CHECKBOX",
            "OUTPUT"
        ]

    def set_state(self, node_id: int, state: str) -> None:
        """设置节点的状态（线程安全）。若状态不在静态集合中则抛错。"""
        with self._lock:
            if state not in self._allowed_states:
                raise UnregisteredStateError(f"Unregistered state: {state}")
            self._state_table[int(node_id)] = state

    def get_state(self, node_id: int) -> Optional[str]:
        """获取指定节点的当前状态；不存在返回 None。"""
        with self._lock:
            return self._state_table.get(int(node_id))

    def read(self) -> List[Dict[str, Any]]:
        """返回当前状态表快照：[{"node_id": id, "state": state}, ...]。"""
        with self._lock:
            return [{"node_id": nid, "state": st} for nid, st in self._state_table.items()]