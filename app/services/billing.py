"""
跨境宝贝 - 计费服务
免费用户：3次/月
Pro用户：¥59/月无限次
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import hashlib
import json


# 内存存储（生产环境应使用数据库）
# 格式: {user_id: {"free_remaining": int, "is_pro": bool, "pro_expires": datetime, "history": []}}
_user_storage: Dict[str, Dict] = {}


FREE_GENERATIONS_PER_MONTH = 3
PRO_PRICE_YUAN = 59
PRO_DAYS_VALID = 30


@dataclass
class BillingInfo:
    """计费信息"""
    user_id: str
    remaining_free: int
    is_pro: bool
    pro_expires_at: Optional[str] = None
    total_generated: int = 0
    
    def can_generate(self) -> bool:
        """是否可以生成"""
        if self.is_pro:
            return True
        return self.remaining_free > 0
    
    def use_generation(self) -> bool:
        """消耗一次生成次数，返回是否成功"""
        if self.is_pro:
            return True
        if self.remaining_free > 0:
            self.remaining_free -= 1
            return True
        return False


def get_user_id_from_request(request_data: dict) -> str:
    """从请求中获取或生成用户ID"""
    # 优先使用前端传来的user_id
    if "user_id" in request_data:
        return request_data["user_id"]
    
    # 使用API Key的hash作为匿名用户ID
    if "api_key" in request_data and request_data["api_key"]:
        api_key = request_data["api_key"]
        return f"anon_{hashlib.md5(api_key[:20].encode()).hexdigest()[:12]}"
    
    # 生成会话ID
    return f"session_{datetime.now().strftime('%Y%m%d%H%M%S')}"


def get_billing_info(user_id: str) -> BillingInfo:
    """获取用户计费信息"""
    if user_id not in _user_storage:
        _user_storage[user_id] = {
            "free_remaining": FREE_GENERATIONS_PER_MONTH,
            "is_pro": False,
            "pro_expires": None,
            "total_generated": 0,
            "created_at": datetime.now().isoformat(),
        }
    
    data = _user_storage[user_id]
    
    # 检查Pro是否过期
    if data["is_pro"] and data["pro_expires"]:
        expires = datetime.fromisoformat(data["pro_expires"])
        if datetime.now() > expires:
            data["is_pro"] = False
            data["pro_expires"] = None
    
    return BillingInfo(
        user_id=user_id,
        remaining_free=data["free_remaining"],
        is_pro=data["is_pro"],
        pro_expires_at=data["pro_expires"],
        total_generated=data["total_generated"],
    )


def record_generation(user_id: str) -> BillingInfo:
    """记录一次生成"""
    if user_id not in _user_storage:
        get_billing_info(user_id)  # 初始化
    
    data = _user_storage[user_id]
    
    # 不对Pro用户扣减次数
    if not data["is_pro"]:
        data["free_remaining"] = max(0, data["free_remaining"] - 1)
    
    data["total_generated"] += 1
    
    return get_billing_info(user_id)


def activate_pro(user_id: str, days: int = PRO_DAYS_VALID) -> BillingInfo:
    """激活Pro会员"""
    if user_id not in _user_storage:
        get_billing_info(user_id)
    
    data = _user_storage[user_id]
    data["is_pro"] = True
    
    # 累加时间
    if data["pro_expires"]:
        current_expires = datetime.fromisoformat(data["pro_expires"])
        if datetime.now() > current_expires:
            new_expires = datetime.now() + timedelta(days=days)
        else:
            new_expires = current_expires + timedelta(days=days)
    else:
        new_expires = datetime.now() + timedelta(days=days)
    
    data["pro_expires"] = new_expires.isoformat()
    
    return get_billing_info(user_id)


def check_generation_quota(user_id: str) -> tuple[bool, str]:
    """
    检查是否可以进行生成
    返回: (can_generate: bool, message: str)
    """
    billing = get_billing_info(user_id)
    
    if billing.can_generate():
        if billing.is_pro:
            return True, "Pro会员无限次生成"
        else:
            return True, f"免费剩余 {billing.remaining_free} 次"
    else:
        return False, f"免费次数已用完（{billing.remaining_free}/3）"


def get_pricing_info() -> dict:
    """获取定价信息"""
    return {
        "free_generations": FREE_GENERATIONS_PER_MONTH,
        "pro_price": PRO_PRICE_YUAN,
        "pro_features": [
            "无限次生成",
            "优先AI处理",
            "支持批量生成",
            "专属客服支持",
        ],
        "upgrade_url": "/#/pro",
    }


# 演示/测试用：预设一些用户
def init_demo_users():
    """初始化演示用户"""
    demo_users = [
        "demo_user_001",
        "test_user_001",
        "pro_user_demo",
    ]
    for uid in demo_users:
        if uid not in _user_storage:
            _user_storage[uid] = {
                "free_remaining": FREE_GENERATIONS_PER_MONTH,
                "is_pro": False,
                "pro_expires": None,
                "total_generated": 0,
                "created_at": datetime.now().isoformat(),
            }
    
    # Pro测试用户
    _user_storage["pro_user_demo"]["is_pro"] = True
    _user_storage["pro_user_demo"]["pro_expires"] = (datetime.now() + timedelta(days=30)).isoformat()


# 启动时初始化
init_demo_users()
