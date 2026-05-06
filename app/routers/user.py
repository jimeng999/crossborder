"""用户相关路由"""
from fastapi import APIRouter

router = APIRouter(prefix="/api/user", tags=["用户"])


@router.get("/status")
async def get_user_status():
    """获取用户状态（模拟）"""
    return {
        "user_id": "guest",
        "is_logged_in": False,
        "remaining_free": 3,
        "is_pro": False,
    }


@router.post("/feedback")
async def submit_feedback(feedback: dict):
    """提交反馈"""
    return {
        "success": True,
        "message": "感谢您的反馈！"
    }
