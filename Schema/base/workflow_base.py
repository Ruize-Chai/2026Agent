
from typing import Any, Dict, List

from Json_Utils.json_validate import is_valid_workflow_dict


class BaseWorkflow:
    """基础工作流类，基于 Python dict 初始化并校验（不包含 version/meta）。"""

    def __init__(self, data: Dict[str, Any]):
        # 使用已有的 dict 校验器，会在失败时抛出对应错误
        is_valid_workflow_dict(data)

        self.workflow_id = data.get("workflow_id")
        self.entry = data.get("entry")
        self.nodes = data.get("nodes", [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "entry": self.entry,
            "nodes": self.nodes,
        }

    def __repr__(self) -> str:
        return f"<BaseWorkflow id={self.workflow_id!r}>"
