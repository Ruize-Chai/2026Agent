from typing import Dict, Any
import importlib
from Logger import PluginImportError, PluginInstantiateError

'''
约定:
- `node_name` 必须与插件包名一致（位于 `Plugins` 目录下）
- 插件包中必须实现名为 `Self_node` 的类，且该类接受单个 dict 作为构造参数

函数 `Search_Node` 会导入 `Plugins.<node_name>` 模块，查找 `Self_node`,
并使用 `node_data` 实例化返回该节点对象。
抛出 ImportError/RuntimeError 以便上层处理。
'''


def Search_Node(node_name: str, node_data: Dict[str, Any]):
    """在 `Plugins` 包中查找并实例化指定名字的节点插件。

    Args:
        node_name: 插件包名（也作为节点类型识别）
        node_data: 传递给插件构造函数的字典

    Returns:
        已实例化的插件节点对象

    Raises:
        PluginImportError: 无法导入插件模块或类不存在
        PluginInstantiateError: 插件类实例化失败
    """
    module_name = f"Plugins.{node_name}"
    try:
        mod = importlib.import_module(module_name)
    except Exception as e:
        raise PluginImportError(f"Cannot import plugin module {module_name}: {e}") from e

    cls = getattr(mod, "Self_node", None)
    if cls is None:
        raise PluginImportError(f"Plugin '{node_name}' does not define a 'Self_node' class")

    try:
        instance = cls(node_data)
    except Exception as e:
        raise PluginInstantiateError(f"Failed to instantiate 'Self_node' from plugin '{node_name}': {e}") from e

    return instance
