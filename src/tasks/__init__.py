"""
反诈骗智能检测系统 - 任务模块
"""

from .anti_fraud_tasks import (
    create_monitor_task,
    create_profile_task,
    create_defend_task
)

__all__ = [
    'create_monitor_task',
    'create_profile_task',
    'create_defend_task'
]
