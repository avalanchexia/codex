#!/usr/bin/env python3
"""快速API测试"""

import os
import requests
import json

# 直接设置API密钥
api_key = "AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk"

def test_gemini_rest_api():
    """使用REST API测试Gemini"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "contents": [{
            "parts": [{
                "text": "Hello, please respond with 'API test successful'"
            }]
        }]
    }
    
    try:
        print("🔍 测试 Gemini REST API...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                text = result['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API 测试成功!")
                print(f"响应: {text}")
                return True
            else:
                print("❌ 响应格式异常")
                print(f"响应内容: {result}")
        else:
            print(f"❌ API 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时 - 可能是网络问题")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误 - 请检查网络连接")
    except Exception as e:
        print(f"❌ 其他错误: {e}")
    
    return False

if __name__ == "__main__":
    print("=" * 50)
    print("快速 Gemini API 测试")
    print("=" * 50)
    
    success = test_gemini_rest_api()
    
    if not success:
        print("\n可能的问题:")
        print("1. 网络连接问题")
        print("2. API密钥无效或过期")
        print("3. API配额已用完")
        print("4. 防火墙阻止连接")
    
    print("=" * 50) 