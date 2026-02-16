"""
FastAPI 接口 - 供前端调用
提供简单的 HTTP API 用于音频分析
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import tempfile
import logging
from typing import Optional

from main import AntiFraudSystem

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="反诈骗智能检测 API",
    description="基于 AI 的诈骗电话识别与防御系统",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局系统实例（避免重复加载模型）
system: Optional[AntiFraudSystem] = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化系统"""
    global system
    logger.info("🚀 启动反诈骗检测系统...")
    
    # 检查是否需要初始化知识库
    kb_exists = os.path.exists("./db/chroma")
    
    system = AntiFraudSystem(
        whisper_model_size="base",
        init_knowledge_base=not kb_exists  # 如果数据库不存在则初始化
    )
    
    logger.info("✅ 系统启动完成！")


@app.get("/")
async def root():
    """健康检查接口"""
    return {
        "status": "running",
        "service": "Anti-Fraud Detection API",
        "version": "1.0.0"
    }


@app.post("/analyze")
async def analyze_audio(
    audio: UploadFile = File(..., description="音频文件（MP3 格式）"),
    role_id: str = Form("R01", description="受害者角色 ID (R01-R10)")
):
    """
    分析音频文件，检测诈骗并生成防御建议
    
    **参数:**
    - audio: 音频文件（支持 MP3 格式）
    - role_id: 受害者角色 ID，默认 R01（李奶奶）
    
    **返回:**
    ```json
    {
        "success": true,
        "data": {
            "transcript": "转录文本",
            "risk_level": "High/Medium/Low/Safe",
            "scam_type": "诈骗类型",
            "defense_advice": "防御建议",
            "victim_info": {...}
        }
    }
    ```
    """
    try:
        logger.info(f"收到分析请求: {audio.filename}, 角色: {role_id}")
        
        # 保存上传的音频到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            content = await audio.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # 分析音频
        result = system.analyze_audio(tmp_path, role_id)
        
        # 删除临时文件
        os.unlink(tmp_path)
        
        # 返回结果（移除 raw_result 避免序列化问题）
        response_data = {
            "transcript": result["transcript"],
            "transcript_segments": result["transcript_segments"],
            "audio_duration": result["audio_duration"],
            "risk_level": result["risk_level"],
            "scam_type": result["scam_type"],
            "defense_advice": result["defense_advice"],
            "victim_info": result["victim_info"]
        }
        
        return JSONResponse({
            "success": True,
            "data": response_data
        })
    
    except Exception as e:
        logger.error(f"分析失败: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.post("/analyze-local")
async def analyze_local_audio(
    audio_path: str = Form(..., description="本地音频文件路径"),
    role_id: str = Form("R01", description="受害者角色 ID")
):
    """
    分析本地音频文件（用于测试）
    
    **参数:**
    - audio_path: 本地音频文件路径
    - role_id: 受害者角色 ID
    """
    try:
        if not os.path.exists(audio_path):
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": f"文件不存在: {audio_path}"
                }
            )
        
        result = system.analyze_audio(audio_path, role_id)
        
        response_data = {
            "transcript": result["transcript"],
            "risk_level": result["risk_level"],
            "scam_type": result["scam_type"],
            "defense_advice": result["defense_advice"],
            "victim_info": result["victim_info"]
        }
        
        return JSONResponse({
            "success": True,
            "data": response_data
        })
    
    except Exception as e:
        logger.error(f"分析失败: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/roles")
async def get_roles():
    """获取所有可用的受害者角色列表"""
    import pandas as pd
    
    roles_df = pd.read_csv("./data/roles.csv")
    roles = roles_df.to_dict('records')
    
    return JSONResponse({
        "success": True,
        "data": roles
    })


if __name__ == "__main__":
    import uvicorn
    
    # 启动服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
