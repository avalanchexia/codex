#!/usr/bin/env python3
"""带超时的 LangChain Gemini 集成测试"""

import os
import signal
import sys
from dotenv import load_dotenv

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("操作超时")

def test_langchain_gemini_with_timeout():
    load_dotenv()
    os.environ['LANGCHAIN_TRACING_V2'] = 'false'
    
    print('开始 LangChain Gemini 测试...')
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print('✅ 导入 ChatGoogleGenerativeAI 成功')
        
        llm = ChatGoogleGenerativeAI(
            model='gemini-2.0-flash-exp',
            temperature=0,
            max_retries=2,
            api_key=os.getenv('GEMINI_API_KEY'),
            timeout=30,  # 添加超时设置
        )
        print('✅ 创建 LLM 实例成功')
        
        # 设置 30 秒超时
        if sys.platform != 'win32':
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
        
        print('🔄 正在调用 LLM...')
        response = llm.invoke('Hello, respond with: LangChain integration successful')
        
        if sys.platform != 'win32':
            signal.alarm(0)  # 取消超时
        
        print(f'✅ LangChain Gemini 集成成功!')
        print(f'响应: {response.content}')
        return True
        
    except TimeoutError:
        print('❌ LangChain Gemini 调用超时 (30秒)')
        return False
    except Exception as e:
        print(f'❌ LangChain Gemini 集成失败: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = test_langchain_gemini_with_timeout()
    if result:
        print('\n🎉 LangChain Gemini 集成测试通过!')
    else:
        print('\n⚠️ LangChain Gemini 集成测试失败')
        print('可能的原因:')
        print('1. 网络连接问题')
        print('2. API 密钥权限问题') 
        print('3. Gemini API 服务暂时不可用')
        print('4. 防火墙或代理设置问题') 