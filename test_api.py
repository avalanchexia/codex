#!/usr/bin/env python3
"""
简单的Gemini API测试脚本
用于验证API密钥是否有效
"""

import os
from dotenv import load_dotenv

# 加载环境变量（从backend目录）
load_dotenv("backend/.env")

def test_gemini_api():
    """测试Gemini API连接"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "placeholder":
        print("❌ 错误: GEMINI_API_KEY 未设置或使用占位符")
        print("请在 .env 文件中设置有效的 API 密钥")
        return False
    
    try:
        # 尝试导入和使用 Google Generative AI
        import google.generativeai as genai
        
        # 配置API密钥
        genai.configure(api_key=api_key)
        
        # 创建模型实例
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # 发送简单测试请求
        print("🔍 测试 Gemini API 连接...")
        response = model.generate_content("Hello, please respond with 'API test successful'")
        
        if response and response.text:
            print(f"✅ API 测试成功!")
            print(f"响应: {response.text}")
            return True
        else:
            print("❌ API 响应为空")
            return False
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装 google-generativeai: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        print("请检查:")
        print("1. API 密钥是否有效")
        print("2. 网络连接是否正常")
        print("3. API 配额是否充足")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Gemini API 连接测试")
    print("=" * 50)
    
    success = test_gemini_api()
    
    if success:
        print("\n🎉 API 配置正确，可以正常使用!")
    else:
        print("\n🔧 请修复上述问题后重新测试")
    
    print("=" * 50) 