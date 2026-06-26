#!/usr/bin/env python3
"""AI 自动化测试框架 — 入口脚本。

使用方式:
    python run.py                              # 运行所有测试用例
    python run.py --case test_cases/login.yaml # 运行指定用例
    python run.py --dir my_tests               # 指定测试用例目录
    python run.py --config my_config.yaml      # 指定配置文件
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

# Windows 终端 UTF-8 支持
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from src.runner import TestRunner


def setup_logging(verbose: bool = False) -> None:
    """配置日志。"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    """主入口。"""
    parser = argparse.ArgumentParser(
        description="🤖 AI 自动化测试框架 — 只写测试用例，AI 自动执行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config", "-c",
        default="config.yaml",
        help="配置文件路径（默认: config.yaml）",
    )
    parser.add_argument(
        "--case",
        help="运行指定的测试用例文件",
    )
    parser.add_argument(
        "--dir", "-d",
        default="test_cases",
        help="测试用例目录（默认: test_cases）",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志",
    )

    args = parser.parse_args()
    setup_logging(args.verbose)

    try:
        runner = TestRunner(config_path=args.config)

        if args.case:
            # 运行单个用例
            runner.run_file(args.case)
            runner.reporter.print_summary()
            runner.reporter.generate_html_report()
        else:
            # 运行目录下所有用例
            runner.run_all(test_dir=args.dir)

    except FileNotFoundError as e:
        logging.error(f"文件未找到: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
