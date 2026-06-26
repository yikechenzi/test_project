"""测试上下文 — 管理步骤间的数据传递和变量存储。"""

from __future__ import annotations

import re
from typing import Any

from jsonpath_ng.ext import parse as jsonpath_parse


class TestContext:
    """测试上下文，存储和管理测试过程中的变量。"""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.variables: dict[str, Any] = {}
        self.responses: list[dict[str, Any]] = []  # 历史响应记录

    def set_variable(self, key: str, value: Any) -> None:
        """设置变量。"""
        self.variables[key] = value

    def get_variable(self, key: str) -> Any:
        """获取变量，不存在则抛出异常。"""
        if key not in self.variables:
            raise KeyError(f"变量 '{key}' 不存在，当前可用变量: {list(self.variables.keys())}")
        return self.variables[key]

    def add_response(self, response: dict[str, Any]) -> None:
        """记录一次 HTTP 响应。"""
        self.responses.append(response)

    def get_last_response(self) -> dict[str, Any] | None:
        """获取最近一次响应。"""
        return self.responses[-1] if self.responses else None

    def extract_jsonpath(self, data: Any, expression: str) -> Any:
        """使用 JSONPath 从数据中提取值。"""
        matches = jsonpath_parse(expression).find(data)
        if not matches:
            raise ValueError(f"JSONPath '{expression}' 未匹配到任何数据")
        return matches[0].value

    def save_from_response(self, save_map: dict[str, str], response_body: Any) -> None:
        """根据 save_map 从响应体中提取值并保存到变量。

        Args:
            save_map: 变量名 -> JSONPath 表达式，如 {"token": "$.data.token"}
            response_body: HTTP 响应体（dict 或 list）
        """
        for var_name, jsonpath_expr in save_map.items():
            value = self.extract_jsonpath(response_body, jsonpath_expr)
            self.set_variable(var_name, value)

    def resolve_variables(self, text: str) -> str:
        """替换文本中的变量引用，如 $token 或 ${token}。"""

        def _replace(match: re.Match) -> str:
            var_name = match.group(1) or match.group(2)
            try:
                return str(self.get_variable(var_name))
            except KeyError:
                return match.group(0)  # 保留原样

        pattern = r"\$\{(\w+)\}|\$(\w+)"
        return re.sub(pattern, _replace, text)

    def resolve_dict(self, data: Any) -> Any:
        """递归替换 dict/list/str 中的变量引用。"""
        if isinstance(data, str):
            return self.resolve_variables(data)
        elif isinstance(data, dict):
            return {self.resolve_variables(k) if isinstance(k, str) else k: self.resolve_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.resolve_dict(item) for item in data]
        return data
