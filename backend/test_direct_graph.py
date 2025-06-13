#!/usr/bin/env python3
"""
测试使用直接 GenAI 客户端的图实现
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_direct_graph():
    """测试直接 GenAI 客户端的图实现"""
    load_dotenv()
    
    # 禁用 LangSmith 追踪
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    
    print("=== 测试直接 GenAI 客户端图实现 ===")
    
    try:
        # 导入图模块
        from agent.graph_direct import create_graph
        print("✅ 成功导入直接图模块")
        
        # 创建图
        graph = create_graph()
        print("✅ 成功创建图实例")
        
        # 准备测试输入
        test_message = HumanMessage(content="什么是人工智能？")
        initial_state = {
            "messages": [test_message],
            "initial_search_query_count": 2,  # 减少查询数量以加快测试
        }
        
        print("🔄 开始测试图执行...")
        print(f"测试问题: {test_message.content}")
        
        # 执行图（使用超时）
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("图执行超时")
        
        # 在 Windows 上不支持 signal.alarm，所以我们使用简单的执行
        try:
            result = graph.invoke(initial_state)
            print("✅ 图执行成功完成")
            
            # 检查结果
            if "messages" in result and result["messages"]:
                final_message = result["messages"][-1]
                print(f"📝 最终答案长度: {len(final_message.content)} 字符")
                print(f"📝 答案预览: {final_message.content[:200]}...")
                return True
            else:
                print("⚠️  未找到最终答案")
                return False
                
        except Exception as e:
            print(f"❌ 图执行失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_individual_components():
    """测试各个组件"""
    print("\n=== 测试各个组件 ===")
    
    try:
        # 测试直接客户端
        from agent.direct_genai_client import DirectGenAIClient
        client = DirectGenAIClient()
        response = client.invoke("简单测试：请回复'组件测试成功'")
        print(f"✅ 直接客户端测试: {response}")
        
        # 测试结构化输出解析
        from agent.graph_direct import parse_structured_output
        test_json = '{"query": ["测试查询1", "测试查询2"], "rationale": "测试用查询"}'
        result = parse_structured_output(test_json, "SearchQueryList")
        print(f"✅ 结构化输出解析测试: {result.query}")
        
        return True
        
    except Exception as e:
        print(f"❌ 组件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试直接 GenAI 客户端图实现...")
    print("=" * 60)
    
    # 测试各个组件
    components_ok = test_individual_components()
    
    if components_ok:
        # 测试完整图
        graph_ok = test_direct_graph()
        
        print("\n" + "=" * 60)
        print("=== 测试总结 ===")
        
        if graph_ok:
            print("🎉 所有测试通过！直接 GenAI 客户端图实现工作正常。")
            print("\n建议:")
            print("1. 可以使用 graph_direct.py 替代原始的 graph.py")
            print("2. 这样可以避免 LangChain 的 gRPC 连接问题")
            print("3. 保持所有功能不变，只是使用不同的底层客户端")
            return 0
        else:
            print("⚠️  图测试失败，但组件测试通过")
            print("可能需要进一步调试图的执行逻辑")
            return 1
    else:
        print("❌ 组件测试失败，请检查基础配置")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 