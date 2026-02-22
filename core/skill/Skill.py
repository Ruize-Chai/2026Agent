from abc import ABC, abstractmethod
from typing import Any, Dict, List

class Skill(ABC):
    '''
    Skill类:
    规范参看plugin_manifest_schema;
    是节点的基类
    '''
    def __init__(self, node: Dict[str, Any]):
        '''
        构造
        '''
        self._validate_node(node)
        self._node_type: str = node["type"]
        self._inputs: List[int] = node["inputs"]
        self._outputs: List[int | None] = node["outputs"]
        self._params: Dict[str, Any] = node["params"]
        self._context_slot: str | None = self._params.get("context_slot")
        self._config_options: List[Any] | None = self._params.get("config_options")

    def _validate_node(self, node: Dict[str, Any]) -> None:
        '''
        校验节点合法性
        '''
        for key in ("type", "inputs", "outputs", "params"):
            if key not in node:
                raise ValueError(f"Missing required field: {key}")

        if not isinstance(node["type"], str):
            raise TypeError("type must be a string")
        
        if not isinstance(node["inputs"], list):
            raise TypeError("inputs must be a list")
        
        if not isinstance(node["outputs"], list):
            raise TypeError("outputs must be a list")
        
        if not isinstance(node["params"], dict):
            raise TypeError("params must be a dict")

        if not all(isinstance(value, int) for value in node["inputs"]):
            raise TypeError("inputs items must be integers")
        
        for value in node["outputs"]:
            if value is not None and not isinstance(value, int):
                raise TypeError("outputs items must be integers or None")

    @property
    def node_type(self) -> str:
        return self._node_type

    @property
    def inputs(self) -> List[int]:
        return self._inputs

    @property
    def outputs(self) -> List[int | None]:
        return self._outputs

    @property
    def params(self) -> Dict[str, Any]:
        return self._params

    @property
    def context_slot(self) -> str | None:
        return self._context_slot

    @property
    def config_options(self) -> List[Any] | None:
        return self._config_options

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> int | None:
        """
        Execute the skill and return the next node id.
        """
        raise NotImplementedError


