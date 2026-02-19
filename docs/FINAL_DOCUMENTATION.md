# 反诈骗智能检测系统 - 快速开始指南

## ⚡ 5 分钟快速上手

### 第一步：安装依赖

```bash
cd AntiFraud-Project
pip install -r requirements.txt
```

**注意**: 安装可能需要几分钟，请耐心等待。

---

### 第二步：配置 API Key

编辑 `.env` 文件（已创建）：

```bash
# 修改以下内容
OPENAI_API_KEY=sk-替换为你的真实API-Key
```

**获取 API Key**: 访问 https://xiaoai.plus 注册并获取

---

### 第三步：运行测试脚本

```bash
python test_system.py
```

**输出示例**:
```
[1/5] 检查环境配置...
  ✓ OPENAI_API_KEY: sk-abc123...
  ✓ OPENAI_BASE_URL: https://xiaoai.plus/v1

[2/5] 检查数据文件...
  ✓ 角色画像表: data/roles.csv
  ✓ 音频文件: 100 个

[3/5] 测试 RAG 知识库...
  ✓ 知识库已构建，共 30 条记录

[4/5] 测试 ASR 转录工具...
  ✓ 转录成功

[5/5] 测试 Agent 创建...
  ✓ Watchdog Agent 创建成功
  ✓ Profiler Agent 创建成功
  ✓ Guardian Agent 创建成功

✅ 所有测试通过！系统已准备就绪
```

如果所有测试通过，说明系统配置正确！

---

### 第四步：测试单个音频

```bash
# 分析第一个测试音频
python main.py data/processed_audio/R01_C01.mp3 --role R01
```

**预期输出**:
```
🎯 反诈骗分析报告
============================================================

📝 转录文本:
李奶奶您好！我是建设银行上海支行的风控专员张强...

⚠️  风险等级: High
🔍 诈骗类型: AI换脸/拟声

💡 防御建议:
### 🚨 立即行动
李奶奶，这是典型的诈骗电话！请立即挂断...

### 🔍 验证问题
1. 如果对方自称是您孙子，问他您最喜欢的菜是什么
2. 拨打银行官方客服 95533 核实

### 📚 防骗科普
真正的银行不会通过电话要求转账...
```

---

## 📚 后续使用

### 命令行模式

```bash
# 基本用法
python main.py <音频路径> --role <角色ID>

# 示例：测试不同角色
python main.py data/processed_audio/R02_C05.mp3 --role R02
python main.py data/processed_audio/R03_C08.mp3 --role R03
```

### API 服务模式

```bash
# 启动 API 服务器
python api.py

# 访问 API 文档
open http://localhost:8000/docs

# 测试 API
curl -X POST "http://localhost:8000/analyze-local" \
  -d "audio_path=data/processed_audio/R01_C01.mp3" \
  -d "role_id=R01"
```

### Python 函数调用（推荐给成员 C）

```python
from main import AntiFraudSystem

# 初始化（只需一次）
system = AntiFraudSystem()

# 分析音频
result = system.analyze_audio(
    audio_path="data/processed_audio/R01_C01.mp3",
    victim_role_id="R01"
)

# 使用结果
print(result['risk_level'])      # 风险等级
print(result['scam_type'])       # 诈骗类型
print(result['defense_advice'])  # 防御建议
```

---

## 🐛 常见问题

### 问题 1: `ModuleNotFoundError: No module named 'XXX'`

**解决方案**:
```bash
pip install -r requirements.txt --upgrade
```

### 问题 2: API Key 无效

检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确填写。

### 问题 3: "知识库为空"

**解决方案**:
```bash
python -c "from src.tools.rag_tool import RAGSearchTool; rag = RAGSearchTool(); rag.build_knowledge_base()"
```

### 问题 4: Whisper 模型下载慢

首次运行 ASR 会自动下载模型（约 140MB），请耐心等待。可以使用更小的模型：
```bash
python main.py test.mp3 --whisper-model tiny
```

---

## 📖 完整文档

详细使用文档请查看: [BACKEND_README.md](BACKEND_README.md)

---

## 👥 团队协作

- **成员 A**: 已完成数据准备 ✅
- **成员 B（你）**: 后端系统开发 ✅
- **成员 C**: 前端 UI 开发 (参考 BACKEND_README.md 的"前端集成方案")

---

**祝测试顺利！有问题随时沟通。** 🚀
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
# 🎯 反诈骗智能检测系统 - 项目交付总结

## 📦 已完成的工作

### ✅ Phase 1-7 全部完成

作为**成员 B（AI 技术指挥官 - 后端）**，已完成以下所有核心任务：

---

## 📂 项目结构

```
AntiFraud-Project/
│
├── 📄 main.py                      # 主程序入口（核心）
├── 📄 api.py                       # FastAPI HTTP 接口
├── 📄 test_system.py               # 系统测试脚本
├── 📄 requirements.txt             # Python 依赖清单
├── 📄 .env                         # 环境配置（需填写 API Key）
├── 📄 .env.example                 # 环境配置模板
├── 📄 .gitignore                   # Git 忽略文件
│
├── 📚 QUICKSTART.md                # 快速开始指南（5 分钟上手）
├── 📚 BACKEND_README.md            # 完整后端文档（给成员 C）
├── 📚 README.markdown              # 数据规范说明（成员 A 提供）
│
├── 📁 config/                      # 配置文件目录
│   ├── agents.yaml                # Agent 的 System Prompts
│   └── tasks.yaml                 # CrewAI 任务流定义
│
├── 📁 src/                         # 源代码目录
│   ├── agents/                    # 智能体定义
│   │   └── anti_fraud_agents.py   # 三个核心 Agent
│   ├── tasks/                     # 任务流定义
│   │   └── anti_fraud_tasks.py    # CrewAI 任务编排
│   ├── tools/                     # 工具模块
│   │   ├── asr_tool.py            # Faster-Whisper 语音转录
│   │   └── rag_tool.py            # ChromaDB 知识检索
│   └── ui/                        # 前端目录（待成员 C 开发）
│
├── 📁 data/                        # 数据目录（成员 A 已完成）
│   ├── roles.csv                  # 10 个角色画像
│   ├── cases.csv                  # 10 个诈骗类型
│   ├── mapping_full.csv           # 100 个完整对话映射
│   ├── raw_audio/                 # 100 个原始音频
│   └── processed_audio/           # 100 个处理后音频
│
├── 📁 db/                          # 数据库目录（自动生成）
│   └── chroma/                    # ChromaDB 向量数据库
│
└── 📁 scripts/                     # 脚本目录（成员 A 的工具）
    ├── audio_pipeline.py          # 音频生成脚本
    ├── config_data.py             # 数据配置
    └── ...
```

---

## 🔧 核心技术实现

### 1️⃣ ASR 语音转录模块 ✅
**文件**: `src/tools/asr_tool.py`

**功能**:
- 使用 Faster-Whisper 实现批处理式语音识别
- 支持 VAD（语音活动检测）过滤静音
- 返回完整转录文本 + 分段信息

**使用示例**:
```python
from src.tools.asr_tool import ASRTool

asr = ASRTool(model_size="base")
result = asr.transcribe_audio("audio.mp3")
print(result['text'])  # 完整转录文本
```

---

### 2️⃣ RAG 知识检索模块 ✅
**文件**: `src/tools/rag_tool.py`

**功能**:
- 基于 ChromaDB 实现本地化向量存储
- 将 100 个诈骗案例向量化
- 支持语义检索相似案例

**知识库内容**:
- 10 个诈骗类型描述
- 20 个典型对话样本（每类型 2 个）

**使用示例**:
```python
from src.tools.rag_tool import RAGSearchTool

rag = RAGSearchTool()
rag.build_knowledge_base()  # 首次运行
results = rag.search_similar_cases("银行卡洗钱", top_k=3)
```

---

### 3️⃣ 三个核心智能体 ✅
**文件**: `src/agents/anti_fraud_agents.py`

#### Agent 1: Watchdog（监控者）
- **角色**: 快速扫描文本，识别高危关键词
- **输出**: 风险等级 + 触发关键词列表

#### Agent 2: Profiler（侧写师）
- **角色**: 通过 RAG 检索匹配诈骗类型
- **工具**: RAG 知识库检索
- **输出**: 诈骗类型 + 历史案例引用

#### Agent 3: Guardian（守护者）
- **角色**: 生成个性化防御话术
- **输入**: 受害者画像 + 诈骗类型
- **输出**: 立即行动建议 + 验证问题 + 科普解释

**配置文件**: `config/agents.yaml`（包含详细的 System Prompts）

---

### 4️⃣ CrewAI 任务流编排 ✅
**文件**: `src/tasks/anti_fraud_tasks.py`

**执行顺序**:
```
监控任务 (Watchdog)
    ↓
侧写任务 (Profiler) ← 依赖监控结果
    ↓
防御任务 (Guardian) ← 依赖前两者
```

**配置文件**: `config/tasks.yaml`（包含详细的任务描述和输出格式）

---

### 5️⃣ 主程序集成 ✅
**文件**: `main.py`

**核心类**: `AntiFraudSystem`

**流程**:
1. ASR 转录音频 → 文本
2. 初始化三个 Agent
3. 创建任务流（设置依赖关系）
4. CrewAI 顺序执行
5. 解析并返回结果

**命令行接口**:
```bash
python main.py <音频路径> --role <角色ID>
```

---

### 6️⃣ FastAPI HTTP 接口 ✅
**文件**: `api.py`

**接口列表**:
- `GET /` - 健康检查
- `POST /analyze` - 上传音频分析
- `POST /analyze-local` - 分析本地音频（测试用）
- `GET /roles` - 获取角色列表

**启动方式**:
```bash
python api.py
# 或
uvicorn api:app --reload
```

**API 文档**: http://localhost:8000/docs

---

## 📖 文档清单

### 1. **QUICKSTART.md** - 快速开始指南
- ⏱️ 5 分钟快速上手
- 🔧 安装配置步骤
- 🧪 测试脚本使用
- ❓ 常见问题解答

### 2. **BACKEND_README.md** - 完整技术文档
- 🏗️ 系统架构详解
- 📚 使用指南（三种模式）
- 🔌 API 接口文档
- 🎨 前端集成方案（给成员 C）
- ❓ 常见问题

### 3. **test_system.py** - 自动化测试脚本
- ✅ 环境配置检查
- ✅ 数据文件验证
- ✅ RAG 知识库测试
- ✅ ASR 转录测试
- ✅ Agent 创建测试

---

## 🚀 使用方式总结

### 方式 1: 命令行（适合快速测试）
```bash
python main.py data/processed_audio/R01_C01.mp3 --role R01
```

### 方式 2: Python 函数（推荐给成员 C 集成）
```python
from main import AntiFraudSystem

system = AntiFraudSystem()
result = system.analyze_audio("audio.mp3", "R01")
```

### 方式 3: HTTP API（适合前后端分离）
```bash
# 启动服务
python api.py

# 调用接口
curl -X POST http://localhost:8000/analyze \
  -F "audio=@test.mp3" \
  -F "role_id=R01"
```

---

## ⚙️ 环境配置要求

### 必需配置
在 `.env` 文件中填写：
```bash
OPENAI_API_KEY=sk-your-key-here        # 必填
OPENAI_BASE_URL=https://xiaoai.plus/v1  # 已配置
OPENAI_MODEL_NAME=gpt-4o-mini           # 已配置
```

### Python 依赖
```bash
pip install -r requirements.txt
```

**主要依赖**:
- `crewai` - AI 智能体框架
- `faster-whisper` - 语音转录
- `chromadb` - 向量数据库
- `sentence-transformers` - 文本嵌入
- `fastapi` - HTTP API
- `openai` - LLM 调用

---

## 🎯 交付给成员 C

### 推荐集成方案（Gradio）

**示例代码** (供成员 C 参考):
```python
import gradio as gr
from main import AntiFraudSystem

# 初始化系统（全局变量，避免重复加载）
system = AntiFraudSystem()

def analyze_callback(audio_file, role_id):
    """Gradio 回调函数"""
    result = system.analyze_audio(audio_file, role_id)
    
    # 根据风险等级设置颜色
    risk_color = {
        "Critical": "🔴",
        "High": "🟠",
        "Medium": "🟡",
        "Safe": "🟢"
    }.get(result['risk_level'], "⚪")
    
    return (
        result['transcript'],              # 转录文本
        f"{risk_color} {result['risk_level']}",  # 风险等级
        result['scam_type'],               # 诈骗类型
        result['defense_advice']           # 防御建议
    )

# 创建 Gradio 界面
with gr.Blocks(title="反诈骗智能检测系统") as demo:
    gr.Markdown("# 🛡️ 反诈骗智能检测系统")
    
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(type="filepath", label="上传音频文件")
            role_select = gr.Dropdown(
                choices=["R01", "R02", "R03", "R04", "R05", 
                        "R06", "R07", "R08", "R09", "R10"],
                value="R01",
                label="选择受害者角色"
            )
            analyze_btn = gr.Button("🔍 开始分析", variant="primary")
        
        with gr.Column():
            transcript_out = gr.Textbox(label="📝 转录文本", lines=5)
            risk_out = gr.Textbox(label="⚠️ 风险等级")
            scam_type_out = gr.Textbox(label="🔍 诈骗类型")
    
    advice_out = gr.Textbox(label="💡 防御建议", lines=10)
    
    analyze_btn.click(
        fn=analyze_callback,
        inputs=[audio_input, role_select],
        outputs=[transcript_out, risk_out, scam_type_out, advice_out]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
```

**保存为**: `src/ui/gradio_app.py`

**运行**:
```bash
python src/ui/gradio_app.py
```

---

## ✅ 验收清单

- [x] ASR 语音转录工具实现
- [x] RAG 知识库构建与检索
- [x] 三个智能体定义（Watchdog, Profiler, Guardian）
- [x] CrewAI 任务流编排
- [x] 主程序 main.py 集成
- [x] FastAPI HTTP 接口
- [x] 环境配置文件（.env, requirements.txt）
- [x] 配置文件（agents.yaml, tasks.yaml）
- [x] 完整文档（QUICKSTART.md, BACKEND_README.md）
- [x] 测试脚本（test_system.py）
- [x] 前端集成示例（Gradio 代码）

---

## 🎉 下一步行动

### 成员 B（你）:
1. ✅ **填写 API Key**: 编辑 `.env` 文件
2. ✅ **运行测试**: `python test_system.py`
3. ✅ **测试分析**: `python main.py data/processed_audio/R01_C01.mp3`
4. ✅ **交付文档**: 将 `BACKEND_README.md` 发给成员 C

### 成员 C:
1. 📖 **阅读文档**: `BACKEND_README.md` 的"前端集成方案"
2. 🎨 **开发 UI**: 参考上面的 Gradio 示例代码
3. 🔌 **集成调用**: 直接 `from main import AntiFraudSystem`
4. 🧪 **联调测试**: 使用 `data/processed_audio/` 中的音频

---

## 📞 技术支持

如遇问题，请检查：
1. `.env` 文件是否正确配置
2. 依赖是否完整安装：`pip list | grep -E "crewai|whisper|chromadb"`
3. 知识库是否已构建：`ls -la db/chroma/`
4. 查看日志输出定位错误

**祝项目顺利！** 🚀
