"""
跨境宝贝 - 主应用入口
CrossBorder Pro - AI产品描述生成器
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os

from app.core.config import settings
from app.routers import generate, user

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="一个产品，卖遍全球 - 输入中文产品信息，一键生成多语言电商产品描述",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(generate.router)
app.include_router(user.router)

# 静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    """首页"""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>跨境宝贝 CrossBorder Pro</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, #0a0a0b 0%, #1a1a2e 50%, #0f1f1a 100%);
                color: #fff;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            .container { text-align: center; padding: 40px; }
            h1 { font-size: 3em; margin-bottom: 20px; background: linear-gradient(90deg, #06b6d4, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
            p { font-size: 1.5em; color: #9ca3af; margin-bottom: 30px; }
            .version { color: #6b7280; font-size: 0.9em; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌍 跨境宝贝 CrossBorder Pro</h1>
            <p>一个产品，卖遍全球</p>
            <p class="version">v""" + settings.APP_VERSION + """ | API Docs: <a href="/api/docs" style="color:#06b6d4;">/api/docs</a></p>
        </div>
    </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": settings.APP_NAME}


# Vercel Serverless 入口
handler = app
