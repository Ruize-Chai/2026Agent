create_workflow	POST	/api/workflows
save_workflow	PUT	/api/workflows/{wf_id}
load_workflow	GET	/api/workflows/{wf_id}
validate_workflow	POST	/api/workflows/validate
refactor_workflow	POST	/api/workflows/refactor
delete_workflow	DELETE	/api/workflows/{wf_id}

start_workflow	POST	/api/workflows/{wf_id}/start
pause_workflow	POST	/api/workflows/{wf_id}/pause
resume_workflow	POST	/api/workflows/{wf_id}/resume
cancel_workflow	POST	/api/workflows/{wf_id}/cancel
unblock_node	POST	/api/nodes/{node_id}/unblock
get_workflow_status	GET	/api/workflows/{wf_id}/status

stream_workflow_status	GET	/api/workflows/{wf_id}/stream
stream_workflow_log	GET	/api/workflows/{wf_id}/log/stream

get_error_codes	GET	/api/metadata/error-codes
get_node_specs	GET	/api/metadata/node-specs
get_workflow_topology	GET	/api/workflows/{wf_id}/topology

upload_file	POST	/api/files/upload
upload_large_file	POST	/api/files/upload/large