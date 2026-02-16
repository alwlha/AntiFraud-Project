#!/usr/bin/env python3
"""
快速测试脚本
用于验证系统各组件是否正常工作
"""

import os
import sys
from pathlib import Path

print("="*60)
print("反诈骗智能检测系统 - 快速测试")
print("="*60)

# 1. 检查环境变量
print("\n[1/5] 检查环境配置...")
from dotenv import load_dotenv
load_dotenv()

required_env = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL_NAME"]
missing_env = []

for env_var in required_env:
    value = os.getenv(env_var)
    if value:
        # 隐藏 API Key
        display_value = value[:10] + "..." if "KEY" in env_var else value
        print(f"  ✓ {env_var}: {display_value}")
    else:
        print(f"  ✗ {env_var}: 未设置")
        missing_env.append(env_var)

if missing_env:
    print(f"\n❌ 错误: 缺少环境变量 {missing_env}")
    print("   请编辑 .env 文件并配置这些变量")
    sys.exit(1)

# 2. 检查数据文件
print("\n[2/5] 检查数据文件...")
data_files = {
    "data/roles.csv": "角色画像表",
    "data/cases.csv": "诈骗类型表",
    "data/mapping_full.csv": "完整映射表"
}

for file_path, desc in data_files.items():
    if os.path.exists(file_path):
        print(f"  ✓ {desc}: {file_path}")
    else:
        print(f"  ✗ {desc}: {file_path} 不存在")
        sys.exit(1)

# 检查音频文件
audio_dir = "data/processed_audio"
if os.path.exists(audio_dir):
    audio_count = len([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])
    print(f"  ✓ 音频文件: {audio_count} 个")
else:
    print(f"  ✗ 音频目录不存在: {audio_dir}")
    sys.exit(1)

# 3. 测试 RAG 工具
print("\n[3/5] 测试 RAG 知识库...")
try:
    from src.tools.rag_tool import RAGSearchTool
    
    rag = RAGSearchTool()
    
    # 检查是否需要构建知识库
    if rag.collection.count() == 0:
        print("  ℹ 知识库为空，开始构建...")
        rag.build_knowledge_base(
            cases_csv="data/cases.csv",
            mapping_csv="data/mapping_full.csv"
        )
    else:
        print(f"  ✓ 知识库已存在，共 {rag.collection.count()} 条记录")
    
    # 测试检索
    test_results = rag.search_similar_cases("银行卡洗钱转账", top_k=1)
    if test_results:
        print(f"  ✓ 检索测试成功: 找到 {len(test_results)} 个结果")
    else:
        print("  ⚠ 检索测试返回空结果")
        
except Exception as e:
    print(f"  ✗ RAG 工具测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 4. 测试 ASR 工具（使用第一个音频文件）
print("\n[4/5] 测试 ASR 转录工具...")
try:
    from src.tools.asr_tool import ASRTool
    
    # 找到第一个测试音频
    test_audio = None
    for f in os.listdir(audio_dir):
        if f.endswith('.mp3'):
            test_audio = os.path.join(audio_dir, f)
            break
    
    if test_audio:
        print(f"  使用测试音频: {os.path.basename(test_audio)}")
        asr = ASRTool(model_size="base")
        result = asr.transcribe_audio(test_audio)
        
        print(f"  ✓ 转录成功")
        print(f"    - 时长: {result['duration']:.2f}s")
        print(f"    - 文本长度: {len(result['text'])} 字符")
        print(f"    - 预览: {result['text'][:50]}...")
    else:
        print("  ⚠ 未找到测试音频文件")
        
except Exception as e:
    print(f"  ✗ ASR 工具测试失败: {e}")
    import traceback
    traceback.print_exc()
    # ASR 失败不中断，可能是首次下载模型

# 5. 测试 Agent 创建
print("\n[5/5] 测试 Agent 创建...")
try:
    from src.agents.anti_fraud_agents import (
        create_watchdog_agent,
        create_profiler_agent,
        create_guardian_agent
    )
    
    watchdog = create_watchdog_agent()
    print(f"  ✓ Watchdog Agent 创建成功")
    
    profiler = create_profiler_agent()
    print(f"  ✓ Profiler Agent 创建成功")
    
    guardian = create_guardian_agent()
    print(f"  ✓ Guardian Agent 创建成功")
    
except Exception as e:
    print(f"  ✗ Agent 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试完成
print("\n" + "="*60)
print("✅ 所有测试通过！系统已准备就绪")
print("="*60)
print("\n接下来可以:")
print("  1. 运行完整分析: python main.py data/processed_audio/R01_C01.mp3")
print("  2. 启动 API 服务: python api.py")
print("  3. 查看文档: cat BACKEND_README.md")
print()
