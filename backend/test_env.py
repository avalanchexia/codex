#!/usr/bin/env python3
import os
from dotenv import load_dotenv

print("Current directory:", os.getcwd())
print("Env file exists:", os.path.exists('.env'))

# 读取文件内容
try:
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
        print("File content:")
        print(repr(content))
except Exception as e:
    print("Error reading file:", e)

# 测试 load_dotenv
print("\nTesting load_dotenv:")
result = load_dotenv('.env')
print("load_dotenv result:", result)

# 检查环境变量
api_key = os.getenv('GEMINI_API_KEY')
print("GEMINI_API_KEY:", api_key)

# 直接设置环境变量测试
os.environ['GEMINI_API_KEY'] = 'AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk'
print("After manual set:", os.getenv('GEMINI_API_KEY')) 