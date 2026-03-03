---
description: 法律案件处理4阶段核心工作流 (File-Driven)
---

# LegalHigh 案件处理核心工作流

本工作流定义了"龙律师"处理一个新案件的标准 4 阶段流程。以 `cases/{case_id}/case.local.md` 作为核心状态容器。

## 前置准备
1. 确认当前处理的案件 ID 以及对应领域（company/labor/criminal/其他）。
2. 复制 `cases/template/case.local.md` 到 `cases/{case_id}/case.local.md` 并初始化基础信息。
3. 加载通用指导 `playbooks/legal.base.md` 和对应领域 Playbook（如 `playbooks/legal.company.md`）。

---

## Phase 1：信息收集与结构化
**目标**：从零散材料中提取确定事实，计算紧急日期，评估案件复杂度。

1. **信息提取**：使用 `cn-case-information-extractor` Skill 从用户提供的初始材料中提取结构化事实。该 Skill 会自动输出 `complexity` 字段（low/medium/high/extreme）。
2. **证据梳理**（如有证据材料）：使用 `cn-evidence-analysis` Skill 对现有证据进行要件映射和证明力评估。
3. **时效检查**：使用 `cn-statute-of-limitations` Skill 计算最紧迫的时效截止日。
4. **填报状态**：将上述信息写入 `case.local.md` 的「已确认事实」「证据清单」「诉讼时效」区域。

**简化模式判断**：如果 `complexity` 为 `low`（事实完整 + 法律问题单一），可跳过 Phase 2 直接进入 Phase 3。

---

## Phase 2：信息缺口处理
**目标**：发现矛盾或缺失要件，引导用户补充或做出假设。

1. **缺口计算**：使用 `cn-information-gap-handler` Skill 对比事实表与领域 Playbook 审查清单，列出 A/B 类缺口。
2. **状态更新**：将缺口清单和情景假设写入 `case.local.md` 的「待办信息缺口」区域。

// human-review
⚠️ **律师审查点**：在继续 Phase 3 之前，请律师在 `case.local.md` 中确认：
1. Agent 推理出的事实是否准确？
2. 向当事人收集缺失信息（或同意按假设继续推进）。

**律师操作**：✅ 批准 → 进入 Phase 3 | ✏️ 修改 → 在文件中编辑 | ❌ 拒绝 → 回退 Phase 1

---

## Phase 3：综合分析
**目标**：生成高价值法律分析结论。

依次执行以下三个核心分析（顺序执行）：
1. **法律检索**：使用 `cn-legal-research` Skill 查找最相关的法条和判例。
2. **请求权基础**：使用 `cn-rights-basis-analysis` Skill 穷举所有请求权路径并推荐最优路径。
3. **风险评估**：使用 `cn-risk-assessment` Skill 从败诉/执行/成本/声誉四维度综合研判。

**刑事案件特别处理**：如 `domain: criminal`，替换使用 `cn-criminal-defense` Skill 进行罪名构成审查、辩护路径和量刑预估。

分析完成后，将深度报告附加至 `case.local.md` 的「深度分析」区域。

// human-review
⚠️ **律师审查点**：综合分析草案已就绪。请律师审阅并进行 diff 修改或签批通过。

**律师操作**：✅ 批准 → 进入 Phase 4 | ✏️ 修改 → Agent 读取 diff 后调整 | ❌ 拒绝 → 回退重新分析

---

## Phase 4：专业服务输出
**目标**：将确认的策略转化为可直接使用的法律文书或方案。

在律师于 `case.local.md` 中签批通过后，根据案件需要启动对应 Skill：

| 场景 | 使用 Skill |
|------|-----------|
| 需要起诉/应诉 | `cn-litigation-strategy`（管辖+路径+赔偿计算）|
| 合同纠纷需对比版本 | `cn-contract-comparison`（条款级 Diff）|
| 审查保密协议 | `cn-nda-review`（6项审查清单）|
| 刑事案件辩护 | `cn-criminal-defense`（辩护策略+取保方案）|

// human-review
⚠️ **律师最终签批**：所有对外文书必须经律师确认后方可使用。

**归档**：将最终文件存入 `cases/{case_id}/` 目录，更新 `case.local.md` 的 `phase` 为 `completed`。
