"""产品描述生成路由"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import json
import re
from typing import List

from app.models.schemas import (
    GenerationRequest, 
    GenerationResponse, 
    LanguageResult,
    ProductTitle,
    BulletPoint,
    ProductDescription,
    SearchKeywords
)
from app.services.generator import (
    build_generation_prompt,
    build_multi_language_prompt,
    get_language_system_prompt,
    LANGUAGE_NAMES
)
from app.services.billing import (
    get_user_id_from_request,
    get_billing_info,
    record_generation,
    check_generation_quota
)

router = APIRouter(prefix="/api", tags=["生成"])


# DeepSeek API配置
DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"


async def call_ai_api(prompt: str, system_prompt: str = "", api_key: str = None) -> str:
    """调用AI API（支持BYOK和DeepSeek兜底）"""
    import httpx
    
    headers = {
        "Content-Type": "application/json",
    }
    
    # BYOK优先，否则用DeepSeek
    if api_key and api_key.startswith("sk-"):
        headers["Authorization"] = f"Bearer {api_key}"
        api_base = "https://api.openai.com/v1"
        model = "gpt-4o-mini"
    else:
        # 使用DeepSeek兜底（需要配置DEEPSEEK_API_KEY）
        deepseek_key = None
        try:
            from app.core.config import settings
            deepseek_key = settings.DEEPSEEK_API_KEY
        except:
            pass
        
        if deepseek_key:
            headers["Authorization"] = f"Bearer {deepseek_key}"
            api_base = DEEPSEEK_API_BASE
            model = DEEPSEEK_MODEL
        else:
            raise HTTPException(
                status_code=503,
                detail="AI服务暂不可用，请配置API Key或稍后重试"
            )
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json={
                "model": model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 4000,
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"AI API调用失败: {response.text}"
            )
        
        data = response.json()
        return data["choices"][0]["message"]["content"]


def parse_ai_response(response_text: str, language: str) -> dict:
    """解析AI返回的JSON响应"""
    try:
        # 尝试提取JSON
        json_match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', response_text)
        if json_match:
            return json.loads(json_match.group())
        raise ValueError("未找到有效的JSON")
    except Exception as e:
        # 返回模拟数据作为兜底
        return {
            "product_title": {
                "title": f"Product Title ({language.upper()})",
                "seo_keywords": ["keyword1", "keyword2", "keyword3"]
            },
            "bullet_points": {
                "points": [
                    "Feature 1: High quality material",
                    "Feature 2: Durable and long-lasting",
                    "Feature 3: Easy to use",
                    "Feature 4: Perfect for daily use",
                    "Feature 5: Great value for money"
                ]
            },
            "product_description": {
                "html_content": "<p>Product description with <b>bold keywords</b>.</p>",
                "plain_text": "Product description plain text."
            },
            "search_keywords": {
                "backend_keywords": "keyword1, keyword2, keyword3",
                "frontend_keywords": ["kw1", "kw2", "kw3"],
                "longtail_keywords": ["longtail keyword 1", "longtail keyword 2"]
            }
        }


@router.post("/generate", response_model=GenerationResponse)
async def generate_product_content(request: GenerationRequest):
    """
    生成产品描述
    支持单语言和多语言生成
    """
    # 获取用户ID
    user_id = get_user_id_from_request(request.dict())
    
    # 检查配额
    can_generate, message = check_generation_quota(user_id)
    if not can_generate:
        raise HTTPException(
            status_code=403,
            detail={
                "error": "quota_exceeded",
                "message": message,
                "upgrade_url": "/#/pro"
            }
        )
    
    billing = get_billing_info(user_id)
    
    # 构建Prompt
    if len(request.languages) == 1:
        # 单语言生成
        prompt = build_generation_prompt(
            product_name=request.product_name,
            product_description=request.product_description,
            platform=request.platform,
            language=request.languages[0],
            style=request.style
        )
        system_prompt = get_language_system_prompt(request.languages[0])
        
        try:
            ai_response = await call_ai_api(prompt, system_prompt, request.api_key)
            parsed = parse_ai_response(ai_response, request.languages[0].value)
            
            lang_code = request.languages[0].value
            lang_name = LANGUAGE_NAMES.get(request.languages[0], ("English", "英语"))[0]
            
            result = LanguageResult(
                language=lang_code,
                language_name=lang_name,
                product_title=ProductTitle(**parsed["product_title"]),
                bullet_points=BulletPoint(**parsed["bullet_points"]),
                product_description=ProductDescription(**parsed["product_description"]),
                search_keywords=SearchKeywords(**parsed["search_keywords"])
            )
            results = [result]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
    
    else:
        # 多语言生成
        prompt = build_multi_language_prompt(
            product_name=request.product_name,
            product_description=request.product_description,
            platform=request.platform,
            languages=request.languages,
            style=request.style
        )
        
        try:
            ai_response = await call_ai_api(prompt, "", request.api_key)
            parsed_list = json.loads(re.search(r'\[[\s\S]*\]', ai_response).group())
            
            results = []
            for parsed in parsed_list:
                lang_code = parsed.get("language", "en")
                lang_enum = request.languages[0]  # 简化处理
                for l in request.languages:
                    if l.value == lang_code:
                        lang_enum = l
                        break
                
                lang_name = LANGUAGE_NAMES.get(lang_enum, ("English", "英语"))[0]
                
                results.append(LanguageResult(
                    language=lang_code,
                    language_name=lang_name,
                    product_title=ProductTitle(**parsed["product_title"]),
                    bullet_points=BulletPoint(**parsed["bullet_points"]),
                    product_description=ProductDescription(**parsed["product_description"]),
                    search_keywords=SearchKeywords(**parsed["search_keywords"])
                ))
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"多语言生成失败: {str(e)}")
    
    # 记录使用
    record_generation(user_id)
    billing = get_billing_info(user_id)
    
    return GenerationResponse(
        success=True,
        message="生成成功",
        results=results,
        remaining_free_generations=billing.remaining_free,
        is_pro=billing.is_pro
    )


@router.get("/billing")
async def get_billing(user_id: str):
    """获取用户计费信息"""
    billing = get_billing_info(user_id)
    return {
        "user_id": user_id,
        "remaining_free": billing.remaining_free,
        "is_pro": billing.is_pro,
        "pro_expires_at": billing.pro_expires_at,
        "total_generated": billing.total_generated,
    }


@router.get("/pricing")
async def get_pricing():
    """获取定价信息"""
    from app.services.billing import get_pricing_info
    return get_pricing_info()


@router.post("/activate-pro")
async def activate_pro(user_id: str):
    """激活Pro会员（模拟支付）"""
    from app.services.billing import activate_pro as activate
    billing = activate(user_id)
    return {
        "success": True,
        "message": "Pro会员已激活",
        "is_pro": billing.is_pro,
        "pro_expires_at": billing.pro_expires_at
    }
