# 多 Agent 框架深度对比 × 法律工作场景选型报告

> 调研时间：2026-03 | 覆盖框架：LangGraph / CrewAI / AutoGen v0.4 / OpenAI Agents SDK / Semantic Kernel / Mastra / Claude Skills+MCP

---

## 一、框架全景图

```
框架定位矩阵（控制精度 vs 开发速度）

高控制精度
    │
    │  LangGraph ●              Semantic Kernel ●
    │  (图状态机，生产级)          (微软生态，企业级)
    │
    │           AutoGen v0.4 ●
    │           (事件驱动，对话中心)
    │
    │                    CrewAI ●
    │                    (角色团队，快速上手)
    │
    │                              Mastra ●
    │                              (TS原生，全栈)
    │
    │                                    Claude Skills+MCP ●
    │                                    (Markdown驱动，零代码)
    │
低控制精度────────────────────────────────────────────→ 快速开发
```

---

## 二、各框架核心特性深度解析

### 2.1 LangGraph（首选候选）

**核心理念：** 图状态机（Graph State Machine）

```python
# 核心概念示例
from langgraph.graph import StateGraph, START, END

class LegalWorkflowState(TypedDict):
    case_info: dict
    phase: int          # 1/2/3/4
    analysis: dict
    attorney_approved: bool

graph = StateGraph(LegalWorkflowState)
graph.add_node("phase1_extract", extract_info)
graph.add_node("phase3_analyze", analyze_parallel)  # 并行分支
graph.add_conditional_edges("phase3_analyze", route_to_review)

# 支持 time-travel debugging（回溯任意历史节点）
config = {"configurable": {"thread_id": "case-001"}}
```

**评分（满分10分）：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态持久化 | 9 | 原生 Checkpointer，支持 SQLite/Redis/PostgreSQL |
| HITL 支持 | 10 | `interrupt_before/after` 精确控制暂停点 |
| 并行执行 | 9 | `Send()` API 动态并行，`parallel_branch` |
| MCP 集成 | 8 | 通过 `langchain-mcp-adapters` 无缝对接 |
| 可观测性 | 9 | LangSmith 全链路追踪 |
| 学习曲线 | 6 | 图概念需要适应，但文档完善 |
| Python 生态 | 10 | 最成熟，社区最大 |
| **综合** | **8.7** | |

**最适合：** 复杂有状态工作流、精确控制、生产级部署

---

### 2.2 CrewAI

**核心理念：** 角色团队（Role-Based Agent Teams）

```python
from crewai import Agent, Task, Crew, Process

# 角色化定义，更贴近龙律师的"人格设定"思路
legal_researcher = Agent(
    role="法律研究员",
    goal="检索相关法律条文和判例",
    backstory="精通中国法律数据库检索...",
    tools=[search_law_db, search_cases],
    llm=claude_sonnet
)

contract_reviewer = Agent(
    role="合同审查律师",
    goal="逐条款审查，识别风险",
    ...
)

crew = Crew(
    agents=[legal_researcher, contract_reviewer],
    tasks=[research_task, review_task],
    process=Process.hierarchical,  # 层级模式（有管理者Agent）
    manager_llm=claude_sonnet
)
```

**评分：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态持久化 | 7 | 支持但不如 LangGraph 精细 |
| HITL 支持 | 7 | `human_input=True` 简单集成 |
| 并行执行 | 8 | `Process.hierarchical` 支持 |
| MCP 集成 | 7 | 通过自定义 Tool 接入 |
| 可观测性 | 7 | CrewAI Cloud 监控 |
| 学习曲线 | 9 | 最友好，概念直觉化 |
| **综合** | **7.5** | |

**最适合：** 快速原型、清晰角色分工、团队协作场景

**法律场景问题：** 4阶段有状态流程控制不够精细；状态回溯能力弱

---

### 2.3 AutoGen v0.4（Microsoft）

**核心理念：** 事件驱动的多 Agent 对话

```python
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.anthropic import AnthropicChatCompletionClient

# v0.4 重构为事件驱动架构，异步消息传递
legal_agent = AssistantAgent(
    name="龙律师",
    model_client=AnthropicChatCompletionClient(model="claude-3-5-sonnet"),
    system_message="你是专业法律顾问...",
)

# 多 Agent 对话团队
team = RoundRobinGroupChat([legal_agent, review_agent])
result = await team.run(task="审查这份合同...")
```

**评分：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态持久化 | 6 | 需要额外实现，v0.4 原生支持有限 |
| HITL 支持 | 8 | `UserProxyAgent` 天然支持 |
| 并行执行 | 7 | 支持但控制不如 LangGraph |
| MCP 集成 | 9 | v0.4 原生 MCP 支持最好 |
| 可观测性 | 7 | 支持 OpenTelemetry |
| 代码执行 | 10 | 内置沙箱代码执行（法律计算场景有用）|
| **综合** | **7.8** | |

**最适合：** 涉及代码执行的场景；AutoGen Studio 无代码界面

---

### 2.4 OpenAI Agents SDK（AgentKit）

**核心理念：** 轻量 Handoff 为核心的编排

```python
from agents import Agent, Runner, handoff

# Swarm 的生产级继承者
triage_agent = Agent(
    name="案件分诊",
    instructions="判断案件类型，分配给专业律师Agent",
    handoffs=[
        handoff(contract_agent, "涉及合同纠纷"),
        handoff(criminal_agent, "涉及刑事问题"),
        handoff(labor_agent, "涉及劳动争议"),
    ]
)

# Tracing 内置，可观测性好
result = Runner.run_sync(triage_agent, "我有一份合同需要审查...")
```

**评分：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态持久化 | 5 | 基本无状态，需要自己实现 |
| HITL 支持 | 7 | 需要自定义 |
| 并行执行 | 7 | 支持并行工具调用 |
| MCP 集成 | 8 | 官方 MCP 支持 |
| 可观测性 | 9 | 内置 Tracing，可视化好 |
| 锁定 OpenAI | ⚠️ | 虽支持其他模型但最优化 OpenAI |
| **综合** | **7.0** | |

**法律场景问题：** 4阶段有状态对话是核心需求，此框架状态管理太弱

---

### 2.5 Semantic Kernel（Microsoft）

**核心理念：** 企业级 AI 编排，Plugins+Skills

```python
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.anthropic import AnthropicChatCompletion

kernel = Kernel()
kernel.add_service(AnthropicChatCompletion(ai_model_id="claude-3-5-sonnet"))

# Plugin 概念最接近 Anthropic Legal Plugin 的 Skill
@kernel_function(description="审查合同条款")
async def review_contract(self, contract_text: str) -> str:
    ...

# Planner 自动规划任务
planner = SequentialPlanner(kernel)
plan = await planner.create_plan("审查这份NDA并生成报告")
```

**评分：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 企业集成 | 10 | Azure/Microsoft 365 深度集成 |
| 状态持久化 | 7 | 需要结合 Azure 服务 |
| Plugin 体系 | 9 | 最接近 Anthropic Skills 概念 |
| Python+C# | 8 | 双语言支持 |
| 学习曲线 | 6 | 概念较多，文档复杂 |
| 国内适用性 | 4 | 高度依赖 Azure，国内访问受限 |
| **综合** | **6.5**（国内场景）| |

---

### 2.6 Mastra（TypeScript 原生）

**核心理念：** TypeScript-first，全栈 AI 应用开发

```typescript
import { Agent, Workflow } from "@mastra/core";

const legalWorkflow = new Workflow({
  name: "legal-case-processing",
  steps: [
    { id: "extract", action: extractCaseInfo },
    { id: "analyze", action: analyzeCase, parallel: true },
    { id: "review", action: attorneyReview, waitForHuman: true },
  ]
});

// 内置 RAG、Memory、Evaluation
const agent = new Agent({
  name: "龙律师",
  model: { provider: "ANTHROPIC", name: "claude-3-5-sonnet" },
  memory: new Memory({ provider: "sqlite" }),
  tools: { legalResearch, caseRetrieval }
});
```

**评分：**
| 维度 | 评分 | 说明 |
|------|------|------|
| TypeScript 生态 | 10 | 如果团队是 TS 栈 |
| 状态持久化 | 8 | 内置持久化 |
| Python 适用性 | 2 | **不适合纯 Python 项目** |
| 全栈集成 | 9 | 前后端一体 |
| 成熟度 | 6 | 2025年新兴，社区较小 |
| **综合（Python项目）** | **4.0** | 不推荐 |

---

### 2.7 Claude Skills + MCP（Anthropic 原生方案）

**核心理念：** Markdown-driven，零代码，Claude Cowork 原生

```
无需写代码框架代码
Skill = SKILL.md 文件（高质量System Prompt）
Commands = 斜杠命令触发
MCP = 外部工具标准协议

优势：
✅ 与 Anthropic Legal Plugin 完全同源
✅ 最小化技术债务
✅ Skills 可移植到任何 Claude 环境

劣势：
❌ 仅适用于 Claude（模型锁定）
❌ 缺乏复杂状态机控制
❌ 不支持自定义并行策略
❌ 律师审查节点难以精确控制
```

**评分：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 快速上手 | 10 | 写 Markdown 即可 |
| 模型灵活性 | 2 | Claude 锁定 |
| 状态控制 | 4 | 依赖对话上下文，不可靠 |
| 生产稳定性 | 5 | 无法可靠管理4阶段流程 |
| MCP 集成 | 10 | 原生最优 |
| **综合** | **5.8** | 适合 MVP 验证期 |

---

## 三、法律场景需求对框架的关键约束

```
法律工作场景特殊需求 → 框架必须满足的能力

1. 4阶段有状态工作流
   必须：持久化状态 + 跨轮次记忆
   → 排除：OpenAI AgentKit（无状态）、Claude Skills（对话依赖）

2. 律师审查门控（HITL）
   必须：精确控制暂停点 + 修改后恢复
   → 最优：LangGraph（interrupt_before/after）

3. Phase 3 并行执行
   必须：法律研究/请求权/风险评估同时运行
   → 最优：LangGraph（Send() + parallel_branch）

4. 模型灵活性
   必须：Claude 3.5（分析）+ 小模型（信息提取）
   → 排除：Semantic Kernel（Azure绑定）、OpenAI AgentKit（OpenAI优化）

5. 数据本地化
   必须：支持私有化部署（数据不出境）
   → 配合 Deepseek-R1-32B 本地推理

6. Skill 模块化
   应该：SKILL.md 规范，可复用可移植
   → 设计层面采用 Anthropic Skill 规范，实现层面用 LangGraph

7. MCP 工具集成
   应该：法律数据库、裁判文书网、法律更新监控
   → LangGraph + langchain-mcp-adapters 均支持

8. 可观测性（法律合规审计）
   必须：每次 AI 决策可追溯，律师改稿可查
   → LangGraph + LangSmith，或自建日志
```

---

## 四、综合评分汇总

| 框架 | 状态管理 | HITL | 并行 | MCP | 模型灵活 | 本地化 | 可观测 | 法律场景综合 |
|------|---------|------|------|-----|---------|-------|-------|------------|
| **LangGraph** | ⭐9 | ⭐10 | ⭐9 | ⭐8 | ⭐9 | ⭐9 | ⭐9 | **🏆 8.7** |
| AutoGen v0.4 | ⭐6 | ⭐8 | ⭐7 | ⭐9 | ⭐8 | ⭐8 | ⭐7 | **7.5** |
| CrewAI | ⭐7 | ⭐7 | ⭐8 | ⭐7 | ⭐8 | ⭐8 | ⭐7 | **7.4** |
| OpenAI AgentKit | ⭐5 | ⭐7 | ⭐7 | ⭐8 | ⭐6 | ⭐7 | ⭐9 | **7.0** |
| Semantic Kernel | ⭐7 | ⭐7 | ⭐7 | ⭐8 | ⭐7 | ⭐4 | ⭐8 | **6.5** |
| Claude Skills+MCP | ⭐4 | ⭐5 | ⭐4 | ⭐10 | ⭐2 | ⭐7 | ⭐5 | **5.8** |
| Mastra (TS) | ⭐8 | ⭐7 | ⭐8 | ⭐8 | ⭐8 | ⭐7 | ⭐7 | **不适用(TS)** |

---

## 五、最终选型决策：三层混合架构

> **结论：** 没有任何单一框架完美满足所有需求。最优解是**分层组合**。

```
┌──────────────────────────────────────────────────────┐
│                  三层混合架构                           │
│                                                      │
│  Layer 1: Skill 定义层                                │
│  ┌───────────────────────────────┐                   │
│  │   Anthropic Skills 规范        │                   │
│  │   SKILL.md + CONNECTORS.md    │                   │
│  │   （内容层，与框架解耦）          │                   │
│  └───────────────────────────────┘                   │
│                   ↓ 加载                              │
│  Layer 2: 编排引擎层                                   │
│  ┌───────────────────────────────┐                   │
│  │   LangGraph StateGraph        │                   │
│  │   - 4阶段状态机                │                   │
│  │   - HITL interrupt 门控        │                   │
│  │   - 并行分支                    │                   │
│  │   - 持久化 Checkpointer        │                   │
│  └───────────────────────────────┘                   │
│                   ↓ 调用                              │
│  Layer 3: 工具集成层                                   │
│  ┌───────────────────────────────┐                   │
│  │   MCP (Model Context Protocol) │                  │
│  │   - 法律数据库                  │                   │
│  │   - 裁判文书网                  │                   │
│  │   - 法律更新监控                │                   │
│  │   - 文档存储                    │                   │
│  └───────────────────────────────┘                   │
└──────────────────────────────────────────────────────┘
```

### 5.1 为什么是 LangGraph（而不是其他）

| 决策点 | LangGraph 的回答 |
|--------|----------------|
| 4阶段状态机 | `StateGraph` 天然支持，节点=Phase，边=条件转换 |
| Phase 3 并行 | `Send()` API 动态并行，汇聚后继续 |
| 律师审查暂停 | `interrupt_before=["attorney_review"]` 精确控制 |
| 状态跨轮次保存 | `SqliteSaver` / `PostgresSaver` 内置 |
| 回溯历史状态 | Time-travel debugging，可回到任意 Phase |
| 模型分层调用 | 节点级别独立配置模型，无框架限制 |
| MCP 集成 | `langchain-mcp-adapters` 成熟方案 |
| 私有化部署 | 纯 Python，无云依赖 |

### 5.2 为什么保留 Anthropic Skills 规范

Anthropic Skills 是**内容标准**而非**技术束缚**：
- `SKILL.md` 文件可以被 LangGraph Node 直接加载为 System Prompt
- 保持内容的可移植性（未来可迁移到任何框架）
- SKILL.md 的精心设计远比框架选择更影响输出质量

```python
# Skills 与 LangGraph 的集成方式
def load_skill(skill_name: str) -> str:
    """加载 Anthropic 格式的 SKILL.md 作为 System Prompt"""
    return Path(f"skills/{skill_name}/SKILL.md").read_text()

def legal_research_node(state: LegalWorkflowState):
    """LangGraph 节点，加载对应 Skill"""
    skill_prompt = load_skill("cn-legal-research")
    playbook = load_playbook(state["case_domain"])  # 领域 Playbook
    
    response = claude_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        system=f"{skill_prompt}\n\n## Playbook\n{playbook}",
        messages=[{"role": "user", "content": state["case_info"]}]
    )
    return {"legal_analysis": response.content[0].text}
```

### 5.3 为什么加入 AutoGen v0.4 的 MCP 层（可选）

AutoGen v0.4 对 MCP 的原生支持是所有框架中最好的，但不用于主编排：

```
方案A（纯 LangGraph）：
LangGraph → langchain-mcp-adapters → MCP Server
（简单，已足够）

方案B（混合，MCP需求复杂时）：
LangGraph（主编排）
    ↓ 当需要复杂 MCP 工具链时
AutoGen MCP Runtime（工具执行子系统）
    ↓
MCP Servers（法律数据库/裁判文书网等）
```

> 建议从方案A开始，MCP 需求复杂时升级方案B

---

## 六、技术选型最终决定

| 组件 | 选择 | 为什么不选其他 |
|------|------|--------------|
| **编排框架** | **LangGraph 0.2+** | 唯一满足所有4个核心约束（状态/HITL/并行/可观测）|
| **Skill 规范** | **Anthropic Skills（SKILL.md）** | 内容与框架解耦，可移植性最强 |
| **工具协议** | **MCP（Model Context Protocol）** | 行业标准，Anthropic+微软+OpenAI 三方背书 |
| **主力推理** | **Claude 3.5 Sonnet API** | 法律推理质量最优 |
| **本地私有化** | **Deepseek-R1-32B（vLLM部署）** | 中文法律理解优秀，无数据出境风险 |
| **信息提取** | **Qwen2.5-7B（量化版）** | 结构化提取任务，成本低60% |
| **状态持久化** | **LangGraph + SQLite** | 轻量，无需额外服务 |
| **向量检索** | **Qdrant + Qwen2.5-7B Embedding** | 本地部署，中文语义最优 |
| **可观测性** | **LangSmith（开发）/ 自建日志（生产）** | 开发调试用 LangSmith，生产用 SQLite 日志保证数据安全 |
| **律师审查UI** | **Streamlit** | 快速开发，内联编辑 + diff 展示 |
| **MCP 集成** | **langchain-mcp-adapters** | LangGraph 生态官方方案 |

---

## 七、关键架构代码骨架

```python
# legal_workflow.py —— 完整骨架
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt
from anthropic import Anthropic
from pathlib import Path
from typing import TypedDict, Optional

class LegalState(TypedDict):
    # 会话管理
    session_id: str
    phase: int  # 1/2/3/4
    mode: str   # "simplified" | "full"
    complexity: str  # "low" | "medium" | "high" | "extreme"
    
    # 案件数据
    case_info: Optional[dict]
    missing_info: Optional[list]
    scenario_analysis: Optional[dict]
    
    # 分析结果（Phase 3 并行产生）
    legal_research: Optional[dict]
    rights_basis: Optional[dict]
    risk_assessment: Optional[dict]
    
    # 律师审查
    draft_report: Optional[str]
    attorney_approved: bool
    attorney_edits: Optional[str]
    
    # 时效管理
    deadlines: Optional[list]

def load_skill(name: str) -> str:
    return Path(f"skills/{name}/SKILL.md").read_text(encoding="utf-8")

def load_playbook(domain: str, case_local: str = "") -> str:
    base = Path("playbooks/legal.base.md").read_text(encoding="utf-8")
    domain_pb = Path(f"playbooks/legal.{domain}.md").read_text(encoding="utf-8")
    case_pb = Path(f"cases/{case_local}/case.local.md").read_text(encoding="utf-8") if case_local else ""
    return f"{base}\n\n{domain_pb}\n\n{case_pb}"

# ─── 节点定义 ────────────────────────────────────────
def complexity_router(state: LegalState) -> dict:
    """前置评估：案件复杂度 → 路由策略"""
    # 小模型完成分类
    complexity = assess_complexity(state["case_info"])
    mode = "simplified" if complexity == "low" else "full"
    return {"complexity": complexity, "mode": mode}

def phase1_extract(state: LegalState) -> dict:
    """信息提取（小模型）"""
    skill = load_skill("cn-case-information-extractor")
    # ... 小模型调用
    return {"case_info": extracted, "phase": 1}

def statute_check(state: LegalState) -> dict:
    """诉讼时效计算（规则引擎，不用LLM）"""
    deadlines = calculate_all_deadlines(state["case_info"])
    return {"deadlines": deadlines}

def gap_handler(state: LegalState) -> dict:
    """信息缺口处理：追问 or 情景假设（小模型）"""
    skill = load_skill("cn-information-gap-handler")
    return {"missing_info": gaps, "scenario_analysis": scenarios}

# Phase 3 三个并行节点（大模型）
def legal_research(state: LegalState) -> dict:
    skill = load_skill("cn-legal-research")
    playbook = load_playbook(state["case_info"]["domain"])
    # Claude 3.5 Sonnet 调用
    return {"legal_research": result}

def rights_basis(state: LegalState) -> dict:
    skill = load_skill("cn-rights-basis-analysis")
    return {"rights_basis": result}

def risk_assessment(state: LegalState) -> dict:
    skill = load_skill("cn-legal-risk-assessment")
    return {"risk_assessment": result}

def attorney_review_gate(state: LegalState) -> dict:
    """律师审查门控 —— 在此暂停，等待人工确认"""
    # 生成审查摘要
    draft = compile_report(state)
    
    # LangGraph interrupt：暂停工作流，等待律师操作
    attorney_response = interrupt({
        "draft_report": draft,
        "red_flags": extract_red_flags(state),
        "uncertain_items": extract_uncertain(state),
        "action": "请律师审查：批准/修改/拒绝"
    })
    
    # 律师确认后继续
    return {
        "attorney_approved": attorney_response["approved"],
        "attorney_edits": attorney_response.get("edits"),
        "draft_report": attorney_response.get("revised_draft", draft)
    }

# ─── 图构建 ──────────────────────────────────────────
def build_legal_workflow():
    graph = StateGraph(LegalState)
    
    # 添加节点
    graph.add_node("complexity_router", complexity_router)
    graph.add_node("phase1_extract", phase1_extract)
    graph.add_node("statute_check", statute_check)
    graph.add_node("gap_handler", gap_handler)
    graph.add_node("legal_research", legal_research)
    graph.add_node("rights_basis", rights_basis)
    graph.add_node("risk_assessment", risk_assessment)
    graph.add_node("attorney_gate", attorney_review_gate)
    
    # 边定义
    graph.add_edge(START, "complexity_router")
    graph.add_edge("complexity_router", "phase1_extract")
    graph.add_edge("phase1_extract", "statute_check")
    graph.add_edge("statute_check", "gap_handler")
    
    # Phase 3 并行执行
    graph.add_edge("gap_handler", "legal_research")
    graph.add_edge("gap_handler", "rights_basis")
    graph.add_edge("gap_handler", "risk_assessment")
    
    # 汇聚后进入律师审查
    graph.add_edge(["legal_research", "rights_basis", "risk_assessment"], "attorney_gate")
    graph.add_conditional_edges("attorney_gate", route_after_review)
    
    # 持久化：支持跨轮次状态保存
    memory = SqliteSaver.from_conn_string("legal_cases.db")
    return graph.compile(checkpointer=memory, interrupt_before=["attorney_gate"])

# 运行示例
workflow = build_legal_workflow()
config = {"configurable": {"thread_id": "case-2026-001"}}

# 第一次运行，遇到律师审查节点自动暂停
result = workflow.invoke({"session_id": "001", "phase": 1}, config)
# → 输出 interrupt 信号，律师在 Streamlit 界面审查

# 律师完成审查后，传入反馈继续执行
result = workflow.invoke(
    Command(resume={"approved": True, "edits": "第三条建议修改为..."}),
    config
)
```

---

## 八、迁移路径（渐进式落地）

```
Week 1-2: 龙律师提示词 → 单体 Agent（无框架）
    ├── 验证业务逻辑正确性
    └── 积累真实案件测试数据

Week 3-4: 引入 LangGraph（骨架搭建）
    ├── 只替换 Phase 1 + 律师审查节点
    └── 其余 Phase 仍用单体 Agent 处理

Month 2: 拆分 Agent + MCP 接入
    ├── 信息提取/时效计算改小模型
    ├── Phase 3 并行化（法律研究/请求权/风险）
    └── 接入第一个 MCP 工具（法律数据库）

Month 3+: 完整多 Agent + 案件记忆
    ├── Skill 文件体系完善
    ├── SQLite 案件记忆库
    └── 全 MCP 工具链
```

---

## 九、Anthropic Agent Teams 专项对比

Anthropic 官方实际上有**两套**完全不同的多 Agent 范式，需要区分清楚。

### 9.1 两套范式的本质区别

```
范式A：Orchestrator + Subagents（API/文档层，稳定）
─────────────────────────────────────────────────
  主 Agent（Orchestrator）
     ├── 子 Agent A（独立 context，单向汇报）
     ├── 子 Agent B（独立 context，单向汇报）
     └── 子 Agent C（独立 context，单向汇报）
  特点：层级型，子 Agent 间无法横向通信
  状态：无内建持久化，依靠主 Agent context
  成熟度：✅ 稳定，生产可用

范式B：Agent Teams（Claude Code 实验功能，2026）
─────────────────────────────────────────────────
  Lead Agent（团队负责人）
     ├── Teammate A ←──→ Teammate B（可直接通信！）
     └── 共享任务列表（类似 GitHub Issues）
  特点：扁平化，成员间点对点通信 + 任务认领
  内建：Mailbox 邮箱、任务认领、生命周期管理
  成熟度：⚠️ 实验性，仅限 Claude Code 场景
```

### 9.2 三方对比：Subagents vs Agent Teams vs 龙律师方案

| 维度 | Anthropic Subagents | Anthropic Agent Teams | 龙律师方案（LangGraph）|
|------|--------------------|-----------------------|---------------------|
| **状态持久化** | ❌ 无内建 | ❌ 无内建 | ✅ SqliteSaver 跨轮次 |
| **4阶段工作流** | ❌ 无状态机 | ❌ 无状态机 | ✅ StateGraph 原生 |
| **律师审查 HITL** | ⚠️ 需自行实现 | ⚠️ 需自行实现 | ✅ `interrupt_before` 精确暂停 |
| **并行执行** | ✅ 天然并行 | ✅ 成员并行 | ✅ `Send()` 动态并行 |
| **模型分层** | ✅ 子 Agent 独立配置 | ✅ Lead/成员不同模型 | ✅ 节点级独立配置 |
| **Agent 间通信** | ❌ 单向汇报 | ✅ 双向 P2P | 按需（主要单向汇聚）|
| **Token 消耗** | 高 | 极高（full session）| 可控（共享 State）|
| **法律场景定制** | ❌ 通用 | ❌ 仅限代码场景 | ✅ 法律 Playbook + 时效 |
| **私有化部署** | ❌ Claude API 绑定 | ❌ Claude Code 绑定 | ✅ 支持本地 Deepseek |
| **Skill 规范** | ✅ Skills System Prompt | ❌ 无 | ✅ 继承 SKILL.md |

### 9.3 Agent Teams 值得借鉴的点

**可借鉴：共享任务队列设计**

Agent Teams 的核心创新是成员可认领共享任务列表。  
法律方案可将此思路引入 Phase 3 State：

```python
# 在 LegalState 中加入任务队列（借鉴 Agent Teams）
phase3_tasks: list[dict]  # [{id, type, status, result}]
# 例：
# {"id": "t1", "type": "legal_research",  "status": "running"}
# {"id": "t2", "type": "rights_basis",    "status": "done", "result": {...}}
# {"id": "t3", "type": "risk_assessment", "status": "pending"}
# 法律研究完成后，风险评估可读取其结果再执行（依赖感知）
```

**不需借鉴：Mailbox 横向通信**

法律 Phase 3 中，法律研究/请求权基础/风险评估三者**高度独立**，  
不需要实时辩论，不需要竞争假设，Mailbox 带来的复杂度远超收益。

### 9.4 最终判断

```
龙律师方案的定位 ≈ Anthropic Subagents 模式
                 + LangGraph 补足状态管理短板
                 + Anthropic SKILL.md 规范内容层

Agent Teams 的用途：代码探索中的「AI 开发团队」
法律工作流的特点：有序推进 + 审查门控，非探索协作
→ 无需切换到 Agent Teams 范式
→ 可从其「共享任务队列」借鉴一个设计细节
```
