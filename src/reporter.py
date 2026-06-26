"""报告生成器 — 控制台彩色输出和 HTML 测试报告。"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from jinja2 import Template
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

# ============================================================
# HTML 报告模板
# ============================================================
HTML_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 测试报告 — {{ timestamp }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f5f5f5; color: #333; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 10px; color: #1a1a2e; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; }
        .summary { display: flex; gap: 20px; justify-content: center; margin-bottom: 30px; flex-wrap: wrap; }
        .summary-card { background: white; border-radius: 12px; padding: 20px 30px; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.08); min-width: 120px; }
        .summary-card .number { font-size: 2.5em; font-weight: bold; }
        .summary-card .label { color: #666; font-size: 0.9em; margin-top: 4px; }
        .pass .number { color: #22c55e; }
        .fail .number { color: #ef4444; }
        .skip .number { color: #eab308; }
        .total .number { color: #3b82f6; }
        .rate .number { color: #8b5cf6; }
        .rate-bar { background: #e5e7eb; border-radius: 8px; height: 16px; margin: 10px 0; overflow: hidden; }
        .rate-bar .fill { height: 100%; border-radius: 8px; transition: width 0.3s; }
        .rate-bar .fill.high { background: #22c55e; }
        .rate-bar .fill.low { background: #ef4444; }
        .test-suite { background: white; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden; }
        .suite-header { padding: 16px 20px; background: #f8f9fa; border-bottom: 1px solid #e5e7eb; cursor: pointer; }
        .suite-header h3 { margin: 0; font-size: 1.1em; }
        .suite-header .tags { display: flex; gap: 6px; margin-top: 6px; }
        .suite-header .tag { background: #e0e7ff; color: #4338ca; padding: 2px 8px; border-radius: 4px; font-size: 0.75em; }
        .case { border-bottom: 1px solid #f0f0f0; }
        .case:last-child { border-bottom: none; }
        .case-header { padding: 12px 20px; display: flex; align-items: center; gap: 10px; cursor: pointer; }
        .case-header:hover { background: #fafafa; }
        .status-badge { padding: 3px 10px; border-radius: 4px; font-size: 0.8em; font-weight: 600; }
        .status-pass { background: #dcfce7; color: #166534; }
        .status-fail { background: #fef2f2; color: #991b1b; }
        .status-skip { background: #fef9c3; color: #854d0e; }
        .case-name { flex: 1; font-weight: 500; }
        .case-time { color: #999; font-size: 0.85em; }
        .case-details { padding: 0 20px 16px; display: none; }
        .case-details.open { display: block; }
        .step { background: #f8f9fa; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px; font-size: 0.9em; }
        .step-action { font-weight: 500; margin-bottom: 4px; }
        .step-expect { color: #666; }
        .step-response { margin-top: 8px; background: #1e1e2e; color: #cdd6f4; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 0.85em; white-space: pre-wrap; word-break: break-all; max-height: 200px; overflow-y: auto; }
        .step-status { display: inline-block; margin-top: 6px; }
        .step-status.pass { color: #22c55e; }
        .step-status.fail { color: #ef4444; }
        .failure-analysis { background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 12px 16px; margin-top: 10px; }
        .failure-analysis h4 { color: #991b1b; margin-bottom: 6px; }
        .failure-analysis p { margin: 4px 0; font-size: 0.9em; }
        footer { text-align: center; color: #999; margin-top: 30px; padding: 20px; font-size: 0.85em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI 自动化测试报告</h1>
        <p class="subtitle">{{ timestamp }}</p>

        <div class="summary">
            <div class="summary-card total">
                <div class="number">{{ total }}</div>
                <div class="label">总用例</div>
            </div>
            <div class="summary-card pass">
                <div class="number">{{ passed }}</div>
                <div class="label">通过</div>
            </div>
            <div class="summary-card fail">
                <div class="number">{{ failed }}</div>
                <div class="label">失败</div>
            </div>
            <div class="summary-card skip">
                <div class="number">{{ skipped }}</div>
                <div class="label">跳过</div>
            </div>
            <div class="summary-card rate">
                <div class="number">{{ pass_rate }}%</div>
                <div class="label">通过率</div>
            </div>
        </div>

        <div class="rate-bar">
            <div class="fill {{ 'high' if pass_rate >= 80 else 'low' }}" style="width: {{ pass_rate }}%;"></div>
        </div>

        {% for suite in suites %}
        <div class="test-suite">
            <div class="suite-header">
                <h3>{{ suite.name }}</h3>
                {% if suite.tags %}
                <div class="tags">
                    {% for tag in suite.tags %}
                    <span class="tag">{{ tag }}</span>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            {% for case in suite.cases %}
            <div class="case">
                <div class="case-header" onclick="this.nextElementSibling.classList.toggle('open')">
                    <span class="status-badge status-{{ case.status }}">{{ case.status | upper }}</span>
                    <span class="case-name">{{ case.name }}</span>
                    <span class="case-time">{{ case.duration }}s</span>
                </div>
                <div class="case-details">
                    {% for step in case.steps %}
                    <div class="step">
                        <div class="step-action">📋 {{ step.action }}</div>
                        <div class="step-expect">✅ 预期: {{ step.expect }}</div>
                        {% if step.response %}
                        <div class="step-response">{{ step.response }}</div>
                        {% endif %}
                        <div class="step-status {{ step.status }}">
                            {% if step.status == 'pass' %}✓ 通过{% else %}✗ 失败: {{ step.reason }}{% endif %}
                        </div>
                    </div>
                    {% endfor %}
                    {% if case.failure_analysis %}
                    <div class="failure-analysis">
                        <h4>🔍 失败分析</h4>
                        <p><strong>根本原因:</strong> {{ case.failure_analysis.root_cause }}</p>
                        <p><strong>建议:</strong> {{ case.failure_analysis.suggestion }}</p>
                        <p><strong>类别:</strong> {{ case.failure_analysis.category }}</p>
                    </div>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
        {% endfor %}

        <footer>
            由 AI 测试框架自动生成 | Powered by Claude
        </footer>
    </div>
</body>
</html>""")


class Reporter:
    """测试报告生成器。"""

    def __init__(self, output_dir: str = "reports") -> None:
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.results: list[dict[str, Any]] = []

    def add_suite_result(self, suite_result: dict[str, Any]) -> None:
        """添加一个测试套件的结果。"""
        self.results.append(suite_result)

    def print_suite_start(self, name: str, description: str = "") -> None:
        """打印测试套件开始。"""
        console.print()
        console.print(Panel(
            f"[bold]{name}[/bold]\n{description}" if description else f"[bold]{name}[/bold]",
            title="🧪 测试套件",
            border_style="blue",
        ))

    def print_case_start(self, name: str) -> None:
        """打印测试用例开始。"""
        console.print(f"\n  [bold cyan]▶ {name}[/bold cyan]")

    def print_step_result(
        self,
        step_num: int,
        action: str,
        passed: bool,
        reason: str = "",
        elapsed_ms: float = 0,
    ) -> None:
        """打印步骤执行结果。"""
        status = "[green]✓ PASS[/green]" if passed else "[red]✗ FAIL[/red]"
        console.print(f"    Step {step_num}: {status}  {action[:60]}{'...' if len(action) > 60 else ''}")
        if not passed and reason:
            console.print(f"      [red]原因: {reason}[/red]")
        if elapsed_ms:
            console.print(f"      [dim]耗时: {elapsed_ms:.0f}ms[/dim]")

    def print_failure_analysis(self, analysis: dict[str, Any]) -> None:
        """打印失败分析。"""
        console.print(Panel(
            f"[bold]根本原因:[/bold] {analysis.get('root_cause', 'N/A')}\n"
            f"[bold]建议:[/bold] {analysis.get('suggestion', 'N/A')}\n"
            f"[bold]类别:[/bold] {analysis.get('category', 'N/A')}",
            title="🔍 失败分析",
            border_style="red",
        ))

    def print_summary(self) -> None:
        """打印测试总结。"""
        total, passed, failed, skipped = 0, 0, 0, 0
        for suite in self.results:
            for case in suite.get("cases", []):
                total += 1
                status = case.get("status", "skip")
                if status == "pass":
                    passed += 1
                elif status == "fail":
                    failed += 1
                else:
                    skipped += 1

        pass_rate = (passed / total * 100) if total > 0 else 0

        table = Table(title="📊 测试结果汇总", show_header=True, header_style="bold")
        table.add_column("指标", style="bold")
        table.add_column("数量", justify="right")
        table.add_row("总用例", str(total))
        table.add_row("✅ 通过", f"[green]{passed}[/green]")
        table.add_row("❌ 失败", f"[red]{failed}[/red]" if failed else "0")
        table.add_row("⏭ 跳过", f"[yellow]{skipped}[/yellow]" if skipped else "0")
        table.add_row("通过率", f"[{'green' if pass_rate >= 80 else 'red'}]{pass_rate:.1f}%[/]")

        console.print()
        console.print(table)

    def generate_html_report(self) -> str:
        """生成 HTML 测试报告。

        Returns:
            报告文件路径
        """
        total, passed, failed, skipped = 0, 0, 0, 0
        for suite in self.results:
            for case in suite.get("cases", []):
                total += 1
                status = case.get("status", "skip")
                if status == "pass":
                    passed += 1
                elif status == "fail":
                    failed += 1
                else:
                    skipped += 1

        pass_rate = round((passed / total * 100) if total > 0 else 0, 1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = HTML_TEMPLATE.render(
            timestamp=timestamp,
            total=total,
            passed=passed,
            failed=failed,
            skipped=skipped,
            pass_rate=pass_rate,
            suites=self.results,
        )

        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        console.print(f"\n[bold green]📄 HTML 报告已生成: {filepath}[/bold green]")
        return filepath
