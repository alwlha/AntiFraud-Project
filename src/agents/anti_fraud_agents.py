"""
核心 Agent 定义模块
定义三个反诈智能体：Watchdog, Profiler, Guardian
"""

import os
import yaml
from crewai import Agent
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置 LLM
def get_llm():
    """获取配置好的 LLM 实例"""
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL", "https://xiaoai.plus/v1"),
        temperature=0.3  # 较低温度确保输出稳定
    )


def load_agent_config(config_path: str = "./config/agents.yaml") -> dict:
    """加载 Agent 配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_watchdog_agent(llm=None) -> Agent:
    """
    创建 Watchdog Agent - 监控专家
    负责快速扫描文本，识别诈骗高危信号
    """
    if llm is None:
        llm = get_llm()
    
    config = load_agent_config()['watchdog']
    
    return Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=config['backstory'],
        llm=llm,
        verbose=True,
        allow_delegation=False,  # 不委托给其他 Agent
        max_iter=3  # 限制推理轮数
    )


def create_profiler_agent(llm=None, tools=None) -> Agent:
    """
    创建 Profiler Agent - 侧写师
    负责通过 RAG 检索匹配诈骗类型
    """
    if llm is None:
        llm = get_llm()
    
    config = load_agent_config()['profiler']
    
    return Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=config['backstory'],
        llm=llm,
        tools=tools or [],  # 需要 RAG 检索工具
        verbose=True,
        allow_delegation=False,
        max_iter=5
    )


def create_guardian_agent(llm=None) -> Agent:
    """
    创建 Guardian Agent - 守护者
    负责生成个性化防御话术
    """
    if llm is None:
        llm = get_llm()
    
    config = load_agent_config()['guardian']
    
    return Agent(
        role=config['role'],
        goal=config['goal'],
        backstory=config['backstory'],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_iter=3
    )


if __name__ == "__main__":
    # 测试 Agent 创建
    print("\n=== 测试 Agent 创建 ===\n")
    
    print("1. 创建 Watchdog Agent...")
    watchdog = create_watchdog_agent()
    print(f"   角色: {watchdog.role}")
    print(f"   目标: {watchdog.goal[:50]}...")
    
    print("\n2. 创建 Profiler Agent...")
    profiler = create_profiler_agent()
    print(f"   角色: {profiler.role}")
    print(f"   目标: {profiler.goal[:50]}...")
    
    print("\n3. 创建 Guardian Agent...")
    guardian = create_guardian_agent()
    print(f"   角色: {guardian.role}")
    print(f"   目标: {guardian.goal[:50]}...")
    
    print("\n✅ 所有 Agent 创建成功！")
