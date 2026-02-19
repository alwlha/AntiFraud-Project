"""
反诈骗智能检测系统 - 主程序
整合 ASR、RAG、CrewAI 智能体实现端到端的诈骗识别与防御
"""

import os
import sys
import pandas as pd
from typing import Dict, Optional
from dotenv import load_dotenv
from crewai import Crew, Process
import logging

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools.asr_tool import ASRTool
from src.tools.rag_tool import RAGSearchTool
from src.agents.anti_fraud_agents import (
    create_watchdog_agent,
    create_profiler_agent,
    create_guardian_agent
)
from src.tasks.anti_fraud_tasks import (
    create_monitor_task,
    create_profile_task,
    create_defend_task
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()


class AntiFraudSystem:
    """反诈骗智能检测系统"""
    
    def __init__(
        self,
        whisper_model_size: str = "base",
        init_knowledge_base: bool = False
    ):
        """
        初始化系统
        
        Args:
            whisper_model_size: Whisper 模型大小
            init_knowledge_base: 是否初始化知识库（首次运行设为 True）
        """
        logger.info("🚀 初始化反诈骗智能检测系统...")
        
        # 1. 初始化 ASR 工具
        logger.info("📝 加载 Faster-Whisper 模型...")
        self.asr_tool = ASRTool(
            model_size=whisper_model_size,
            device=os.getenv("WHISPER_DEVICE", "cpu"),
            compute_type=os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        )
        
        # 2. 初始化 RAG 工具
        logger.info("📚 加载 RAG 知识库...")
        self.rag_tool = RAGSearchTool(
            persist_dir=os.getenv("CHROMA_PERSIST_DIR", "./db/chroma"),
            embedding_model=os.getenv("EMBEDDING_MODEL", 
                                     "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        )
        
        # 如果需要，构建知识库
        if init_knowledge_base:
            logger.info("🔨 构建知识库（首次运行）...")
            self.rag_tool.build_knowledge_base(
                cases_csv="./data/cases.csv",
                mapping_csv="./data/mapping_full.csv"
            )
        
        # 3. 加载角色数据
        logger.info("👥 加载受害者角色数据...")
        self.roles_df = pd.read_csv("./data/roles.csv")
        
        logger.info("✅ 系统初始化完成！")
    
    def get_victim_info(self, role_id: str) -> Dict:
        """
        根据角色 ID 获取受害者信息
        
        Args:
            role_id: 角色 ID (如 R01)
            
        Returns:
            受害者信息字典
        """
        row = self.roles_df[self.roles_df['id'] == role_id]
        
        if row.empty:
            logger.warning(f"未找到角色 {role_id}，使用默认信息")
            return {
                'name': '用户',
                'age': '未知',
                'tag': '普通用户',
                'weakness': '无特殊信息'
            }
        
        row = row.iloc[0]
        return {
            'name': row['name'],
            'age': row['age'],
            'tag': row['tag'],
            'weakness': row['weakness']
        }
    
    def analyze_audio(
        self,
        audio_path: str,
        victim_role_id: str = "R01"
    ) -> Dict:
        """
        分析音频文件，检测诈骗并生成防御建议
        
        Args:
            audio_path: 音频文件路径
            victim_role_id: 受害者角色 ID
            
        Returns:
            {
                "transcript": "转录文本",
                "risk_level": "风险等级",
                "scam_type": "诈骗类型",
                "defense_advice": "防御建议",
                "raw_results": {...}  # 完整的 Agent 输出
            }
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 开始分析音频: {audio_path}")
        logger.info(f"👤 受害者角色: {victim_role_id}")
        logger.info(f"{'='*60}\n")
        
        # Step 1: 语音转录
        logger.info("📝 Step 1: 语音转录...")
        transcript_result = self.asr_tool.transcribe_audio(audio_path)
        transcript_text = transcript_result['text']
        logger.info(f"   转录完成，文本长度: {len(transcript_text)} 字符")
        logger.info(f"   内容预览: {transcript_text[:100]}...")
        
        # Step 2: 获取受害者信息
        victim_info = self.get_victim_info(victim_role_id)
        logger.info(f"\n👤 受害者信息: {victim_info['name']} ({victim_info['age']}岁)")
        
        # Step 3: 创建智能体
        logger.info("\n🤖 Step 2: 初始化智能体...")
        watchdog = create_watchdog_agent()
        
        # 为 Profiler 创建 RAG 工具
        from crewai_tools import tool
        
        @tool("搜索诈骗案例知识库")
        def search_knowledge_base(query: str) -> str:
            """在反诈骗知识库中搜索相似案例。参数 query 必须是一个描述诈骗场景或关键词的字符串。"""
            # 兼容性处理：如果 LLM 错误地传递了字典
            if isinstance(query, dict):
                query = query.get("query", str(query))
            
            results = self.rag_tool.search_similar_cases(query, top_k=3)
            if not results:
                return "未找到相关案例。"
            
            output = "### 检索到的相似案例：\n\n"
            for i, result in enumerate(results, 1):
                output += f"**案例 {i}**: {result['case_type']}\n"
                output += f"相似度: {1 - result['distance']:.2f}\n"
                output += f"{result['document'][:200]}...\n\n"
            return output
        
        profiler = create_profiler_agent(tools=[search_knowledge_base])
        guardian = create_guardian_agent()
        
        # Step 4: 创建任务（顺序执行）
        logger.info("📋 Step 3: 创建任务流...")
        
        # 任务1: 监控
        task1 = create_monitor_task(watchdog, transcript_text)
        
        # 任务2: 侧写（依赖任务1）
        task2 = create_profile_task(
            profiler,
            monitor_result="{monitor_task_output}",  # 占位符，CrewAI 会自动替换
            transcript_text=transcript_text
        )
        task2.context = [task1]  # 设置依赖关系
        
        # 任务3: 防御（依赖任务1和任务2）
        task3 = create_defend_task(
            guardian,
            monitor_result="{monitor_task_output}",
            profile_result="{profile_task_output}",
            victim_info=victim_info
        )
        task3.context = [task1, task2]
        
        # Step 5: 创建 Crew 并执行
        logger.info("🚀 Step 4: 执行智能体协作...")
        crew = Crew(
            agents=[watchdog, profiler, guardian],
            tasks=[task1, task2, task3],
            process=Process.sequential,  # 顺序执行
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Step 6: 解析结果
        logger.info("\n📊 Step 5: 解析结果...")
        
        # 提取各个任务的输出以便精确解析
        monitor_output = task1.output.raw if task1.output else ""
        profile_output = task2.output.raw if task2.output else ""
        defense_advice = str(result)
        
        # 1. 从监控专家输出提取风险等级
        risk_level = "Unknown"
        if "Critical" in monitor_output:
            risk_level = "Critical"
        elif "High" in monitor_output:
            risk_level = "High"
        elif "Medium" in monitor_output:
            risk_level = "Medium"
        elif "Safe" in monitor_output:
            risk_level = "Safe"
            
        # 2. 从侧写师输出提取诈骗类型
        scam_type = "Unknown"
        # 优先通过正则匹配 "诈骗类型: [内容]"
        import re
        scam_type_match = re.search(r"诈骗类型:\s*([^\n\r]+)", profile_output)
        if scam_type_match:
            scam_type = scam_type_match.group(1).strip()
        else:
            # 备选方案：关键词扫描
            for case_type in ["AI换脸", "FaceTime诈骗", "百万保障", "公检法", "杀猪盘", 
                             "ETC", "退改签", "征信修复", "冒充领导", "虚假客服"]:
                if case_type in profile_output:
                    scam_type = case_type
                    break
        
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ 分析完成！")
        logger.info(f"   风险等级: {risk_level}")
        logger.info(f"   诈骗类型: {scam_type}")
        logger.info(f"{'='*60}\n")
        
        return {
            "transcript": transcript_text,
            "transcript_segments": transcript_result['segments'],
            "audio_duration": transcript_result['duration'],
            "risk_level": risk_level,
            "scam_type": scam_type,
            "defense_advice": defense_advice,
            "victim_info": victim_info,
            "raw_result": result
        }


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='反诈骗智能检测系统')
    parser.add_argument('audio_path', help='音频文件路径')
    parser.add_argument('--role', default='R01', help='受害者角色 ID (默认: R01)')
    parser.add_argument('--init-kb', action='store_true', help='初始化知识库（首次运行）')
    parser.add_argument('--whisper-model', default='base', help='Whisper 模型大小')
    
    args = parser.parse_args()
    
    # 初始化系统
    system = AntiFraudSystem(
        whisper_model_size=args.whisper_model,
        init_knowledge_base=args.init_kb
    )
    
    # 分析音频
    result = system.analyze_audio(args.audio_path, args.role)
    
    # 输出结果
    print("\n" + "="*60)
    print("🎯 反诈骗分析报告")
    print("="*60)
    print(f"\n📝 转录文本:\n{result['transcript']}\n")
    print(f"⚠️  风险等级: {result['risk_level']}")
    print(f"🔍 诈骗类型: {result['scam_type']}")
    print(f"\n💡 防御建议:\n{result['defense_advice']}\n")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
