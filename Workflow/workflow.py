"""工作流运行时引擎。

职责：
- 构建并复用运行时单例：`InCommunicateHub`, `ExCommunicateHub`, `Interrupt`, `FlowListener`, `PinManager`。
- 根据传入的 workflow payload（包含 nodes 列表）实例化节点（通过 `Nodes.pluginSeeker.find_plugin`），并将 runtime 对象注入。
- 提供 `start()` / `stop()` / `run_once()` 简单控制接口；`run_once()` 会按简单驱动：启动 entry 节点（id==0 或指定），并异步等待节点 `serve()` 完成。

注意：这是一个轻量示例引擎，适合作为集成测试与进一步扩展的基础。
"""

from typing import Dict, List, Any, Optional
import asyncio

from Workflow.In_communicateHub import InCommunicateHub
from Workflow.Ex_communicateHub import ExCommunicateHub
from Workflow.interrupt import Interrupt
from Workflow.listener import FlowListener
from Workflow.pin_manager import PinManager

from Nodes.pluginSeeker import find_plugin


class WorkflowEngine:
    def __init__(self, workflow_payload: Dict[str, Any]):
        """传入已验证的 workflow payload（含 `nodes` 列表）。"""
        self.payload = workflow_payload

        # 运行时单例
        self.in_hub = InCommunicateHub()
        self.ex_hub = ExCommunicateHub()
        self.interrupt = Interrupt()
        self.listener = FlowListener()
        self.pin_manager = PinManager()

        # 节点实例表：node_id -> node_instance
        self.nodes: Dict[int, Any] = {}

        # 构建节点
        self._build_nodes()

        # 控制状态
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def _build_nodes(self) -> None:
        nodes = self.payload.get("nodes", [])
        for n in nodes:
            if n.get("id") is None:
                # skip nodes without explicit id
                continue
            node_id = int(n.get("id"))
            node_type = n.get("type")
            # pass contexts from node top-level or empty list
            contexts = n.get("context", {})
            # instantiate via plugin seeker
            inst = find_plugin(
                node_type,
                n,
                in_hub=self.in_hub,
                ex_hub=self.ex_hub,
                interrupt=self.interrupt,
                listener=self.listener,
                pin_manager=self.pin_manager,
                contexts=[contexts] if isinstance(contexts, dict) else contexts,
                # 注入 node_getter，使插件能安全地获取其它节点实例以读取其 context
                node_getter=(lambda nid, _nodes=self.nodes: _nodes.get(int(nid))),
            )
            # ensure node_id attached
            inst.node_id = node_id
            self.nodes[node_id] = inst

    async def _start_entry(self, entry_id: Optional[int] = 0) -> None:
        # Find entry node (default id 0)
        entry_id = int(entry_id) if entry_id is not None else 0
        entry = self.nodes.get(entry_id)
        if entry is None:
            return

        # start serve on entry; nodes may themselves trigger downstream via pin_manager/in_hub
        await entry.serve()

    def start(self, entry_id: Optional[int] = 0) -> None:
        """在后台事件循环中启动一次性运行（非阻塞）。"""
        if self._running:
            return
        self._running = True
        loop = asyncio.get_event_loop()
        self._task = loop.create_task(self._start_entry(entry_id))

    def stop(self) -> None:
        """请求停止：设置 interrupt 标志并取消后台任务（若存在）。"""
        self.interrupt.set_true()
        self._running = False
        if self._task is not None and not self._task.done():
            self._task.cancel()

    async def run_once(self, entry_id: Optional[int] = 0, timeout: Optional[float] = None) -> None:
        """直接在当前协程中运行一次工作流，从 entry 节点开始。

        - 会等待 `entry.serve()` 返回；节点间的触发通过 pin_manager/in_hub 完成。
        - `timeout` 会传给 `asyncio.wait_for` 包裹 entry 执行。
        """
        entry_id = int(entry_id) if entry_id is not None else 0
        entry = self.nodes.get(entry_id)
        if entry is None:
                raise RuntimeError(f"Entry node {entry_id} not found")

        if timeout is None:
            await entry.serve()
        else:
            await asyncio.wait_for(entry.serve(), timeout=timeout)

    def get_node(self, node_id: int) -> Any:
        return self.nodes.get(int(node_id))

    def list_nodes(self) -> List[int]:
        return list(self.nodes.keys())
