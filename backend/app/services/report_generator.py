import os
import uuid
from datetime import datetime
from typing import List, Optional
from jinja2 import Template

from app.core.config import settings
from app.models.test_report import TestReport
from app.models.test_execution import TestExecution


class ReportGenerator:
    """
    Generate test reports in HTML format
    """
    
    def __init__(self):
        self.reports_dir = settings.REPORTS_DIR
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def generate_html_report(
        self,
        report: TestReport,
        executions: List[TestExecution]
    ) -> str:
        """
        Generate HTML report
        """
        # HTML template
        template = Template("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ report.title }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 30px;
            margin-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .summary-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .summary-card.passed {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        }
        .summary-card.failed {
            background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        }
        .summary-card.skipped {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .summary-card h3 {
            margin: 0;
            font-size: 2em;
        }
        .summary-card p {
            margin: 5px 0 0;
            opacity: 0.9;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #3498db;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .status {
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status.passed {
            background-color: #d4edda;
            color: #155724;
        }
        .status.failed {
            background-color: #f8d7da;
            color: #721c24;
        }
        .status.error {
            background-color: #fff3cd;
            color: #856404;
        }
        .status.pending {
            background-color: #e2e3e5;
            color: #383d41;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #11998e, #38ef7d);
            transition: width 0.3s ease;
        }
        .meta {
            color: #666;
            font-size: 0.9em;
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ report.title }}</h1>
        
        <div class="meta">
            <p><strong>Generated:</strong> {{ report.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</p>
            {% if report.description %}
            <p><strong>Description:</strong> {{ report.description }}</p>
            {% endif %}
        </div>

        <h2>Summary</h2>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ report.pass_rate }}%"></div>
        </div>
        <p style="text-align: center; font-size: 1.2em;">
            <strong>Pass Rate: {{ report.pass_rate }}%</strong>
        </p>

        <div class="summary">
            <div class="summary-card">
                <h3>{{ report.total_tests }}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-card passed">
                <h3>{{ report.passed_tests }}</h3>
                <p>Passed</p>
            </div>
            <div class="summary-card failed">
                <h3>{{ report.failed_tests }}</h3>
                <p>Failed</p>
            </div>
            <div class="summary-card skipped">
                <h3>{{ report.skipped_tests + report.error_tests }}</h3>
                <p>Skipped/Error</p>
            </div>
        </div>

        {% if report.start_time and report.end_time %}
        <div class="meta">
            <p><strong>Duration:</strong> {{ report.duration }} seconds</p>
            <p><strong>Start Time:</strong> {{ report.start_time.strftime('%Y-%m-%d %H:%M:%S') }}</p>
            <p><strong>End Time:</strong> {{ report.end_time.strftime('%Y-%m-%d %H:%M:%S') }}</p>
        </div>
        {% endif %}

        <h2>Test Executions</h2>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Test Case</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Executed At</th>
                </tr>
            </thead>
            <tbody>
                {% for execution in executions %}
                <tr>
                    <td>{{ execution.id }}</td>
                    <td>{{ execution.test_case_id }}</td>
                    <td>
                        <span class="status {{ execution.status.value }}">
                            {{ execution.status.value }}
                        </span>
                    </td>
                    <td>{{ "%.2f"|format(execution.duration or 0) }}s</td>
                    <td>{{ execution.created_at.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                </tr>
                {% if execution.error_message %}
                <tr>
                    <td colspan="5">
                        <details>
                            <summary>Error Details</summary>
                            <pre>{{ execution.error_message }}</pre>
                        </details>
                    </td>
                </tr>
                {% endif %}
                {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>Generated by AI Test Platform</p>
    </div>
</body>
</html>
        """)
        
        # Render template
        html_content = template.render(
            report=report,
            executions=executions
        )
        
        # Save to file
        filename = f"report_{uuid.uuid4().hex[:8]}.html"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath