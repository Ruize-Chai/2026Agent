from typing import List, Optional
from pydantic import BaseModel, Field


class ContextCheckOptions(BaseModel):
    """Options controlling the recursive context availability check.

    - `recursive`: whether to walk upstream nodes recursively
    - `max_depth`: optional maximum recursion depth (None = unlimited)
    - `include_values`: whether to include the actual context values in the result
    - `include_sources`: include source node ids for each context key
    - `keys`: optional whitelist of context keys to check (empty = all)
    """

    recursive: bool = True
    max_depth: Optional[int] = None
    include_values: bool = False
    include_sources: bool = False
    keys: Optional[List[str]] = Field(default_factory=list)


class NodeContextCheckPayload(BaseModel):
    """Payload for requesting a recursive availability check of context for a node.

    Fields:
    - `workflow_id`: workflow identifier containing the node
    - `node_id`: target node id to inspect
    - `options`: check behaviour options
    - `request_id`: optional client-specified id for tracing
    """

    workflow_id: str
    node_id: int
    # options 可选，缺省为 None，调用方可省略以使用默认行为
    options: Optional[ContextCheckOptions] = None
    request_id: Optional[str] = None
