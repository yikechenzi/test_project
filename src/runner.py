"""测试运行器 — 编排测试执行流程。"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import yaml

from .ai_engine import AIEngine
from .openai_engine import OpenAIEngine
from .context import TestContext
from .executor import HTTPExecutor, HTTPRequest
from .reporter import Reporter

logger = logging.getLogger(__name__)


@dataclass
class StepResult:
    """单个步骤的执行结果。"""
    step_num: int
    action: str
    expect: str
    status: str  # "pass" | "fail" | "error"
    reason: str = ""
    request: dict[str, Any] = field(default_factory=dict)
    response: dict[str, Any] = field(default_factory=dict)
    failure_analysis: dict[str, Any] = field(default_factory=dict)
    elapsed_ms: float = 0


@dataclass
class CaseResult:
    """单个测试用例的结果。"""
    name: str
    status: str  # "pass" | "fail" | "error" | "skip"
    steps: list[StepResult] = field(default_factory=list)
    failure_analysis: dict[str, Any] = field(default_factory=dict)
    duration: float = 0


class TestRunner:
    """测试运行器。"""

    def __init__(self, config_path: str = "config.yaml") -> None:
        # 加载配置
        with open(config_path, encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # 根据 provider 选择 AI 引擎
        provider = self.config.get("provider", "claude")
        max_retries = self.config.get("max_retries", 3)

        if provider == "mimo":
            self.ai = OpenAIEngine(
                api_key=self.config["mimo_api_key"],
                model=self.config.get("mimo_model", "MiMo-2.5-Pro"),
                base_url=self.config.get("mimo_base_url", "https://api.siliconflow.cn/v1"),
                max_retries=max_retries,
            )
            logger.info(f"使用 MiMo 引擎: {self.config.get('mimo_model', 'MiMo-2.5-Pro')}")
        else:
            self.ai = AIEngine(
                api_key=self.config["claude_api_key"],
                model=self.config.get("claude_model", "claude-sonnet-4-6"),
                max_retries=max_retries,
            )
            logger.info(f"使用 Claude 引擎: {self.config.get('claude_model', 'claude-sonnet-4-6')}")
        self.executor = HTTPExecutor(
            base_url=self.config["base_url"],
            timeout=self.config.get("timeout", 30),
        )
        self.reporter = Reporter(output_dir=self.config.get("report_dir", "reports"))

    def run_file(self, filepath: str) -> dict[str, Any]:
        """运行单个测试用例文件。

        Args:
            filepath: YAML 测试用例文件路径

        Returns:
            测试套件结果
        """
        with open(filepath, encoding="utf-8") as f:
            suite = yaml.safe_load(f)

        return self.run_suite(suite)

    def run_suite(self, suite: dict[str, Any]) -> dict[str, Any]:
        """运行一个测试套件。

        Args:
            suite: 解析后的测试套件 dict

        Returns:
            套件执行结果
        """
        suite_name = suite.get("name", "未命名测试套件")
        suite_desc = suite.get("description", "")
        tags = suite.get("tags", [])
        cases = suite.get("cases", [])

        self.reporter.print_suite_start(suite_name, suite_desc)

        # 创建测试上下文
        context = TestContext(base_url=self.config["base_url"])

        # 执行 setup
        setup_steps = suite.get("setup", [])
        if setup_steps:
            logger.info("执行 setup 步骤...")
            for setup_action in setup_steps:
                self._execute_action(context, setup_action, "")

        # 执行测试用例
        case_results: list[dict[str, Any]] = []
        for case in cases:
            result = self._run_case(context, case)
            case_results.append(result)

        # 执行 teardown
        teardown_steps = suite.get("teardown", [])
        if teardown_steps:
            logger.info("执行 teardown 步骤...")
            for teardown_action in teardown_steps:
                try:
                    self._execute_action(context, teardown_action, "")
                except Exception as e:
                    logger.warning(f"Teardown 步骤失败: {e}")

        suite_result = {
            "name": suite_name,
            "description": suite_desc,
            "tags": tags,
            "cases": case_results,
        }

        self.reporter.add_suite_result(suite_result)
        return suite_result

    def run_all(self, test_dir: str = "test_cases") -> None:
        """运行指定目录下的所有测试用例。

        Args:
            test_dir: 测试用例目录
        """
        import glob
        import os

        pattern = os.path.join(test_dir, "*.yaml")
        files = sorted(glob.glob(pattern))

        if not files:
            logger.warning(f"在 {test_dir} 目录下未找到测试用例文件")
            return

        logger.info(f"找到 {len(files)} 个测试用例文件")

        for filepath in files:
            try:
                self.run_file(filepath)
            except Exception as e:
                logger.error(f"运行 {filepath} 时出错: {e}")

        # 输出汇总
        self.reporter.print_summary()

        # 生成 HTML 报告
        self.reporter.generate_html_report()

    def _run_case(self, context: TestContext, case: dict[str, Any]) -> dict[str, Any]:
        """运行单个测试用例。

        Args:
            context: 测试上下文
            case: 测试用例定义

        Returns:
            用例执行结果
        """
        case_name = case.get("name", "未命名用例")
        steps = case.get("steps", [])

        self.reporter.print_case_start(case_name)
        start_time = time.time()

        step_results: list[dict[str, Any]] = []
        case_status = "pass"
        case_failure = {}

        for i, step in enumerate(steps, 1):
            action = step.get("action", "")
            expect = step.get("expect", "")
            save_map = step.get("save", {})

            try:
                result = self._execute_step(context, i, action, expect, save_map)
                step_results.append(result)

                if result.status != "pass":
                    case_status = "fail"
                    # 失败时进行 AI 分析
                    if not result.failure_analysis:
                        analysis = self.ai.analyze_failure(
                            action, expect, result.response,
                            {"passed": False, "reason": result.reason, "details": {}},
                        )
                        result.failure_analysis = analysis
                        case_failure = analysis
                        self.reporter.print_failure_analysis(analysis)
                    break  # 用例失败后不再继续执行后续步骤

            except Exception as e:
                logger.error(f"步骤 {i} 执行异常: {e}")
                step_results.append({
                    "step_num": i,
                    "action": action,
                    "expect": expect,
                    "status": "error",
                    "reason": str(e),
                    "request": {},
                    "response": {},
                    "failure_analysis": {},
                    "elapsed_ms": 0,
                })
                case_status = "error"
                case_failure = {"root_cause": str(e), "suggestion": "请检查配置和网络连接", "category": "config_error"}
                break

        duration = time.time() - start_time

        return {
            "name": case_name,
            "status": case_status,
            "steps": [s if isinstance(s, dict) else self._step_to_dict(s) for s in step_results],
            "failure_analysis": case_failure,
            "duration": round(duration, 2),
        }

    def _execute_step(
        self,
        context: TestContext,
        step_num: int,
        action: str,
        expect: str,
        save_map: dict[str, str],
    ) -> StepResult:
        """执行单个测试步骤。"""
        start_time = time.time()

        # 1. 解析变量
        resolved_action = context.resolve_variables(action)

        # 2. AI 解析 action → HTTP 请求
        last_resp = context.get_last_response()
        last_resp_dict = last_resp.to_dict() if last_resp else None

        parsed_request = self.ai.parse_action(
            resolved_action,
            context.variables,
            last_resp_dict,
        )

        # 3. 执行 HTTP 请求
        http_request = HTTPRequest(
            method=parsed_request.get("method", "GET"),
            url=parsed_request.get("url", ""),
            headers=context.resolve_dict(parsed_request.get("headers", {})),
            body=context.resolve_dict(parsed_request.get("body")),
            params=context.resolve_dict(parsed_request.get("params", {})),
        )

        http_response = self.executor.execute(http_request)
        context.add_response(http_response)

        response_dict = http_response.to_dict()
        elapsed = http_response.elapsed_ms

        # 4. AI 验证 expect
        if expect:
            validation = self.ai.validate_result(expect, response_dict, context.variables)
            passed = validation.get("passed", False)
            reason = validation.get("reason", "")
        else:
            passed = True
            reason = "无断言，自动通过"

        # 5. 保存变量
        if save_map and http_response.body:
            try:
                context.save_from_response(save_map, http_response.body)
            except Exception as e:
                logger.warning(f"保存变量失败: {e}")

        # 6. 打印结果
        self.reporter.print_step_result(step_num, action, passed, reason, elapsed)

        result = StepResult(
            step_num=step_num,
            action=action,
            expect=expect,
            status="pass" if passed else "fail",
            reason=reason,
            request=parsed_request,
            response=response_dict,
            elapsed_ms=elapsed,
        )

        return result

    def _execute_action(self, context: TestContext, action: str, expect: str) -> StepResult:
        """执行单个 action（用于 setup/teardown）。"""
        return self._execute_step(context, 0, action, expect, {})

    @staticmethod
    def _step_to_dict(step: StepResult) -> dict[str, Any]:
        """将 StepResult 转为 dict。"""
        return {
            "step_num": step.step_num,
            "action": step.action,
            "expect": step.expect,
            "status": step.status,
            "reason": step.reason,
            "request": step.request,
            "response": step.response,
            "failure_analysis": step.failure_analysis,
            "elapsed_ms": step.elapsed_ms,
        }
