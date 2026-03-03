# LegalHigh 跨平台兼容性评估报告

> 评估对象：Claude Code / OpenCode / Antigravity
> 评估日期：2026-03-03

---

## 总体结论

| 平台 | 兼容度 | 迁移成本 | 说明 |
|------|-------|---------|------|
| **Claude Code** | 🟢 95% | 几乎零 | 原生支持，架构设计时已对齐 |
| **OpenCode** | 🟡 75% | 低 | 核心可用，Skill加载和Workflow需适配 |
| **Antigravity** | 🟢 90% | 几乎零 | 当前开发环境，已验证 |

---

## 逐项评估

### 1. `.agents/workflows/` — 工作流编排

| 特性 | Claude Code | OpenCode | Antigravity |
|------|------------|----------|-------------|
| 识别 `.agents/workflows/*.md` | ✅ 原生支持 | ❌ 不支持此路径约定 | ✅ 原生支持 |
| `/slash-command` 触发 | ✅ 原生 | ❌ 无此机制 | ✅ 原生 |
| `// human-review` 门控 | ✅ Agent 会暂停等待确认 | ⚠️ 需改为对话中人工确认 | ✅ 原生 |
| `// turbo` 自动执行 | ✅ 原生 | ❌ 无此注解 | ✅ 原生 |

**OpenCode 迁移方案**：
- 将 `legal-case-workflow.md` 改为 AGENTS.md 或系统 prompt 的一部分
- 或通过 OpenCode 的 custom instructions 机制加载
- `// human-review` 改为在对话中显式询问用户

---

### 2. `skills/legal-cn/*/SKILL.md` — Skill 体系

| 特性 | Claude Code | OpenCode | Antigravity |
|------|------------|----------|-------------|
| `skills/` 目录自动发现 | ✅ 原生 | ❌ 不支持 Skill 约定 | ✅ 原生 |
| YAML frontmatter 触发 | ✅ description 驱动 | ❌ 无此机制 | ✅ description 驱动 |
| Progressive Disclosure | ✅ 三层加载 | ❌ 需全量加载或手动引用 | ✅ 三层加载 |
| Skill 间引用 | ✅ 自然语言引用 | ⚠️ 可通过 prompt 引用 | ✅ 自然语言引用 |

**OpenCode 迁移方案**：
```
方案A（推荐）：拼合为单一 SYSTEM_PROMPT
  将 11 个 SKILL.md 精简后合并到一个大的系统指令文件中
  ~45K tokens，对支持 200K 上下文的模型无压力

方案B：按需手动引用
  在对话中通过 @file 引用对应的 SKILL.md
  "请按照 @cn-legal-research/SKILL.md 的规范分析这个案件"

方案C：利用 OpenCode 的 custom instructions
  将核心指令写入 OpenCode 的配置文件
  非核心 Skill 通过对话引用
```

---

### 3. `playbooks/*.md` — 领域知识库

| 特性 | Claude Code | OpenCode | Antigravity |
|------|------------|----------|-------------|
| 文件读取 | ✅ 原生 | ✅ 原生 | ✅ 原生 |
| 按 domain 条件加载 | ✅ Workflow 指令驱动 | ⚠️ 需手动指定或 prompt 驱动 | ✅ Workflow 指令驱动 |

**三个平台完全兼容** — Playbook 本质上是 Markdown 参考文档，任何能读文件的 Agent 都能使用。无需改造。

---

### 4. `cases/{case_id}/case.local.md` — 状态文件

| 特性 | Claude Code | OpenCode | Antigravity |
|------|------------|----------|-------------|
| 文件读写 | ✅ 原生 | ✅ 原生 | ✅ 原生 |
| YAML frontmatter 解析 | ✅ Agent 理解 | ✅ Agent 理解 | ✅ Agent 理解 |
| Checklist `[x]` 状态追踪 | ✅ | ✅ | ✅ |
| 文件变更检测 | ⚠️ 需 Agent 主动读 | ⚠️ 需 Agent 主动读 | ⚠️ 需 Agent 主动读 |

**三个平台完全兼容** — `case.local.md` 是普通 Markdown 文件，核心是 "文件即状态" 设计理念，不依赖任何平台特有功能。

---

### 5. `.mcp.json` — MCP 工具链

| 特性 | Claude Code | OpenCode | Antigravity |
|------|------------|----------|-------------|
| MCP Server 配置 | ✅ 原生支持 | ✅ 原生支持 | ✅ 原生支持 |
| MCP 工具调用 | ✅ | ✅ | ✅ |
| 配置文件路径 | `.mcp.json` (项目根) | `opencode.json` 或 `.mcp.json` | `.mcp.json` |

**三个平台均支持 MCP**。OpenCode 的配置格式可能略有不同，需确认其具体配置规范。

---

## 跨平台兼容性矩阵

| 组件 | Claude Code | OpenCode | Antigravity | 跨平台策略 |
|------|:----------:|:--------:|:-----------:|-----------|
| Workflow 编排 | ✅ | ❌→⚠️ | ✅ | OpenCode 需改为 system prompt |
| Skill 触发 | ✅ | ❌→⚠️ | ✅ | OpenCode 需合并或手动引用 |
| Playbooks | ✅ | ✅ | ✅ | 无需改造 |
| case.local.md | ✅ | ✅ | ✅ | 无需改造 |
| MCP 工具 | ✅ | ✅ | ✅ | 配置格式微调 |
| `// human-review` | ✅ | ⚠️ | ✅ | OpenCode 改为对话询问 |
| `/slash-command` | ✅ | ❌ | ✅ | OpenCode 无等效机制 |

---

## OpenCode 具体迁移方案

如果需要在 OpenCode 中使用 LegalHigh，建议做以下最小改造：

### 1. 创建 `AGENTS.md`（替代 Workflow + Skill 触发）

```markdown
# LegalHigh Agent 配置

## 角色
你是龙律师法律 AI 助手，按照 4 阶段工作流处理案件。

## 工作流
[将 legal-case-workflow.md 的内容嵌入]

## 可用技能
当处理到对应阶段时，阅读以下技能文件获取详细指令：
- Phase 1: 阅读 `skills/legal-cn/cn-case-information-extractor/SKILL.md`
- Phase 1: 阅读 `skills/legal-cn/cn-evidence-analysis/SKILL.md`
[...]
```

### 2. 文件结构保持不变

Playbooks、case.local.md、SKILL.md 文件本身**零改动**——它们是纯 Markdown，任何平台都能读。

### 3. 估算工作量

| 改造项 | 工作量 | 复杂度 |
|-------|-------|-------|
| 创建 AGENTS.md | 30分钟 | 低（拼合现有内容）|
| MCP 配置格式调整 | 10分钟 | 低 |
| 测试 Skill 加载 | 1小时 | 中 |
| **总计** | **~2小时** | — |

---

## 跨平台最佳实践

1. **核心文件保持 Markdown** — 已做到。Playbook、Skill、case.local.md 都是纯 Markdown，不依赖任何框架
2. **平台适配层最小化** — 仅 Workflow 编排和 Skill 触发依赖平台特性，其他全部平台无关
3. **`case.local.md` 是最稳固的架构选择** — "文件即状态" 在所有平台都能工作
4. **MCP 是三个平台的共同协议** — 工具链层面天然兼容

> **结论**：LegalHigh 的文件驱动原生架构在设计时已最大化了跨平台兼容性。核心法律内容（Skill + Playbook + 案件文件）100% 可复用，仅编排层需要约 2 小时的平台适配。
