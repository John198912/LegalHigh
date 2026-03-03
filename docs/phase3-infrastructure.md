# LegalHigh Phase 3 基础设施设计

> 本文件为 Phase 3 基础设施的技术设计文档，需接入外部系统后实施。

---

## 1. 本地法规向量库

### 架构

```
法规原文（txt/pdf）
    ↓ OCR + 清洗
分段器（按条/款/项切分）
    ↓
Embedding（Qwen2.5-Embedding 或 bge-large-zh-v1.5）
    ↓
Qdrant（本地部署，Collection: legal_statutes）
    ↓ 语义检索
cn-legal-research Skill 调用
```

### 数据源

| 数据类型 | 来源 | 状态 |
|---------|------|------|
| 法律法规全文 | 国家法律法规数据库 (flk.npc.gov.cn) | 需爬取 |
| 司法解释 | 最高人民法院网站 | 需爬取 |
| 指导性案例 | 最高人民法院指导案例数据库 | 需爬取 |
| 地方性法规 | 各省人大网站 | 按需 |

### 分段策略

```
# 按法律结构切分
法律名称 → Collection 级别
编/章/节 → 元数据标记
条/款/项 → Chunk 粒度（每条为一个 Chunk）

# 元数据
{
  "law_name": "中华人民共和国民法典",
  "effective_date": "2021-01-01",
  "article_number": 985,
  "chapter": "第三编 合同 / 第二十九章 不当得利",
  "is_effective": true,
  "supersedes": ["合同法第92条"]
}
```

### 部署

```bash
# Qdrant 本地部署
docker run -p 6333:6333 qdrant/qdrant

# Embedding 推理
# 方案A：本地 Ollama
ollama run qwen2.5:7b-embedding

# 方案B：API 调用
# 使用硅基流动/智谱 Embedding API
```

---

## 2. 裁判文书网 MCP Server

### 接口设计

```json
{
  "tool": "search_court_cases",
  "input": {
    "keywords": "不当得利 同居 转账",
    "case_type": "民事",
    "court_level": "中级人民法院",
    "year_range": [2022, 2025],
    "province": "广东",
    "limit": 10
  },
  "output": {
    "cases": [
      {
        "case_number": "(2024)粤01民终XXXX号",
        "court": "广州市中级人民法院",
        "case_type": "不当得利纠纷",
        "judgment_date": "2024-06-15",
        "summary": "...",
        "ruling": "支持原告返还请求",
        "key_holdings": ["目的性给付型不当得利的认定标准..."]
      }
    ]
  }
}
```

### 实现路径

| 方案 | 优劣 |
|------|------|
| 直接爬取裁判文书网 | 数据全，但反爬严格 |
| 接入北大法宝 API | 稳定可靠，需商业授权 |
| 使用 OpenLaw 开源数据 | 免费但数据可能滞后 |
| 自建判例库（手动添加） | 冷启动可用，长期不可持续 |

**推荐**：短期用 OpenLaw + 手动补充，中期接入北大法宝 API。

---

## 3. 法律文档 OCR 管道

### 流程

```
输入（PDF/JPG/PNG/手写扫描件）
    ↓ 文件类型判断
┌─── 电子PDF → PyMuPDF 直接提取文字
├─── 扫描PDF/图片 → Surya OCR
└─── 手写文档 → Surya + GPT-4V 辅助校验
    ↓
文字清洗（去水印、去页眉页脚、修正OCR错误）
    ↓
结构化提取（合同条款切分 / 判决书段落识别）
    ↓
输出为 Markdown → 后续 Skill 消费
```

### 工具选择

| 工具 | 用途 | 安装 |
|------|------|------|
| Surya | 中文 OCR（开源，支持 GPU） | `pip install surya-ocr` |
| PyMuPDF | PDF 文字提取 | `pip install pymupdf` |
| pdf2image | PDF 转图片（供 OCR） | `pip install pdf2image` |

### 脚本占位

```python
# scripts/ocr_pipeline.py（占位）
"""
使用方式：
    python scripts/ocr_pipeline.py input.pdf --output output.md

功能：
    1. 判断 PDF 是电子版还是扫描版
    2. 电子版直接提取，扫描版走 OCR
    3. 输出清洗后的 Markdown
"""

def process_document(input_path: str, output_path: str):
    """TODO: 实现完整管道"""
    raise NotImplementedError("待接入 Surya OCR")
```

---

## 4. 质量评估指标追踪

### 指标定义

| 指标 | 计算方式 | 目标值 |
|------|---------|-------|
| **法条引用准确率** | 人工抽检：引用的法条是否现行有效且条序号正确 | ≥95% |
| **时效计算准确率** | 人工抽检：到期日计算是否正确（含节假日顺延） | ≥99% |
| **信息提取完整度** | 对比原始输入与提取结果，标记遗漏项 | ≥90% |
| **HITL 干预率** | Phase 3 报告中被律师修改的比例 | 趋势下降 |
| **平均案件处理时间** | 从 Phase 1 到 Phase 4 完成的时间 | 逐步优化 |
| **后续引用频率** | 冷启动案件摘要被后续案件引用的次数 | 持续积累 |

### 追踪方式

```markdown
# cases/{case_id}/quality_log.md

| 时间 | 指标 | 值 | 备注 |
|------|------|---|------|
| 2026-03-03 | 法条准确率 | 100% | 3条引用全部正确 |
| 2026-03-03 | 时效计算 | 正确 | 顺延判定准确 |
| 2026-03-03 | HITL干预 | 否 | 律师未修改分析结论 |
```

前期人工记录，后期可自动化（Agent 每次输出后自检 + 律师反馈回收）。
