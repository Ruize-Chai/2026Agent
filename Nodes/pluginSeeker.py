"""插件查找器：根据节点 `type` 在 `Plugins` 包中加载对应实现。

约定：
- 插件包位于 `Plugins.<type>`（例如 `Plugins.start`）或 `Plugins/<type>/__init__.py`。
- 插件实现类命名为 `Self_Node`，接受 `(data, in_hub=None, ex_hub=None, interrupt=None, listener=None, pin_manager=None, contexts=None)`。

函数：
- `find_plugin(node_type: str, data: dict, **runtime_kwargs) -> object`：返回已实例化的插件节点对象。
"""

from importlib import import_module
from typing import Any, Dict, Optional, List, Callable
from Logger import PluginImportError


_DEFAULT_IN_HUB = None
_DEFAULT_EX_HUB = None
_DEFAULT_INTERRUPT = None
_DEFAULT_LISTENER = None
_DEFAULT_PIN_MANAGER = None


def _ensure_defaults(in_hub, ex_hub, interrupt, listener, pin_manager):
	global _DEFAULT_IN_HUB, _DEFAULT_EX_HUB, _DEFAULT_INTERRUPT, _DEFAULT_LISTENER, _DEFAULT_PIN_MANAGER
	from Workflow.In_communicateHub import InCommunicateHub
	from Workflow.Ex_communicateHub import ExCommunicateHub
	from Workflow.interrupt import Interrupt
	from Workflow.listener import FlowListener
	from Workflow.pin_manager import PinManager

	if in_hub is None:
		if _DEFAULT_IN_HUB is None:
			_DEFAULT_IN_HUB = InCommunicateHub()
		in_hub = _DEFAULT_IN_HUB
	if ex_hub is None:
		if _DEFAULT_EX_HUB is None:
			_DEFAULT_EX_HUB = ExCommunicateHub()
		ex_hub = _DEFAULT_EX_HUB
	if interrupt is None:
		if _DEFAULT_INTERRUPT is None:
			_DEFAULT_INTERRUPT = Interrupt()
		interrupt = _DEFAULT_INTERRUPT
	if listener is None:
		if _DEFAULT_LISTENER is None:
			_DEFAULT_LISTENER = FlowListener()
		listener = _DEFAULT_LISTENER
	if pin_manager is None:
		if _DEFAULT_PIN_MANAGER is None:
			_DEFAULT_PIN_MANAGER = PinManager()
		pin_manager = _DEFAULT_PIN_MANAGER

	return in_hub, ex_hub, interrupt, listener, pin_manager


def find_plugin(
	node_type: str,
	data: Dict[str, Any],
	in_hub=None,
	ex_hub=None,
	interrupt=None,
	listener=None,
	pin_manager=None,
	contexts: Optional[List[Any]] = None,
	node_getter: Optional[Callable[[int], Any]] = None,
	**runtime_kwargs,
) -> Any:
	"""尝试按以下顺序加载插件并实例化：

	1. 尝试导入 `Plugins.{node_type}` 并获取 `Self_Node`。
	2. 若不存在则尝试 `Plugins.{node_type.lower()}`（容错大小写）。
	3. 若找不到则抛出 `ImportError`。

	`runtime_kwargs` 会被传入插件构造函数，用于绑定 `in_hub`/`ex_hub`/`interrupt` 等运行时对象。
	"""

	# Ensure runtime defaults exist if not provided
	in_hub, ex_hub, interrupt, listener, pin_manager = _ensure_defaults(
		in_hub, ex_hub, interrupt, listener, pin_manager
	)

	candidates = [node_type, node_type.lower()]
	last_err: Optional[Exception] = None
	for name in candidates:
		module_name = f"Plugins.{name}"
		try:
			mod = import_module(module_name)
		except Exception as e:
			last_err = e
			continue

		# Prefer attribute Self_Node
		cls = getattr(mod, "Self_Node", None)
		if cls is None:
			# Try common alternatives
			cls = getattr(mod, "PluginNode", None) or getattr(mod, "Node", None)

		if cls is None:
			last_err = ImportError(f"Module {module_name} found but no Self_Node/PluginNode/Node class present")
			continue

		# Merge explicit runtime objects into kwargs (explicit params take precedence)
		merged_kwargs = dict(runtime_kwargs)
		merged_kwargs.setdefault("in_hub", in_hub)
		merged_kwargs.setdefault("ex_hub", ex_hub)
		merged_kwargs.setdefault("interrupt", interrupt)
		merged_kwargs.setdefault("listener", listener)
		merged_kwargs.setdefault("pin_manager", pin_manager)
		merged_kwargs.setdefault("contexts", list(contexts) if contexts is not None else [])
		# Allow plugins to get other node instances via an injected getter (node_id -> Node)
		merged_kwargs.setdefault("node_getter", node_getter)

		# Provide global llm_config module to LLM plugins (if they choose to use it)
		try:
			from Workflow import llm_config
			merged_kwargs.setdefault("llm_config", llm_config)
		except Exception:
			# ignore if module not available
			pass

		# Instantiate with data and runtime kwargs
		try:
			instance = cls(data, **merged_kwargs)
			return instance
		except TypeError:
			# Fallback: try passing only data
			instance = cls(data)
			return instance

	raise PluginImportError(f"Could not load plugin for type '{node_type}'") from last_err
