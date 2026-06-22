# AI Test Platform

AI驱动的自动化测试平台，支持多公司、多项目管理，具备测试用例编写、自动化执行、报告生成和用户权限控制功能。

## 功能特性

- **用户认证与权限管理**
  - JWT Token认证
  - 角色权限控制（管理员/普通用户）
  - 项目级数据隔离

- **项目管理**
  - 多公司支持
  - 项目CRUD操作
  - 项目成员管理

- **测试用例管理**
  - 多种测试类型（黑盒、白盒、API、UI）
  - 代码编辑器支持
  - AI辅助生成测试脚本
  - 测试用例分类和标签

- **测试执行引擎**
  - Playwright浏览器自动化
  - 实时日志推送
  - 截图和视频录制
  - 执行状态管理

- **测试报告系统**
  - 自动生成测试报告
  - 统计图表展示
  - 历史报告查询
  - 报告导出（HTML）

- **用户管理**
  - 用户CRUD操作
  - 项目绑定管理
  - 权限分配

## 技术栈

- **前端**: Vue.js 3 + Vite + Element Plus + Pinia
- **后端**: Python FastAPI + SQLAlchemy + Alembic
- **数据库**: PostgreSQL 15
- **测试引擎**: Playwright (Python)
- **AI集成**: OpenAI API (GPT-4)
- **部署**: Docker + Docker Compose
- **认证**: JWT Token

## 快速开始

### 使用Docker Compose（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd ai-test-platform
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，配置必要的环境变量
```

3. **启动服务**
```bash
docker-compose up -d
```

4. **访问应用**
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

5. **默认管理员账号**
- 用户名: admin
- 密码: admin123

### 本地开发

#### 后端

1. **安装依赖**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **配置数据库**
```bash
# 安装PostgreSQL并创建数据库
createdb ai_test_db
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件
```

4. **运行后端**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **运行前端**
```bash
npm run dev
```

## 项目结构

```
ai-test-platform/
├── frontend/                 # Vue.js前端
│   ├── src/
│   │   ├── api/             # API接口
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面
│   │   ├── router/          # 路由
│   │   ├── stores/          # Pinia状态管理
│   │   └── utils/           # 工具函数
│   └── Dockerfile
├── backend/                  # Python后端
│   ├── app/
│   │   ├── api/             # API路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据模型
│   │   ├── services/        # 业务逻辑
│   │   └── utils/           # 工具函数
│   ├── Dockerfile
│   └── requirements.txt
├── nginx/                    # Nginx配置
├── docker-compose.yml        # Docker编排（开发）
├── docker-compose.prod.yml   # Docker编排（生产）
└── .env.example             # 环境变量示例
```

## API文档

启动后端服务后，访问以下地址查看API文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| DATABASE_URL | 数据库连接URL | postgresql://postgres:postgres123@localhost:5432/ai_test_db |
| REDIS_URL | Redis连接URL | redis://localhost:6379/0 |
| SECRET_KEY | JWT密钥 | your-secret-key-here |
| OPENAI_API_KEY | OpenAI API密钥 | - |
| CORS_ORIGINS | CORS允许的源 | http://localhost:5173 |

## 部署说明

### 生产环境部署

1. **配置生产环境变量**
```bash
cp .env.production .env
# 编辑.env文件，配置生产环境参数
```

2. **启动生产环境**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

3. **配置SSL证书**
```bash
# 将SSL证书放置到nginx/ssl目录
# 更新nginx配置以启用HTTPS
```

## 开发指南

### 添加新的API端点

1. 在`backend/app/api/`目录下创建新的路由文件
2. 在`backend/app/main.py`中注册路由
3. 在`backend/app/models/`中定义数据模型
4. 在`backend/app/services/`中实现业务逻辑

### 添加新的前端页面

1. 在`frontend/src/views/`目录下创建新的Vue组件
2. 在`frontend/src/router/index.ts`中添加路由
3. 在`frontend/src/api/`中添加API调用
4. 在`frontend/src/stores/`中添加状态管理

## 测试

### 运行后端测试
```bash
cd backend
pytest
```

### 运行前端测试
```bash
cd frontend
npm run test
```

## 常见问题

### 数据库连接失败
- 检查PostgreSQL服务是否启动
- 验证数据库连接URL是否正确
- 确保数据库用户有足够权限

### AI功能无法使用
- 检查OPENAI_API_KEY是否配置
- 确认OpenAI API账户有足够额度
- 检查网络连接是否正常

### 测试执行失败
- 确保Playwright浏览器已安装
- 检查测试脚本语法是否正确
- 查看执行日志获取详细错误信息

## 贡献指南

1. Fork项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交Issue或联系开发团队。