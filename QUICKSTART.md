# 跨境宝贝 - 快速启动指南

## 🚀 本地运行

### 1. 安装依赖
```bash
cd AI-CrossBorder
pip install -r requirements.txt
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入你的 API Key
```

### 3. 启动服务
```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问应用
- 前端界面: http://localhost:8000
- API文档: http://localhost:8000/api/docs

## 🌐 Vercel 部署

### 1. 安装 Vercel CLI
```bash
npm install -g vercel
```

### 2. 登录并部署
```bash
vercel login
vercel
```

### 3. 设置环境变量
```bash
vercel env add DEEPSEEK_API_KEY
```

### 4. 生产环境部署
```bash
vercel --prod
```

## 📝 API 调用示例

### 生成产品描述
```python
import requests

response = requests.post("http://localhost:8000/api/generate", json={
    "product_name": "无线蓝牙耳机",
    "product_description": "主动降噪，30小时续航，适合通勤运动",
    "platform": "amazon",
    "languages": ["en", "ja"],
    "style": "professional"
})

print(response.json())
```

### 使用自己的 API Key (BYOK)
```python
response = requests.post("http://localhost:8000/api/generate", json={
    "product_name": "产品名",
    "product_description": "产品描述",
    "platform": "amazon",
    "languages": ["en"],
    "style": "professional",
    "api_key": "sk-your-key"  # 使用自己的Key
})
```

## 🎨 功能概览

| 功能 | 免费版 | Pro版 |
|------|--------|-------|
| 生成次数 | 3次/月 | 无限 |
| 支持平台 | 4个 | 4个 |
| 支持语言 | 10种 | 10种 |
| 文案风格 | 4种 | 4种 |
| API访问 | ✅ | ✅ |

## 🔧 技术栈

- **后端**: Python FastAPI
- **前端**: 原生 HTML/CSS/JS
- **AI**: OpenAI / DeepSeek
- **部署**: Vercel Serverless

## 📞 支持

- 提交 Issue: GitHub Issues
- 文档: http://localhost:8000/api/docs
