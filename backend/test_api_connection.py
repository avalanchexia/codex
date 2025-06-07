#!/usr/bin/env python3
"""
测试 Gemini API 连接的脚本
用于验证环境变量设置和 API 调用是否正常
"""

import os
import sys
from dotenv import load_dotenv
from google.genai import Client
from langchain_google_genai import ChatGoogleGenerativeAI

def test_environment_variables():
    """测试环境变量设置"""
    print("=== 测试环境变量 ===")
    
    load_dotenv()
    
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("❌ GEMINI_API_KEY 未设置")
        return False
    
    print(f"✅ GEMINI_API_KEY 已设置: {gemini_api_key[:10]}...")
    
    if not gemini_api_key.startswith("AIza"):
        print("⚠️  警告: GEMINI_API_KEY 格式可能不正确")
    
    return True

def test_gemini_client():
    """测试 Google GenAI 客户端"""
    print("\n=== 测试 Google GenAI 客户端 ===")
    
    try:
        client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        # 简单的测试调用
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Hello, this is a test. Please respond with 'API connection successful'.",
            config={"temperature": 0}
        )
        
        print(f"✅ GenAI 客户端测试成功")
        print(f"响应: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ GenAI 客户端测试失败: {e}")
        return False

def test_langchain_gemini():
    """测试 LangChain Gemini 集成"""
    print("\n=== 测试 LangChain Gemini 集成 ===")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0,
            max_retries=2,
            api_key=os.getenv("GEMINI_API_KEY"),
        )
        
        response = llm.invoke("Hello, this is a test. Please respond with 'LangChain integration successful'.")
        print(f"✅ LangChain Gemini 测试成功")
        print(f"响应: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ LangChain Gemini 测试失败: {e}")
        return False

def test_google_search():
    """测试 Google Search API"""
    print("\n=== 测试 Google Search API ===")
    
    try:
        client = Client(api_key=os.getenv("GEMINI_API_KEY"))
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents="Search for information about Python programming language",
            config={
                "tools": [{"google_search": {}}],
                "temperature": 0,
            }
        )
        
        print(f"✅ Google Search API 测试成功")
        print(f"响应长度: {len(response.text)} 字符")
        
        # 检查是否有 grounding metadata
        if hasattr(response.candidates[0], 'grounding_metadata'):
            print(f"✅ 找到 grounding metadata")
        else:
            print("⚠️  未找到 grounding metadata")
        
        return True
        
    except Exception as e:
        print(f"❌ Google Search API 测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试 Gemini API 连接...")
    
    tests = [
        test_environment_variables,
        test_gemini_client,
        test_langchain_gemini,
        test_google_search
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ 测试过程中发生未预期错误: {e}")
            results.append(False)
    
    print("\n=== 测试总结 ===")
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！API 连接正常。")
        return 0
    else:
        print("⚠️  部分测试失败，请检查配置和网络连接。")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 