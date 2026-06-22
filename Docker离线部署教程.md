# AI自动化测试平台 - Docker 离线部署教程

> 适用于无法联网的服务器环境，通过在有网的机器上打包镜像，再传输到离线服务器部署。

---

## 总体流程

```
有网机器 ──打包镜像──> 镜像文件(.tar) ──传输──> 离线服务器 ──加载镜像──> 启动服务
```

---

## 一、在有网的机器上准备

### 1.1 安装 Docker（如果还没安装）

**Windows:**
访问 https://www.docker.com/products/docker-desktop/ 下载安装。

**Ubuntu:**
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo usermod -aG docker $USER
```

### 1.2 克隆项目代码

```bash
git clone -b test https://github.com/yikechenzi/test_project.git
cd test_project/ai-test-platform
```

### 1.3 构建所有 Docker 镜像

```bash
# 在项目根目录执行
docker compose build
```

等待构建完成（首次可能需要 10-30 分钟）。

### 1.4 查看已构建的镜像

```bash
docker images | grep ai-test
```

你应该看到类似：

```
ai-test-platform-backend     latest    xxxxx    2 hours ago    1.5GB
ai-test-platform-frontend    latest    xxxxx    2 hours ago    800MB
postgres                     15        xxxxx    ...
redis                        7-alpine  xxxxx    ...
```

### 1.5 导出镜像为 tar 文件

```bash
# 创建导出目录
mkdir -p offline-images

# 导出后端镜像
docker save ai-test-platform-backend:latest -o offline-images/backend.tar

# 导出前端镜像
docker save ai-test-platform-frontend:latest -o offline-images/frontend.tar

# 导出 PostgreSQL 镜像
docker save postgres:15 -o offline-images/postgres.tar

# 导出 Redis 镜像
docker save redis:7-alpine -o offline-images/redis.tar

# 导出 Nginx 镜像（如果使用生产部署）
docker save nginx:alpine -o offline-images/nginx.tar
```

### 1.6 确认镜像大小

```bash
ls -lh offline-images/
```

预计总大小约 2-4 GB。

---

## 二、打包传输文件

### 2.1 准备传输包

```bash
# 创建离线部署包目录
mkdir -p offline-package

# 复制项目文件（排除 node_modules 等）
cp -r backend frontend nginx docker-compose.yml docker-compose.prod.yml .env.example start.bat stop.bat offline-package/

# 复制镜像文件
cp -r offline-images offline-package/

# 创建部署脚本
cat > offline-package/deploy.sh << 'EOF'
#!/bin/bash
echo "=== AI自动化测试平台 - 离线部署脚本 ==="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 未检测到 Docker，请先安装 Docker"
    exit 1
fi

echo "✅ Docker 已安装: $(docker --version)"
echo ""

# 加载镜像
echo ">>> 正在加载 Docker 镜像..."
for img in offline-images/*.tar; do
    echo "  加载: $img"
    docker load -i "$img"
done
echo "✅ 所有镜像加载完成"
echo ""

# 复制环境配置
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ 已创建 .env 文件（请根据需要修改）"
fi

# 启动服务
echo ""
echo ">>> 是否立即启动服务？(y/n)"
read answer
if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    docker compose up -d
    echo ""
    echo "✅ 服务已启动！"
    echo "  前端: http://localhost:5173"
    echo "  后端: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
else
    echo "跳过启动，你可以稍后手动执行: docker compose up -d"
fi
EOF

chmod +x offline-package/deploy.sh

# 创建 Windows 部署脚本
cat > offline-package/deploy.bat << 'EOF'
@echo off
echo === AI自动化测试平台 - 离线部署脚本 ===
echo.

:: 检查 Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo 未检测到 Docker，请先安装 Docker Desktop
    pause
    exit /b 1
)

echo 正在加载 Docker 镜像...
for %%f in (offline-images\*.tar) do (
    echo   加载: %%f
    docker load -i "%%f"
)
echo 所有镜像加载完成
echo.

:: 复制环境配置
if not exist .env (
    copy .env.example .env
    echo 已创建 .env 文件
)

:: 启动服务
set /p answer="是否立即启动服务？(y/n): "
if /i "%answer%"=="y" (
    docker compose up -d
    echo.
    echo 服务已启动！
    echo   前端: http://localhost:5173
    echo   后端: http://localhost:8000
)
pause
EOF
```

### 2.2 压缩传输包

```bash
# Linux/Mac
tar -czf ai-test-offline.tar.gz offline-package/

# Windows PowerShell
# 使用 7-Zip 或 WinRAR 压缩 offline-package 文件夹
```

### 2.3 传输到离线服务器

将 `ai-test-offline.tar.gz` 文件通过以下方式传输到离线服务器：

- **U盘/移动硬盘**：直接复制
- **局域网传输**：
  ```bash
  scp ai-test-offline.tar.gz user@离线服务器IP:/home/user/
  ```
- **Windows 共享文件夹**

---

## 三、在离线服务器上部署

### 3.1 安装 Docker（离线安装）

如果离线服务器没有安装 Docker，需要离线安装：

**Ubuntu 离线安装 Docker：**

在有网的机器上下载 Docker 安装包：

```bash
# 下载 Docker 离线包（访问 https://download.docker.com/linux/static/stable/）
wget https://download.docker.com/linux/static/stable/x86_64/docker-24.0.7.tgz
```

将 `docker-24.0.7.tgz` 拷贝到离线服务器后：

```bash
# 解压
tar xzf docker-24.0.7.tgz

# 移动到系统目录
sudo mv docker/* /usr/bin/

# 创建 Docker 服务
sudo cat > /etc/systemd/system/docker.service << 'EOF'
[Unit]
Description=Docker Application Container Engine
After=network-online.target firewalld.service
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

# 启动 Docker
sudo systemctl daemon-reload
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker --version
```

### 3.2 解压部署包

```bash
# 解压
tar -xzf ai-test-offline.tar.gz
cd offline-package

# 查看内容
ls -la
```

### 3.3 执行部署脚本

```bash
# 一键部署
./deploy.sh
```

### 3.4 或手动执行

```bash
# 1. 加载所有镜像
for img in offline-images/*.tar; do
    docker load -i "$img"
done

# 2. 确认镜像已加载
docker images

# 3. 复制环境配置
cp .env.example .env

# 4. 编辑配置（可选）
nano .env

# 5. 启动服务
docker compose up -d
```

---

## 四、一键部署脚本（完整版）

以下是一个完整的一键部署脚本，保存为 `offline-deploy.sh`：

```bash
#!/bin/bash
set -e

echo "╔════════════════════════════════════════════╗"
echo "║   AI自动化测试平台 - 离线部署工具          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# 检查是否 root
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  建议使用 root 或 sudo 运行此脚本"
    echo "   当前用户需要有 docker 组权限"
fi

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    echo "   请先手动安装 Docker 或使用离线安装包"
    exit 1
fi

echo "✅ Docker: $(docker --version)"

# 检查 docker compose
if docker compose version &> /dev/null; then
    COMPOSE="docker compose"
    echo "✅ Docker Compose: $(docker compose version)"
elif command -v docker-compose &> /dev/null; then
    COMPOSE="docker-compose"
    echo "✅ docker-compose: $(docker-compose --version)"
else
    echo "❌ Docker Compose 未安装"
    exit 1
fi

echo ""
echo ">>> 步骤 1/4: 加载 Docker 镜像"
echo "─────────────────────────────────"

IMAGE_DIR="./offline-images"
if [ ! -d "$IMAGE_DIR" ]; then
    echo "❌ 未找到 offline-images 目录"
    echo "   请确保镜像文件在当前目录的 offline-images 文件夹中"
    exit 1
fi

for img in "$IMAGE_DIR"/*.tar; do
    if [ -f "$img" ]; then
        size=$(du -h "$img" | cut -f1)
        echo "  📦 加载: $(basename $img) ($size)"
        docker load -i "$img" 2>&1 | grep -v "^$" | sed 's/^/     /'
    fi
done

echo "  ✅ 镜像加载完成"
echo ""
docker images --format "  {{.Repository}}:{{.Tag}} ({{.Size}})" | grep -E "ai-test|postgres|redis|nginx"
echo ""

echo ">>> 步骤 2/4: 配置环境"
echo "─────────────────────────────────"

if [ ! -f .env ]; then
    cp .env.example .env
    echo "  ✅ 已创建 .env 文件"
    
    # 自动生成 SECRET_KEY
    SECRET=$(openssl rand -hex 32 2>/dev/null || head -c 64 /dev/urandom | xxd -p | head -1)
    sed -i "s/your-secret-key-here-change-in-production/$SECRET/" .env 2>/dev/null || true
    echo "  ✅ 已自动生成 SECRET_KEY"
else
    echo "  ⚠️  .env 文件已存在，跳过创建"
fi

echo ""
echo ">>> 步骤 3/4: 启动服务"
echo "─────────────────────────────────"

$COMPOSE up -d

echo ""
echo "  等待服务启动..."
sleep 5

echo ""
echo ">>> 步骤 4/4: 验证服务"
echo "─────────────────────────────────"

# 检查容器状态
echo "  容器状态:"
$COMPOSE ps --format "  {{.Name}}\t{{.Status}}" 2>/dev/null || $COMPOSE ps

echo ""

# 检查端口
for port in 5173 8000; do
    if ss -tlnp 2>/dev/null | grep -q ":$port " || netstat -tlnp 2>/dev/null | grep -q ":$port "; then
        echo "  ✅ 端口 $port 已监听"
    else
        echo "  ⚠️  端口 $port 未监听（服务可能还在启动中）"
    fi
done

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║   🎉 部署完成！                            ║"
echo "╠════════════════════════════════════════════╣"
echo "║                                            ║"
echo "║   前端界面: http://localhost:5173           ║"
echo "║   后端 API: http://localhost:8000           ║"
echo "║   API 文档: http://localhost:8000/docs      ║"
echo "║                                            ║"
echo "║   默认账号: admin                          ║"
echo "║   默认密码: admin123                       ║"
echo "║                                            ║"
echo "║   常用命令:                                 ║"
echo "║     查看日志: docker compose logs -f        ║"
echo "║     停止服务: docker compose down           ║"
echo "║     重启服务: docker compose restart        ║"
echo "║                                            ║"
echo "╚════════════════════════════════════════════╝"
```

---

## 五、常见问题

### Q1: docker load 报错 "no space left on device"

磁盘空间不足，清理磁盘或扩展分区：

```bash
# 查看磁盘使用
df -h

# 清理 Docker 无用资源
docker system prune -af

# 清理旧镜像
docker image prune -af
```

### Q2: 加载镜像很慢

```bash
# 增加 Docker 存储驱动配置
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json << 'EOF'
{
  "storage-driver": "overlay2"
}
EOF

sudo systemctl restart docker
```

### Q3: 离线服务器缺少依赖库

```bash
# 在有网机器上下载依赖并打包
sudo apt download $(apt-cache depends docker.io | grep Depends | sed 's/.*ends: //' | tr '\n' ' ')
tar -czf docker-deps.tar.gz *.deb

# 在离线服务器上安装
tar -xzf docker-deps.tar.gz
sudo dpkg -i *.deb
```

### Q4: 镜像标签不对

```bash
# 查看镜像实际标签
docker images

# 重新打标签（如果需要）
docker tag 旧镜像名:旧标签 新镜像名:新标签
```

---

## 六、部署文件清单

完整的离线部署包应包含：

```
offline-package/
├── offline-images/          # Docker 镜像文件
│   ├── backend.tar          # 后端镜像 (~1.5GB)
│   ├── frontend.tar         # 前端镜像 (~800MB)
│   ├── postgres.tar         # PostgreSQL (~380MB)
│   ├── redis.tar            # Redis (~30MB)
│   └── nginx.tar            # Nginx (~40MB) 可选
├── backend/                 # 后端代码
├── frontend/                # 前端代码
├── nginx/                   # Nginx 配置
├── docker-compose.yml       # Docker 编排文件
├── docker-compose.prod.yml  # 生产编排文件
├── .env.example             # 环境变量示例
├── deploy.sh                # Linux 部署脚本
├── deploy.bat               # Windows 部署脚本
└── README.md                # 说明文档
```

---

## 七、快速命令参考

```bash
# ===== 有网机器上执行 =====
# 构建镜像
docker compose build

# 导出镜像
docker save ai-test-platform-backend:latest -o backend.tar
docker save ai-test-platform-frontend:latest -o frontend.tar
docker save postgres:15 -o postgres.tar
docker save redis:7-alpine -o redis.tar

# 打包
tar -czf ai-test-offline.tar.gz offline-package/

# ===== 离线服务器上执行 =====
# 解压
tar -xzf ai-test-offline.tar.gz
cd offline-package

# 加载镜像
docker load -i offline-images/backend.tar
docker load -i offline-images/frontend.tar
docker load -i offline-images/postgres.tar
docker load -i offline-images/redis.tar

# 配置并启动
cp .env.example .env
nano .env
docker compose up -d
```

---

> 如有问题，请检查各容器日志：`docker compose logs -f 服务名`
