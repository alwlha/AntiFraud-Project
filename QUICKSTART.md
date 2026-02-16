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
