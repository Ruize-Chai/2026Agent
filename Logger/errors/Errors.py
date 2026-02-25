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

	子类可通过 `DEFAULT_LEVEL` 覆盖默认等级，构造时传入的 `level` 优先级更高。
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
	"NodeTypeError",
	"NodeInputsTypeError",
	"NodeOutputsTypeError",
	"NodeParamsTypeError",
	"NodeListenTypeError",
	"WorkflowIDTypeError",
	"WorkflowEntryTypeError",
	"WorkflowNodesTypeError",
]


#809
class NodePayloadValidationError(OriflowError, ValidationError):
	DEFAULT_CODE = 809

	def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
		if message is None:
			message = "NodePayload validation failed"
		OriflowError.__init__(self, message, code or self.DEFAULT_CODE, level)


#810
class WorkflowPayloadValidationError(OriflowError, ValidationError):
	DEFAULT_CODE = 810

	def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
		if message is None:
			message = "WorkflowPayload validation failed"
		OriflowError.__init__(self, message, code or self.DEFAULT_CODE, level)


#811
class NodeDictValidationError(OriflowError, ValidationError):
	DEFAULT_CODE = 811

	def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
		if message is None:
			message = "Node dict validation failed"
		OriflowError.__init__(self, message, code or self.DEFAULT_CODE, level)


#812
class WorkflowDictValidationError(OriflowError, ValidationError):
	DEFAULT_CODE = 812

	def __init__(self, message: Optional[str] = None, code: Optional[int] = None, level: Optional[SeverityLevel] = None):
		if message is None:
			message = "Workflow dict validation failed"
		OriflowError.__init__(self, message, code or self.DEFAULT_CODE, level)


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


