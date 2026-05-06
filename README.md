# 跨境宝贝 CrossBorder Pro
**一个产品，卖遍全球**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](./README.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](./LICENSE)

## 🎯 产品简介

跨境宝贝是一款专为跨境电商卖家打造的AI产品描述生成工具。输入中文产品信息，一键生成Amazon、Shopee、速卖通、Temu等多平台的英文、日语、韩语、泰语等多语言产品描述。

### 核心功能

- 🌍 **多语言支持**: 英语、日语、韩语、泰语、越南语、西班牙语、葡萄牙语、法语、德语、俄语
- 🏪 **全平台覆盖**: Amazon、Shopee、速卖通、Temu
- ✨ **4种文案风格**: 专业卖点型、场景故事型、问题解决型、高端品牌型
- 📝 **完整输出**: SEO标题、五点描述、详情HTML、搜索关键词
- 💰 **灵活计费**: 免费3次/月，Pro ¥59/月无限次

## 🚀 快速开始

### 本地开发

```bash
# 克隆项目
git clone https://github.com/your-repo/crossborder-pro.git
cd crossborder-pro

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API Key

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Vercel部署

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 部署
vercel

# 设置环境变量
vercel env add DEEPSEEK_API_KEY
```

## 📁 项目结构

```
AI-CrossBorder/
├── api/
│   └── index.py              # Vercel Serverless 函数入口
├── app/
│   ├── main.py               # FastAPI 主应用
│   ├── core/
│   │   └── config.py         # 配置管理
│   ├── routers/
│   │   ├── generate.py       # 生成路由
│   │   └── user.py           # 用户路由
│   ├── services/
│   │   ├── generator.py      # Prompt生成核心
│   │   └── billing.py        # 计费服务
│   └── models/
│       └── schemas.py        # 数据模型
├── static/
│   └── index.html            # 前端单页应用
├── vercel.json               # Vercel配置
├── requirements.txt          # Python依赖
└── README.md                 # 项目文档
```

## 🔑 API文档

### 生成产品描述

```http
POST /api/generate
Content-Type: application/json

{
  "product_name": "无线蓝牙耳机",
  "product_description": "降噪设计，30小时续航，佩戴舒适，适合运动和通勤使用",
  "platform": "amazon",
  "languages": ["en", "ja", "ko"],
  "style": "professional",
  "api_key": "your-api-key"  // 可选，使用自己的API Key
}
```

### 响应格式

```json
{
  "success": true,
  "message": "生成成功",
  "results": [
    {
      "language": "en",
      "language_name": "English",
      "product_title": {
        "title": "Wireless Bluetooth Headphones with Active Noise Cancellation...",
        "seo_keywords": ["bluetooth headphones", "noise cancelling", ...]
      },
      "bullet_points": {
        "points": [
          "CRYSTAL-CLEAR AUDIO...",
          "30-HOUR BATTERY LIFE...",
          ...
        ]
      },
      "product_description": {
        "html_content": "<p>...</p>",
        "plain_text": "..."
      },
      "search_keywords": {
        "backend_keywords": "wireless earbuds, bluetooth headphones, ...",
        "frontend_keywords": [...],
        "longtail_keywords": [...]
      }
    }
  ],
  "remaining_free_generations": 2,
  "is_pro": false
}
```

### 获取计费信息

```http
GET /api/billing?user_id=xxx
```

### 获取定价信息

```http
GET /api/pricing
```

## 🎨 前端预览

前端采用深色+蓝绿渐变主题，具有以下特点：

- **主色调**: 深色底(#0a0a0b) + 蓝绿渐变(#06b6d4 → #10b981) + 橙色CTA
- **布局**: 左侧输入区 + 右侧输出区
- **动效**: 生成中"翻译中🌐..."动画
- **移动端**: 响应式设计，适配手机/平板

## 💡 使用技巧

### 1. 如何获得更好的生成结果？

- 产品描述尽量详细，包含核心卖点
- 选择与产品匹配的文案风格
- 批量生成多种语言后再筛选

### 2. 如何提升SEO效果？

- 产品名称包含核心关键词
- 五点描述开头使用大写关键词
- 后台关键词覆盖短尾+长尾

### 3. API Key配置

- **BYOK模式**: 使用自己的OpenAI API Key（推荐gpt-4o-mini）
- **DeepSeek兜底**: 配置`DEEPSEEK_API_KEY`环境变量

## 📊 计费说明

| 方案 | 价格 | 次数 | 权益 |
|------|------|------|------|
| 免费版 | ¥0 | 3次/月 | 基础生成功能 |
| Pro版 | ¥59/月 | 无限次 | 无限生成 + 优先处理 |

## 🔧 技术栈

- **后端**: Python 3.9+ / FastAPI
- **前端**: 原生 HTML5 + CSS3 + JavaScript
- **AI**: OpenAI API / DeepSeek API
- **部署**: Vercel Serverless

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

Made with ❤️ for Cross-border Sellers 🌍
