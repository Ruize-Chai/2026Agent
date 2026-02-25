from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowNode(BaseModel):
    id: int
    type: str
    listen: Optional[List[int]] = Field(default_factory=list)
    outputs: Optional[List[Optional[int]]] = Field(default_factory=list)
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WorkflowPayload(BaseModel):
    workflow_id: str
    entry: int
    nodes: List[WorkflowNode]
