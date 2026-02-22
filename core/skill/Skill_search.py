import importlib
from typing import Any, Dict, Type

from core.skill.Skill import Skill

'''
约定:
skill_name必须作为插件包名
Skill的子类实现必须名字为Self_skill
'''
def Search_Skill(skill_name: str, skill_data: Dict[str, Any]) -> Skill:
    module_path = f"plugins.{skill_name}"
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError as exc:
        raise ImportError(f"Plugin module not found: {module_path}") from exc

    try:
        skill_class: Type[Skill] = getattr(module, "Self_skill")
    except AttributeError as exc:
        raise ImportError(f"Plugin missing Self_skill: {module_path}") from exc

    return skill_class(skill_data)
