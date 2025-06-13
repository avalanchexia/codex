#!/usr/bin/env python3
"""快速测试 LangChain Gemini 集成"""

import os
from dotenv import load_dotenv

def test_langchain_gemini():
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
        )
        print('✅ 创建 LLM 实例成功')
        
        response = llm.invoke('Hello, respond with: LangChain integration successful')
        print(f'✅ LangChain Gemini 集成成功!')
        print(f'响应: {response.content}')
        return True
        
    except Exception as e:
        print(f'❌ LangChain Gemini 集成失败: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_langchain_gemini() 