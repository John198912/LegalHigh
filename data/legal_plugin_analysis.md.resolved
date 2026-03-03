# Anthropic Legal Plugin 深度架构分析 & 本地化方案

> 源码参考：[anthropics/knowledge-work-plugins/legal](https://github.com/anthropics/knowledge-work-plugins/tree/main/legal)

---

## 一、设计哲学：Plugin 是什么

Anthropic 的 Legal Plugin 不是传统意义上的"应用程序"，它本质是一套**结构化的提示词工程体系（Prompt Engineering System）**，通过 Markdown 文件定义 AI 的行为规范，配合 MCP（Model Context Protocol）连接外部数据和工具。

**三层核心结构：**

```
Plugin = Skills（能力模块） + Commands（调用入口） + Connectors（外部集成）
```

这套设计的核心理念：
- **Skill = 高质量 System Prompt** —— 每个 Skill 就是一个专家级别的角色设定文件
- **渐进式加载（Progressive Disclosure）** —— 按需激活对应 Skill，避免 Token 浪费
- **单一职责** —— 一个 Skill 只做一件事，但可组合
- **可定制化 Playbook** —— 通过 `legal.local.md` 注入企业特定的标准和政策

---

## 二、完整目录结构解析

```
legal/
├── .claude-plugin/          # Plugin 元信息（定义 Plugin 身份、名称、图标等）
├── .mcp.json                # MCP 服务器配置（连接外部工具）
├── CONNECTORS.md            # 支持连接的外部服务清单
├── README.md                # 安装和使用文档
├── commands/                # 斜杠命令定义（用户触发入口）
│   ├── nda-triage.md
│   ├── contract-review.md
│   └── ...
└── skills/                  # 核心能力模块（6个 Skill）
    ├── contract-review/
    │   └── SKILL.md         # ~10.8KB，合同审查专家提示词
    ├── nda-triage/
    │   └── SKILL.md         # ~11.5KB，NDA 分诊专家提示词
    ├── compliance/
    │   └── SKILL.md         # ~12.8KB，合规监控专家提示词
    ├── legal-risk-assessment/
    │   └── SKILL.md         # ~12.6KB，法律风险评估专家提示词
    ├── meeting-briefing/
    │   └── SKILL.md         # 会议简报生成专家提示词
    └── canned-responses/
        └── SKILL.md         # 标准化回复模板专家提示词
```

---

## 三、核心 Skill 功能解析

### 3.1 contract-review（合同审查）— 最核心 Skill

**设计模式：Playbook-Driven Review**

```
输入：合同文档 + legal.local.md（企业Playbook）
处理：逐条款分析 → 风险标注 → 建议修改
输出：结构化审查报告
```

**输出格式设计（RED/YELLOW/GREEN 三色风险体系）：**
```markdown
## 条款 X：[条款名称]
**风险等级：🔴 RED / 🟡 YELLOW / 🟢 GREEN**
**当前文本：**[原文]
**问题：**[具体问题描述]
**建议修改：**[具体 Redline 文本]
**理由：**[法律依据]
```

**关键设计思路：**
- AI 不替代律师判断，而是提供"结构化的第一轮审查"
- Playbook 文件存储企业的谈判底线，AI 依此对照
- 每个条款独立评估，防止遗漏

### 3.2 nda-triage（NDA 分诊）

**设计模式：快速分类 + 优先级排序**

处理高频、低难度的 NDA 审查：
- 识别 NDA 类型（单向/双向/多方）
- 检查关键条款完整性
- 快速输出：批准/需修改/需律师介入

**核心设计决策：** 将律师的精力从常规 NDA 解放出来，AI 处理 80% 标准情况

### 3.3 compliance（合规监控）

**设计模式：持续监控 + 变更感知**

- 追踪法规变化对现有合同/流程的影响
- 生成合规差距分析报告
- 连接外部数据源（通过 MCP）获取最新法规

### 3.4 legal-risk-assessment（法律风险评估）

**设计模式：多维度风险矩阵**

- 跨合同/跨项目的系统性风险识别
- 概率 × 影响 = 风险优先级评分
- 输出：风险热力图 + 缓解建议

### 3.5 meeting-briefing（会议简报）

**设计模式：上下文聚合 → 精炼摘要**

会议前自动汇总：
- 相关合同状态
- 对方历史交互记录
- 待决事项清单
- 谈判要点提示

### 3.6 canned-responses（标准化回复）

**设计模式：模板库 + 场景匹配**

- 针对常见法律查询生成标准措辞
- 保持法律措辞的一致性
- 可定制企业专用模板库

---

## 四、MCP 连接器架构

`.mcp.json` 定义了 Legal Plugin 可以连接的外部服务：

```json
{
  "mcpServers": {
    "filesystem": {...},    // 读取本地/网络文件系统的合同文档
    "slack": {...},         // 接收任务、发送通知
    "google-drive": {...},  // 文档存储
    "box": {...},           // 企业文档管理
    "imanage": {...}        // 法律行业专用文档管理系统
  }
}
```

**CONNECTORS.md 声明的集成清单：**
- 文档管理：iManage、Clio、Box、Egnyte
- 通信：Slack、Microsoft Teams
- 生产力：Google Workspace、Microsoft 365
- 法律专属：DocuSign、LegalZoom

---

## 五、Commands（斜杠命令）机制

```
用户输入 → /legal:nda-triage → 加载对应 SKILL.md → 执行任务
```

Commands 是用户面向的触发接口，Markdown 定义格式：
```markdown
---
name: nda-triage
description: 快速分析 NDA 风险和条款完整性
---

请使用 nda-triage Skill 分析附件或剪贴板中的 NDA 文档...
```

---

## 六、核心设计原则总结（可复用）

| 原则 | 实现方式 |
|------|---------|
| **单一职责** | 每个 Skill 只做一件事 |
| **Token 效率** | 按需加载，不一次性注入所有提示词 |
| **可定制化** | `.local.md` 文件注入企业专属规则 |
| **结构化输出** | 固定输出格式（表格/评级/建议），而非自由文本 |
| **人机协作** | AI 提供初稿，人类做最终判断 |
| **可审计性** | 每个结论附带推理过程，便于验证 |

---

## 七、本地化个性化法律多 Agent 架构方案

### 7.1 整体架构设计

```
用户请求
    │
    ▼
┌─────────────────────────────────────────────────────┐
│               Orchestrator Agent（路由层）            │
│  - 理解意图，分发到专业子 Agent                        │
│  - 汇聚多 Agent 结果                                  │
│  - 模型：Claude 3.5 Sonnet / GPT-4o                  │
└─────────────┬──────────────────────────┬────────────┘
              │                          │
    ┌─────────▼──────────┐    ┌─────────▼──────────┐
    │  合同审查 Agent     │    │  法律研究 Agent     │
    │  - 条款风险识别     │    │  - 法规检索        │
    │  - Redline 建议     │    │  - 案例分析        │
    │  - 合规对照         │    │  - 政策解读        │
    └────────────────────┘    └────────────────────┘
    ┌────────────────────┐    ┌────────────────────┐
    │  风险评估 Agent     │    │  文书起草 Agent     │
    │  - 多维度风险矩阵   │    │  - 合同起草        │
    │  - 优先级评分       │    │  - 法律函件        │
    │  - 缓解建议         │    │  - NDA 快速处理    │
    └────────────────────┘    └────────────────────┘
              │
    ┌─────────▼──────────┐
    │  验证 Agent（QA）   │
    │  - 检查输出准确性   │
    │  - 标注不确定内容   │
    └────────────────────┘
```

### 7.2 技术选型（本地化优先）

| 层次 | 推荐技术 | 说明 |
|------|---------|------|
| **框架** | LangGraph / CrewAI | 多 Agent 编排，支持状态机流转 |
| **模型（在线）** | Claude 3.5 Sonnet API | 最强法律推理能力 |
| **模型（本地）** | Qwen2.5-72B / Deepseek-R1 | 私有化部署，数据不出境 |
| **向量库** | Qdrant / Chroma | 本地法规知识库存储 |
| **文档解析** | PyMuPDF + Unstructured | 解析合同/法规 PDF |
| **MCP 工具** | 自建 MCP Server | 连接本地文件系统和数据库 |
| **知识库** | 本地法规文本 + 企业Playbook | 代替订阅制法规数据库 |

### 7.3 核心 Skill 文件设计（复用 Anthropic 模式）

每个 Agent 的行为由 `SKILL.md` 定义，参考结构：

```markdown
---
name: cn-contract-review
description: 中国法律体系下的合同审查专家
version: 1.0
---

# 角色定位
你是一位精通中国合同法、公司法的资深法律顾问...

# 审查框架
按以下顺序逐条审查：
1. 主体资格条款
2. 核心权利义务条款
3. 违约责任条款
4. 争议解决条款（仲裁/诉讼/管辖）
5. 保密条款
6. 知识产权归属

# 输出格式
## [条款名称]（第X条）
**风险等级：** 🔴高 / 🟡中 / 🟢低
**法律依据：** [具体法条，如《合同法》第X条]
**建议修改：** [具体替代文本]

# 例外情况
若文档涉及以下场景需额外注意：
- 跨境交易（适用法律选择问题）
- 国有资产（特殊审批要求）
- 数据处理（PIPL合规要求）

# Playbook（从 legal.local.md 加载）
{{COMPANY_PLAYBOOK}}
```

### 7.4 企业 Playbook 配置文件（`legal.local.md`）

```markdown
# 公司法律立场 Playbook

## 合同谈判底线
- 付款账期：最长 60 天（绝不接受超过 90 天）
- 违约金比例：不低于合同金额的 20%
- 争议解决：优先选择仲裁（北京仲裁委员会）

## 自动标红条款
- 无限制赔偿责任条款
- 单方终止权（无故终止）
- 知识产权完整转让（默认拒绝）

## 行业特殊要求
- B端SaaS合同必须包含数据处理协议（DPA）
- 涉及医疗数据必须符合《个人信息保护法》第28条
```

### 7.5 快速启动：用 LangGraph 实现核心流程

```python
from langgraph.graph import StateGraph
from anthropic import Anthropic

# 状态定义
class LegalWorkflowState(TypedDict):
    document: str           # 原始法律文档
    intent: str             # 用户意图（合同审查/风险评估/...）
    review_result: dict     # 审查结果
    risk_scores: dict       # 风险评分
    final_report: str       # 最终报告

# Agent 节点
def orchestrator(state):
    """路由层：判断意图，分发任务"""
    ...

def contract_review_agent(state):
    """加载 contract-review/SKILL.md 作为 system prompt"""
    skill = load_skill("skills/contract-review/SKILL.md")
    playbook = load_playbook("legal.local.md")
    # 调用 Claude API
    ...

def qa_validator(state):
    """验证输出，标注不确定项"""
    ...

# 构建图
graph = StateGraph(LegalWorkflowState)
graph.add_node("orchestrator", orchestrator)
graph.add_node("contract_review", contract_review_agent)
graph.add_node("risk_assessment", risk_assessment_agent)
graph.add_node("qa_validator", qa_validator)

# 边（条件路由）
graph.add_conditional_edges("orchestrator", route_by_intent)
```

### 7.6 与 Anthropic 设计的关键差异点

| 特性 | Anthropic Legal Plugin | 本地化方案 |
|------|----------------------|-----------|
| 运行环境 | Claude Cowork 桌面客户端 | 本地服务/API |
| 模型 | Claude（必须） | 灵活选择（含国产模型） |
| 法律体系 | 英美法系为主 | **中国法律体系** |
| 数据安全 | 数据上 Anthropic 云 | **数据完全本地** |
| 法规知识库 | 内置通用知识 | **接入最新中国法规库** |
| 定制方式 | 修改 `.local.md` | 同样方式 + 更多扩展 |

---

## 八、推荐实施路径

```
Phase 1（1-2周）：基础搭建
├── 搭建 LangGraph / CrewAI 环境
├── 实现 Orchestrator + 1个 Skill Agent（先做合同审查）
├── 配置 Playbook 文件
└── 接入本地文档解析（PyMuPDF）

Phase 2（2-4周）：能力扩充
├── 添加 NDA 分诊、风险评估 Agent
├── 构建本地法规向量知识库（最高院案例 + 重要法规）
├── 实现 MCP Server 连接本地文件目录
└── 添加 QA 验证 Agent

Phase 3（4-8周）：生产化
├── Web UI（Streamlit / Gradio）
├── 合同版本追踪
├── 审查历史记录和学习
└── 接入钉钉/企微通知
```

---

**参考资源：**
- [官方仓库](https://github.com/anthropics/knowledge-work-plugins/tree/main/legal)
- [Anthropic 多 Agent 最佳实践](https://www.anthropic.com/research/building-effective-agents)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [CrewAI 文档](https://docs.crewai.com/)
