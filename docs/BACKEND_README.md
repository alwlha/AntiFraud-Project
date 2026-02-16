# 反诈骗智能检测系统 - 后端文档

## 📋 目录
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [使用指南](#使用指南)
- [API 接口文档](#api-接口文档)
- [前端集成方案](#前端集成方案)
- [常见问题](#常见问题)

---

## 🏗️ 系统架构

### 核心组件

```
AntiFraud-Project/
├── main.py                 # 主程序入口
├── api.py                  # FastAPI HTTP 接口
├── requirements.txt        # Python 依赖
├── .env                    # 环境配置
│
├── src/
│   ├── agents/            # 三个智能体定义
│   │   └── anti_fraud_agents.py
│   ├── tasks/             # 任务流定义
│   │   └── anti_fraud_tasks.py
│   └── tools/             # 工具模块
│       ├── asr_tool.py    # Faster-Whisper 语音转录
│       └── rag_tool.py    # ChromaDB 知识检索
│
├── config/                # 配置文件
│   ├── agents.yaml        # Agent Prompts
│   └── tasks.yaml         # Task 定义
│
├── data/                  # 数据目录（由成员 A 提供）
│   ├── roles.csv          # 角色画像
│   ├── cases.csv          # 诈骗类型
│   ├── mapping_full.csv   # 完整数据映射
│   └── processed_audio/   # 音频文件
│
└── db/                    # 数据库（自动生成）
    └── chroma/            # ChromaDB 向量库
```

### 技术栈

- **ASR**: Faster-Whisper (base 模型)
- **LLM**: OpenAI API (通过 https://xiaoai.plus/v1)
- **向量数据库**: ChromaDB
- **AI 框架**: CrewAI
- **API 框架**: FastAPI

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd AntiFraud-Project

# 安装 Python 依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件，填入你的 API Key：

```bash
# .env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://xiaoai.plus/v1
OPENAI_MODEL_NAME=gpt-4o-mini
```

### 3. 初始化知识库（首次运行）

```bash
# 方法 1: 使用命令行
python main.py data/processed_audio/R01_C01.mp3 --init-kb

# 方法 2: 使用 Python 脚本
python -c "from src.tools.rag_tool import RAGSearchTool; rag = RAGSearchTool(); rag.build_knowledge_base()"
```

### 4. 测试系统

```bash
# 测试单个音频文件
python main.py data/processed_audio/R01_C01.mp3 --role R01
```

---

## 📖 使用指南

### 方式一：命令行模式

```bash
python main.py <音频路径> --role <角色ID>

# 示例
python main.py data/processed_audio/R01_C01.mp3 --role R01
```

**参数说明:**
- `音频路径`: 必填，音频文件路径
- `--role`: 受害者角色 ID (R01-R10)，默认 R01
- `--init-kb`: 首次运行时添加此参数初始化知识库
- `--whisper-model`: Whisper 模型大小，默认 base

### 方式二：Python 函数调用

```python
from main import AntiFraudSystem

# 初始化系统
system = AntiFraudSystem(
    whisper_model_size="base",
    init_knowledge_base=False  # 首次运行设为 True
)

# 分析音频
result = system.analyze_audio(
    audio_path="data/processed_audio/R01_C01.mp3",
    victim_role_id="R01"
)

# 获取结果
print(f"风险等级: {result['risk_level']}")
print(f"诈骗类型: {result['scam_type']}")
print(f"防御建议:\n{result['defense_advice']}")
```

**返回结果结构:**
```python
{
    "transcript": "完整转录文本",
    "transcript_segments": [...],  # 分段信息
    "audio_duration": 30.5,        # 音频时长（秒）
    "risk_level": "High",          # Safe/Medium/High/Critical
    "scam_type": "冒充公检法",      # 诈骗类型
    "defense_advice": "...",       # 完整防御建议
    "victim_info": {               # 受害者信息
        "name": "李奶奶",
        "age": 72,
        "tag": "独居老人",
        "weakness": "..."
    }
}
```

### 方式三：FastAPI 服务

#### 启动 API 服务

```bash
# 方式 1: 直接运行
python api.py

# 方式 2: 使用 uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

服务启动后访问：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/

---

## 🔌 API 接口文档

### 1. 健康检查

**请求:**
```http
GET /
```

**响应:**
```json
{
    "status": "running",
    "service": "Anti-Fraud Detection API",
    "version": "1.0.0"
}
```

---

### 2. 分析上传的音频文件

**请求:**
```http
POST /analyze
Content-Type: multipart/form-data

audio: [音频文件]
role_id: R01
```

**cURL 示例:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "audio=@/path/to/audio.mp3" \
  -F "role_id=R01"
```

**Python 示例:**
```python
import requests

url = "http://localhost:8000/analyze"
files = {'audio': open('test.mp3', 'rb')}
data = {'role_id': 'R01'}

response = requests.post(url, files=files, data=data)
result = response.json()

if result['success']:
    print(f"风险等级: {result['data']['risk_level']}")
    print(f"诈骗类型: {result['data']['scam_type']}")
```

**响应:**
```json
{
    "success": true,
    "data": {
        "transcript": "...",
        "risk_level": "High",
        "scam_type": "冒充公检法",
        "defense_advice": "...",
        "victim_info": {...}
    }
}
```

---

### 3. 分析本地音频（测试用）

**请求:**
```http
POST /analyze-local
Content-Type: application/x-www-form-urlencoded

audio_path=data/processed_audio/R01_C01.mp3
role_id=R01
```

**cURL 示例:**
```bash
curl -X POST "http://localhost:8000/analyze-local" \
  -d "audio_path=data/processed_audio/R01_C01.mp3" \
  -d "role_id=R01"
```

---

### 4. 获取角色列表

**请求:**
```http
GET /roles
```

**响应:**
```json
{
    "success": true,
    "data": [
        {
            "id": "R01",
            "name": "李奶奶",
            "age": 72,
            "tag": "独居老人/退休",
            "weakness": "关心孙辈、害怕生病、对智能手机不熟"
        },
        ...
    ]
}
```

---

## 🎨 前端集成方案

### 方案 A: 直接调用 Python 函数（推荐用于 Gradio）

成员 C 可以在 Gradio 界面中直接调用 `AntiFraudSystem`：

```python
# src/ui/gradio_app.py
import gradio as gr
from main import AntiFraudSystem

# 初始化系统（全局，避免重复加载）
system = AntiFraudSystem()

def analyze_audio_ui(audio_file, role_id):
    """Gradio 回调函数"""
    result = system.analyze_audio(audio_file, role_id)
    
    return (
        result['transcript'],
        result['risk_level'],
        result['scam_type'],
        result['defense_advice']
    )

# 创建 Gradio 界面
with gr.Blocks() as demo:
    gr.Markdown("# 反诈骗智能检测系统")
    
    with gr.Row():
        audio_input = gr.Audio(type="filepath", label="上传音频")
        role_select = gr.Dropdown(
            choices=["R01", "R02", "R03", ...],
            label="选择受害者角色"
        )
    
    analyze_btn = gr.Button("开始分析")
    
    with gr.Row():
        transcript_output = gr.Textbox(label="转录文本")
        risk_output = gr.Textbox(label="风险等级")
    
    scam_type_output = gr.Textbox(label="诈骗类型")
    advice_output = gr.Textbox(label="防御建议", lines=10)
    
    analyze_btn.click(
        fn=analyze_audio_ui,
        inputs=[audio_input, role_select],
        outputs=[transcript_output, risk_output, scam_type_output, advice_output]
    )

demo.launch()
```

### 方案 B: HTTP API 调用

如果前端是独立的 Web 应用：

```javascript
// JavaScript 示例
async function analyzeAudio(audioFile, roleId) {
    const formData = new FormData();
    formData.append('audio', audioFile);
    formData.append('role_id', roleId);
    
    const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        body: formData
    });
    
    const result = await response.json();
    
    if (result.success) {
        displayResults(result.data);
    }
}
```

---

## ❓ 常见问题

### Q1: 首次运行时提示 "知识库为空"

**解决方案:**
```bash
# 手动构建知识库
python -c "from src.tools.rag_tool import RAGSearchTool; rag = RAGSearchTool(); rag.build_knowledge_base()"

# 或在运行时添加 --init-kb 参数
python main.py test.mp3 --init-kb
```

### Q2: API Key 无效或请求失败

检查 `.env` 文件配置：
```bash
OPENAI_API_KEY=sk-your-actual-key
OPENAI_BASE_URL=https://xiaoai.plus/v1
```

### Q3: Whisper 模型下载慢

Faster-Whisper 首次运行会自动下载模型，可以：
- 使用更小的模型：`--whisper-model tiny`
- 手动下载模型到缓存目录

### Q4: 如何批量测试多个音频？

```python
from main import AntiFraudSystem
import os

system = AntiFraudSystem()
audio_dir = "data/processed_audio"

for filename in os.listdir(audio_dir):
    if filename.endswith(".mp3"):
        audio_path = os.path.join(audio_dir, filename)
        role_id = filename.split("_")[0]  # 从文件名提取角色 ID
        
        result = system.analyze_audio(audio_path, role_id)
        print(f"{filename}: {result['risk_level']} - {result['scam_type']}")
```

---

## 📞 联系与支持

- **成员 B（后端）**: 负责系统架构与 AI 逻辑
- **成员 C（前端）**: 使用本文档集成前端 UI

**注意事项:**
1. 确保 `.env` 文件中的 API Key 有效
2. 首次运行必须初始化知识库
3. 音频文件格式建议使用 MP3，16kHz 采样率
4. 系统加载需要 10-30 秒，请耐心等待

---

**最后更新时间**: 2026-02-16
