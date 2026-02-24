Core日志管理修改
todo-list

错误:
json-utils:
1.改一下confirm中的校验错误raise,加日志
++:[ERROR]JSON_skill_format_Error
++:[ERROR]JSON_workflow_format_Error

2.读写json,是否需要路径错误类(而不是仅检查是否有效).可以告诉前端这个问题，json路径已损坏.(提示在对应位置重建json)
++:[CRITICAL]JSON_write_path_Error

skill:
1.skill_search 模块和成员未找到是个问题。可以返回前端告诉工作流/插件已损坏.(提示重新安装.)
++[CRITICAL]PLUGINS_module_NotFound_Error
++[CRITICAL]PLUGINS_attribute_NotFound_Error

2.skill中的skill校验,捕获TypeError后抛出Skill结构异常
++[ERROR]Skill_param_type_Error
++[CRITICAL]Skill_not_inplemented_Error

workflow:

1.workflow出现环，抛出错误.提示用户workflow出现可能的环路(不符合DAG设计结构)，请尝试修改结构。
++[WARN]Workflow_not_Acyclic_Error

2.workflow校验:成员不合法
++[ERROR]Workflow_attr_validate_Error



