# LegalHigh —— 龙律师法律 AI 助手设计方案

> 最新更新：2026-03-03 | 架构：文件驱动原生架构 | 兼容：Claude Code / Antigravity

---

## 一、核心工作需求

### 1.1 四阶段案件处理流程

| 阶段 | 核心动作 | 关键输出 |
|------|---------|---------| 
| **Phase 1** 信息收集 | 结构化整理事实、当事人、证据、诉求 | 《案件信息汇总表》+ 时效预警 |
| **Phase 2** 信息补充 | 追问缺失要件；处理事实不明 | 信息缺口清单 + 情景假设 |
| **Phase 3** 综合分析 | 法律检索、请求权基础、风险评估 | 《案件分析报告草稿》→ 律师审查 |
| **Phase 4** 专业服务 | 文书起草、诉讼策略、执行方案 | 可直接使用的法律文书/策略文件 |

**关键设计决策：** Phase 1 有意不做法律定性（防止早期误判），定性推迟到 Phase 3。

### 1.2 业务需求矩阵

```
├── 【案件管理】事实整理 / 证据梳理 / 争议焦点 / 多轮追问
├── 【法律研究】法条精确引用 / 司法解释 / 指导案例 / 废止校验
├── 【文书起草】诉讼文书 / 法律意见书 / 合同协议 / 执行文书
├── 【诉讼策略】管辖选择 / 举证分配 / 庭审策略 / 赔偿计算
├── 【执行专项】追加被执行人 / 恢复执行 / 执行异议
├── 【合规监控】时效校验 / 争议预警 / 地域差异
└── 【风险管理】确信度标注(🟢🟡🔴⚪) / 情景假设 / 免责声明
```

### 1.3 中国法律体系特殊约束

| 特征 | 系统设计影响 |
|------|-----------|
| 成文法体系 | 精确条文引用引擎 |
| 司法解释准立法效力 | 同步跟踪司法解释更新 |
| 会议纪要实质约束审判 | 维护《九民纪要》等知识库 |
| 近5年法律高频修订 | 时效性校验是核心硬需求 |
| 地域裁判尺度差异 | 区分"当地实务"维度 |
| 废止法律黑名单 | 《合同法》《物权法》等已废止，严禁引用 |

---

## 二、系统架构：文件驱动原生架构

> 该架构以 Anthropic Skills + MCP + Markdown 文件状态为核心，原生兼容 Claude Code 和 Antigravity，无需外部运行时。

### 2.1 架构总览

```
用户请求（案件材料/口述/截图）
    │
    ▼
┌───────────────────────────────────────────────────────┐
│              .agents/workflows/legal-case-workflow.md   │
│              （4阶段编排，// human-review 门控）           │
└───────────────────────┬───────────────────────────────┘
                        │ 按 Phase 调度对应 Skill
    ┌───────────────────▼───────────────────────────────┐
    │              skills/legal-cn/                       │
    │              （每个 Skill = 一个 SKILL.md）            │
    │                                                    │
    │  Phase 1-2:                  Phase 3:              │
    │  ┌──────────────────┐   ┌──────────────────────┐  │
    │  │ 信息提取          │   │ 法律研究              │  │
    │  │ 信息缺口处理       │   │ 请求权基础分析        │  │
    │  │ 诉讼时效计算       │   │ 风险评估              │  │
    │  └──────────────────┘   └──────────────────────┘  │
    │                                                    │
    │  Phase 4:                                          │
    │  ┌─────────────────────────────────────────────┐  │
    │  │ 合同对比 / 诉讼文书 / 执行策略（待开发）       │  │
    │  └─────────────────────────────────────────────┘  │
    └──────────────────────┬────────────────────────────┘
                           │ 加载领域规则
    ┌──────────────────────▼────────────────────────────┐
    │              playbooks/                             │
    │  legal.base.md（底线） + legal.{domain}.md（领域）   │
    └──────────────────────┬────────────────────────────┘
                           │ 读写案件状态
    ┌──────────────────────▼────────────────────────────┐
    │              cases/{case-id}/case.local.md          │
    │              （文件即状态，跨会话持久化）               │
    └──────────────────────┬────────────────────────────┘
                           │ 调用外部工具
    ┌──────────────────────▼────────────────────────────┐
    │              .mcp.json（MCP 工具协议）               │
    │  法律数据库 / 裁判文书网 / 执行信息网 / 通知          │
    └───────────────────────────────────────────────────┘
```

### 2.2 Workflow ↔ Skill 绑定与调度机制

`legal-case-workflow.md` 是编排中枢，通过**自然语言指令**引导 Agent 在每个 Phase 加载对应 Skill：

```
Workflow 执行流程：

1. Agent 读取 legal-case-workflow.md → 识别当前处于哪个 Phase
2. Workflow 中写明："使用 cn-legal-research Skill 进行法律检索"
3. Agent 自动读取 skills/legal-cn/cn-legal-research/SKILL.md → 作为当前任务的 System Prompt
4. 同时加载 playbooks/legal.{domain}.md → 叠加领域规则约束
5. 执行结果写入 cases/{case-id}/case.local.md 的对应区域
6. 遇到 // human-review 标注 → 暂停并等待律师批注
```

**Phase 转换条件（状态机规则）：**

| 转换 | 条件 | 模式判断 |
|------|------|--------|
| Phase 1 入口 | 事实三要素完整 + 法律问题单一 | 启用简化模式，跳过 Phase 2 直达 Phase 3 |
| Phase 1 → 2 | 事实表已填写 + 时效已计算 | 自动 |
| Phase 2 → 3 | 律师确认事实准确 OR 接受假设推进 | // human-review |
| Phase 3 → 4 | 律师审批分析报告通过 | // human-review |
| 任意 → 退回 | 律师标注"需重新分析" | 手动回退 |

`case.local.md` 的 frontmatter 中 `complexity` 字段（low/medium/high/extreme）由 Phase 1 信息提取 Skill 自动填写，用于上述简化模式判断。

**Phase 3 执行策略：** 法律研究 → 请求权基础 → 风险评估，**顺序执行**（文件驱动架构无原生并行能力；如未来引入 LangGraph 升级，可改为 `Send()` 并行）。

### 2.3 三层设计原则

| 层 | 载体 | 职责 | 兼容性 |
|----|------|------|-------|
| **Skill 内容层** | `SKILL.md`（Anthropic 规范）| Agent 的专业能力定义 | ✅ 原生 |
| **领域控制层** | `playbooks/*.md` | 律所价值观 + 领域审查清单 | ✅ 原生 |
| **状态持久化层** | `case.local.md` | 案件事实表 + 进度 + 审查记录 | ✅ 原生 |

### 2.4 目录结构

```
d:\#WorkSpace\Antigravity\LegalHigh\
├── .agents\workflows\
│   └── legal-case-workflow.md          ← 4阶段编排（/legal-case-workflow 触发）
├── skills\legal-cn\
│   ├── cn-case-information-extractor\SKILL.md    [Phase 1] ✅ 已实现
│   ├── cn-information-gap-handler\SKILL.md       [Phase 2] ✅ 已实现
│   ├── cn-statute-of-limitations\SKILL.md        [Phase 1-2] ✅ 已实现
│   ├── cn-legal-research\SKILL.md                [Phase 3] ✅ 已实现
│   ├── cn-rights-basis-analysis\SKILL.md         [Phase 3] ✅ 已实现
│   ├── cn-risk-assessment\SKILL.md               [Phase 3] ✅ 已实现
│   ├── cn-contract-comparison\SKILL.md           [Phase 4] ✅ 已实现
│   ├── cn-nda-review\SKILL.md                    [Phase 4] ✅ 已实现
│   ├── cn-litigation-strategy\SKILL.md           [Phase 4] ✅ 已实现
│   ├── cn-evidence-analysis\SKILL.md             [Phase 1] ✅ 已实现
│   └── cn-criminal-defense\SKILL.md              [Phase 3] ✅ 已实现
├── playbooks\
│   ├── legal.base.md            ✅ 已创建
│   ├── legal.company.md         ✅ 已创建
│   ├── legal.labor.md           ✅ 已创建
│   └── legal.criminal.md       ✅ 已创建
├── cases\
│   └── template\case.local.md   ✅ 已创建
└── .mcp.json                    ✅ 已配置（占位）
```

---

## 三、Skill 与 Playbook 体系

### 3.1 Skill 完整清单

| Skill | 功能 | 所属 Phase | 状态 |
|-------|------|-----------|------|
| `cn-case-information-extractor` | 从零散材料提取结构化事实 | Phase 1 | ✅ |
| `cn-information-gap-handler` | 识别信息缺口 + A/B类追问 + 情景假设 | Phase 2 | ✅ |
| `cn-statute-of-limitations` | 时效计算 + 节假日顺延 + 中断事由 | Phase 1-2 | ✅ |
| `cn-legal-research` | 法条检索 + 要件涵摄 + 废止校验 | Phase 3 | ✅ |
| `cn-rights-basis-analysis` | 请求权穷举 + 最优路径推荐 + 抗辩预测 | Phase 3 | ✅ |
| `cn-risk-assessment` | 败诉/执行/成本/声誉四维风险雷达 | Phase 3 | ✅ |
| `cn-contract-comparison` | 合同条款级 Diff + 风险标注 | Phase 4 | ✅ |
| `cn-nda-review` | 保密协议6项审查 + 竞业限制专项 | Phase 4 | ✅ |
| `cn-litigation-strategy` | 管辖分析 + 路径选择 + 庭审策略 + 赔偿计算 | Phase 4 | ✅ |
| `cn-evidence-analysis` | 要件→证据映射 + 证明力评级 + 举证策略 | Phase 1 | ✅ |
| `cn-criminal-defense` | 罪名要件审查 + 辩护路径 + 取保评估 + 量刑预估 | Phase 3 | ✅ |

### 3.2 Playbook 三层设计

```
加载优先级：case.local.md > legal.{domain}.md > legal.base.md

第一层 legal.base.md ——— 律所通用底线
  ├── 执业操守红线（绝不协助违法、避免绝对承诺）
  ├── 文风要求（结论先行、法言法语、禁废话起手式）
  └── IRAC 分析范式（Issue-Rule-Application-Conclusion）

第二层 legal.{domain}.md ——— 领域专项
  ├── legal.company.md（公司法审查清单 + 新公司法要点）
  ├── legal.labor.md（劳动法要点 + 仲裁前置 + 竞业限制）
  └── legal.criminal.md（程序审查 + 四要件 + 量刑参考）✅ 已创建

第三层 case.local.md ——— 案件专属（运行时动态更新）
  ├── YAML frontmatter（case_id, phase, domain）
  ├── 已确认事实 + 时效雷达
  ├── 信息缺口 TODO
  ├── 深度分析产出区
  └── 律师审批记录
```

### 3.3 反幻觉校验（装饰器模式）

不设独立 Agent，而是作为后处理管道集成到所有输出中：

```
每次法律引用前自动执行：
[] 该法是否属于废止黑名单？（《合同法》《物权法》等）
□ 案号格式是否规范？（年份+法院+类型+编号）
□ 司法解释是否已被替代？
□ 不确定 → 标注 ⚪ 并提示律师核实

确信度标注体系：
🟢 确认（法律明确 + 主流观点一致）
🟡 倾向（主流支持但有少数异议）
🔴 争议（学术/实务分歧大，须披露）
⚪ 待核实（无法确认，提示用核实工具查证）
```

### 3.4 律师审查门控（HITL 核心）

律师审查是整个系统的合规命门，不可简化。

**触发场景：**
1. Phase 2 → 3 转换前（律师确认事实和缺口处理结果）
2. Phase 3 分析报告生成后（律师审批法律结论）
3. Phase 4 重要文书起草后（律师最终签批）
4. 任何涉及 🔴 争议标注或刑事风险的输出

**审查操作：**
- ✅ **批准** → 进入下一 Phase，`case.local.md` 记录审批时间戳
- ✏️ **修改** → 律师直接在 `case.local.md` 内联编辑，Agent 读取 diff 后调整
- ❌ **拒绝** → 回退到上一 Phase 重新分析

**Diff 追踪与反哺：**
```
AI 生成稿 (v1) → 律师编辑 → 律师改稿 (v2)
                              ↓
              自动计算 diff (v1 vs v2)
              + 律师填写改稿理由标签
              + 存入 case.local.md 的「审批记录」区域
                              ↓
              长期积累 → 用作 Few-shot 示例 / 微调数据
```

### 3.5 输出 Schema 标准化

所有 Skill 的输出须遵循统一结构。以下 Pydantic 定义作为各 SKILL.md 中「输出要求」章节的参考蓝图（当前架构下 LLM 按 Markdown 格式输出；如引入 LangGraph 编排层，可直接用作 Runtime 校验）：

```python
# output_schemas.py (Pydantic v2)
from pydantic import BaseModel

class LegalAnalysisOutput(BaseModel):
    agent_name: str                    # 产出该结果的 Skill 名称
    confidence_level: str              # GREEN | YELLOW | RED | GRAY
    legal_basis: list[str]             # ["《民法典》第577条", ...]
    analysis: str                      # 核心分析文本
    uncertain_items: list[str]         # 待律师核实项
    recommendations: list[str]         # 行动建议
    requires_attorney_review: bool     # 是否触发审查门控

class CaseInfoOutput(BaseModel):
    parties: dict                      # {我方, 对方, 关联方}
    timeline: list[dict]               # [{date, fact, evidence}]
    evidence_list: list[dict]          # [{编号, 名称, 类型, 证明力}]
    claim_labels: list[str]            # 用户诉求标签（不做定性）
    missing_info: list[dict]           # [{category, question, impact}]

class StatuteOutput(BaseModel):
    deadlines: list[dict]              # [{type, start, deadline, remaining, urgency}]
    most_urgent: dict                  # 最紧急的一个
    alerts: list[str]                  # 预警消息
```

---

## 四、工程化设计

### 4.1 法律 RAG 检索策略

**法律文档按法律结构分块（非按字数切）：**
- 法律法规 → 按条文号切（保留条序号）
- 合同 → 按条款切（标注权利/义务/违约性质）
- 判决书 → 按"查明事实/本院认为/判决如下"三段切

**四阶段混合检索管道：**
1. BM25 关键词召回（精确匹配法条号/案号）
2. 语义向量召回（相似案情/法律问题）
3. RRF 融合排序（倒数排名融合）
4. 时效性过滤（废止法律黑名单剔除）

### 4.2 跨会话上下文注入

采用**结构化注入**策略：每次新会话仅注入 `case.local.md` 的 YAML frontmatter + 已确认事实摘要，不全量注入历史对话。

```
注入内容 = case.local.md 的 frontmatter
         + 已确认事实区域
         + 诉讼时效状态
         + 上次律师批注
         + 未解决缺口列表
```

每次会话结束后，Agent 自动更新 `case.local.md` 的对应区域。

### 4.3 证据 OCR 分类管道

| 证据类型 | 处理方式 | 输出 |
|---------|---------|------|
| 扫描合同 | Surya OCR + 合同字段提取 | 金额/日期/当事人/签名 |
| 微信截图 | Surya OCR(chat layout) + 时间戳保全 | 发送方/时间/关键内容 |
| 银行流水 | PyMuPDF 表格提取 | 金额汇总/关键时点 |
| 法院文书 | Surya OCR + 印章识别 | 案号/当事人/判决内容 |
| 手写合同 | Surya OCR(handwriting) + **强制人工复核** | 需律师核实原件 |

统一输出为 `EvidenceCard`（doc_type, key_facts, dates, amounts, parties, reliability, ocr_confidence）。

### 4.4 合规免责声明

每个输出根据置信度自动附加免责文本：

| 等级 | 触发条件 | 声明 |
|------|---------|------|
| 🟢 GREEN | 法律明确 + 律师已审查 | 可引用 |
| 🟡 YELLOW | 存在争议/待补充事实 | 须经律师审查 |
| 🔴 RED | 废止法律/刑事风险 | 必须全面复核 |
| ⚪ GRAY | 司法解释争议/地区差异 | 须结合实践判断 |

所有输出底部附加：`[AI 辅助生成] + 生成时间 + 模型版本 + 审查律师（待填）`

### 4.5 API 降级链

```
Claude 3.5 Sonnet（首选）
    ↓ 超时30s / 限流
Deepseek-R1-32B（本地 vLLM）
    ↓ 本地不可用
Qwen2.5-7B（本地轻量）
    ↓ 全部失败
保存任务队列 + 通知律师等待
```

降级时在输出中标注使用了备用模型。

### 4.6 数据隔离

- **文件系统**：`cases/{client_id}/{case-id}/` 目录级隔离，禁止跨目录访问
- **向量库**（Phase 3 后）：每客户独立 Collection（`legal_kb_{client_id}`）
- **LLM 调用**：禁止在同一 prompt 混入不同客户案件信息

### 4.7 质量评估指标

| 指标 | 计算方式 |
|------|---------|
| 法律引用准确率 | 有效法条引用 / 总引用 |
| 律师修改率 | 律师改稿行数 / 总行数 |
| 重大错误率 | 🔴标注被律师否定 / 总🔴标注 |
| 阶段完成率 | 到达 Phase 4 的案件 / 总案件 |

### 4.8 冷启动策略

```
Step 1（上线前）：导入 10-20 个律师历史胜诉案件结构化摘要
Step 2（上线后）：接入裁判文书网同类案件语料（标注 LOW 置信度）
Step 3（3个月后）：自有案件积累 >50 个后，逐步替换公开案件
```

### 4.9 案件记忆与跨案关联

长期积累的知识资产，实现「同一对方出现过」「类似案件怎么赢的」跨案学习。

**三个持久化维度：**

| 维度 | 存储内容 | 应用场景 |
|------|---------|----------|
| **案件库** | case_id, client, opponent, domain, outcome, key_arguments, attorney_edits | 跨案件检索 |
| **对方档案** | name, past_cases, enforcement_records, litigation_style, winning_args_against | 新案件开始时自动注入"对方历史" |
| **类案经验库** | fact_pattern, winning_strategy, key_evidence, cited_cases, outcome | 语义检索相似案件+胜率统计 |

**自动记忆注入：** 每个新案件进入 Phase 1 时，Workflow 自动检索：
1. 同一对方的历史案件 → 注入对方画像
2. 相似事实模式的类案 → 注入成功策略
3. 时效状态 → 注入紧急程度

在文件驱动架构下，案件记忆以 `cases/{case-id}/case.local.md` 为单元自然积累。跨案检索通过目录遍历或向量库（Phase 3 建设后）实现。

### 4.10 模型分级调用策略

**核心原则：** 简单任务用小模型省钱，复杂推理用大模型保质。

| 任务类型 | 模型选择 | 理由 |
|---------|---------|------|
| 信息提取（结构化字段） | Qwen2.5-7B | 模式匹配，无需深度推理 |
| 信息缺口分类（A/B/C/D） | Qwen2.5-7B | 决策树逻辑 |
| 诉讼时效计算 | Qwen2.5-7B | 日期计算 |
| 反幻觉校验 | Qwen2.5-7B | 规则匹配 |
| 法律关系定性 | Claude 3.5 Sonnet | 需要深度法律推理 |
| 请求权基础分析 | Claude 3.5 Sonnet | 需要穷举+涵摄 |
| 诉讼策略制定 | Claude 3.5 Sonnet | 需要对抗性思维 |
| 法律文书起草 | Claude 3.5 / Deepseek-R1-32B | 长文本+法言法语 |

**超长文档处理：** 当输入 Token > 70% 模型上限时，自动按法律结构分段处理后摘要合并。

---

## 五、技术选型

> 框架深度对比见 → [agent_framework_comparison.md](./agent_framework_comparison.md)

### 5.1 选型决策

经过 LangGraph / CrewAI / AutoGen v0.4 / OpenAI AgentKit / Semantic Kernel / Mastra / Claude Skills+MCP 的 7 框架对比，最终选择**文件驱动原生架构**：

- **编排层**：`.agents/workflows/*.md`（Antigravity 原生），替代 LangGraph
- **Skill 层**：Anthropic `SKILL.md` 规范（Claude Code / Antigravity 原生）
- **工具层**：MCP 协议（`.mcp.json`）
- **状态层**：Markdown 文件（`case.local.md`），替代 SQLite

> **设计演进说明**：早期设计基于 LangGraph + SQLite + Streamlit 方案。经兼容性评估后，为实现 Claude Code / Antigravity 原生应用，迁移至当前文件驱动架构。核心逻辑（4阶段工作流、HITL 审查、Skill 模块化）完全保留，状态管理从数据库切换为 Markdown 文件。如未来需要更强的并行执行和状态回溯能力，可在此基础上引入 LangGraph 作为编排层升级。

### 5.2 组件选型清单

| 组件 | 选择 | 理由 |
|------|------|------|
| **编排** | Antigravity Workflow | 原生兼容，零运行时依赖 |
| **Skill 规范** | Anthropic SKILL.md | 内容可移植，质量积累独立于框架 |
| **工具协议** | MCP | 行业标准 |
| **主力模型（大）** | Claude 3.5 Sonnet | 法律推理 + 200K 上下文 |
| **主力模型（小）** | Qwen2.5-7B | 信息提取/计算，节省 60% Token |
| **本地私有化** | Deepseek-R1-32B (vLLM) | 数据不出境 |
| **Embedding** | Qwen2.5-7B | 中文语义最优 |
| **向量库** | Qdrant（本地部署）| 混合检索 |
| **文档解析** | PyMuPDF + Surya OCR | 扫描件/手写/印章 |
| **状态存储** | case.local.md | 文件即状态，防灾 |

### 5.3 MCP 工具链规划

```json
{
  "mcpServers": {
    "filesystem":         {"formats": ["pdf","docx","jpg","png"], "ocr": true},
    "law-database":       {"sources": ["北大法宝","威科先行","国家法律法规数据库"]},
    "case-retrieval":     {"source": "中国裁判文书网", "search_type": "semantic+keyword"},
    "enforcement-check":  {"source": "中国执行信息公开网", "watch": ["失信被执行人","限消"]},
    "notification":       {"channels": ["企业微信","钉钉"], "triggers": ["时效预警","审查请求"]}
  }
}
```

---

## 六、实施路径

```
Phase 1（当前已完成 ✅）：
├── [x] 目录结构初始化
├── [x] 核心工作流 legal-case-workflow.md
├── [x] 三层 Playbook（base + company + labor）
├── [x] case.local.md 状态模板
└── [x] 7 个核心 SKILL.md 文件

Phase 2（下一步）：
├── [ ] 补充 4 个待开发 Skill（NDA/诉讼策略/证据/刑事）
├── [ ] 创建 legal.criminal.md Playbook
├── [ ] 配置 .mcp.json 占位文件
├── [ ] 在真实案件上端到端测试工作流
└── [ ] 冷启动：导入 10-20 个历史案件摘要

Phase 3（知识库建设）：
├── [ ] 构建本地法规向量库（Qwen2.5 Embedding + Qdrant）
├── [ ] 接入裁判文书网 MCP Server
├── [ ] 法律文档 OCR 管道（5类证据分类处理）
└── [ ] 质量评估指标追踪

Phase 4（生产化）：
├── [ ] 法律更新订阅（国家法律法规数据库变更推送）
├── [ ] 案件优先级队列（时效/开庭日期排序）
└── [ ] 多律师协作（权限分层 + 案件交接）
```

---

## 附录

### A. 与 Anthropic Legal Plugin 对比

| 维度 | Anthropic Legal Plugin | 龙律师（LegalHigh）|
|------|----------------------|-------------------|
| Agent 粒度 | 细粒度 Skill | 细粒度 Skill ✅ |
| 状态管理 | 无状态 | 有状态（case.local.md）✅ |
| 法律体系 | 英美法系 | 中国大陆法系 ✅ |
| 多阶段工作流 | ❌ | ✅ 4阶段 |
| 请求权基础 | ❌ | ✅ 大陆法系特有 |
| HITL 审查 | ❌ | ✅ human-review 门控 |
| Playbook | 2层 | 3层（base/domain/case）|

### B. 框架选型对比速览

当前采用**文件驱动原生架构**，LangGraph 保留为未来升级路径。

| 框架 | 核心优势 | 核心短板 | 结论 |
|------|---------|---------|------|
| **文件驱动原生** | 零依赖、原生兼容 Claude Code/Antigravity | 无并行、状态回溯弱 | **🏆 采用** |
| LangGraph | 状态管理最强 + HITL 精控 | 需 Python 运行时 | 升级路径 |
| CrewAI | 角色框架直观 | 精细控制不足 | 淘汰 |
| AutoGen v0.4 | MCP 集成好 | 状态管理弱 | 淘汰 |

> 详见 [agent_framework_comparison.md](./agent_framework_comparison.md)
