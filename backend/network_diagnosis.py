#!/usr/bin/env python3
"""
网络诊断脚本
用于诊断 LangChain Gemini 集成的网络连接问题
"""

import os
import ssl
import socket
import requests
from dotenv import load_dotenv

def check_network_connectivity():
    """检查基本网络连接"""
    print("=== 网络连接诊断 ===")
    
    # 检查基本网络连接
    try:
        response = requests.get("https://www.google.com", timeout=10)
        print("✅ 基本网络连接正常")
    except Exception as e:
        print(f"❌ 基本网络连接失败: {e}")
        return False
    
    # 检查 Google API 端点
    try:
        response = requests.get("https://generativelanguage.googleapis.com", timeout=10)
        print("✅ Google Generative Language API 端点可达")
    except Exception as e:
        print(f"❌ Google API 端点连接失败: {e}")
        print("   这可能表明存在防火墙或代理问题")
    
    return True

def check_ssl_certificates():
    """检查 SSL 证书配置"""
    print("\n=== SSL 证书诊断 ===")
    
    hostname = "generativelanguage.googleapis.com"
    port = 443
    
    try:
        # 创建 SSL 上下文
        context = ssl.create_default_context()
        
        # 尝试连接
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                print(f"✅ SSL 连接成功到 {hostname}")
                print(f"   证书主题: {cert.get('subject', 'Unknown')}")
                print(f"   证书颁发者: {cert.get('issuer', 'Unknown')}")
                
    except ssl.SSLError as e:
        print(f"❌ SSL 错误: {e}")
        print("   这表明存在证书验证问题")
        print("   可能的解决方案:")
        print("   1. 检查系统时间是否正确")
        print("   2. 更新系统证书存储")
        print("   3. 如果使用代理，需要导入代理的根证书")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        return False
    
    return True

def check_proxy_settings():
    """检查代理设置"""
    print("\n=== 代理设置检查 ===")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    proxy_found = False
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"🔍 发现代理设置: {var}={value}")
            proxy_found = True
    
    if not proxy_found:
        print("ℹ️  未检测到代理环境变量")
    else:
        print("⚠️  检测到代理设置，这可能影响 gRPC 连接")
        print("   建议:")
        print("   1. 确保代理支持 gRPC 流量")
        print("   2. 配置 GRPC_DEFAULT_SSL_ROOTS_FILE_PATH 环境变量")
    
    return proxy_found

def test_grpc_connection():
    """测试 gRPC 连接"""
    print("\n=== gRPC 连接测试 ===")
    
    try:
        # 尝试导入 grpc
        import grpc
        print("✅ gRPC 库可用")
        
        # 尝试创建 gRPC 通道
        channel = grpc.insecure_channel('generativelanguage.googleapis.com:443')
        
        # 检查通道状态
        try:
            grpc.channel_ready_future(channel).result(timeout=10)
            print("✅ gRPC 通道连接成功")
            channel.close()
            return True
        except grpc.FutureTimeoutError:
            print("❌ gRPC 通道连接超时")
            channel.close()
            return False
            
    except ImportError:
        print("⚠️  gRPC 库未安装")
        return False
    except Exception as e:
        print(f"❌ gRPC 连接测试失败: {e}")
        return False

def suggest_solutions():
    """提供解决方案建议"""
    print("\n=== 解决方案建议 ===")
    
    print("基于诊断结果，建议尝试以下解决方案:")
    print()
    print("1. **网络配置**:")
    print("   - 确保防火墙允许出站 gRPC 流量到 Google 端点")
    print("   - 检查企业网络是否阻止 gRPC 协议")
    print()
    print("2. **代理配置** (如果使用代理):")
    print("   - 在 LangChain 中配置代理:")
    print("     ChatGoogleGenerativeAI(proxy='http://your-proxy:port')")
    print("   - 设置 gRPC SSL 根证书路径:")
    print("     os.environ['GRPC_DEFAULT_SSL_ROOTS_FILE_PATH'] = 'path/to/ca.pem'")
    print()
    print("3. **证书问题**:")
    print("   - 更新系统证书存储")
    print("   - 如果网络进行 TLS 拦截，导入代理的根证书")
    print()
    print("4. **临时解决方案**:")
    print("   - 使用直接的 Google GenAI 客户端而不是 LangChain 包装器")
    print("   - 在代码中实现超时和重试机制 (已在后端实现)")

def main():
    """主诊断函数"""
    print("开始网络诊断...")
    print("=" * 50)
    
    load_dotenv()
    
    # 运行所有诊断
    network_ok = check_network_connectivity()
    ssl_ok = check_ssl_certificates()
    proxy_detected = check_proxy_settings()
    grpc_ok = test_grpc_connection()
    
    print("\n" + "=" * 50)
    print("=== 诊断总结 ===")
    
    if network_ok and ssl_ok and grpc_ok:
        print("🎉 网络配置看起来正常，LangChain 应该可以工作")
    else:
        print("⚠️  检测到网络配置问题")
        if not network_ok:
            print("   - 基本网络连接有问题")
        if not ssl_ok:
            print("   - SSL/TLS 证书验证失败")
        if not grpc_ok:
            print("   - gRPC 连接无法建立")
        if proxy_detected:
            print("   - 检测到代理，可能需要额外配置")
    
    suggest_solutions()

if __name__ == "__main__":
    main() 