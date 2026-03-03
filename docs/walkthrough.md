# LegalHigh 项目 Walkthrough

## 项目概述

龙律师法律 AI 助手（LegalHigh），采用文件驱动原生架构，兼容 Claude Code / Antigravity。

## 完成工作

### 1. 设计方案（6轮Review + 完整重构）

[longlu_vs_anthropic_design.md](file:///C:/Users/Admin/.gemini/antigravity/brain/b15b2a2b-fba2-4a79-b787-b199a99331e8/longlu_vs_anthropic_design.md) — ~510 行，六章结构：

| 章 | 内容 |
|----|------|
| 一 | 四阶段案件流程 + 业务矩阵 + 中国法律约束 |
| 二 | 文件驱动架构 + Workflow↔Skill绑定 + Phase转换条件 |
| 三 | 11个Skill清单 + 三层Playbook + HITL门控 + Schema |
| 四 | RAG + 上下文注入 + OCR + 免责 + 降级 + 隔离 + 质量 + 冷启动 + 记忆 + 模型路由 |
| 五 | 技术选型 + MCP工具链 |
| 六 | 实施路径（4阶段） |

### 2. 已落地文件清单

| 文件 | 路径 | 状态 |
|------|------|------|
| 核心工作流 | [legal-case-workflow.md](file:///d:/%23WorkSpace/Antigravity/LegalHigh/.agents/workflows/legal-case-workflow.md) | ✅ |
| 通用Playbook | [legal.base.md](file:///d:/%23WorkSpace/Antigravity/LegalHigh/playbooks/legal.base.md) | ✅ |
| 公司法Playbook | [legal.company.md](file:///d:/%23WorkSpace/Antigravity/LegalHigh/playbooks/legal.company.md) | ✅ |
| 劳动法Playbook | [legal.labor.md](file:///d:/%23WorkSpace/Antigravity/LegalHigh/playbooks/legal.labor.md) | ✅ |
| 案件状态模板 | [case.local.md](file:///d:/%23WorkSpace/Antigravity/LegalHigh/cases/template/case.local.md) | ✅ |

### 3. Skills（7个已实现，已按 skill-creator 规范优化）

| Skill | Phase | 优化要点 |
|-------|-------|---------|
| [cn-case-information-extractor](file:///d:/%23WorkSpace/Antigravity/LegalHigh/skills/legal-cn/cn-case-information-extractor/SKILL.md) | 1 | +complexity输出 +买卖示例 |
| [cn-information-gap-handler](file:///d:/%23WorkSpace/Antigravity/LegalHigh/skills/legal-cn/cn-information-gap-handler/SKILL.md) | 2 | +劳动纠纷示例 +A/B分级why |
| [cn-statute-of-limitations](file:///d:/%23WorkSpace/Antigravity/LegalHigh/skills/legal-cn/cn-statute-of-limitations/SKILL.md) | 1-2 | +时效中断示例 +节假日顺延规则 |
| [cn-legal-research](file:///d:/%23WorkSpace/Antigravity/LegalHigh/skills/legal-cn/cn-legal-research/SKILL.md) | 3 | +废止黑名单内联 +确信度标注 |
| [cn-rights-basis-analysis](file:///d:/%23WorkSpace/Antigravity/LegalHigh/skills/legal-cn/cn-rights-basis-analysis/SKILL.md) | 3 | +穷举why +竞合处理 +股东示例 |
| [cn-risk-assessment](file:///d:/%23WorkSpace/Antigravity/LegalHigh/skills/legal-cn/cn-risk-assessment/SKILL.md) | 3 | +四维why +交叉验证 +劳动示例 |
| [cn-contract-comparison](file:///d:/%23WorkSpace/Antigravity/LegalHigh/skills/legal-cn/cn-contract-comparison/SKILL.md) | 4 | +隐蔽修改why +采购合同示例 |

### 4. Skill 优化维度（skill-creator 规范）

每个 SKILL.md 统一升级了：
- **Pushy description**：明确触发场景和触发短语
- **Why 解释**：每个 Skill 增加设计决策理由段
- **真实示例**：输入→输出完整示例
- **确信度对齐**：🟢🟡🔴⚪ 标注体系
- **祈使语气**：从角色设定改为指令式

## 使用方式

```
/legal-case-workflow   ← 触发完整4阶段案件处理
```

## 后续待办

Phase 2：补充4个Skill + criminal Playbook + .mcp.json + 端到端测试
Phase 3：向量库 + 裁判文书网MCP + OCR管道 + 质量追踪
