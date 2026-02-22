"""
工作流引擎日志模块
功能：控制台彩色输出 + 文件日志记录 + 错误码管理 + 错误恢复
"""

import json
import os
import sys
import time
import traceback
import platform
import inspect
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum

# ==================== 错误等级定义 ====================

class ErrorLevel(Enum):
    """错误等级细化"""
    
    FATAL = {
        "level": "FATAL", "code_range": "1xxx", "color": "red", 
        "desc": "致命错误", "recoverable": False, "action": "exit", "priority": 1
    }
    CRITICAL = {
        "level": "CRITICAL", "code_range": "2xxx", "color": "red", 
        "desc": "严重错误", "recoverable": False, "action": "prompt", "priority": 2
    }
    ERROR = {
        "level": "ERROR", "code_range": "3xxx", "color": "red", 
        "desc": "一般错误", "recoverable": True, "action": "prompt", "priority": 3
    }
    RETRY = {
        "level": "RETRY", "code_range": "4xxx", "color": "yellow", 
        "desc": "可重试", "recoverable": True, "action": "retry", "priority": 4
    }
    WARN = {
        "level": "WARN", "code_range": "5xxx", "color": "yellow", 
        "desc": "警告", "recoverable": True, "action": "ignore", "priority": 5
    }
    INFO = {
        "level": "INFO", "code_range": "6xxx", "color": "green", 
        "desc": "提示", "recoverable": True, "action": "ignore", "priority": 6
    }
    DEBUG = {
        "level": "DEBUG", "code_range": "7xxx", "color": "blue", 
        "desc": "调试", "recoverable": True, "action": "ignore", "priority": 7
    }
    IGNORE = {
        "level": "IGNORE", "code_range": "8xxx", "color": "gray", 
        "desc": "可忽略", "recoverable": True, "action": "ignore", "priority": 8
    }
    
    @property
    def level_str(self) -> str:
        return self.value["level"]
    
    @property
    def color(self) -> str:
        return self.value["color"]
    
    @property
    def recoverable(self) -> bool:
        return self.value.get("recoverable", False)
    
    @property
    def action(self) -> str:
        return self.value.get("action", "ignore")
    
    @classmethod
    def from_code(cls, error_code: str):
        """根据错误码返回对应的错误等级"""
        if not error_code or len(error_code) == 0:
            return cls.INFO
        
        first_digit = error_code[0]
        mapping = {
            '1': cls.FATAL, '2': cls.CRITICAL, '3': cls.ERROR,
            '4': cls.RETRY, '5': cls.WARN, '6': cls.INFO,
            '7': cls.DEBUG, '8': cls.IGNORE
        }
        return mapping.get(first_digit, cls.INFO)


# ==================== 彩色输出处理 ====================

class ColorFormatter:
    """跨平台彩色输出处理"""
    
    COLORS = {
        "reset": "\033[0m", "bold": "\033[1m",
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
        "blue": "\033[94m", "magenta": "\033[95m", "cyan": "\033[96m",
        "white": "\033[97m", "gray": "\033[90m",
    }
    
    def __init__(self):
        self.system = platform.system()
        self.is_windows = (self.system == "Windows")
        self.is_mac = (self.system == "Darwin")
        self.is_linux = (self.system == "Linux")
        self.supports_color = self._check_color_support()
        
        if self.is_windows:
            self._init_windows_console()
    
    def _check_color_support(self) -> bool:
        """检查终端是否支持彩色输出"""
        if "NO_COLOR" in os.environ:
            return False
        if not sys.stdout.isatty():
            return False
        
        if self.is_windows:
            try:
                version = platform.version()
                major = int(version.split('.')[0]) if '.' in version else 0
                return major >= 10
            except:
                return False
        return True
    
    def _init_windows_console(self):
        """初始化Windows控制台以支持颜色"""
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            hStdout = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(hStdout, ctypes.byref(mode))
            mode.value |= 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            kernel32.SetConsoleMode(hStdout, mode)
        except:
            pass
    
    def colorize(self, text: str, color: str, bold: bool = False) -> str:
        """为文本添加颜色"""
        if not self.supports_color or not text:
            return text
        
        color_code = self.COLORS.get(color, self.COLORS["reset"])
        bold_code = self.COLORS["bold"] if bold else ""
        reset_code = self.COLORS["reset"]
        
        return f"{bold_code}{color_code}{text}{reset_code}"
    
    def level_color(self, level: str) -> str:
        """根据日志级别返回对应的颜色"""
        color_map = {
            "FATAL": "red", "CRITICAL": "red", "ERROR": "red",
            "RETRY": "yellow", "WARN": "yellow",
            "INFO": "green", "DEBUG": "blue", "IGNORE": "gray",
        }
        return color_map.get(level, "white")


# ==================== 自定义错误类 ====================

class ErrorAction(Enum):
    """错误处理动作"""
    EXIT = "exit"              # 退出程序
    RETRY = "retry"            # 自动重试
    PROMPT_RETRY = "prompt"    # 提示用户重试
    IGNORE = "ignore"          # 忽略
    CONTINUE = "continue"      # 继续执行

class WorkflowError(Exception):
    """基础工作流错误类"""
    
    def __init__(
        self, 
        code: str, 
        message: str, 
        level: str = "ERROR",
        action: ErrorAction = ErrorAction.PROMPT_RETRY,
        suggestion: Optional[str] = None,
        recoverable: bool = True,
        details: Optional[Dict] = None
    ):
        self.code = code
        self.message = message
        self.level = level
        self.action = action
        self.suggestion = suggestion
        self.recoverable = recoverable
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self):
        return f"[{self.code}] {self.message}"
    
    def to_dict(self) -> Dict:
        return {
            "code": self.code, "message": self.message, "level": self.level,
            "action": self.action.value if self.action else None,
            "suggestion": self.suggestion, "recoverable": self.recoverable,
            "details": self.details
        }

# 便捷错误类
class NetworkError(WorkflowError):
    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        if url: details["url"] = url
        super().__init__(
            code="4001", message=message, level="RETRY",
            action=ErrorAction.RETRY, suggestion="请检查网络连接后重试",
            recoverable=True, details=details, **kwargs
        )

class ConfigError(WorkflowError):
    def __init__(self, message: str, config_path: Optional[str] = None, fatal: bool = False, **kwargs):
        details = kwargs.get("details", {})
        if config_path: details["config_path"] = config_path
        super().__init__(
            code="1001" if fatal else "2001",
            message=message,
            level="FATAL" if fatal else "CRITICAL",
            action=ErrorAction.EXIT if fatal else ErrorAction.PROMPT_RETRY,
            recoverable=not fatal,
            details=details, **kwargs
        )

class UserMistakeError(WorkflowError):
    def __init__(self, message: str, field: Optional[str] = None, auto_fixed: bool = False, **kwargs):
        details = kwargs.get("details", {})
        if field: details["field"] = field
        if auto_fixed: details["auto_fixed"] = True
        super().__init__(
            code="8001", message=message, level="IGNORE",
            action=ErrorAction.IGNORE,
            suggestion="系统已自动处理，无需担心" if auto_fixed else None,
            recoverable=True, details=details, **kwargs
        )

class SkillError(WorkflowError):
    def __init__(self, skill_name: str, message: str, node_id: Optional[str] = None, **kwargs):
        details = kwargs.get("details", {})
        details["skill_name"] = skill_name
        if node_id: details["node_id"] = node_id
        super().__init__(
            code="3001", message=f"技能 '{skill_name}' 执行失败: {message}",
            level="ERROR", action=ErrorAction.CONTINUE,
            suggestion="请检查技能实现或参数",
            recoverable=True, details=details, **kwargs
        )


# ==================== 错误恢复管理器 ====================

class ErrorRecoveryManager:
    """错误恢复管理器 - 处理重试/忽略等策略"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_counts: Dict[str, int] = {}
        self.recovery_handlers: Dict[str, Callable] = {}
        self.error_history: list = []
    
    def should_retry(self, error_code: str) -> bool:
        return self.retry_counts.get(error_code, 0) < self.max_retries
    
    def increment_retry(self, error_code: str) -> int:
        current = self.retry_counts.get(error_code, 0) + 1
        self.retry_counts[error_code] = current
        return current
    
    def reset_retry(self, error_code: str):
        self.retry_counts.pop(error_code, None)
    
    def register_handler(self, error_code: str, handler: Callable):
        self.recovery_handlers[error_code] = handler
    
    def handle_error(self, error: WorkflowError) -> ErrorAction:
        """处理错误，返回应该采取的动作"""
        # 记录错误历史
        self.error_history.append({
            "timestamp": time.time(), "error": error,
            "retry_count": self.retry_counts.get(error.code, 0)
        })
        
        # 限制历史记录大小
        if len(self.error_history) > 100:
            self.error_history = self.error_history[-100:]
        
        # 检查自定义处理器
        if error.code in self.recovery_handlers:
            try:
                result = self.recovery_handlers[error.code](error)
                if result and isinstance(result, ErrorAction):
                    return result
            except Exception as e:
                print(f"错误处理器执行失败: {e}")
        
        # 默认处理逻辑
        if error.action == ErrorAction.RETRY:
            if self.should_retry(error.code):
                retry_count = self.increment_retry(error.code)
                time.sleep(self.retry_delay * retry_count)
                return ErrorAction.RETRY
            else:
                return ErrorAction.PROMPT_RETRY
        
        return error.action
    
    def get_stats(self) -> Dict:
        """获取错误统计信息"""
        stats = {}
        for record in self.error_history:
            code = record["error"].code
            if code not in stats:
                stats[code] = {"count": 0, "last_seen": 0, "last_message": ""}
            stats[code]["count"] += 1
            stats[code]["last_seen"] = max(stats[code]["last_seen"], record["timestamp"])
            stats[code]["last_message"] = str(record["error"])
        return stats


# ==================== 日志条目定义 ====================

@dataclass
class LogEntry:
    """日志条目数据类"""
    timestamp: str
    level: str
    message: str
    code: Optional[str] = None
    category: Optional[str] = None
    suggestion: Optional[str] = None
    action: Optional[str] = None
    recoverable: bool = True
    filename: Optional[str] = None
    lineno: Optional[int] = None
    function: Optional[str] = None
    details: Optional[Dict] = None
    traceback: Optional[list] = None
    platform: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


# ==================== 主日志类 ====================

class Logger:
    """增强版日志器 - 控制台彩色输出 + 文件日志记录"""
    
    def __init__(
        self,
        log_dir: str = "logs",
        app_name: str = "workflow_engine",
        error_codes_path: str = "config/error_lists.json",
        console_output: bool = True,
        max_retries: int = 3
    ):
        self.app_name = app_name
        self.console_output = console_output
        self.color = ColorFormatter()
        self.recovery = ErrorRecoveryManager(max_retries=max_retries)
        
        # 创建日志目录
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)
        
        # 当前日志文件（按日期分割）
        date_str = datetime.now().strftime('%Y%m%d')
        self.log_file = self.log_dir / f"{app_name}_{date_str}.log"
        
        # 错误码表
        self.error_codes = self._load_error_codes(error_codes_path)
        
        # 记录启动
        self.info("日志系统初始化", file=self.log_file.name)
    
    def _load_error_codes(self, path: str) -> Dict:
        """加载错误码定义"""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 创建默认错误码文件
                self._create_default_error_codes(path)
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"警告: 无法加载错误码文件 {path}: {e}")
            return {"errors": {}, "categories": {}}
    
    def _create_default_error_codes(self, path: str):
        """创建默认错误码文件"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        default = {
            "version": "1.0",
            "categories": {},
            "errors": {
                "6001": {
                    "category": "INFO",
                    "message": "操作成功完成",
                    "suggestion": ""
                }
            }
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
    
    def _get_caller_info(self):
        """获取调用者信息"""
        frame = inspect.currentframe()
        # 向上跳过几层找到实际调用者
        for _ in range(4):
            if frame:
                frame = frame.f_back
            else:
                break
        
        if frame:
            return {
                "filename": os.path.basename(frame.f_code.co_filename),
                "lineno": frame.f_lineno,
                "function": frame.f_code.co_name
            }
        return {}
    
    def _get_error_info(self, code: str) -> Dict:
        """从错误码表获取错误信息"""
        if not code:
            return {}
        
        error_info = self.error_codes.get("errors", {}).get(code, {})
        category = error_info.get("category", "INFO")
        category_info = self.error_codes.get("categories", {}).get(category, {})
        
        return {
            "message": error_info.get("message", ""),
            "suggestion": error_info.get("suggestion", ""),
            "category": category_info.get("name", category),
            "action": category_info.get("action", "ignore"),
            "recoverable": category_info.get("recoverable", True)
        }
    
    def _write_to_file(self, entry: LogEntry):
        """写入日志文件"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + '\n')
        except Exception as e:
            # 文件写入失败时，至少打印到控制台
            print(f"日志文件写入失败: {e}")
    
    def _output_to_console(self, entry: LogEntry):
        """输出到控制台（带颜色）"""
        # 时间戳
        time_str = self.color.colorize(f"[{entry.timestamp}]", "gray")
        
        # 日志级别
        level_color = self.color.level_color(entry.level)
        level_str = self.color.colorize(f"[{entry.level:7}]", level_color, bold=True)
        
        # 错误码
        code_str = ""
        if entry.code:
            code_str = self.color.colorize(f"[{entry.code}]", "cyan")
        
        # 消息内容
        message = entry.message
        if entry.level in ["FATAL", "CRITICAL", "ERROR"]:
            message = self.color.colorize(message, "red")
        elif entry.level in ["RETRY", "WARN"]:
            message = self.color.colorize(message, "yellow")
        elif entry.level == "INFO":
            message = self.color.colorize(message, "green")
        
        # 建议
        suggestion_str = ""
        if entry.suggestion:
            suggestion_str = self.color.colorize(f" 💡 {entry.suggestion}", "green")
        
        # 组合输出
        print(f"{time_str} {level_str} {code_str} {message}{suggestion_str}")
        
        # 额外提示
        if entry.recoverable and entry.level not in ["FATAL", "CRITICAL"]:
            if entry.action == "retry":
                print(self.color.colorize("   ↪ 正在自动重试...", "yellow"))
            elif entry.action == "prompt":
                print(self.color.colorize("   ↪ 请检查后重试操作", "yellow"))
        
        # 如果有详细信息，也打印出来
        if entry.details and self.color.supports_color:
            for key, value in entry.details.items():
                if key not in ["password", "token", "secret"]:  # 避免打印敏感信息
                    print(self.color.colorize(f"   ├─ {key}: {value}", "gray"))
    
    def log(
        self,
        level: str,
        message: str,
        code: Optional[str] = None,
        suggestion: Optional[str] = None,
        action: Optional[str] = None,
        recoverable: bool = True,
        details: Optional[Dict] = None,
        error: Optional[Exception] = None,
        **kwargs
    ):
        """通用日志方法 - 同时写入文件和输出到控制台"""
        
        # 如果有错误码，从错误码表获取信息
        if code and not suggestion:
            error_info = self._get_error_info(code)
            if error_info.get("message") and message == code:
                message = error_info["message"]
            suggestion = suggestion or error_info.get("suggestion")
            action = action or error_info.get("action")
            recoverable = recoverable if not code else error_info.get("recoverable", True)
        
        # 处理异常
        traceback_lines = None
        if error:
            traceback_lines = traceback.format_exc().split('\n')
        
        # 合并details和kwargs
        combined_details = details or {}
        combined_details.update(kwargs)
        
        # 获取调用者信息
        caller = self._get_caller_info()
        
        # 创建日志条目
        entry = LogEntry(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            level=level,
            message=message,
            code=code,
            suggestion=suggestion,
            action=action,
            recoverable=recoverable,
            filename=caller.get("filename"),
            lineno=caller.get("lineno"),
            function=caller.get("function"),
            details=combined_details if combined_details else None,
            traceback=traceback_lines,
            platform=self.color.system
        )
        
        # 1. 写入文件
        self._write_to_file(entry)
        
        # 2. 输出到控制台
        if self.console_output:
            self._output_to_console(entry)
        
        # 处理错误恢复
        if error and isinstance(error, WorkflowError):
            return self.recovery.handle_error(error)
        
        return None
    
    # ========== 便捷方法 ==========
    
    def info(self, message: str, code: str = "6001", **kwargs):
        """信息日志"""
        self.log("INFO", message, code=code, **kwargs)
    
    def warning(self, message: str, code: str = "5001", **kwargs):
        """警告日志"""
        self.log("WARN", message, code=code, **kwargs)
    
    def error(self, message: str, code: str = "3001", **kwargs):
        """错误日志"""
        self.log("ERROR", message, code=code, **kwargs)
    
    def retryable(self, message: str, code: str = "4001", **kwargs):
        """可重试错误"""
        self.log("RETRY", message, code=code, action="retry", recoverable=True, **kwargs)
    
    def ignorable(self, message: str, code: str = "8001", **kwargs):
        """可忽略错误"""
        self.log("IGNORE", message, code=code, action="ignore", recoverable=True, **kwargs)
    
    def debug(self, message: str, code: str = "7001", **kwargs):
        """调试日志"""
        self.log("DEBUG", message, code=code, **kwargs)
    
    def fatal(self, message: str, code: str = "1001", **kwargs):
        """致命错误"""
        self.log("FATAL", message, code=code, action="exit", recoverable=False, **kwargs)
        sys.exit(1)
    
    def handle_error(self, error: WorkflowError):
        """处理工作流错误"""
        action = self.recovery.handle_error(error)
        self.log(
            level=error.level,
            message=str(error),
            code=error.code,
            suggestion=error.suggestion,
            action=action.value if action else None,
            recoverable=error.recoverable,
            details=error.details,
            error=error
        )
        return action


# ==================== 全局实例 ====================

# 创建默认日志实例
_default_logger = None

def get_logger(
    log_dir: str = "logs",
    app_name: str = "workflow_engine",
    error_codes_path: str = "config/error_lists.json"
) -> Logger:
    """获取日志实例（单例模式）"""
    global _default_logger
    if _default_logger is None:
        _default_logger = Logger(
            log_dir=log_dir,
            app_name=app_name,
            error_codes_path=error_codes_path
        )
    return _default_logger

# 导出常用类和函数
__all__ = [
    'Logger', 'get_logger',
    'WorkflowError', 'NetworkError', 'ConfigError', 
    'UserMistakeError', 'SkillError', 'ErrorAction',
    'ErrorLevel'
]
