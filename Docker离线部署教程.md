# AI自动化测试平台 - Docker 离线部署教程

> 适用于无法联网的服务器环境，通过在有网的机器上准备基础镜像，再传输到离线服务器部署。

---

## 总体流程

```
有网机器 ──拉取/打包镜像──> 镜像文件(.tar) ──传输──> 离线服务器 ──加载镜像──> 构建并启动服务
```

---

## 一、在有网的机器上准备基础镜像

### 1.1 拉取所有基础镜像

首先，在有网络的环境中拉取所有需要的基础镜像：

```bash
# PostgreSQL 15 数据库
docker pull postgres:15-alpine

# Redis 7 缓存
docker pull redis:7-alpine

# Python 3.11 后端运行环境
docker pull python:3.11-slim

# Node.js 18 前端构建环境
docker pull node:18-alpine

# Playwright 自动化测试环境
docker pull mcr.microsoft.com/playwright/python:v1.40.0-jammy
```

### 1.2 验证镜像已拉取

```bash
docker images | grep -E "postgres|redis|python|node|playwright"
```

你应该看到类似输出：

```
postgres                              15-alpine    xxxxx   200MB
redis                                 7-alpine     xxxxx   40MB
python                                3.11-slim    xxxxx   150MB
node                                  18-alpine    xxxxx   180MB
mcr.microsoft.com/playwright/python   v1.40.0-jammy xxxxx  2.1GB
```

### 1.3 导出镜像为 tar 文件

将拉取到的基础镜像分别打包：

```bash
# 1. PostgreSQL 数据库镜像
docker save -o postgres_15-alpine.tar postgres:15-alpine

# 2. Redis 缓存镜像
docker save -o redis_7-alpine.tar redis:7-alpine

# 3. Python 后端运行环境
docker save -o python_3.11-slim.tar python:3.11-slim

# 4. Node.js 前端构建环境
docker save -o node_18-alpine.tar node:18-alpine

# 5. Playwright 自动化测试环境
docker save -o playwright_python_v1.40.0-jammy.tar mcr.microsoft.com/playwright/python:v1.40.0-jammy
```

### 1.4 确认镜像文件大小

```bash
ls -lh *.tar
```

预计文件大小：

| 镜像文件 | 大小 | 用途 |
|---------|------|------|
| postgres_15-alpine.tar | ~200MB | PostgreSQL 数据库 |
| redis_7-alpine.tar | ~40MB | Redis 缓存 |
| python_3.11-slim.tar | ~150MB | Python 后端运行环境 |
| node_18-alpine.tar | ~180MB | Node.js 前端构建环境 |
| playwright_python_v1.40.0-jammy.tar | ~2.1GB | Playwright 测试环境 |
| **总计** | **~2.7GB** | |

---

## 二、准备项目代码

### 2.1 克隆项目代码

```bash
git clone -b test https://github.com/yikechenzi/test_project.git
cd test_project/ai-test-platform
```

### 2.2 查看项目结构

```bash
ls -la
```

你应该看到：

```
ai-test-platform/
├── backend/              # 后端代码
├── frontend/             # 前端代码
├── nginx/                # Nginx 配置
├── docker-compose.yml    # Docker 编排文件
├── docker-compose.prod.yml
├── .env.example          # 环境变量示例
├── Dockerfile            # 后端镜像构建文件
├── frontend/Dockerfile   # 前端镜像构建文件
└── README.md
```

---

## 三、打包传输文件

### 3.1 创建离线部署包

```bash
# 创建离线部署目录
mkdir -p ai-test-offline

# 复制项目代码（排除不需要的文件）
cp -r backend frontend nginx docker-compose.yml docker-compose.prod.yml .env.example start.bat stop.bat ai-test-offline/

# 复制基础镜像文件
mkdir -p ai-test-offline/docker-images
cp postgres_15-alpine.tar redis_7-alpine.tar python_3.11-slim.tar node_18-alpine.tar playwright_python_v1.40.0-jammy.tar ai-test-offline/docker-images/

# 创建部署脚本（见下方）
```

### 3.2 创建一键部署脚本

创建 `ai-test-offline/deploy.sh`：

```bash
#!/bin/bash
echo "============================================"
echo "  AI自动化测试平台 - 离线部署工具"
echo "============================================"
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 未检测到 Docker，请先安装 Docker"
    exit 1
fi

echo "✅ Docker 版本: $(docker --version)"
echo ""

# 加载基础镜像
echo ">>> 步骤 1/4: 加载 Docker 基础镜像..."
for img in docker-images/*.tar; do
    if [ -f "$img" ]; then
        size=$(du -h "$img" | cut -f1)
        echo "  📦 加载: $(basename $img) ($size)"
        docker load -i "$img"
    fi
done
echo "  ✅ 基础镜像加载完成"
echo ""

# 复制环境配置
echo ">>> 步骤 2/4: 配置环境变量..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ✅ 已创建 .env 文件"
    
    # 生成随机 SECRET_KEY
    if command -v openssl &> /dev/null; then
        SECRET=$(openssl rand -hex 32)
        sed -i "s/your-secret-key-here-change-in-production/$SECRET/" .env 2>/dev/null || true
        echo "  ✅ 已自动生成 SECRET_KEY"
    fi
else
    echo "  ⚠️  .env 文件已存在，跳过创建"
fi

# 构建应用镜像
echo ""
echo ">>> 步骤 3/4: 构建应用镜像（使用基础镜像）..."
echo "  这可能需要 5-15 分钟，请耐心等待..."
docker compose build
echo "  ✅ 应用镜像构建完成"

# 启动服务
echo ""
echo ">>> 步骤 4/4: 启动服务..."
docker compose up -d

echo ""
echo "  等待服务启动..."
sleep 10

echo ""
echo "============================================"
echo "  🎉 部署完成！"
echo "============================================"
echo ""
echo "  前端界面: http://localhost:5173"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo ""
echo "  默认管理员账号:"
echo "    用户名: admin"
echo "    密码: admin123"
echo ""
echo "  常用命令:"
echo "    查看状态: docker compose ps"
echo "    查看日志: docker compose logs -f"
echo "    停止服务: docker compose down"
echo "    重启服务: docker compose restart"
echo ""
```

### 3.3 压缩传输包

```bash
# 压缩整个离线部署包
tar -czf ai-test-offline.tar.gz ai-test-offline/
```

预计压缩后大小约 **1-1.5GB**。

### 3.4 传输到离线服务器

通过以下方式将 `ai-test-offline.tar.gz` 传输到离线服务器：

- **U盘/移动硬盘**：直接复制文件
- **局域网传输**：
  ```bash
  scp ai-test-offline.tar.gz user@离线服务器IP:/home/user/
  ```
- **内网共享文件夹**

---

## 四、在离线服务器上部署

### 4.1 安装 Docker（如果还没有安装）

如果离线服务器没有 Docker，需要先在有网机器下载离线安装包：

**Ubuntu 离线安装 Docker：**

```bash
# 在有网机器下载
wget https://download.docker.com/linux/static/stable/x86_64/docker-24.0.7.tgz

# 拷贝到离线服务器后执行
tar xzf docker-24.0.7.tgz
sudo cp docker/* /usr/bin/

# 创建 systemd 服务
sudo cat > /etc/systemd/system/docker.service << 'EOF'
[Unit]
Description=Docker Application Container Engine
After=network-online.target

[Service]
Type=notify
ExecStart=/usr/bin/dockerd
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 启动 Docker
sudo systemctl daemon-reload
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker --version
```

### 4.2 解压离线部署包

```bash
# 解压
tar -xzf ai-test-offline.tar.gz
cd ai-test-offline

# 查看内容
ls -la
```

### 4.3 导入（加载）Docker 镜像

这是离线部署的关键步骤。在有网机器上打包的镜像 tar 文件，需要在离线服务器上导入到 Docker 中。

**方法1: 逐个加载镜像**

```bash
# 进入离线部署包目录
cd ai-test-offline

# 1. 加载 PostgreSQL 数据库镜像
docker load -i docker-images/postgres_15-alpine.tar

# 2. 加载 Redis 缓存镜像
docker load -i docker-images/redis_7-alpine.tar

# 3. 加载 Python 后端运行环境
docker load -i docker-images/python_3.11-slim.tar

# 4. 加载 Node.js 前端构建环境
docker load -i docker-images/node_18-alpine.tar

# 5. 加载 Playwright 自动化测试环境
docker load -i docker-images/playwright_python_v1.40.0-jammy.tar
```

**方法2: 批量加载所有镜像（推荐）**

```bash
# 使用循环一次性加载所有镜像
cd ai-test-offline
for img in docker-images/*.tar; do
    echo "正在加载: $img"
    docker load -i "$img"
done
```

**方法3: 使用 shell 单行命令**

```bash
cd ai-test-offline && ls docker-images/*.tar | xargs -I {} docker load -i {}
```

**验证镜像是否加载成功：**

```bash
# 查看所有 Docker 镜像
docker images

# 应该能看到以下镜像
docker images | grep -E "postgres|redis|python|node|playwright"
```

正常输出示例：

```
REPOSITORY                                TAG           IMAGE ID       CREATED        SIZE
postgres                                  15-alpine     xxxxx          2 weeks ago    200MB
redis                                     7-alpine      xxxxx          2 weeks ago    40MB
python                                    3.11-slim     xxxxx          2 weeks ago    150MB
node                                      18-alpine     xxxxx          2 weeks ago    180MB
mcr.microsoft.com/playwright/python       v1.40.0-jammy xxxxx          3 weeks ago    2.1GB
```

> **注意**：
> - `docker load` 命令会恢复镜像及其标签（tag）
> - 加载过程可能需要几分钟，特别是较大的镜像（如 playwright 2.1GB）
> - 如果加载失败，检查磁盘空间：`df -h`

### 4.4 执行一键部署

```bash
# 添加执行权限
chmod +x deploy.sh

# 执行部署
./deploy.sh
```

### 4.5 或手动逐步部署

```bash
# 1. 加载基础镜像（详见 4.3 节）
cd ai-test-offline
for img in docker-images/*.tar; do
    docker load -i "$img"
done

# 2. 验证镜像
docker images

# 3. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置，修改 SECRET_KEY

# 4. 构建应用镜像（使用已加载的基础镜像）
docker compose build

# 5. 启动服务
docker compose up -d

# 6. 查看服务状态
docker compose ps
```

---

## 五、验证部署

### 5.1 检查容器状态

```bash
docker compose ps
```

正常应该看到以下容器都是 `Up` 状态：

| 服务 | 说明 | 端口 |
|------|------|------|
| postgres | PostgreSQL 数据库 | 5432 |
| redis | Redis 缓存 | 6379 |
| backend | 后端 API | 8000 |
| frontend | 前端界面 | 5173 |
| playwright | 自动化测试环境 | - |

### 5.2 检查服务端口

```bash
# 检查端口是否监听
ss -tlnp | grep -E "5173|8000"
```

### 5.3 测试后端 API

```bash
curl http://localhost:8000/health
```

应该返回：

```json
{"status":"healthy"}
```

### 5.4 访问前端

打开浏览器访问：

- **前端界面**：http://localhost:5173
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs

---

## 六、登录和使用

### 6.1 登录系统

1. 打开浏览器访问 http://localhost:5173
2. 输入默认管理员账号：
   - **用户名**：`admin`
   - **密码**：`admin123`
3. 点击 **登录**

> ⚠️ **安全提示**：首次登录后请立即修改默认密码！

### 6.2 基本使用流程

```
1. 公司管理 → 创建公司
2. 项目管理 → 创建项目
3. 测试用例 → 编写测试脚本
4. 测试执行 → 执行自动化测试
5. 测试报告 → 查看测试报告
6. 用户管理 → 添加用户并绑定项目
```

---

## 七、离线环境 Docker 安装完整指南

### 7.1 Ubuntu 20.04/22.04/24.04

**在有网机器准备：**

```bash
# 下载 Docker 静态二进制包
wget https://download.docker.com/linux/static/stable/x86_64/docker-24.0.7.tgz

# 下载 Docker Compose 插件
wget https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-linux-x86_64 -O docker-compose
```

**在离线服务器上安装：**

```bash
# 1. 安装 Docker
tar xzf docker-24.0.7.tgz
sudo cp docker/* /usr/bin/

# 2. 安装 Docker Compose
chmod +x docker-compose
sudo cp docker-compose /usr/local/bin/

# 3. 创建 Docker 服务
sudo tee /etc/systemd/system/docker.service > /dev/null << 'EOF'
[Unit]
Description=Docker Application Container Engine
After=network-online.target firewalld.service containerd.service
Wants=network-online.target

[Service]
Type=notify
ExecStart=/usr/bin/dockerd
ExecReload=/bin/kill -s HUP $MAINPID
LimitNOFILE=infinity
LimitNPROC=infinity
TimeoutStartSec=0
Delegate=yes
KillMode=process
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# 4. 启动 Docker
sudo systemctl daemon-reload
sudo systemctl start docker
sudo systemctl enable docker

# 5. 配置用户权限
sudo usermod -aG docker $USER
newgrp docker

# 6. 验证
docker --version
docker compose version
```

### 7.2 CentOS/RHEL 7/8/9

**在有网机器准备：**

```bash
# 下载 RPM 包
yumdownloader --resolve docker-ce docker-ce-cli containerd.io

# 或使用离线包
wget https://download.docker.com/linux/centos/9/x86_64/stable/Packages/docker-ce-24.0.7-1.el9.x86_64.rpm
wget https://download.docker.com/linux/centos/9/x86_64/stable/Packages/docker-ce-cli-24.0.7-1.el9.x86_64.rpm
wget https://download.docker.com/linux/centos/9/x86_64/stable/Packages/containerd.io-1.6.25-3.1.el9.x86_64.rpm
```

**在离线服务器上安装：**

```bash
# 安装 RPM 包
sudo rpm -ivh docker-ce-*.rpm docker-ce-cli-*.rpm containerd.io-*.rpm

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

---

## 八、常见问题

### Q1: docker load 报错 "no space left on device"

磁盘空间不足：

```bash
# 查看磁盘使用
df -h

# 清理 Docker 无用资源
docker system prune -af

# 清理后重新加载
docker load -i docker-images/postgres_15-alpine.tar
```

### Q2: 镜像加载后 docker compose build 失败

检查基础镜像是否正确加载：

```bash
# 查看所有镜像
docker images

# 确认以下镜像存在
docker images | grep postgres
docker images | grep redis
docker images | grep python
docker images | grep node
docker images | grep playwright
```

如果标签不对，重新打标签：

```bash
docker tag postgres:15-alpine postgres:15-alpine
```

### Q3: docker compose 命令找不到

Docker Compose 未安装或路径不对：

```bash
# 检查是否安装
which docker-compose
which docker

# 使用 docker-compose（旧版本）
docker-compose up -d

# 或使用 docker compose（新版本）
docker compose up -d
```

### Q4: Playwright 容器启动失败

确保已加载 Playwright 基础镜像：

```bash
# 检查镜像
docker images | grep playwright

# 如果不存在，重新加载
docker load -i docker-images/playwright_python_v1.40.0-jammy.tar
```

### Q5: 端口冲突

```bash
# 查看端口占用
sudo lsof -i :5173
sudo lsof -i :8000

# 杀掉占用进程
sudo kill -9 <PID>

# 或修改 docker-compose.yml 中的端口映射
```

### Q6: 服务器外网无法访问

```bash
# 1. 检查防火墙
sudo ufw status
sudo ufw allow 5173/tcp
sudo ufw allow 8000/tcp

# 2. 云服务器需要在控制台安全组中开放端口

# 3. 确认 Docker 端口映射
docker compose ps
```

---

## 九、停止和清理

### 9.1 停止服务

```bash
# 停止所有容器（保留数据）
docker compose stop

# 停止并移除容器（保留数据卷）
docker compose down

# 停止并删除所有数据（谨慎！）
docker compose down -v
```

### 9.2 清理 Docker 资源

```bash
# 清理未使用的镜像
docker image prune -f

# 清理所有未使用的资源
docker system prune -af
```

---

## 十、常用命令速查

```bash
# ===== 有网机器上执行 =====
# 拉取基础镜像
docker pull postgres:15-alpine
docker pull redis:7-alpine
docker pull python:3.11-slim
docker pull node:18-alpine
docker pull mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 导出镜像
docker save -o postgres_15-alpine.tar postgres:15-alpine
docker save -o redis_7-alpine.tar redis:7-alpine
docker save -o python_3.11-slim.tar python:3.11-slim
docker save -o node_18-alpine.tar node:18-alpine
docker save -o playwright_python_v1.40.0-jammy.tar mcr.microsoft.com/playwright/python:v1.40.0-jammy

# 打包
tar -czf ai-test-offline.tar.gz ai-test-offline/

# ===== 离线服务器上执行 =====
# 加载镜像
docker load -i docker-images/postgres_15-alpine.tar
docker load -i docker-images/redis_7-alpine.tar
docker load -i docker-images/python_3.11-slim.tar
docker load -i docker-images/node_18-alpine.tar
docker load -i docker-images/playwright_python_v1.40.0-jammy.tar

# 构建应用镜像
docker compose build

# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f backend
docker compose logs -f frontend
```

---

## 十一、部署文件清单

完整的离线部署包应包含：

```
ai-test-offline/
├── docker-images/              # 基础镜像文件
│   ├── postgres_15-alpine.tar         (~200MB)
│   ├── redis_7-alpine.tar             (~40MB)
│   ├── python_3.11-slim.tar           (~150MB)
│   ├── node_18-alpine.tar             (~180MB)
│   └── playwright_python_v1.40.0-jammy.tar  (~2.1GB)
├── backend/                    # 后端代码
├── frontend/                   # 前端代码
├── nginx/                      # Nginx 配置
├── docker-compose.yml          # Docker 编排文件
├── docker-compose.prod.yml     # 生产编排文件
├── .env.example                # 环境变量示例
├── deploy.sh                   # Linux 一键部署脚本
├── deploy.bat                  # Windows 一键部署脚本
└── README.md                   # 说明文档
```

---

> 部署完成后，如有问题请查看日志：`docker compose logs -f 服务名`
