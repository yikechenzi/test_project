"""HTTP 请求执行器 — 发送请求并返回响应。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass
class HTTPResponse:
    """HTTP 响应封装。"""
    status_code: int
    headers: dict[str, str]
    body: Any
    elapsed_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "status_code": self.status_code,
            "headers": dict(self.headers),
            "body": self.body,
            "elapsed_ms": self.elapsed_ms,
        }


@dataclass
class HTTPRequest:
    """结构化的 HTTP 请求。"""
    method: str
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: Any = None
    params: dict[str, str] = field(default_factory=dict)


class HTTPExecutor:
    """HTTP 请求执行器。"""

    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def execute(self, request: HTTPRequest) -> HTTPResponse:
        """执行 HTTP 请求。

        Args:
            request: 结构化的 HTTP 请求对象

        Returns:
            HTTPResponse 封装的响应
        """
        # 拼接完整 URL
        url = request.url
        if not url.startswith(("http://", "https://")):
            url = f"{self.base_url}{url if url.startswith('/') else '/' + url}"

        # 设置默认 Content-Type
        headers = request.headers.copy()
        if request.body and "Content-Type" not in headers:
            headers["Content-Type"] = "application/json"

        # 发送请求
        response = self.session.request(
            method=request.method.upper(),
            url=url,
            headers=headers,
            json=request.body if isinstance(request.body, (dict, list)) else None,
            data=request.body if isinstance(request.body, str) else None,
            params=request.params or None,
            timeout=self.timeout,
        )

        # 解析响应体
        try:
            body = response.json()
        except (json.JSONDecodeError, ValueError):
            body = response.text

        return HTTPResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=body,
            elapsed_ms=response.elapsed.total_seconds() * 1000,
        )

    def close(self) -> None:
        """关闭 session。"""
        self.session.close()
