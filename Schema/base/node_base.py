from Json_Utils.json_validate import is_valid_node_dict


class BaseNode:
    """基础节点类，基于 Python dict 初始化并校验。

    构造函数接受单个 `data: dict` 参数，校验失败时会抛出 `NodeDictValidationError`。
    """

    def __init__(self, data: dict):
        # 使用已有的 dict 校验器，会在失败时抛出对应错误
        is_valid_node_dict(data)

        # 赋值（保留原有属性名）
        self.node_id = data.get("id")
        self.type = data.get("type")
        self.inputs = data.get("inputs", [])
        self.outputs = data.get("outputs", [])
        self.params = data.get("params", {})
        self.listen = data.get("listen", [])

    def to_dict(self):
        """返回符合 schema 的字典表示。"""
        return {
            "type": self.type,
            "listen": self.listen,
            "outputs": self.outputs,
            "params": self.params,
            "inputs": self.inputs,
        }

    def __repr__(self):
        return f"<BaseNode id={self.node_id!r} type={self.type!r}>"
