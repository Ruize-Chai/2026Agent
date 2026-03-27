from fastapi import APIRouter, HTTPException
from typing import Any, Dict
from Server.utils import save_workflow, load_workflow, delete_workflow, read_workflow_lists
from Schema.payload.workflow_payload import WorkflowPayload as SchemaWorkflowPayload
from Json_Utils.json_validate import is_valid_workflow_dict
import uuid

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.post("/create")
def create_workflow(payload: SchemaWorkflowPayload):
    # 按 Schema/payload/workflow_payload.py 中的约定使用字段
    wid = payload.workflow_id or str(uuid.uuid4())
    data = payload.dict()
    data["workflow_id"] = wid
    try:
        is_valid_workflow_dict(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    save_workflow(wid, data)
    return {"status": "ok", "workflow_id": wid}


@router.post("/alter")
def alter_workflow(payload: SchemaWorkflowPayload):
    if not payload.workflow_id:
        raise HTTPException(status_code=400, detail="workflow_id required")
    data = payload.dict()
    try:
        is_valid_workflow_dict(data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    save_workflow(payload.workflow_id, data)
    return {"status": "ok", "workflow_id": payload.workflow_id}


@router.post("/delete")
def remove_workflow(body: dict):
    wid = body.get("workflow_id") or body.get("id")
    if not wid:
        raise HTTPException(status_code=400, detail="workflow_id required")
    ok = delete_workflow(wid)
    if not ok:
        raise HTTPException(status_code=500, detail="delete failed")
    return {"status": "ok", "workflow_id": wid}


@router.get("/list")
def list_workflows():
    return read_workflow_lists()


@router.get("/{workflow_id}")
def get_workflow(workflow_id: str):
    wf = load_workflow(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail="workflow not found")
    return wf
