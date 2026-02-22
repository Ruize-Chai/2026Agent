from typing import Any, Dict, List, Set
from core.skill import Skill
from core.skill.Skill_search import Search_Skill


class Workflow:
    def __init__(self, data: Dict[str, Any]):
        self._validate_workflow(data)
        self._workflow_id: str = data["workflow_id"]
        self._entry: int = data["entry"]
        self._nodes: List[Dict[str, Any]] = data["nodes"]
        self._meta: Dict[str, Any] = data.get("meta", {})
        self._node_map: Dict[int, Dict[str, Any]] = {
            node["id"]: node for node in self._nodes
        }
        self._skills: List[Skill] | None = None
        self._skill_map: Dict[int, Skill] | None = None
        

    
    def _validate_workflow(self, data: Dict[str, Any]) -> None:
        #合法性检查
        for key in ("workflow_id", "entry", "nodes"):
            if key not in data:
                raise ValueError(f"Missing required field: {key}")

        if not isinstance(data["workflow_id"], str):
            raise TypeError("workflow_id must be a string")
        if not isinstance(data["entry"], int):
            raise TypeError("entry must be an integer")
        if not isinstance(data["nodes"], list):
            raise TypeError("nodes must be a list")
        if "meta" in data and not isinstance(data["meta"], dict):
            raise TypeError("meta must be a dict")

        node_ids: List[int] = []
        for node in data["nodes"]:
            for key in ("id", "type", "inputs", "outputs", "params"):
                if key not in node:
                    raise ValueError(f"Missing required node field: {key}")
                #键检查
                
            #节点参数值检查
            if not isinstance(node["id"], int):
                raise TypeError("node id must be an integer")
            if not isinstance(node["type"], str):
                raise TypeError("node type must be a string")
            if not isinstance(node["inputs"], list):
                raise TypeError("node inputs must be a list")
            if not isinstance(node["outputs"], list):
                raise TypeError("node outputs must be a list")
            if not isinstance(node["params"], dict):
                raise TypeError("node params must be a dict")

            if not all(isinstance(value, int) for value in node["inputs"]):
                raise TypeError("node inputs items must be integers")
            for value in node["outputs"]:
                if value is not None and not isinstance(value, int):
                    raise TypeError("node outputs items must be integers or None")

            node_ids.append(node["id"])

        #节点id唯一性检查
        if len(set(node_ids)) != len(node_ids):
            raise ValueError("node ids must be unique")
        if data["entry"] not in node_ids:
            raise ValueError("entry must reference an existing node id")

    def get_skills(self) -> List[Skill]:
        if self._skills is None:
            self._skills = [Search_Skill(node["type"], node) for node in self._nodes]
        return self._skills

    def _get_skill_map(self) -> Dict[int, Skill]:
        if self._skill_map is None:
            self._skill_map = {}
            for node in self._nodes:
                self._skill_map[node["id"]] = Search_Skill(node["type"], node)
        return self._skill_map

    def _validate_next(self, current_id: int, next_id: int | None) -> None:
        #跳转合法性检验
        outputs = self._node_map[current_id]["outputs"]
        if next_id is None:
            if None not in outputs:
                raise ValueError("next_id is None but outputs has no None marker")
            return

        if next_id not in outputs:
            raise ValueError("next_id not found in current node outputs")

    def execute(self, context: Dict[str, Any]) -> None:
        #执行逻辑：根据Skill.execute()的返回值作为下一个节点进行跳转
        skill_map = self._get_skill_map()
        current_id = self._entry

        while True:
            if current_id not in skill_map:
                raise ValueError(f"Unknown node id: {current_id}")

            next_id = skill_map[current_id].execute(context)
            if next_id is None:
                self._validate_next(current_id, next_id)
                return

            if not isinstance(next_id, int):
                raise TypeError("execute must return an integer node id or None")
            self._validate_next(current_id, next_id)
            current_id = next_id

    