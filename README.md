# 🤖 AI 自动化测试框架

**只写测试用例，AI 自动执行。**

这是一个基于 Claude AI 的 Web API 自动化测试框架。你只需要用**自然语言（中文）**编写测试用例，AI 会自动理解、执行、验证并生成报告。

## ✨ 特性

- 📝 **自然语言测试用例** — 用中文描述测试步骤和预期结果
- 🤖 **AI 智能解析** — Claude 自动将自然语言转换为 HTTP 请求
- ✅ **AI 自动验证** — AI 判断结果是否符合预期
- 🔗 **步骤间数据传递** — 支持变量保存和引用（如 token 传递）
- 🔍 **失败智能分析** — 测试失败时 AI 分析原因并给出建议
- 📊 **HTML 测试报告** — 生成美观的测试报告

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置

编辑 `config.yaml`：

```yaml
base_url: "http://localhost:8000"       # 你的被测服务地址
claude_api_key: "sk-ant-..."            # 你的 Claude API Key
claude_model: "claude-sonnet-4-6"       # 使用的模型
timeout: 30                              # 请求超时时间（秒）
```

### 3. 编写测试用例

在 `test_cases/` 目录下创建 `.yaml` 文件：

```yaml
name: "用户登录测试"
description: "测试用户登录功能"
tags: [登录]

cases:
  - name: "正常登录"
    steps:
      - action: "发送 POST 请求到 /api/login，body 包含用户名 admin 和密码 123456"
        expect: "返回状态码 200，响应中包含 token"
        save: { token: "$.data.token" }

      - action: "使用 $token 发送 GET 请求到 /api/user/profile"
        expect: "返回状态码 200，用户名为 admin"
```

### 4. 运行测试

```bash
# 运行所有测试用例
python run.py

# 运行指定用例
python run.py --case test_cases/example_login.yaml

# 指定配置文件
python run.py --config my_config.yaml

# 详细日志
python run.py --verbose
```

## 📖 测试用例格式

### 完整结构

```yaml
name: "测试套件名称"
description: "测试套件描述"
tags: [标签1, 标签2]

setup:
  - "准备步骤（自然语言）"

cases:
  - name: "用例名称"
    steps:
      - action: "执行什么操作（自然语言）"
        expect: "期望什么结果（自然语言）"
        save: { 变量名: "$.jsonpath表达式" }

teardown:
  - "清理步骤（自然语言）"
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | ✅ | 测试套件/用例名称 |
| `description` | ❌ | 套件描述 |
| `tags` | ❌ | 标签列表 |
| `setup` | ❌ | 套件执行前的准备步骤列表 |
| `cases` | ✅ | 测试用例列表 |
| `teardown` | ❌ | 套件执行后的清理步骤列表 |
| `action` | ✅ | 自然语言描述的操作步骤 |
| `expect` | ❌ | 自然语言描述的预期结果 |
| `save` | ❌ | 从响应中提取数据保存为变量 |

### 变量使用

```yaml
# 保存变量
save: { token: "$.data.token", user_id: "$.data.id" }

# 引用变量（两种方式）
action: "使用 $token 发送 GET 请求到 /api/users/$user_id"
action: "使用 ${token} 发送 GET 请求到 /api/users/${user_id}"
```

### 自然语言编写技巧

```yaml
# ✅ 好的写法 — 清晰明确
action: "发送 POST 请求到 /api/login，body 包含用户名 admin 和密码 123456"
expect: "返回状态码 200，响应中包含 token 字段"

# ✅ 变量引用
action: "使用上一步获取的 token 发送 GET 请求到 /api/user/profile"
expect: "返回状态码 200，用户名为 admin"

# ✅ 查询参数
action: "发送 GET 请求到 /api/users，查询参数包含 page=1 和 limit=10"
expect: "返回状态码 200，返回用户列表，数量不超过 10"

# ✅ 删除操作
action: "发送 DELETE 请求到 /api/users/123"
expect: "返回状态码 204"
```

## 📊 测试报告

运行完成后自动生成两种报告：

- **控制台报告** — 实时彩色输出
- **HTML 报告** — 保存在 `reports/` 目录

## 🏗 项目结构

```
ai_test/
├── config.yaml              # 全局配置
├── test_cases/              # 测试用例目录
│   └── example_login.yaml   # 示例用例
├── src/
│   ├── ai_engine.py         # AI 解析引擎（Claude API）
│   ├── executor.py          # HTTP 请求执行器
│   ├── context.py           # 测试上下文（变量管理）
│   ├── runner.py            # 测试运行器
│   └── reporter.py          # 报告生成器
├── reports/                 # 测试报告输出
├── run.py                   # 入口脚本
├── requirements.txt         # Python 依赖
└── README.md                # 本文件
```

## 💡 工作原理

```
编写 YAML 用例 → AI 解析 action → 发送 HTTP 请求 → AI 验证结果 → 生成报告
      (自然语言)    (Claude API)     (requests)      (Claude API)    (HTML)
```

1. 读取 YAML 测试用例
2. 将自然语言 `action` 发送给 Claude，AI 返回结构化 HTTP 请求
3. 执行 HTTP 请求，获取响应
4. 将响应和自然语言 `expect` 发送给 Claude，AI 判断是否通过
5. 如需保存变量，用 JSONPath 从响应中提取
6. 失败时，AI 分析原因并给出建议
7. 生成 HTML 测试报告
