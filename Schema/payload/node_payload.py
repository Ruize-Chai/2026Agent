from typing import Any, List, Optional
from pydantic import BaseModel, Field


class NodeParams(BaseModel):
    context_slot: Optional[str] = None
    config_options: Optional[List[Any]] = None


class NodePayload(BaseModel):
    """Pydantic payload 对应 node_data_schema.json"""

    type: str
    inputs: List[int] = Field(default_factory=list)
    outputs: List[Optional[int]] = Field(default_factory=list)
    params: NodeParams
    listen: Optional[List[int]] = Field(default_factory=list)
