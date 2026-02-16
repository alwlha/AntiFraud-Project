"""
CrewAI 任务定义模块
定义三个顺序执行的任务：监控 -> 侧写 -> 防御
"""

import yaml
from crewai import Task


def load_task_config(config_path: str = "./config/tasks.yaml") -> dict:
    """加载任务配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def create_monitor_task(agent, transcript_text: str) -> Task:
    """
    创建监控任务
    
    Args:
        agent: Watchdog Agent
        transcript_text: 转录的通话文本
        
    Returns:
        Task 对象
    """
    config = load_task_config()['monitor_task']
    
    return Task(
        description=config['description'].format(transcript_text=transcript_text),
        expected_output=config['expected_output'],
        agent=agent
    )


def create_profile_task(agent, monitor_result: str, transcript_text: str) -> Task:
    """
    创建侧写任务
    
    Args:
        agent: Profiler Agent
        monitor_result: 监控任务的输出结果
        transcript_text: 原始转录文本
        
    Returns:
        Task 对象
    """
    config = load_task_config()['profile_task']
    
    return Task(
        description=config['description'].format(
            monitor_result=monitor_result,
            transcript_text=transcript_text
        ),
        expected_output=config['expected_output'],
        agent=agent
    )


def create_defend_task(
    agent,
    monitor_result: str,
    profile_result: str,
    victim_info: dict
) -> Task:
    """
    创建防御任务
    
    Args:
        agent: Guardian Agent
        monitor_result: 监控结果
        profile_result: 侧写结果
        victim_info: 受害者信息字典，包含 name, age, tag, weakness
        
    Returns:
        Task 对象
    """
    config = load_task_config()['defend_task']
    
    return Task(
        description=config['description'].format(
            victim_name=victim_info.get('name', '用户'),
            victim_age=victim_info.get('age', '未知'),
            victim_tag=victim_info.get('tag', '普通用户'),
            victim_weakness=victim_info.get('weakness', '无特殊信息'),
            monitor_result=monitor_result,
            profile_result=profile_result
        ),
        expected_output=config['expected_output'],
        agent=agent
    )


if __name__ == "__main__":
    # 测试任务创建
    print("\n=== 测试 Task 创建 ===\n")
    
    from src.agents.anti_fraud_agents import (
        create_watchdog_agent,
        create_profiler_agent,
        create_guardian_agent
    )
    
    # 创建 Agents
    watchdog = create_watchdog_agent()
    profiler = create_profiler_agent()
    guardian = create_guardian_agent()
    
    # 测试数据
    test_transcript = "您好，我是建设银行客服，您的账户涉嫌洗钱，需要立即转账到安全账户..."
    test_victim = {
        'name': '李奶奶',
        'age': 72,
        'tag': '独居老人',
        'weakness': '关心孙辈，对智能手机不熟'
    }
    
    print("1. 创建监控任务...")
    monitor_task = create_monitor_task(watchdog, test_transcript)
    print(f"   描述长度: {len(monitor_task.description)} 字符")
    
    print("\n2. 创建侧写任务...")
    profile_task = create_profile_task(profiler, "[监控结果占位]", test_transcript)
    print(f"   描述长度: {len(profile_task.description)} 字符")
    
    print("\n3. 创建防御任务...")
    defend_task = create_defend_task(guardian, "[监控结果]", "[侧写结果]", test_victim)
    print(f"   描述长度: {len(defend_task.description)} 字符")
    
    print("\n✅ 所有 Task 创建成功！")
