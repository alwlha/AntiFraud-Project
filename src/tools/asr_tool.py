"""
ASR 语音转录工具
基于 Faster-Whisper 实现批处理式语音识别
"""

import os
from typing import Dict, List, Optional
from faster_whisper import WhisperModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ASRTool:
    """Faster-Whisper 语音转录工具类"""
    
    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        初始化 Whisper 模型
        
        Args:
            model_size: 模型大小 (tiny, base, small, medium, large-v3)
            device: 运行设备 (cpu, cuda)
            compute_type: 计算精度 (int8, float16, float32)
        """
        logger.info(f"加载 Faster-Whisper 模型: {model_size} on {device}")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type
        )
        
    def transcribe_audio(
        self,
        audio_path: str,
        language: str = "zh",
        vad_filter: bool = True
    ) -> Dict:
        """
        转录音频文件为文本
        
        Args:
            audio_path: 音频文件路径
            language: 语言代码 (zh, en)
            vad_filter: 是否启用语音活动检测（过滤静音）
            
        Returns:
            {
                "text": "完整转录文本",
                "segments": [{"start": 0.0, "end": 2.5, "text": "..."}],
                "language": "zh"
            }
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        logger.info(f"开始转录: {audio_path}")
        
        # 执行转录
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            vad_filter=vad_filter,
            beam_size=5
        )
        
        # 处理结果
        segment_list = []
        full_text = ""
        
        for segment in segments:
            seg_dict = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip()
            }
            segment_list.append(seg_dict)
            full_text += segment.text.strip() + " "
        
        result = {
            "text": full_text.strip(),
            "segments": segment_list,
            "language": info.language,
            "duration": info.duration
        }
        
        logger.info(f"转录完成，共 {len(segment_list)} 个片段，总时长 {info.duration:.2f}s")
        
        return result


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """
    简化接口：直接返回转录文本
    
    Args:
        audio_path: 音频文件路径
        model_size: Whisper 模型大小
        
    Returns:
        完整转录文本
    """
    asr = ASRTool(model_size=model_size)
    result = asr.transcribe_audio(audio_path)
    return result["text"]


if __name__ == "__main__":
    # 测试代码
    import sys
    
    if len(sys.argv) > 1:
        test_audio = sys.argv[1]
    else:
        # 默认测试第一个音频文件
        test_audio = "../data/processed_audio/R01_C01.mp3"
    
    print(f"\n=== 测试 ASR 工具 ===")
    print(f"音频文件: {test_audio}\n")
    
    asr_tool = ASRTool(model_size="base")
    result = asr_tool.transcribe_audio(test_audio)
    
    print(f"检测语言: {result['language']}")
    print(f"音频时长: {result['duration']:.2f}s")
    print(f"\n完整转录文本:\n{result['text']}\n")
    print(f"分段数量: {len(result['segments'])}")
    for i, seg in enumerate(result['segments'][:3], 1):
        print(f"  [{seg['start']:.2f}s - {seg['end']:.2f}s] {seg['text']}")
