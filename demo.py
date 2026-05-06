#!/usr/bin/env python3
"""
跨境宝贝 - API演示脚本
演示如何调用生成API
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def demo_generate():
    """演示产品描述生成"""
    
    # 示例产品信息
    product_info = {
        "product_name": "无线蓝牙降噪耳机",
        "product_description": """
        主动降噪设计（ANC），可过滤高达38dB环境噪音
        40mm定制动圈单元，支持Hi-Res认证音质
        30小时超长续航，支持快充（充电10分钟播放5小时）
        人体工学头梁设计，蛋白皮耳罩，佩戴舒适
        支持蓝牙5.3连接，可同时连接两台设备
        折叠设计便携收纳，适合通勤、旅行、运动
        """,
        "platform": "amazon",
        "languages": ["en", "ja", "ko"],
        "style": "professional"
    }
    
    print("=" * 60)
    print("跨境宝贝 API 演示")
    print("=" * 60)
    print()
    print("📦 产品信息:")
    print(f"   名称: {product_info['product_name']}")
    print(f"   平台: {product_info['platform']}")
    print(f"   语言: {', '.join(product_info['languages'])}")
    print(f"   风格: {product_info['style']}")
    print()
    
    print("⏳ 正在调用生成API...")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/generate",
            json=product_info,
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 生成成功!")
            print()
            
            for result in data.get("results", []):
                print("-" * 50)
                print(f"🌐 {result['language_name']}")
                print("-" * 50)
                
                print(f"\n📌 产品标题:")
                print(f"   {result['product_title']['title']}")
                
                print(f"\n✨ 五点描述:")
                for i, point in enumerate(result['bullet_points']['points'], 1):
                    print(f"   {i}. {point}")
                
                print(f"\n📄 详情描述:")
                print(f"   {result['product_description']['plain_text'][:200]}...")
                
                print(f"\n🔍 搜索关键词:")
                print(f"   后台: {result['search_keywords']['backend_keywords']}")
                
                break  # 只显示第一个语言的结果
                
            print()
            print(f"📊 剩余免费次数: {data.get('remaining_free_generations', 'N/A')}")
            print(f"🏆 Pro会员: {'是' if data.get('is_pro') else '否'}")
            
        else:
            print(f"❌ 生成失败: {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器")
        print("   请确保服务器已启动: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ 错误: {e}")


def demo_billing():
    """演示计费API"""
    print("\n" + "=" * 60)
    print("计费API演示")
    print("=" * 60)
    
    user_id = "demo_user"
    
    # 获取计费信息
    response = requests.get(f"{BASE_URL}/api/billing?user_id={user_id}")
    if response.status_code == 200:
        data = response.json()
        print(f"\n用户: {data['user_id']}")
        print(f"剩余免费次数: {data['remaining_free']}")
        print(f"Pro会员: {'是' if data['is_pro'] else '否'}")
        print(f"总生成次数: {data['total_generated']}")
    
    # 获取定价信息
    response = requests.get(f"{BASE_URL}/api/pricing")
    if response.status_code == 200:
        data = response.json()
        print(f"\n💰 定价方案:")
        print(f"   免费版: {data['free_generations']}次/月")
        print(f"   Pro版: ¥{data['pro_price']}/月")
        print(f"   Pro特权: {', '.join(data['pro_features'])}")


def demo_health():
    """演示健康检查"""
    print("\n" + "=" * 60)
    print("健康检查")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ 服务状态: {data['status']}")
        print(f"   服务名称: {data['service']}")


if __name__ == "__main__":
    print("\n🧪 跨境宝贝 CrossBorder Pro - API演示")
    print("   一个产品，卖遍全球\n")
    
    demo_health()
    demo_billing()
    demo_generate()
