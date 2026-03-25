from enum import Enum
from typing import Optional
from pydantic import ValidationError


class SeverityLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class OriflowError(Exception):
    """项目专用基础错误类型，包含错误码与等级信息。
    捕获错误后均应归类至此抛出。捕获后由日志器处理.
    """

    DEFAULT_LEVEL = SeverityLevel.ERROR

    def __init__(self, message: str, code: int, level: Optional[SeverityLevel] = None):
        self.message = message
        self.code = code
        self.level = level or self.DEFAULT_LEVEL
        super().__init__(f"[{self.code}] {self.message}")

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "level": self.level.value,
        }

#801
class NodeTypeError(OriflowError):
    DEFAULT_CODE = 801

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`type` must be a string"
        super().__init__(message, code or self.DEFAULT_CODE, level)


#802
class NodeInputsTypeError(OriflowError):
    DEFAULT_CODE = 802

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`inputs` must be a list of integers"
        super().__init__(message, code or self.DEFAULT_CODE, level)


#806
class WorkflowIDTypeError(OriflowError):
    DEFAULT_CODE = 806

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`workflow_id` must be a non-empty string"
        super().__init__(message, code or self.DEFAULT_CODE, level)


#807
class WorkflowEntryTypeError(OriflowError):
    DEFAULT_CODE = 807

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`entry` must be an integer"
        super().__init__(message, code or self.DEFAULT_CODE, level)


#808
class WorkflowNodesTypeError(OriflowError):
    DEFAULT_CODE = 808

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`nodes` must be a non-empty list"
        super().__init__(message, code or self.DEFAULT_CODE, level)

#803
class NodeOutputsTypeError(OriflowError):
    DEFAULT_CODE = 803

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`outputs` must be a list of integers or None"
        super().__init__(message, code or self.DEFAULT_CODE, level)

#804
class NodeParamsTypeError(OriflowError):
    DEFAULT_CODE = 804

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`params` must be an object (dict)"
        super().__init__(message, code or self.DEFAULT_CODE, level)

#805
class NodeListenTypeError(OriflowError):
    DEFAULT_CODE = 805

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`listen` must be a list of integers"
        super().__init__(message, code or self.DEFAULT_CODE, level)


__all__ = [
    "SeverityLevel",
    "OriflowError",
    "NodeInputsTypeError",
    "NodeOutputsTypeError",
    "NodeParamsTypeError",
    "NodeListenTypeError",
    "WorkflowIDTypeError",
    "WorkflowEntryTypeError",
    "WorkflowNodesTypeError",
]


#809
class NodePayloadValidationError(OriflowError):
    DEFAULT_CODE = 809

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None, validation_error: Optional[ValidationError] = None):
        if message is None:
            message = "NodePayload validation failed"
        super().__init__(message, code or self.DEFAULT_CODE, level)
        self.validation_error: Optional[ValidationError] = validation_error

    def to_dict(self):
        base = super().to_dict()
        if self.validation_error is not None:
            try:
                base["validation_errors"] = self.validation_error.errors()
            except Exception:
                base["validation_errors"] = str(self.validation_error)
        return base


#810
class WorkflowPayloadValidationError(OriflowError):
    DEFAULT_CODE = 810

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None, validation_error: Optional[ValidationError] = None):
        if message is None:
            message = "WorkflowPayload validation failed"
        super().__init__(message, code or self.DEFAULT_CODE, level)
        self.validation_error: Optional[ValidationError] = validation_error

    def to_dict(self):
        base = super().to_dict()
        if self.validation_error is not None:
            try:
                base["validation_errors"] = self.validation_error.errors()
            except Exception:
                base["validation_errors"] = str(self.validation_error)
        return base


#811
class NodeDictValidationError(OriflowError):
    DEFAULT_CODE = 811

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None, validation_error: Optional[ValidationError] = None):
        if message is None:
            message = "Node dict validation failed"
        super().__init__(message, code or self.DEFAULT_CODE, level)
        self.validation_error: Optional[ValidationError] = validation_error

    def to_dict(self):
        base = super().to_dict()
        if self.validation_error is not None:
            try:
                base["validation_errors"] = self.validation_error.errors()
            except Exception:
                base["validation_errors"] = str(self.validation_error)
        return base


#812
class WorkflowDictValidationError(OriflowError):
    DEFAULT_CODE = 812

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None, validation_error: Optional[ValidationError] = None):
        if message is None:
            message = "Workflow dict validation failed"
        super().__init__(message, code or self.DEFAULT_CODE, level)
        self.validation_error: Optional[ValidationError] = validation_error

    def to_dict(self):
        base = super().to_dict()
        if self.validation_error is not None:
            try:
                base["validation_errors"] = self.validation_error.errors()
            except Exception:
                base["validation_errors"] = str(self.validation_error)
        return base


__all__.extend([
    "NodePayloadValidationError",
    "WorkflowPayloadValidationError",
    "NodeDictValidationError",
    "WorkflowDictValidationError",
])


#813
class ReadFileNotFoundError(OriflowError):
    DEFAULT_CODE = 813

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "Requested JSON file not found"
        super().__init__(message, code or self.DEFAULT_CODE, level)


#814
class WriteFileNotFoundError(OriflowError):
    DEFAULT_CODE = 814

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "Target file path not found for writing"
        super().__init__(message, code or self.DEFAULT_CODE, level)


__all__.extend([
    "ReadFileNotFoundError",
    "WriteFileNotFoundError",
])


#901
class PluginImportError(OriflowError):
    DEFAULT_CODE = 901

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "Plugin module import failed"
        super().__init__(message, code or self.DEFAULT_CODE, level)


#902
class PluginInstantiateError(OriflowError):
    DEFAULT_CODE = 902

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
        if message is None:
            message = "Plugin instantiation failed"
        super().__init__(message, code or self.DEFAULT_CODE, level)


__all__.extend([
    "PluginImportError",
    "PluginInstantiateError",
])

class JSONTopLevelNotObject(OriflowError):
    DEFAULT_CODE = 815

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "JSON file does not contain an object at top level"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class JSONDoesNotRepresentObject(OriflowError):
    DEFAULT_CODE = 816

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "JSON does not represent an object"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class InvalidJSON(OriflowError):
    DEFAULT_CODE = 817

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "Invalid JSON"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class UnsupportedDataTypeError(OriflowError):
    DEFAULT_CODE = 818

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "Unsupported data type, expected dict or JSON string"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class DataMustBeDict(OriflowError):
    DEFAULT_CODE = 819

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "data must be a dict"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class RecordMustBeDict(OriflowError):
    DEFAULT_CODE = 820

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "record must be a dict"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class RecordNotJSONSerializable(OriflowError):
    DEFAULT_CODE = 821

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "record is not JSON serializable"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class PayloadNotADict(OriflowError):
    DEFAULT_CODE = 822

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "payload is not a dict"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class TypeMissingOrInvalid(OriflowError):
    DEFAULT_CODE = 823

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`type` missing or invalid"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class InputsMissingOrInvalid(OriflowError):
    DEFAULT_CODE = 824

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`inputs` missing or invalid"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class OutputsMissingOrInvalid(OriflowError):
    DEFAULT_CODE = 825

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`outputs` missing or invalid"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class ParamsMissingOrInvalid(OriflowError):
    DEFAULT_CODE = 826

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`params` missing or invalid"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class ListenMissingOrInvalid(OriflowError):
    DEFAULT_CODE = 827

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`listen` missing or invalid"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class WorkflowIDMissingOrInvalid(OriflowError):
    DEFAULT_CODE = 828

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`workflow_id` missing or invalid"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class EntryMissingOrInvalid(OriflowError):
    DEFAULT_CODE = 829

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`entry` missing or invalid"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class NodesMissingOrInvalid(OriflowError):
    DEFAULT_CODE = 830

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "`nodes` missing or invalid"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class EachNodeMustBeObject(OriflowError):
    DEFAULT_CODE = 831

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "each node must be an object/dict"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class NodeIDMustBeInteger(OriflowError):
    DEFAULT_CODE = 832

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "node.id must be an integer"
        super().__init__(message, code or self.DEFAULT_CODE, level)


class NodeTypeMustBeString(OriflowError):
    DEFAULT_CODE = 833

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "node.type must be a string"
        super().__init__(message, code or self.DEFAULT_CODE, level)


__all__.extend([
    "JSONTopLevelNotObject",
    "JSONDoesNotRepresentObject",
    "InvalidJSON",
    "UnsupportedDataTypeError",
    "DataMustBeDict",
    "RecordMustBeDict",
    "RecordNotJSONSerializable",
    "PayloadNotADict",
    "TypeMissingOrInvalid",
    "InputsMissingOrInvalid",
    "OutputsMissingOrInvalid",
    "ParamsMissingOrInvalid",
    "ListenMissingOrInvalid",
    "WorkflowIDMissingOrInvalid",
    "EntryMissingOrInvalid",
    "NodesMissingOrInvalid",
    "EachNodeMustBeObject",
    "NodeIDMustBeInteger",
    "NodeTypeMustBeString",
    "UnregisteredStateError",
])


#834
class UnregisteredStateError(OriflowError):
    DEFAULT_CODE = 834

    def __init__(self, message: Optional[str] = None, code: Optional[int] = None,
                 level: Optional[SeverityLevel] = None):
        if message is None:
            message = "Unregistered state"
        super().__init__(message, code or self.DEFAULT_CODE, level)


