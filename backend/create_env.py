#!/usr/bin/env python3
"""创建.env文件的脚本"""

env_content = """GEMINI_API_KEY=AIzaSyCB2cI-2SYqvtuLQJoc7FXhMK7I0nkpBDk
LANGSMITH_API_KEY=lsv2_pt_placeholder_for_development
"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("✅ .env 文件已创建")
print("内容:")
print(env_content) 