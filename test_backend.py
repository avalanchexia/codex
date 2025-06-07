#!/usr/bin/env python3
"""测试后端API连接"""

import requests
import json
import time

def test_backend_api():
    """测试后端API是否正常工作"""
    base_url = "http://127.0.0.1:2024"
    
    try:
        # 1. 测试API文档
        print("🔍 测试API文档...")
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API文档可访问")
        else:
            print(f"❌ API文档访问失败: {response.status_code}")
            return False
        
        # 2. 测试创建线程
        print("🔍 测试创建线程...")
        thread_response = requests.post(
            f"{base_url}/threads",
            json={},
            timeout=10
        )
        
        if thread_response.status_code == 200:
            thread_data = thread_response.json()
            thread_id = thread_data.get("thread_id")
            print(f"✅ 线程创建成功: {thread_id}")
            
            # 3. 测试发送消息
            print("🔍 测试发送消息...")
            message_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": "Who won the Euro 2024?"
                    }
                ],
                "config": {
                    "configurable": {
                        "query_generator_model": "gemini-2.0-flash-exp",
                        "reasoning_model": "gemini-2.0-flash-exp"
                    }
                }
            }
            
            run_response = requests.post(
                f"{base_url}/threads/{thread_id}/runs",
                json=message_data,
                timeout=30
            )
            
            if run_response.status_code == 200:
                run_data = run_response.json()
                run_id = run_data.get("run_id")
                print(f"✅ 消息发送成功: {run_id}")
                return True
            else:
                print(f"❌ 消息发送失败: {run_response.status_code}")
                print(f"错误信息: {run_response.text}")
                return False
        else:
            print(f"❌ 线程创建失败: {thread_response.status_code}")
            print(f"错误信息: {thread_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 - 请确保后端正在运行")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("后端API连接测试")
    print("=" * 50)
    
    success = test_backend_api()
    
    if success:
        print("\n🎉 后端API测试成功！")
        print("现在可以在前端页面测试功能了")
    else:
        print("\n🔧 后端API测试失败，请检查后端服务")
    
    print("=" * 50) 