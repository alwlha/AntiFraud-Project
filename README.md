# 🛡️ 反诈骗智能检测系统 (AntiFraud-Project)

> **基于 AI 多智能体与 RAG 技术的诈骗电话实时识别与防御系统**

本项目是一个端到端的反诈骗解决方案，整合了语音转录 (ASR)、知识检索 (RAG) 以及多智能体协作 (CrewAI) 流程，旨在实时识别诈骗电话并为受害者提供个性化的防御建议。

---

## 📖 项目简介

本项目能够：

- 🎙️ **语音转录**：使用 Faster-Whisper 将诈骗电话音频转为文本。
- 🔍 **智能识别**：通过三个 AI 智能体协作识别诈骗风险及类型。
- 📚 **知识检索**：基于 RAG 技术匹配 100+ 历史诈骗案例。
- 🛡️ **个性化防御**：根据受害者画像（如年龄、心理弱点）生成针对性防御建议。

---

## 🏗️ 系统架构

系统遵循 **监控 -> 识别 -> 防御** 的闭环逻辑：

1. **语音转录 (ASR)**: 使用 `Faster-Whisper` 将通话音频转换为文本。
2. **CrewAI 智能体协作网络**:
   - **Watchdog (反诈监控专家)**: 识别高危关键词并评估风险等级 (Critical/High/Medium/Safe)。
   - **Profiler (诈骗剧本侧写师)**: 利用 RAG 检索匹配诈骗类型。
   - **Guardian (个性化防御策略专家)**: 生成针对性验证问题与行动建议。
3. **结果输出**: 风险等级、诈骗类型及针对性防御建议。

---

## 🚀 快速开始

### 1️⃣ 安装依赖

```bash
cd AntiFraud-Project
pip install -r requirements.txt
```

### 2️⃣ 配置环境变量

编辑 `.env` 文件，填入您的 API Key：

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://xiaoai.plus/v1
OPENAI_MODEL_NAME=gpt-4o-mini
```

### 3️⃣ 运行测试与初始化

```bash
# 运行自动化测试，检查环境并初始化 RAG 知识库
python test_system.py
```

### 4️⃣ 分析音频

```bash
# 分析示例音频
python main.py data/processed_audio/R01_C02.mp3 --role R01
```

---

## 📦 核心模块

| 模块             | 技术栈         | 说明                              |
| :--------------- | :------------- | :-------------------------------- |
| **ASR**    | Faster-Whisper | 高精度语音转文本，支持 VAD 过滤。 |
| **RAG**    | ChromaDB       | 基于向量检索的历史诈骗案例库。    |
| **Agents** | CrewAI         | 模拟专家协作的多智能体决策系统。  |
| **API**    | FastAPI        | 标准化的 RESTful 接口服务。       |

---

## 📚 使用方式

### 命令行

```bash
python main.py <音频路径> --role <角色ID>
```

### Python 调用

```python
from main import AntiFraudSystem
system = AntiFraudSystem()
result = system.analyze_audio("audio.mp3", "R01")
```

### HTTP API

```bash
python api.py
# 调用接口: POST /analyze
```

---

## 🧪 测试覆盖

运行 `python test_system.py` 可自动验证：

- ✅ 环境配置 (API Key, Base URL)
- ✅ 数据文件完整性 (CSV, MP3)
- ✅ RAG 知识库功能
- ✅ ASR 转录精度
- ✅ Agent 逻辑链路

---

## 👥 团队分工

- **成员 A**: 数据集构建、剧本编写及音频资产处理。
- **成员 B**: 后端算法开发 (ASR, RAG, CrewAI) 及系统集成。
- **成员 C**: 前端 UI 开发 (Gradio) 与接口联调。

---

## 📄 许可证

本项目采用 MIT 许可证。
