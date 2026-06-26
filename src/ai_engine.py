"""AI 解析引擎 — 调用 Claude API 解析自然语言为 HTTP 请求和断言。"""

from __future__ import annotations

import json
import logging
from typing import Any

import anthropic

logger = logging.getLogger(__name__)

# ============================================================
# Tool 定义：让 Claude 通过 tool_use 返回结构化数据
# ============================================================

PARSE_ACTION_TOOL = {
    "name": "execute_http_request",
    "description": "将自然语言描述解析为一个 HTTP 请求并执行",
    "input_schema": {
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                "description": "HTTP 请求方法",
            },
            "url": {
                "type": "string",
                "description": "请求路径或完整 URL，如 /api/login",
            },
            "headers": {
                "type": "object",
                "description": "请求头，如 {\"Authorization\": \"Bearer $token\"}",
                "additionalProperties": {"type": "string"},
            },
            "body": {
                "type": "object",
                "description": "请求体（JSON），仅 POST/PUT/PATCH 需要",
            },
            "params": {
                "type": "object",
                "description": "URL 查询参数，如 {\"page\": \"1\"}",
                "additionalProperties": {"type": "string"},
            },
        },
        "required": ["method", "url"],
    },
}

VALIDATE_RESULT_TOOL = {
    "name": "validate_result",
    "description": "验证 HTTP 响应是否符合预期",
    "input_schema": {
        "type": "object",
        "properties": {
            "passed": {
                "type": "boolean",
                "description": "验证是否通过",
            },
            "reason": {
                "type": "string",
                "description": "验证结果的详细说明",
            },
            "details": {
                "type": "object",
                "description": "验证的具体细节",
                "properties": {
                    "expected": {"type": "string", "description": "预期结果"},
                    "actual": {"type": "string", "description": "实际结果"},
                },
            },
        },
        "required": ["passed", "reason"],
    },
}

FAILURE_ANALYSIS_TOOL = {
    "name": "analyze_failure",
    "description": "分析测试失败的原因并给出建议",
    "input_schema": {
        "type": "object",
        "properties": {
            "root_cause": {
                "type": "string",
                "description": "失败的根本原因",
            },
            "suggestion": {
                "type": "string",
                "description": "修复或改进的建议",
            },
            "category": {
                "type": "string",
                "enum": ["api_error", "assertion_error", "network_error", "config_error", "unknown"],
                "description": "错误类别",
            },
        },
        "required": ["root_cause", "suggestion", "category"],
    },
}


class AIEngine:
    """AI 解析引擎，调用 Claude API。"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6", max_retries: int = 3) -> None:
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.max_retries = max_retries

    def parse_action(
        self,
        action_text: str,
        context_variables: dict[str, Any],
        last_response: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """将自然语言 action 解析为 HTTP 请求结构。

        Args:
            action_text: 自然语言描述的测试步骤
            context_variables: 当前上下文变量
            last_response: 上一步的响应（如有）

        Returns:
            解析后的 HTTP 请求 dict (method, url, headers, body, params)
        """
        system_prompt = self._build_parse_system_prompt(context_variables, last_response)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            tools=[PARSE_ACTION_TOOL],
            messages=[{"role": "user", "content": action_text}],
        )

        # 提取 tool_use 结果
        for block in response.content:
            if block.type == "tool_use" and block.name == "execute_http_request":
                return block.input

        # 如果没有调用 tool，尝试从文本解析
        raise RuntimeError(f"AI 未能解析 action: {action_text}，响应: {[b.text for b in response.content if hasattr(b, 'text')]}")

    def validate_result(
        self,
        expect_text: str,
        actual_response: dict[str, Any],
        context_variables: dict[str, Any],
    ) -> dict[str, Any]:
        """验证实际响应是否符合预期。

        Args:
            expect_text: 自然语言描述的预期结果
            actual_response: 实际的 HTTP 响应
            context_variables: 当前上下文变量

        Returns:
            验证结果 dict (passed, reason, details)
        """
        user_message = f"""## 预期结果
{expect_text}

## 实际响应
状态码: {actual_response.get('status_code')}
响应体: {json.dumps(actual_response.get('body'), ensure_ascii=False, indent=2)}
响应头: {json.dumps(actual_response.get('headers', {}), ensure_ascii=False)}
耗时: {actual_response.get('elapsed_ms', 0):.0f}ms"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="你是一个 API 测试验证专家。根据用户的预期结果描述，验证实际的 HTTP 响应是否符合预期。调用 validate_result 工具返回验证结果。",
            tools=[VALIDATE_RESULT_TOOL],
            messages=[{"role": "user", "content": user_message}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "validate_result":
                return block.input

        raise RuntimeError("AI 未能验证结果")

    def analyze_failure(
        self,
        action_text: str,
        expect_text: str,
        actual_response: dict[str, Any],
        validation_result: dict[str, Any],
    ) -> dict[str, Any]:
        """分析测试失败的原因。

        Args:
            action_text: 测试步骤描述
            expect_text: 预期结果描述
            actual_response: 实际响应
            validation_result: 验证结果

        Returns:
            分析结果 dict (root_cause, suggestion, category)
        """
        user_message = f"""## 测试步骤
{action_text}

## 预期结果
{expect_text}

## 实际响应
状态码: {actual_response.get('status_code')}
响应体: {json.dumps(actual_response.get('body'), ensure_ascii=False, indent=2)}

## 验证结果
通过: {validation_result.get('passed')}
原因: {validation_result.get('reason')}
期望: {validation_result.get('details', {}).get('expected', 'N/A')}
实际: {validation_result.get('details', {}).get('actual', 'N/A')}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system="你是一个 API 测试故障分析专家。分析测试失败的根本原因并给出修复建议。调用 analyze_failure 工具返回分析结果。",
            tools=[FAILURE_ANALYSIS_TOOL],
            messages=[{"role": "user", "content": user_message}],
        )

        for block in response.content:
            if block.type == "tool_use" and block.name == "analyze_failure":
                return block.input

        return {"root_cause": "无法分析", "suggestion": "请人工检查", "category": "unknown"}

    def _build_parse_system_prompt(
        self,
        context_variables: dict[str, Any],
        last_response: dict[str, Any] | None,
    ) -> str:
        """构建解析 action 的系统提示词。"""
        parts = [
            "你是一个 API 测试执行助手。用户会用自然语言描述一个 HTTP 请求操作，"
            "你需要将其解析为结构化的 HTTP 请求，并调用 execute_http_request 工具执行。",
            "",
            "## 当前上下文变量",
            json.dumps(context_variables, ensure_ascii=False, indent=2) if context_variables else "（无）",
        ]

        if last_response:
            parts.extend([
                "",
                "## 上一步的响应",
                f"状态码: {last_response.get('status_code')}",
                f"响应体: {json.dumps(last_response.get('body'), ensure_ascii=False, indent=2)}",
            ])

        parts.extend([
            "",
            "## 规则",
            "1. URL 中的变量用 $变量名 引用，如 $token",
            "2. 如果用户提到「使用上一步的 xxx」，从上一步响应中获取",
            "3. body 中的值直接使用用户描述的内容",
            "4. 如果用户没有指定 method，根据上下文推断（创建=POST，查询=GET，更新=PUT，删除=DELETE）",
        ])

        return "\n".join(parts)
