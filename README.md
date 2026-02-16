# 🛡️ 反诈骗智能检测系统

> 基于 AI 多智能体的诈骗电话实时识别与防御系统

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![CrewAI](https://img.shields.io/badge/CrewAI-0.86.0-green.svg)](https://github.com/joaomdmoura/crewAI)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 项目简介

本项目是一个**端到端的反诈骗智能检测系统**，能够：

- 🎙️ **语音转录**：使用 Faster-Whisper 将诈骗电话音频转为文本
- 🔍 **智能识别**：通过三个 AI 智能体协作识别诈骗类型
- 📚 **知识检索**：基于 RAG 技术匹配历史诈骗案例
- 🛡️ **个性化防御**：根据受害者画像生成针对性防御建议

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
pip install -r requirements.txt
```

### 2️⃣ 配置 API Key

编辑 `.env` 文件：

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

### 3️⃣ 运行测试

```bash
# 测试系统环境
python test_system.py

# 分析示例音频
python main.py data/processed_audio/R01_C01.mp3
```

**完整指南**: 📘 [QUICKSTART.md](QUICKSTART.md)

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户输入音频                         │
└───────────────────┬─────────────────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  ASR 语音转录模块      │
        │  (Faster-Whisper)     │
        └───────────┬───────────┘
                    │ 转录文本
                    ▼
        ┌───────────────────────────────────────┐
        │      CrewAI 智能体协作网络             │
        │                                       │
        │  ┌─────────────────────────────────┐  │
        │  │ Agent 1: Watchdog（监控者）     │  │
        │  │ 识别高危关键词 + 风险评级        │  │
        │  └──────────┬──────────────────────┘  │
        │             │                         │
        │             ▼                         │
        │  ┌─────────────────────────────────┐  │
        │  │ Agent 2: Profiler（侧写师）     │  │
        │  │ RAG 检索 + 匹配诈骗类型         │◄─┼─ 知识库 (ChromaDB)
        │  └──────────┬──────────────────────┘  │
        │             │                         │
        │             ▼                         │
        │  ┌─────────────────────────────────┐  │
        │  │ Agent 3: Guardian（守护者）     │  │
        │  │ 生成个性化防御话术              │  │
        │  └──────────┬──────────────────────┘  │
        └─────────────┼───────────────────────┘
                      │
                      ▼
          ┌───────────────────────┐
          │     分析结果输出       │
          │ - 风险等级            │
          │ - 诈骗类型            │
          │ - 防御建议            │
          └───────────────────────┘
```

---

## 📦 核心功能

### 🎯 三大智能体

| 智能体 | 角色 | 功能 |
|--------|------|------|
| **Watchdog** 🔍 | 监控专家 | 扫描文本，识别高危关键词（验证码、转账、公检法等） |
| **Profiler** 🕵️ | 侧写师 | 通过 RAG 检索匹配历史案例，识别诈骗类型 |
| **Guardian** 🛡️ | 守护者 | 根据受害者画像生成个性化防御话术 |

### 📊 技术栈

- **ASR**: Faster-Whisper (base 模型)
- **LLM**: OpenAI API (gpt-4o-mini)
- **向量数据库**: ChromaDB
- **AI 框架**: CrewAI
- **API 框架**: FastAPI

---

## 📚 使用方式

### 方式 1: 命令行

```bash
python main.py <音频路径> --role <角色ID>
```

### 方式 2: Python 函数

```python
from main import AntiFraudSystem

system = AntiFraudSystem()
result = system.analyze_audio("audio.mp3", "R01")

print(f"风险等级: {result['risk_level']}")
print(f"诈骗类型: {result['scam_type']}")
print(f"防御建议: {result['defense_advice']}")
```

### 方式 3: HTTP API

```bash
# 启动服务
python api.py

# 调用接口
curl -X POST http://localhost:8000/analyze \
  -F "audio=@test.mp3" \
  -F "role_id=R01"
```

**API 文档**: http://localhost:8000/docs

---

## 📖 完整文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](QUICKSTART.md) | 5 分钟快速上手指南 |
| [BACKEND_README.md](BACKEND_README.md) | 完整技术文档（含 API 说明） |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | 项目交付总结（含前端集成示例） |

---

## 🗂️ 数据集

系统使用以下数据（由成员 A 提供）：

- **10 个角色画像** (data/roles.csv)
  - 包括：独居老人、企业主、大学生、程序员等
  
- **10 个诈骗类型** (data/cases.csv)
  - 包括：AI 换脸、冒充公检法、杀猪盘、虚假客服等
  
- **100 个对话样本** (data/mapping_full.csv)
  - 10 角色 × 10 案例 = 100 组完整对话音频

---

## 🎨 前端集成

推荐使用 **Gradio** 快速搭建 UI：

```python
import gradio as gr
from main import AntiFraudSystem

system = AntiFraudSystem()

def analyze(audio, role_id):
    result = system.analyze_audio(audio, role_id)
    return result['transcript'], result['risk_level'], result['defense_advice']

gr.Interface(
    fn=analyze,
    inputs=[gr.Audio(type="filepath"), gr.Dropdown(choices=["R01", "R02", ...])],
    outputs=[gr.Textbox(), gr.Textbox(), gr.Textbox()]
).launch()
```

**完整示例**: 见 [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) 的"前端集成方案"

---

## 🧪 测试

运行系统测试脚本：

```bash
python test_system.py
```

测试覆盖：
- ✅ 环境配置检查
- ✅ 数据文件验证
- ✅ RAG 知识库测试
- ✅ ASR 转录测试
- ✅ Agent 创建测试

---

## 👥 团队分工

| 成员 | 职责 | 状态 |
|------|------|------|
| **成员 A** | 数据与剧本架构师 | ✅ 已完成 |
| **成员 B** | AI 技术指挥官（后端） | ✅ 已完成 |
| **成员 C** | 前端开发与交付 | 🚧 进行中 |

---

## ❓ 常见问题

**Q: 首次运行提示 "知识库为空"？**

A: 运行以下命令构建知识库：
```bash
python -c "from src.tools.rag_tool import RAGSearchTool; rag = RAGSearchTool(); rag.build_knowledge_base()"
```

**Q: API Key 无效？**

A: 检查 `.env` 文件中的 `OPENAI_API_KEY` 是否正确填写。

**更多问题**: 见 [BACKEND_README.md](BACKEND_README.md) 的"常见问题"章节

---

## 📄 许可证

MIT License

---

## 📞 联系方式

- **成员 B（后端）**: 负责系统架构与 AI 逻辑
- **成员 C（前端）**: 使用 BACKEND_README.md 集成 UI

---

**祝项目顺利！** 🚀
