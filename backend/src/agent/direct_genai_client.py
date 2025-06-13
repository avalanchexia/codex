#!/usr/bin/env python3
"""
直接使用 Google GenAI 客户端的替代实现
避免 LangChain 的 gRPC 连接问题
"""

import os
import logging
from typing import Dict, Any, Optional
from google.genai import Client
from dotenv import load_dotenv

# 设置日志
logger = logging.getLogger(__name__)

class DirectGenAIClient:
    """直接使用 Google GenAI 客户端的包装器"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.0-flash-exp"):
        """
        初始化客户端
        
        Args:
            api_key: Gemini API 密钥，如果为 None 则从环境变量获取
            model: 使用的模型名称
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY 未设置")
        
        self.model = model
        self.client = Client(api_key=self.api_key)
        
        logger.info(f"DirectGenAIClient 初始化完成，使用模型: {self.model}")
    
    def invoke(self, prompt: str, **kwargs) -> str:
        """
        调用模型生成响应
        
        Args:
            prompt: 输入提示
            **kwargs: 额外参数（temperature, max_tokens 等）
            
        Returns:
            生成的响应文本
        """
        try:
            # 构建配置
            config = {
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2048),
            }
            
            # 如果需要搜索功能
            tools = []
            if kwargs.get("use_search", False):
                tools.append({"google_search": {}})
            
            if tools:
                config["tools"] = tools
            
            logger.debug(f"调用模型 {self.model}，配置: {config}")
            
            # 调用 API
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            result = response.text
            logger.debug(f"模型响应长度: {len(result)} 字符")
            
            return result
            
        except Exception as e:
            logger.error(f"DirectGenAIClient 调用失败: {e}")
            raise
    
    def stream(self, prompt: str, **kwargs):
        """
        流式调用模型
        
        Args:
            prompt: 输入提示
            **kwargs: 额外参数
            
        Yields:
            生成的响应片段
        """
        try:
            config = {
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2048),
            }
            
            tools = []
            if kwargs.get("use_search", False):
                tools.append({"google_search": {}})
            
            if tools:
                config["tools"] = tools
            
            logger.debug(f"流式调用模型 {self.model}")
            
            # 流式调用
            response = self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"DirectGenAIClient 流式调用失败: {e}")
            raise

def create_direct_genai_llm(model: str = "gemini-2.0-flash-exp", **kwargs) -> DirectGenAIClient:
    """
    创建 DirectGenAIClient 实例的便捷函数
    
    Args:
        model: 模型名称
        **kwargs: 额外参数
        
    Returns:
        DirectGenAIClient 实例
    """
    return DirectGenAIClient(model=model, **kwargs)

# 测试函数
def test_direct_genai_client():
    """测试 DirectGenAIClient"""
    try:
        client = DirectGenAIClient()
        response = client.invoke("Hello, please respond with 'Direct GenAI client working!'")
        print(f"✅ DirectGenAIClient 测试成功: {response}")
        return True
    except Exception as e:
        print(f"❌ DirectGenAIClient 测试失败: {e}")
        return False

if __name__ == "__main__":
    test_direct_genai_client() 