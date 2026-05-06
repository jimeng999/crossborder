"""Pydantic数据模型定义"""
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Platform(str, Enum):
    """支持的电商平台"""
    AMAZON = "amazon"
    SHOPEE = "shopee"
    ALIEXPRESS = "aliexpress"
    TEMU = "temu"


class Style(str, Enum):
    """文案风格"""
    PROFESSIONAL = "professional"      # 专业卖点型
    STORY = "story"                     # 场景故事型
    PROBLEM_SOLVING = "problem_solving" # 问题解决型
    PREMIUM = "premium"                 # 高端品牌型


class Language(str, Enum):
    """支持的目标语言"""
    EN = "en"    # 英语
    JA = "ja"    # 日语
    KO = "ko"    # 韩语
    TH = "th"    # 泰语
    VI = "vi"    # 越南语
    ES = "es"    # 西班牙语
    PT = "pt"    # 葡萄牙语
    FR = "fr"    # 法语
    DE = "de"    # 德语
    RU = "ru"    # 俄语


# ============ 请求模型 ============

class GenerationRequest(BaseModel):
    """产品描述生成请求"""
    product_name: str = Field(..., min_length=1, max_length=200, description="产品名称（中文）")
    product_description: str = Field(..., min_length=10, max_length=5000, description="产品描述/卖点（中文）")
    platform: Platform = Field(..., description="目标电商平台")
    languages: List[Language] = Field(..., min_length=1, description="目标语言列表")
    style: Style = Field(default=Style.PROFESSIONAL, description="文案风格")
    api_key: Optional[str] = Field(None, description="用户自己的API Key（BYOK模式）")
    
    class Config:
        use_enum_values = True


class BillingCheckRequest(BaseModel):
    """计费检查请求"""
    user_id: str = Field(..., description="用户ID")


# ============ 响应模型 ============

class ProductTitle(BaseModel):
    """产品标题"""
    language: str
    title: str
    seo_keywords: List[str]


class BulletPoint(BaseModel):
    """五点描述/Bullet Points"""
    language: str
    points: List[str]  # 5个要点


class ProductDescription(BaseModel):
    """产品详情描述"""
    language: str
    html_content: str
    plain_text: str


class SearchKeywords(BaseModel):
    """搜索关键词"""
    language: str
    backend_keywords: str  # 后台搜索词
    frontend_keywords: List[str]  # 前端可见关键词
    longtail_keywords: List[str]  # 长尾关键词建议


class LanguageResult(BaseModel):
    """单语言生成结果"""
    language: str
    language_name: str
    product_title: ProductTitle
    bullet_points: BulletPoint
    product_description: ProductDescription
    search_keywords: SearchKeywords


class GenerationResponse(BaseModel):
    """产品描述生成响应"""
    success: bool
    message: str
    results: List[LanguageResult]
    remaining_free_generations: int = 3
    is_pro: bool = False


class BillingResponse(BaseModel):
    """计费状态响应"""
    user_id: str
    remaining_free: int
    is_pro: bool
    pro_expires_at: Optional[str] = None


class CopyriteResponse(BaseModel):
    """复制版权信息"""
    success: bool
    content: str
    format: str
