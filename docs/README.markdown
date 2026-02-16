请保持以下目录结构，以确保代码能正确读取资源。
```text
AntiFraud-Project/
├── data/
│   ├── processed_audio/    # 最终交付音频 (已加噪/16kHz/单声道)
│   ├── raw_audio/          # 原始音频
│   ├── mapping_full.csv    # 数据总表 
│   ├── roles.csv           # 角色画像参考
│   └── cases.csv           # 诈骗类型参考 

```
## 1. 概述
本规范定义了仿真数据集的**物理存储结构**与**逻辑字段定义**。
所有后端读取操作（RAG 检索、ASR 评测）及前端展示（案例回放、风险预警）均需严格遵循本规范。

## 2. 物理存储接口 (File System Interface)



| 目录/文件路径 | 文件说明 | 核心格式要求 | 业务逻辑用途 |
| :--- | :--- | :--- | :--- |
| `data/processed_audio/` | **音频源文件库** | MP3, 16kHz, Mono, -25dB Noise | **后端入口**: 作为 Faster-Whisper 推理模型的原始输入 |
| `data/mapping_full.csv` | **核心索引总表** | UTF-8-SIG (CSV) | **系统“大脑”**: 连接音频 ID、剧本真值与风险等级标签 |
| `data/roles.csv` | **角色画像表** | UTF-8-SIG (CSV) | **上下文加载**: 供 Profiler Agent 读取受害者心理弱点 |
| `data/cases.csv` | **案例知识库** | UTF-8-SIG (CSV) | **RAG检索**: 供后端进行反诈套路特征比对与科普输出 |

### 📂 访问规范说明
1. **音频调用**: 所有音频文件名格式为 `{RoleID}_{CaseID}.mp3`（例如 `R01_C01.mp3`），与 `mapping_full.csv` 中的 `id` 字段一一对应。
2. **编码标准**: 为了防止在 Windows/Linux 环境下出现中文字符乱码，所有 CSV 文件必须保存为 **UTF-8-SIG** 编码。
3. **数据完整性**: `data/processed_audio/` 目录下应包含总计 100 个 MP3 文件，对应 10 类角色与 10 类案例的完全笛卡尔积生成的对话脚本。

## 3. 核心数据字典 (Database Schema)

### 3.1 主索引表 (`mapping_full.csv`)
**用途**: 该表为全系统的核心总表，用于连接音频物理路径、剧本真值与 AI 评测标签。

| 字段名 (Key) | 类型 | 必填 | 示例值 | 业务逻辑说明 |
| :--- | :--- | :--- | :--- | :--- |
| `id` | String | Yes | `R01-C01` | **主键**: 格式为 `{RoleID}-{CaseID}`。 |
| `dialogue_json` | JSON | Yes | `[...]` | **结构化剧本**: 包含单句情绪、语速、性别及文本的列表。 |
| `text` | String | Yes | `"李奶奶您好..."` | **ASR 真值**: 剔除括号提示词后的全量对话文本。 |
| `case_type` | String | Yes | `FaceTime诈骗` | **前端联动**: 决定 UI 触发哪类反诈科普卡片。 |
| `risk_level` | Enum | Yes | `High` | **预警控制**: 决定前端告警灯状态（High/Critical）。 |
| `processed_audio_path` | Path | Yes | `data/processed_audio/R01_C01.mp3` | **后端入口**: Whisper 模型读取的物理文件路径。 |

---

### 3.2 结构化对话字段 (`dialogue_json`) 定义
**解析规范**: 该字段存储为 JSON 字符串，读取后需解析为 `List[Dict]` 结构。每一项代表一轮通话内容：

| 内部字段 | 说明 | 取值范围 / 示例 |
| :--- | :--- | :--- |
| `speaker` | 当前说话人 | `Scammer` (骗子) 或 `Victim` (受害人)。 |
| `gender` | 骗子音色性别 | `male` 或 `female`（已实现同一剧本内音色锁定）。 |
| `mood` | 情感标签 | `angry`, `fearful`, `sad`, `customerservice`, `chat`。 |
| `speed` | 语速标签 | `fast`, `normal`, `slow`。 |
| `text` | **纯净文本** | 用于 ASR 比对及字幕显示。 |

---

### 3.3 角色画像表 (`roles.csv`)
**用途**: 辅助后端 Agent 理解受害者背景，用于生成更具同理心的劝阻策略。

| 字段名 | 类型 | 说明 | 示例 |
| :--- | :--- | :--- | :--- |
| `id` | String | 角色唯一标识 | `R01`。 |
| `name` | String | 受害人姓名 | `李奶奶`。 |
| `age` | Int | 受害人年龄 | `72`。 |
| `weakness` | String | 心理弱点 | `关心孙辈、对新技术认知较低`。 |
