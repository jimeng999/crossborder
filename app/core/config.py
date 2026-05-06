"""应用配置"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    APP_NAME: str = "跨境宝贝 CrossBorder Pro"
    APP_VERSION: str = "1.0.0"
    
    # DeepSeek API（兜底）
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    
    # OpenAI API（BYOK模式）
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # CORS设置
    CORS_ORIGINS: list = ["*"]
    
    # 服务器设置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
