# CPA Assistant 部署文档 & 问题记录

本文档记录了将 CPA Assistant 项目部署到 Alibaba Cloud ECS (Ubuntu 22.04) 上的完整流程，以及过程中遇到的问题和解决方案。

## 1. 环境准备

### 1.1 系统要求
- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.12+
- **Node.js**: 18+ (推荐 LTS)
- **Database**: SQLite (默认) 或 PostgreSQL
- **Web Server**: Nginx

### 1.2 用户权限管理
为了安全起见，不建议使用 `root` 用户运行应用。
```bash
# 创建专用用户
sudo useradd -m -s /bin/bash cpa-user
sudo passwd cpa-user

# 赋予 sudo 权限 (可选，视管理需求而定)
sudo usermod -aG sudo cpa-user
```

**遇到的问题 (Permission Denied)**:
- **现象**: `npm install` 报错 `EACCES: permission denied`。
- **原因**: `cpa-user` 的 home 目录未正确创建或权限归属 root。
- **解决**:
  ```bash
  # 确保 home 目录存在且归属正确
  sudo mkdir -p /home/cpa-user
  sudo chown -R cpa-user:cpa-user /home/cpa-user
  ```

## 2. 后端部署 (FastAPI)

### 2.1 依赖安装
```bash
# 安装 Python 3.12 及开发工具
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev python3.12-distutils -y

# 解决 pip 缺失问题
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.12
```

**遇到的问题 (ModuleNotFoundError: No module named 'distutils')**:
- **原因**: Python 3.12 移除了 `distutils`，但在某些环境中 `pip` 或 `virtualenv` 仍依赖它。
- **解决**: 显式安装 `python3.12-distutils`。

### 2.2 代码与虚拟环境
```bash
# 目录结构
sudo mkdir -p /opt/cpa-assistant/backend
sudo chown -R cpa-user:cpa-user /opt/cpa-assistant

# 切换用户操作
su - cpa-user
cd /opt/cpa-assistant/backend

# 创建虚拟环境
python3.12 -m venv venv
source venv/bin/activate

# 安装项目依赖
pip install -r requirements.txt
```

### 2.3 环境变量 (.env)
在 `/opt/cpa-assistant/backend/.env` 创建生产配置：
```ini
DEBUG=False
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secure-production-key
API_KEY=your-api-key
# 数据库路径确保 cpa-user 可写
DATABASE_URL=sqlite:///./infrastructure/data/cpa_assistant.db
```

### 2.4 Systemd 服务配置
文件: `/etc/systemd/system/cpa-assistant.service`
```ini
[Unit]
Description=CPA Assistant FastAPI Application
After=network.target

[Service]
Type=simple
User=cpa-user
Group=cpa-user
WorkingDirectory=/opt/cpa-assistant/backend
Environment=PATH=/opt/cpa-assistant/backend/venv/bin
ExecStart=/opt/cpa-assistant/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**遇到的问题 (SQLAlchemy AttributeError)**:
- **现象**: `AttributeError: 'Engine' object has no attribute 'table_names'`。
- **原因**: 旧版 SQLAlchemy 代码在新版库中不兼容。
- **解决**: 使用 `inspect(engine).get_table_names()` 替代。

## 3. 前端部署 (Vue.js)

### 3.1 代码准备 (重要)
**注意**：请勿将本地的 `node_modules` 目录上传到服务器。
- **原因 1**：文件数量巨大，传输极慢。
- **原因 2**：本地 (Windows) 的依赖包可能包含与服务器 (Linux) 不兼容的二进制文件。
- **操作**：建议在上传前删除本地 `node_modules`，或在 `.gitignore` 中排除。如果在服务器上构建报错，请先尝试删除该目录：
  ```bash
  rm -rf node_modules package-lock.json
  ```

### 3.2 代码修改
在构建前，必须修改前端 API 请求地址，使其适应生产环境的反向代理。

1. **`src/utils/api.js`**:
   ```javascript
   // 修改前: const API_BASE_URL = 'http://127.0.0.1:8000/api/v1'
   // 修改后 (使用相对路径):
   const API_BASE_URL = '/api/v1'
   ```

2. **`src/main.js`**:
   ```javascript
   // 修改前: axios.defaults.baseURL = 'http://127.0.0.1:8000/api/v1';
   // 修改后:
   axios.defaults.baseURL = '/api/v1';
   ```

3. **`vite.config.js`** (开发环境代理，生产环境不生效但建议保留):
   ```javascript
   proxy: {
     '/api': { target: 'http://127.0.0.1:8000', ... },
     '/auth': { target: 'http://127.0.0.1:8000/api/v1', ... }
   }
   ```

### 3.2 构建
```bash
cd /opt/cpa-assistant/cpa-frontend
npm install
# 补充缺失依赖
npm install element-plus @element-plus/icons-vue
npm run build
```

**遇到的问题 (Build Error)**:
- **现象**: `Rollup failed to resolve import "element-plus"`。
- **原因**: `package.json` 中缺少 `element-plus` 依赖。
- **解决**: 手动安装 `npm install element-plus`。

### 3.3 部署静态文件
```bash
sudo mkdir -p /var/www/auditoreyes
# 将 dist 目录内容复制过去
sudo cp -r dist/* /var/www/auditoreyes/
sudo chown -R www-data:www-data /var/www/auditoreyes
```

## 4. Nginx 配置 (关键)

域名: `auditoreyes.com`

### 4.1 配置文件
文件: `/etc/nginx/sites-available/auditoreyes.com`

```nginx
server {
    listen 80;
    server_name auditoreyes.com www.auditoreyes.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name auditoreyes.com www.auditoreyes.com;

    ssl_certificate /etc/letsencrypt/live/auditoreyes.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/auditoreyes.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # 1. 登录接口特殊处理 (解决 405 Method Not Allowed)
    location = /auth/login {
        proxy_pass http://127.0.0.1:8000/api/v1/auth/login;
        proxy_method POST;  # 强制确保 POST 方法
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 2. 通用 API 代理
    location ^~ /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 3. 前端静态文件
    location / {
        root /var/www/auditoreyes;
        try_files $uri $uri/ /index.html;
        index index.html;
    }
}
```

### 4.2 遇到的 Nginx/网络问题

1. **DNS 解析错误**:
   - **现象**: `ping auditoreyes.com` 返回错误的 IP 地址。
   - **原因**: 域名注册商 (GoDaddy) 的 Nameserver 未指向阿里云，或者阿里云解析未生效。
   - **解决**: 使用 `dig +trace` 排查，确认权威 DNS 服务器，并在正确的地方 (GoDaddy) 修改 Nameserver 或添加 A 记录。

2. **405 Method Not Allowed (Login)**:
   - **现象**: 登录时 POST 请求被 Nginx 返回 405。
   - **原因**: Nginx 对静态文件默认不支持 POST，或者重定向配置错误导致 POST 变成了 GET。
   - **解决**: 
     - 确保 `/auth/login` 精确匹配并正确 `proxy_pass` 到后端。
     - 检查前端代码是否请求了错误的 URL (如 HTTP 而非 HTTPS，导致 301 重定向丢失 POST body)。
     - 配置 `location = /auth/login` 块。

3. **依赖安装失败 / 权限错误**:
   - **现象**: `npm install` 报错 `EACCES: permission denied` 或 `Rollup failed`。
   - **原因**: 之前使用 `root` 安装过导致权限归属错误，或上传了 Windows 平台的 `node_modules`。
   - **解决**: 暴力清除并重装。
     ```bash
     rm -rf node_modules package-lock.json
     npm install
     ```

4. **域名拼写错误**:
   - **现象**: 证书申请失败，访问不通。
   - **原因**: 混淆了 `auditeyes.com` 和 `auditoreyes.com`。
   - **解决**: 全局搜索替换，重置 Nginx 配置和 Certbot 证书。

## 5. 常用维护命令

```bash
# 重启后端
sudo systemctl restart cpa-assistant

# 查看后端日志
sudo journalctl -u cpa-assistant -f

# 重载 Nginx
sudo nginx -t
sudo systemctl reload nginx

# 重新部署前端
cd /opt/cpa-assistant/cpa-frontend
git pull
npm run build
sudo cp -r dist/* /var/www/auditoreyes/
```


