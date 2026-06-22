# AI自动化测试平台 - Ubuntu 部署教程

> 本文档面向 Ubuntu 系统用户，手把手教你在 Ubuntu 上部署和运行 AI 自动化测试平台。
> 适用于 Ubuntu 20.04 / 22.04 / 24.04 等版本。

---

## 一、环境准备

### 1.1 更新系统

打开终端（快捷键 `Ctrl + Alt + T`），首先更新系统软件包：

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.2 安装 Docker

```bash
# 安装必要的依赖
sudo apt install -y ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新包索引并安装 Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 验证安装
docker --version
docker compose version
```

### 1.3 配置 Docker 用户权限（免 sudo）

```bash
# 将当前用户加入 docker 组
sudo usermod -aG docker $USER

# 刷新组信息（或者重新登录/重启生效）
newgrp docker

# 验证
docker run hello-world
```

> 如果 `newgrp docker` 后还是不行，请注销重新登录或重启电脑。

### 1.4 安装 Git

```bash
sudo apt install -y git
git --version
```

### 1.5 安装 Python 3 和 pip（可选，本地开发时需要）

```bash
sudo apt install -y python3 python3-pip python3-venv
python3 --version
pip3 --version
```

### 1.6 安装 Node.js（可选，本地开发前端时需要）

```bash
# 使用 NodeSource 安装 Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 验证
node --version
npm --version
```

---

## 二、获取项目代码

```bash
# 进入你想存放项目的目录
cd ~

# 克隆项目（test 分支）
git clone -b test https://github.com/yikechenzi/test_project.git

# 进入项目目录
cd test_project/ai-test-platform

# 查看项目结构
ls -la
```

你应该能看到以下目录和文件：

```
ai-test-platform/
├── backend/              # Python 后端
├── frontend/             # Vue.js 前端
├── nginx/                # Nginx 配置
├── docker-compose.yml    # Docker 编排文件
├── .env.example          # 环境变量示例
├── README.md             # 项目说明
└── ...
```

---

## 三、配置环境变量

### 3.1 复制配置文件

```bash
cp .env.example .env
```

### 3.2 编辑配置文件

```bash
# 使用 nano 编辑器（适合新手）
nano .env

# 或使用 vim（适合进阶用户）
vim .env
```

**必须修改的配置项：**

```env
# JWT 密钥 - 必须修改！生成一个随机字符串
SECRET_KEY=$(openssl rand -hex 32)

# 数据库密码（本地开发可保持默认）
POSTGRES_PASSWORD=postgres123

# OpenAI API 密钥（AI 功能需要，没有可留空）
OPENAI_API_KEY=

# CORS 允许的域名
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

> **nano 编辑器操作提示：**
> - 编辑完成后按 `Ctrl + O` 保存
> - 按 `Enter` 确认文件名
> - 按 `Ctrl + X` 退出

### 3.3 生成安全的 SECRET_KEY

```bash
# 生成随机密钥并自动写入 .env 文件
SECRET=$(openssl rand -hex 32)
sed -i "s/your-secret-key-here-change-in-production/$SECRET/" .env

# 验证
grep SECRET_KEY .env
```

---

## 四、使用 Docker 部署（推荐方式）

### 4.1 启动项目

```bash
# 确保在项目根目录
pwd
# 应输出: ~/test_project/ai-test-platform

# 启动所有服务（首次会下载镜像，需要 5-15 分钟）
docker compose up -d
```

> **注意：** 如果你的 Docker 版本较旧，可能需要使用 `docker-compose`（带连字符）代替 `docker compose`。

### 4.2 查看服务状态

```bash
# 查看所有容器状态
docker compose ps
```

正常输出应包含以下容器：

| 服务 | 状态 | 端口 |
|------|------|------|
| postgres | Up (healthy) | 5432 |
| redis | Up (healthy) | 6379 |
| backend | Up | 8000 |
| frontend | Up | 5173 |
| playwright | Up | - |

### 4.3 查看日志

```bash
# 查看所有服务日志
docker compose logs -f

# 查看某个服务的日志
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres

# 按 Ctrl+C 退出日志查看
```

### 4.4 验证服务

```bash
# 测试后端 API
curl http://localhost:8000/health

# 应返回: {"status":"healthy"}

# 测试前端
curl -I http://localhost:5173
# 应返回 HTTP 200
```

### 4.5 访问项目

打开浏览器（如果是服务器，需要在同一局域网内的电脑访问）：

- **前端界面**：http://localhost:5173 （服务器替换为服务器 IP）
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

---

## 五、登录系统

1. 打开浏览器访问 http://localhost:5173
2. 进入登录页面
3. 输入默认管理员账号：
   - **用户名**：`admin`
   - **密码**：`admin123`
4. 点击 **登录**

> **重要提示**：首次登录后请立即修改默认密码！

---

## 六、基本使用流程

### 6.1 创建公司

1. 点击左侧菜单 **公司管理**
2. 点击 **新建公司**
3. 填写公司名称（如"测试科技有限公司"）和描述
4. 点击 **确定**

### 6.2 创建项目

1. 点击左侧菜单 **项目管理**
2. 点击 **新建项目**
3. 填写项目名称，选择刚创建的公司
4. 点击 **确定**

### 6.3 编写测试用例

1. 点击 **测试用例** 菜单
2. 点击 **新建用例**
3. 填写用例信息：
   - 用例名称：如"百度搜索测试"
   - 选择项目
   - 测试类型：黑盒测试
   - 优先级：中
4. 编写测试脚本：

```python
# 示例：百度搜索测试
import asyncio

async def test_baidu_search(page):
    await page.goto("https://www.baidu.com")
    await page.fill("#kw", "AI自动化测试")
    await page.click("#su")
    await page.wait_for_timeout(3000)
    title = await page.title()
    print(f"页面标题: {title}")
    assert "百度" in title
```

5. 点击 **确定** 保存

### 6.4 执行测试

1. 在测试用例列表中，点击 **执行** 按钮
2. 系统会自动启动 Playwright 浏览器执行测试
3. 可在 **测试执行** 页面查看实时状态

### 6.5 生成测试报告

1. 点击 **测试报告** 菜单
2. 选择项目
3. 点击 **生成报告**
4. 系统自动统计数据并生成可视化报告

### 6.6 管理用户

1. 点击 **用户管理** 菜单
2. 点击 **新增用户**
3. 填写用户名、邮箱、密码
4. 选择角色（普通用户/管理员）
5. 点击 **绑定项目**，限制用户只能看到指定项目

---

## 七、服务器部署（远程访问）

如果你是在云服务器上部署，需要额外配置：

### 7.1 开放防火墙端口

```bash
# Ubuntu 使用 ufw 防火墙
sudo ufw allow 5173/tcp    # 前端端口
sudo ufw allow 8000/tcp    # 后端端口
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable

# 查看防火墙状态
sudo ufw status
```

### 7.2 修改 CORS 配置

编辑 `.env` 文件，将 `CORS_ORIGINS` 改为你的服务器域名或 IP：

```env
CORS_ORIGINS=http://你的服务器IP:5173,http://你的域名.com
```

然后重启后端：

```bash
docker compose restart backend
```

### 7.3 配置 Nginx 反向代理（可选）

如果需要绑定域名，可以使用项目自带的 Nginx 配置：

```bash
# 编辑 nginx 配置
nano nginx/nginx.conf
```

修改 `server_name` 为你的域名：

```nginx
server {
    listen 80;
    server_name yourdomain.com;    # 改为你的域名
    # ...
}
```

然后启动 Nginx 容器：

```bash
docker compose -f docker-compose.prod.yml up -d nginx
```

### 7.4 配置 SSL/HTTPS（可选）

```bash
# 安装 certbot
sudo apt install -y certbot

# 获取证书（需要先停止 80 端口占用）
sudo certbot certonly --standalone -d yourdomain.com

# 复制证书到项目目录
sudo mkdir -p nginx/ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/
```

---

## 八、不使用 Docker 的手动部署

如果你不想使用 Docker，可以按以下步骤手动部署。

### 8.1 安装 PostgreSQL

```bash
# 安装 PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# 启动服务
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 创建数据库和用户
sudo -u postgres psql

# 在 psql 中执行：
CREATE DATABASE ai_test_db;
CREATE USER ai_test_user WITH PASSWORD 'postgres123';
GRANT ALL PRIVILEGES ON DATABASE ai_test_db TO ai_test_user;
ALTER DATABASE ai_test_db OWNER TO ai_test_user;
\q
```

### 8.2 安装 Redis

```bash
sudo apt install -y redis-server

# 启动 Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# 验证
redis-cli ping
# 应返回: PONG
```

### 8.3 部署后端

```bash
cd ~/test_project/ai-test-platform/backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
playwright install-deps chromium

# 配置环境变量
export DATABASE_URL="postgresql://ai_test_user:postgres123@localhost:5432/ai_test_db"
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="$(openssl rand -hex 32)"
export CORS_ORIGINS="http://localhost:5173"

# 启动后端
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> 后端启动后，访问 http://localhost:8000/docs 验证 API 是否正常。

### 8.4 部署前端

打开 **新终端** 窗口：

```bash
cd ~/test_project/ai-test-platform/frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev -- --host 0.0.0.0
```

> 前端启动后，访问 http://localhost:5173 验证页面是否正常。

---

## 九、后台持久运行（生产环境）

### 9.1 使用 Systemd 管理后端服务

```bash
# 创建服务文件
sudo nano /etc/systemd/system/ai-test-backend.service
```

写入以下内容：

```ini
[Unit]
Description=AI Test Platform Backend
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/home/你的用户名/test_project/ai-test-platform/backend
Environment="DATABASE_URL=postgresql://ai_test_user:postgres123@localhost:5432/ai_test_db"
Environment="REDIS_URL=redis://localhost:6379/0"
Environment="SECRET_KEY=你的密钥"
ExecStart=/home/你的用户名/test_project/ai-test-platform/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-test-backend
sudo systemctl start ai-test-backend

# 查看状态
sudo systemctl status ai-test-backend
```

### 9.2 Docker 方式设置开机自启

```bash
# 创建 systemd 服务
sudo nano /etc/systemd/system/ai-test-docker.service
```

写入：

```ini
[Unit]
Description=AI Test Platform Docker Services
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/你的用户名/test_project/ai-test-platform
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```

启用服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-test-docker
```

---

## 十、常见问题排查

### Q1: Docker 权限问题

```bash
# 方法1: 加入 docker 组
sudo usermod -aG docker $USER
newgrp docker

# 方法2: 每次加 sudo
sudo docker compose up -d
```

### Q2: 端口被占用

```bash
# 查看端口占用
sudo lsof -i :5173
sudo lsof -i :8000

# 杀掉进程
sudo kill -9 <PID>

# 或修改 docker-compose.yml 中的端口映射
```

### Q3: PostgreSQL 连接失败

```bash
# 检查 PostgreSQL 服务
sudo systemctl status postgresql

# 重启 PostgreSQL
sudo systemctl restart postgresql

# Docker 方式检查
docker compose logs postgres
docker compose restart postgres
```

### Q4: Playwright 浏览器安装失败

```bash
# Docker 容器内安装
docker compose exec backend playwright install chromium
docker compose exec backend playwright install-deps chromium

# 手动部署时安装系统依赖
sudo apt install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
  libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
  libxrandr2 libgbm1 libasound2
```

### Q5: 服务器外网无法访问

```bash
# 1. 检查防火墙
sudo ufw status
sudo ufw allow 5173/tcp
sudo ufw allow 8000/tcp

# 2. 检查云服务器安全组规则（阿里云/腾讯云/AWS等）
# 在云控制台的安全组中放行 5173 和 8000 端口

# 3. 确认 Docker 容器端口映射
docker compose ps
# 确保 0.0.0.0:5173->5173/tcp 和 0.0.0.0:8000->8000/tcp
```

### Q6: 内存不足导致容器崩溃

```bash
# 查看容器资源使用
docker stats

# 如果内存不足，可以增加服务器配置或限制容器资源
# 在 docker-compose.yml 中为每个服务添加资源限制：
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

---

## 十一、停止与清理

### 11.1 停止项目

```bash
# Docker 方式
docker compose stop        # 停止容器（保留数据）
docker compose down        # 停止并移除容器
docker compose down -v     # 停止并删除所有数据（谨慎！）
```

### 11.2 手动部署停止

```bash
# 停止后端
sudo systemctl stop ai-test-backend

# 或如果在终端运行的
# 在运行 uvicorn 的终端按 Ctrl+C

# 停止前端
# 在运行 npm 的终端按 Ctrl+C
```

### 11.3 清理 Docker 资源

```bash
# 清理未使用的镜像
docker image prune -f

# 清理所有未使用的资源
docker system prune -f
```

---

## 十二、常用命令速查

```bash
# ===== Docker 部署 =====
docker compose up -d              # 启动
docker compose down               # 停止
docker compose restart            # 重启
docker compose ps                 # 查看状态
docker compose logs -f            # 查看日志
docker compose logs -f backend    # 查看后端日志
docker compose exec backend bash  # 进入后端容器

# ===== 手动部署 =====
# 后端
cd backend && source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend && npm run dev -- --host 0.0.0.0

# ===== 系统服务 =====
sudo systemctl start ai-test-backend     # 启动
sudo systemctl stop ai-test-backend      # 停止
sudo systemctl status ai-test-backend    # 状态
sudo systemctl restart ai-test-backend   # 重启

# ===== Git =====
git pull origin test              # 更新代码
```

---

## 十三、更新项目

```bash
# 进入项目目录
cd ~/test_project/ai-test-platform

# 拉取最新代码
git pull origin test

# Docker 方式重建
docker compose down
docker compose up -d --build

# 手动部署方式重启
sudo systemctl restart ai-test-backend
```

---

> 祝你部署顺利！如有问题请查看日志或在 GitHub 提交 Issue。
