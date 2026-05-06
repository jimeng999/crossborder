"""
跨境宝贝 - AI产品描述生成核心服务
包含4种风格×多平台×多语言的Prompt模板
"""
import re
from typing import Dict, List
from app.models.schemas import Platform, Style, Language


# 语言名称映射
LANGUAGE_NAMES = {
    Language.EN: ("English", "英语"),
    Language.JA: ("日本語", "日语"),
    Language.KO: ("한국어", "韩语"),
    Language.TH: ("ภาษาไทย", "泰语"),
    Language.VI: ("Tiếng Việt", "越南语"),
    Language.ES: ("Español", "西班牙语"),
    Language.PT: ("Português", "葡萄牙语"),
    Language.FR: ("Français", "法语"),
    Language.DE: ("Deutsch", "德语"),
    Language.RU: ("Русский", "俄语"),
}


# 平台特定的格式要求
PLATFORM_RULES = {
    Platform.AMAZON: {
        "title_length": "150-200 characters",
        "bullet_length": "80-120 characters per point",
        "description_length": "300-500 words",
        "has_html": True,
        "max_bullets": 5,
        "title_format": "Brand + Core Keyword + Features + Use Case",
        "banned_words": ["free shipping", " bestseller", " hot sale", " discount", " promotion"],
    },
    Platform.SHOPEE: {
        "title_length": "60-120 characters",
        "bullet_length": "50-100 characters per point",
        "description_length": "200-400 words",
        "has_html": True,
        "max_bullets": 5,
        "title_format": "Keywords + Model + Features + Hot",
        "banned_words": ["free", "best", "cheapest"],
    },
    Platform.ALIEXPRESS: {
        "title_length": "100-150 characters",
        "bullet_length": "60-100 characters per point",
        "description_length": "250-450 words",
        "has_html": True,
        "max_bullets": 5,
        "title_format": "Core Keyword + Secondary + Features",
        "banned_words": [],
    },
    Platform.TEMU: {
        "title_length": "80-120 characters",
        "bullet_length": "50-80 characters per point",
        "description_length": "200-350 words",
        "has_html": True,
        "max_bullets": 4,
        "title_format": "Trendy Keywords + Features",
        "banned_words": ["free shipping over"],
    },
}


# 风格指南
STYLE_GUIDES = {
    Style.PROFESSIONAL: {
        "name": "专业卖点型 / Professional",
        "focus": "参数、功能、规格、认证",
        "tone": "专业、权威、数据驱动",
        "structure": "功能点→参数→对比优势→品质保证",
    },
    Style.STORY: {
        "name": "场景故事型 / Story",
        "focus": "使用场景、情感共鸣、生活方式",
        "tone": "温暖、亲切、有画面感",
        "structure": "场景引入→产品价值→情感连接→行动号召",
    },
    Style.PROBLEM_SOLVING: {
        "name": "问题解决型 / Problem-Solving",
        "focus": "痛点、解决方案、效果对比",
        "tone": "直接、有说服力、解决问题导向",
        "structure": "痛点描述→解决方案→产品特性→效果验证→购买理由",
    },
    Style.PREMIUM: {
        "name": "高端品牌型 / Premium",
        "focus": "品质、设计理念、品牌故事",
        "tone": "优雅、精致、有品味",
        "structure": "品牌调性→设计理念→材质工艺→细节品质→身份象征",
    },
}


def get_style_prompt(style: Style) -> str:
    """获取风格特定的指导Prompt"""
    guide = STYLE_GUIDES.get(style, STYLE_GUIDES[Style.PROFESSIONAL])
    return f"""
【文案风格指导 - {guide['name']}】
- 核心焦点：{guide['focus']}
- 语气语调：{guide['tone']}
- 内容结构：{guide['structure']}
"""


def get_platform_prompt(platform: Platform) -> str:
    """获取平台特定的格式要求Prompt"""
    rules = PLATFORM_RULES.get(platform, PLATFORM_RULES[Platform.AMAZON])
    return f"""
【平台格式要求 - {platform.value.upper()}】
- 标题长度：{rules['title_length']}
- 五点描述：{rules['bullet_length']}，最多{rules['max_bullets']}个要点
- 详情描述：{rules['description_length']}
- 标题格式：{rules['title_format']}
- 禁用词：{', '.join(rules['banned_words']) if rules['banned_words'] else '无'}
"""


def get_language_system_prompt(language: Language) -> str:
    """获取语言特定的系统Prompt"""
    prompts = {
        Language.EN: "You are an expert Amazon/e-commerce product copywriter specializing in English content for global marketplaces. Write in natural, SEO-friendly English.",
        Language.JA: "あなたは跨境EC製品の専門コピーライターです。自然でSEO友好的な日本語で書いてください。",
        Language.KO: "당신은 글로벌 이커머스 제품 카피라이터입니다. 자연스럽고 SEO 친화적인 한국어로 작성하세요.",
        Language.TH: "คุณคือนักเขียนคัดลอกผลิตภัณฑ์ EC ข้ามพรมแดน จงเขียนภาษาไทยที่เป็นธรรมชาติและเหมาะกับ SEO",
        Language.VI: "Bạn là chuyên gia viết bản sao sản phẩm thương mại điện tử xuyên biên giới. Hãy viết tiếng Việt tự nhiên, thân thiện với SEO.",
        Language.ES: "Eres un redactor experto en copywriting de productos e-commerce. Escribe en español natural y SEO-friendly.",
        Language.PT: "Você é um redator especialista em copywriting de produtos e-commerce. Escreva em português natural e otimizado para SEO.",
        Language.FR: "Vous êtes un rédacteur expert en copywriting de produits e-commerce. Écrivez en français naturel et adapté au SEO.",
        Language.DE: "Sie sind ein erfahrener Produkt-Kopiertexter für E-Commerce. Schreiben Sie in natürlichem, SEO-freundlichem Deutsch.",
        Language.RU: "Вы эксперт по копирайтингу товаров для электронной коммерции. Пишите на естественном, SEO-оптимизированном русском языке.",
    }
    return prompts.get(language, prompts[Language.EN])


def build_generation_prompt(
    product_name: str,
    product_description: str,
    platform: Platform,
    language: Language,
    style: Style
) -> str:
    """构建完整的生成Prompt"""
    
    lang_name, lang_cn = LANGUAGE_NAMES.get(language, ("English", "英语"))
    platform_rules = PLATFORM_RULES.get(platform, PLATFORM_RULES[Platform.AMAZON])
    style_guide = STYLE_GUIDES.get(style)
    
    prompt = f"""# 跨境电商产品描述生成任务

## 产品信息
- **产品名称（中文）**: {product_name}
- **产品描述/卖点（中文）**: {product_description}

## 输出语言
- 目标语言: {lang_name} ({lang_cn})

## 目标平台
{platform.value.upper()}

## 平台规则
{get_platform_prompt(platform)}

## 风格要求
{get_style_prompt(style)}

## 输出要求
请严格按照以下JSON格式输出，不要包含任何其他内容：

```json
{{
    "product_title": {{
        "title": "SEO优化的产品标题",
        "seo_keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"]
    }},
    "bullet_points": {{
        "points": [
            "五点描述第1点（突出关键词，大写开头）",
            "五点描述第2点",
            "五点描述第3点",
            "五点描述第4点",
            "五点描述第5点"
        ]
    }},
    "product_description": {{
        "html_content": "HTML格式的详情描述，包含<b>加粗关键词</b>",
        "plain_text": "纯文本版本，用于预览"
    }},
    "search_keywords": {{
        "backend_keywords": "后台搜索词，用逗号分隔，控制在200字符内",
        "frontend_keywords": ["前端可见关键词1", "关键词2", "关键词3"],
        "longtail_keywords": ["长尾关键词建议1", "长尾关键词建议2", "长尾关键词建议3"]
    }}
}}
```

## 重要提醒
1. 标题必须包含核心搜索关键词
2. 五点描述每点开头要用大写字母，并包含关键卖点词
3. HTML描述要有合理的标签结构：<b>、<ul>、<li>、<p>
4. 搜索关键词要覆盖短尾+长尾
5. 内容要自然，避免关键词堆砌
6. 输出必须是有效的JSON格式

请开始生成："""
    
    return prompt


def build_multi_language_prompt(
    product_name: str,
    product_description: str,
    platform: Platform,
    languages: List[Language],
    style: Style
) -> str:
    """构建多语言同时生成的Prompt"""
    
    lang_list = ", ".join([LANGUAGE_NAMES.get(l, ("English", "英语"))[0] for l in languages])
    
    prompt = f"""# 跨境电商产品描述多语言批量生成

## 产品信息
- **产品名称（中文）**: {product_name}
- **产品描述/卖点（中文）**: {product_description}

## 目标语言（一次性生成所有语言）
{lang_list}

## 目标平台
{platform.value.upper()}

## 风格要求
{get_style_prompt(style)}

## 输出要求
请为每种语言生成完整的产品描述，输出JSON数组格式：

```json
[
    {{
        "language": "en",
        "language_name": "English",
        "product_title": {{
            "title": "SEO优化的英文标题",
            "seo_keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
        }},
        "bullet_points": {{
            "points": ["Point 1", "Point 2", "Point 3", "Point 4", "Point 5"]
        }},
        "product_description": {{
            "html_content": "<p>HTML内容...</p>",
            "plain_text": "纯文本预览"
        }},
        "search_keywords": {{
            "backend_keywords": "backend keywords, comma separated",
            "frontend_keywords": ["kw1", "kw2", "kw3"],
            "longtail_keywords": ["longtail 1", "longtail 2", "longtail 3"]
        }}
    }},
    {{
        "language": "ja",
        "language_name": "日本語",
        ...
    }}
]
```

请一次性生成所有{len(languages)}种语言的描述："""
    
    return prompt


def extract_keywords_from_description(description: str) -> List[str]:
    """从中文描述中提取潜在关键词"""
    # 简单提取：去除标点，按长度筛选词组
    cleaned = re.sub(r'[^\w\u4e00-\u9fff]', ' ', description)
    words = cleaned.split()
    # 过滤：保留2-8个字的中文词
    keywords = [w for w in words if 2 <= len(w) <= 8]
    return list(set(keywords))[:10]


def format_for_copy(content: str, format_type: str) -> str:
    """格式化内容以便于复制到各平台"""
    if format_type == "title":
        return content.strip()
    elif format_type == "bullets":
        # 转换为换行分隔
        lines = content.split('\n')
        return '\n'.join([f"• {line.strip()}" for line in lines if line.strip()])
    elif format_type == "html":
        return content.strip()
    elif format_type == "keywords":
        return content.strip().replace(', ', '\n')
    return content
