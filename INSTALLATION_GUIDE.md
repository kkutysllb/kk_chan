# KK缠论量化分析系统 - 安装指南

## 📋 环境要求

- **Python**: 3.8+ (推荐 3.10+)
- **Node.js**: 18.0+ (前端开发)
- **MongoDB**: 5.0+
- **Redis**: 6.0+ (可选，用于缓存)

## 🚀 安装步骤

### 1. 后端环境安装

#### 1.1 创建虚拟环境
```bash
# 进入项目目录
cd /home/libing/kk_Projects/kk_stock/kk_chan

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

#### 1.2 安装核心依赖
```bash
# 升级pip
pip install --upgrade pip

# 安装核心依赖（不包括qlib）
pip install -r requirements.txt
```

#### 1.3 处理Qlib安装（可选）

由于qlib版本兼容性问题，推荐按需安装：

**选项1: 安装最新开发版本**
```bash
# 从GitHub安装最新开发版
pip install git+https://github.com/microsoft/qlib.git

# 或者安装特定版本
pip install "qlib==0.0.2.dev20" --no-deps
pip install pandas numpy scipy matplotlib seaborn plotly
```

**选项2: 使用系统内置策略（推荐）**
```bash
# 不安装qlib，使用我们自己实现的策略系统
# 系统已经包含完整的缠论分析功能，不依赖qlib
```

### 2. 前端环境安装

```bash
# 进入前端目录
cd frontend

# 安装Node.js依赖
npm install

# 或使用yarn
yarn install
```

### 3. 数据库配置

#### 3.1 MongoDB配置
```bash
# 启动MongoDB服务
sudo systemctl start mongod    # Linux
brew services start/stop mongodb-community  # Mac

# 创建数据库用户（可选）
mongo
> use quant_analysis
> db.createUser({
  user: "quant_user",
  pwd: "your_password",
  roles: ["readWrite"]
})
```

#### 3.2 Redis配置（可选）
```bash
# 启动Redis服务
sudo systemctl start redis     # Linux
brew services start redis      # Mac

# 测试连接
redis-cli ping
```

### 4. 环境变量配置

```bash
# 复制环境配置文件
cp env_example.txt .env

# 编辑配置文件
vim .env
```

**环境变量配置示例：**
```bash
# 数据库配置
MONGO_URI=mongodb://localhost:27017/quant_analysis
MONGO_URI_CLOUD=mongodb://root:example@vip.cd.frp.one:48714/quant_analysis?authSource=admin

# Redis配置
REDIS_URL=redis://localhost:6379/0

# API配置
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# 前端配置
VITE_API_BASE_URL=http://localhost:8000
```

## 🧪 验证安装

### 1. 测试后端环境
```bash
# 激活虚拟环境
source venv/bin/activate

# 测试核心功能
python -c "
import pandas as pd
import numpy as np
import pymongo
from datetime import datetime
print('✅ 核心依赖安装成功')

# 测试数据库连接
try:
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    client.server_info()
    print('✅ MongoDB连接成功')
except:
    print('⚠️  MongoDB连接失败，请检查服务状态')

# 测试缠论核心模块
try:
    from chan_theory.models.enhanced_chan_models import EnhancedFenXing, TrendLevel
    print('✅ 缠论模块导入成功')
except Exception as e:
    print(f'⚠️  缠论模块导入失败: {e}')
"
```

### 2. 启动后端服务
```bash
# 方法1: 直接启动
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 方法2: 使用脚本启动
python api/main.py
```

**验证API服务：**
- 访问: http://localhost:8000/health
- API文档: http://localhost:8000/docs

### 3. 启动前端服务
```bash
cd frontend

# 启动开发服务器
npm run dev

# 访问前端应用
# http://localhost:3000
```

## 🔧 常见问题解决

### 1. Qlib安装问题

**问题**: `ERROR: No matching distribution found for qlib>=0.9.0`

**解决方案**:
```bash
# 方案1: 安装开发版本
pip install git+https://github.com/microsoft/qlib.git

# 方案2: 跳过qlib，使用内置策略
# 系统不强依赖qlib，可以正常运行缠论分析功能
```

### 2. PyTorch安装问题

**问题**: PyTorch安装失败或版本冲突

**解决方案**:
```bash
# 根据系统选择合适版本
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 或GPU版本（如果有CUDA）
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 3. MongoDB连接问题

**问题**: 数据库连接失败

**解决方案**:
```bash
# 检查MongoDB服务状态
sudo systemctl status mongod

# 启动MongoDB
sudo systemctl start mongod

# 检查配置文件
sudo vim /etc/mongod.conf

# 测试连接
mongo --host localhost --port 27017
```

### 4. 权限问题

**问题**: 文件权限或目录访问问题

**解决方案**:
```bash
# 设置项目目录权限
sudo chown -R $USER:$USER /home/libing/kk_Projects/kk_stock/kk_chan

# 确保虚拟环境可执行
chmod +x venv/bin/activate
```

### 5. 前端依赖问题

**问题**: npm install失败

**解决方案**:
```bash
# 清理缓存
npm cache clean --force

# 删除node_modules重新安装
rm -rf node_modules package-lock.json
npm install

# 或使用yarn
npm install -g yarn
yarn install
```

## 📚 开发环境配置

### 1. IDE配置推荐

**Python开发**:
- PyCharm Professional
- VS Code + Python扩展
- Jupyter Lab（数据分析）

**前端开发**:
- VS Code + Vue扩展
- WebStorm

### 2. 代码格式化

**Python**:
```bash
pip install black isort flake8
black . --line-length 88
isort . --profile black
```

**前端**:
```bash
npm run lint
npm run format
```

### 3. 调试配置

**后端调试**:
```python
# 在main.py中添加调试配置
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True,
        log_level="debug"
    )
```

**前端调试**:
```bash
# 开启调试模式
npm run dev --debug
```

## 🚀 生产环境部署

### 1. 生产依赖安装
```bash
pip install gunicorn
pip install uvicorn[standard]
```

### 2. 生产环境启动
```bash
# Gunicorn启动
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 前端构建
cd frontend
npm run build
```

### 3. Docker部署（可选）
```dockerfile
# Dockerfile示例
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

现在你可以重新运行安装命令：

```bash
pip install -r requirements.txt
```

系统已经设计为不强依赖qlib，核心的缠论分析功能都是独立实现的，可以正常运行。如果后续需要qlib的特定功能，可以按照上面的指南单独安装。