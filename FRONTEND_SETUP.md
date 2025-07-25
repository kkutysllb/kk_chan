# 前端环境设置指南

## 🚀 快速启动

### 1. 安装依赖
```bash
cd frontend

# 清理缓存（如果之前安装失败）
npm cache clean --force
rm -rf node_modules package-lock.json

# 重新安装依赖
npm install
```

### 2. 配置环境变量
```bash
# 复制环境配置文件
cp .env.example .env.local

# 编辑配置（可选）
vim .env.local
```

### 3. 启动开发服务器
```bash
npm run dev
```

访问: http://localhost:3000

## 🔧 解决依赖问题

### 问题1: 某些包无法安装
```bash
# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 或临时使用
npm install --registry https://registry.npmmirror.com
```

### 问题2: Node版本问题
```bash
# 检查Node版本
node --version

# 如果版本过低，使用nvm安装新版本
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

### 问题3: 权限问题
```bash
# 修复npm权限
sudo chown -R $USER ~/.npm
sudo chown -R $USER /usr/local/lib/node_modules
```

## 📦 核心依赖说明

- **Vue 3**: 前端框架
- **TypeScript**: 类型支持
- **Element Plus**: UI组件库
- **ECharts**: 图表库
- **Vue Router**: 路由管理
- **Pinia**: 状态管理
- **Axios**: HTTP客户端
- **@vueuse/core**: Vue组合式API工具库

## 🎨 自定义配置

### 修改API地址
编辑 `.env.local`:
```bash
VITE_API_BASE_URL=http://your-api-server:8000
```

### 修改端口
编辑 `vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 3001  // 修改为其他端口
  }
})
```

## 🏗 构建生产版本

```bash
# 构建
npm run build

# 预览构建结果
npm run preview
```

构建文件将生成在 `dist/` 目录中。

## 📱 开发模式特性

- **热重载**: 代码修改自动刷新
- **类型检查**: TypeScript实时类型检查
- **代理配置**: 自动代理API请求到后端
- **自动导入**: 常用API自动导入，无需手动import

## 🎯 项目结构

```
frontend/
├── src/
│   ├── components/     # 组件
│   │   └── charts/     # 图表组件
│   ├── stores/         # 状态管理
│   ├── services/       # API服务
│   ├── utils/          # 工具函数
│   ├── types/          # TypeScript类型
│   ├── styles/         # 样式文件
│   ├── views/          # 页面组件
│   └── router/         # 路由配置
├── public/             # 静态资源
└── dist/              # 构建输出
```