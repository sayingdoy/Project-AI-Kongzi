# Audit Log

> 审计追踪日志。每轮方案评审在此记录。

---

## 当前活跃审计

（无活跃审计）

| 项目 | 版本 | 状态 | 完成日期 |
|------|------|:---:|------|
| InvestmentOS | v1.8 综合改进计划 | 🚀 已释放 | 2026-06-17 |
| InvestmentOS | v1.7.0 | ✅ 已通过 | 2026-06-17 |

---

## 已完成审计

| 项目 | 版本 | 状态 | 完成日期 |
|------|------|:---:|------|
| AI-Kongzi 错题整理系统 | v0.1 Phase 2A 规范体系 | ✅ 已完成 | 2026-06-28 |
| AI-Kongzi 错题整理系统 | v0.1 Phase 2B Core Engine MVP | ✅ 已完成 | 2026-06-29 |
| AI-Kongzi 错题整理系统 | v0.2 Sprint 3 状态机闭环 | ✅ 已完成 | 2026-06-29 |
| AI-Kongzi 错题整理系统 | v0.3 Sprint 4 学习仪表盘+多学科 | ✅ 已完成 | 2026-06-29 |
| InvestmentOS | v1.8 | ✅ 已通过 | 2026-06-17 |
| InvestmentOS | v1.7.0 | ✅ 已通过 | 2026-06-17 |
| InvestmentOS | v1.5 | ✅ 已通过 | 2026-06-12 |
| InvestmentOS | v1.5.1 | ✅ 已通过 | 2026-06-12 |

---

## AI-Kongzi Sprint 2B — Core Engine MVP

### Round 1：方案 + 审计 + 异议 + 终版

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v0.1_Sprint2B_R1_方案_tbd_CodeWhale.md` | Planner (CodeWhale) | 两条垂直切片：Slice 1 录入→查看，Slice 2 AI 复习 |
| 2 | `v0.1_Sprint2B_R1_审计_tbA_Hermes.md` | Auditor (Hermes) | 3 建议 + 1 批量导入建议。全部采纳或异议 |
| 3 | `v0.1_Sprint2B_R1_异议_tbd_CodeWhale.md` | Planner (CodeWhale) | 3 项采纳，1 项异议（`mkt add --raw`，引 R2+R3+R5） |
| 4 | 复审 | Auditor (Hermes) | 让步，分歧清零 |
| 5 | `v0.1_Sprint2B_终版_OK_CodeWhale.md` | Planner (CodeWhale) | 终版方案 |

### 产出

```
pytest tests/ -v → 49/49 通过

modules/错题整理系统/src/
├── cli/main.py            # 6 个命令
├── core/models.py         # 4 个数据类
├── core/repository.py     # 8 个文件操作
├── core/service.py        # 6 个业务方法 + 校验
├── core/ai.py             # AI 分析+出题（含 Constitution prompt）
└── core/profile.py        # 画像更新+趋势检测

modules/错题整理系统/tests/
├── conftest.py            # 共享 fixture
├── test_models.py         # 14 tests
├── test_repository.py     # 15 tests
├── test_service.py        # 14 tests
├── test_profile.py        # 5 tests
└── test_cli.py            # 1 test (stub)
```

✅ **Phase 2B 完成**。Core Engine MVP 可运行。

---

## AI-Kongzi Sprint 3 — 状态机闭环

### Round 1：方案 + 审计 + 终版（无异议）

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v0.2_Sprint3_R1_方案_tbd_CodeWhale.md` | Planner (CodeWhale) | 三条垂直切片：已掌握状态、二次错误回滚、基础设施完善 |
| 2 | `v0.2_Sprint3_R1_审计_tbA_Hermes.md` | Auditor (Hermes) | 4 建议：next_review 可见性、AI mock 提示、命令更名 verify、SOP 更新 |
| 3 | `v0.2_Sprint3_终版_OK_CodeWhale.md` | Planner (CodeWhale) | 4 项全部采纳，分歧清零 |

### 审计变更摘要

| 来源 | 变更 |
|------|------|
| ⚠️ 1 next_review 可见性 | `mkt profile` 输出待复测 topic 列表 |
| ⚠️ 2 AI mock 提示 | `_call_llm` 检测 mock 时输出不可忽略的提示 |
| 📝 3 命令更名 | `mkt master` → `mkt verify` |
| 📝 4 SOP 更新 | 补充 raw 导入 MD 格式示例 |

### 产出计划

```
Slice 1：状态机闭环   → mkt verify + 已掌握判定 + next_review + pending_reviews
Slice 2：二次错误回滚 → 录入自动回滚 + mkt recall 根因探究
Slice 3：基础设施完善 → mkt add --raw + AI Provider 配置化 + check 持久化 + SOP 更新
```

✅ **Sprint 3 审计完成**。待编码执行。

---

## AI-Kongzi Sprint 4 — 学习仪表盘 + 多学科

### Round 1：方案 + 审计 + 终版（无异议）

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v0.2_Sprint4_R1_方案_tbd_CodeWhale.md` | Planner (CodeWhale) | 仪表盘(dashboard/trend/recommend) + 多学科 |
| 2 | `v0.2_Sprint4_R1_审计_tbA_Hermes.md` | Auditor (Hermes) | 4 建议：session 完整性验证、推荐阈值 30%、test_cli.py 遗留、SOP 更新 |
| 3 | `v0.2_Sprint4_终版_OK_CodeWhale.md` | Planner (CodeWhale) | 4 项全部采纳，分歧清零 |

### 产出

```
新增命令：
  mkt dashboard --student         学习概览（6 个数据字段）
  mkt trend --student --topic     知识点时间线
  mkt recommend --student         智能推荐（5 因子加权，阈值 20%）

知识库扩展：
  英语：7+5 个知识点（五年级上下）
  语文：8+5 个知识点（五年级上下）

bug 修复：
  ReviewSession 文件名含 session_id，避免同天同 topic 覆盖
  _parse_knowledge_points_yaml 支持 key: value 格式

回归测试：pytest tests/ -v → 49/49 通过
```

✅ **Sprint 4 完成**。

---

## AI-Kongzi Sprint 2 — 规范体系建立

### Round 1：文件系统方案 + 审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v0.1_文件系统搭建_R1_方案_tbd_Kongzi.md` | Planner (Kongzi) | 提出模块级 Spec 目录 + src/tests/data 骨架 |
| 2 | 审计（Hermes，本次会话） | Auditor (Hermes) | 3 个问题：项目/模块 Spec 未分层、垂直编程未定义、文件重复 |

### 审计结论

| # | 问题 | 严重度 | 处理 |
|:---:|------|:---:|:---:|
| 1 | 缺少项目级 PRD 预留 | ⚠️ 中 | 文件系统已预留 `LearningOS Spec/prd.md`；本次 Sprint 暂不写 |
| 2 | 「垂直编程」未定义 | ⚠️ 中 | Sprint 2 拆为 2A（规范体系）+ 2B（垂直切片代码） |
| 3 | 方案文件重复存储 | 📝 低 | 已删除子模块内副本，保留 `OS Audit/` 一份 |

### Phase 2A 产出

| 序号 | 文件 | 作者 |
|:---:|------|:---:|
| 3 | `错题整理系统/Spec/prd.md` | Chief Architect (Hermes) |
| 4 | `错题整理系统/Spec/architecture.md` | Chief Architect (Hermes) |
| 5 | `错题整理系统/Spec/adr/adr-001-data-model.md` | Chief Architect (Hermes) |

✅ **Phase 2A 完成**。Phase 2B（垂直切片代码）待 CodeWhale 执行。

---

## InvestmentOS v1.5 — 完整决策链

### Round 1：方案提出 + 双审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `InvestmentOS_v1.5_架构评审报告_Hermes.md` | Auditor (Hermes) | lib/ 模块化拆分、strategy 分类体系统一、快照基础设施、L2.1 假阳性。评分 3.5/5。 |
| 2 | `InvestmentOS_v1.5_架构评审报告_Mimo.md` | Auditor (Mimo) | 10 个具体实现问题：akshare API、schema 校验、Shell 重写、流动性对账等。 |
| 3 | `InvestmentOS_v1.5_方案整合报告_Karpathy准则.md` | Integrator (Hermes) | 合并双审计 + Karpathy 12 准则校准。采纳 7/10，修正 3 项（Shell 重写过度、版本号精简过度、缺失模块化）。 |

### Round 2：改进计划 v1 → 交叉审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 4 | `InvestmentOS_v1.5_综合改进计划_MiMoCode.md` | Planner (Mimo) | 整合三方输入后的执行方案。P0-P3 优先级、Phase 0-3 分阶段、检查点机制。 |
| 5 | `InvestmentOS_v1.5_第二轮审计_Hermes.md` | Auditor (Hermes) | 采纳率 7/11。3 个未采纳项全部指向同一模式（统一重写 vs 精准修复）。评分 8.5/10。 |

### Round 3：分歧清零 → 终版

| 序号 | 文件 | 角色 | 结果 |
|:---:|------|:---:|------|
| 6 | `InvestmentOS_v1.5_综合改进计划_终版.md` | Planner (Mimo) | ✅ 分歧清零。Shell 保留、版本溯源保留、API 抽象简化。评分 9.5/10。可以执行。 |

### 关键分歧消解记录

| 分歧点 | Round 1 Hermes | Round 1 Mimo | Round 2 裁决 | Round 3 终版 |
|------|:---:|:---:|:---:|:---:|
| Shell 脚本重写 | 保留不动 | Python 重写 | Hermes（R2+R3） | ✅ 保留 |
| Git hooks 重写 | 修 shebang | Python 重写 | Hermes（R3） | ✅ 修 shebang |
| 版本号精简 | 保留 6 处 | 减至 3 处 | Hermes（数据溯源≠过度工程） | ✅ 6→6（减 dashboard，增 handover） |
| API 抽象层 | ABC 接口 | 直接调用 | — | ✅ try/except（比 Hermes 方案更简） |
| 分类体系统一 | strategy 字段 | 未涉及 | Hermes | ✅ 采纳 |

---

## 审计模板

新项目审计时复制以下格式：

```markdown
## {Project} {Version} — 决策链

### Round 1：方案提出 + 审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `{Project}_{Version}_架构评审报告_{Auditor}.md` | Auditor | |
| 2 | `{Project}_{Version}_方案整合报告.md` | Integrator | |

### Round 2：交叉审计（如有分歧）

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 3 | `{Project}_{Version}_综合改进计划_{Planner}.md` | Planner | |
| 4 | `{Project}_{Version}_第{N}轮审计_{Auditor}.md` | Auditor | |

### 分歧消解

| 分歧点 | Auditor A | Auditor B | 裁决 | 终版 |
|------|:---:|:---:|:---:|:---:|
| | | | | |

### 终版

| 序号 | 文件 | 角色 | 评分 |
|:---:|------|:---:|:---:|
| N | `{Project}_{Version}_综合改进计划_终版.md` | Planner | /10 |
```

---

> 最后更新：2026-06-12 | InvestmentOS v1.5 审计结束，v1.5.1 待审计

---

## InvestmentOS v1.5.1 — 维护协议

### 背景

v1.5 Phase 0-2 执行过程中暴露两个系统性问题：
1. Phase 完成后忘升版本号
2. Phase 完成后忘更新 project_handover

根因相同：**"做完事之后该做什么"没有编码进系统**。

### 方案

| 文件 | 角色 | 核心内容 |
|------|:---:|------|
| `v1.5.1_维护协议_R1_方案_tbd_MiMo.md` | Planner | 4 层自动化约束：pre-commit + health_check L4.2 + system_prompt 协议 + CLAUDE.md 策略 |

### 审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v1.5.1_维护协议_R1_方案_tbd_MiMo.md` | Planner (MiMo) | 四层防线方案 |
| 2 | `v1.5.1_维护协议_R1_审计_tbA_Hermes.md` | Auditor (Hermes) | 3 处修正（版本号规则冲突、pre-commit 描述矛盾、脚本引用错误），均为文案级。修正后通过。 |

✅ **已通过** — 已执行并归档至 `Archive/`。

---

## InvestmentOS v1.5.0 Phase 3 — 体检补全

### 方案

| 文件 | 角色 | 核心内容 |
|------|:---:|------|
| `v1.5.0_体检补全_R1_方案_tbd_MiMo.md` | Planner | Phase 3 收尾：L3.5 交易↔决策、L3.6 宪法格式、CHANGELOG、README 简化、sync_version 确认 |

### 审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v1.5.0_体检补全_R1_方案_tbd_MiMo.md` | Planner (MiMo) | 5 个检查补全，100 分钟工时 |
| 2 | `v1.5.0_体检补全_R1_审计_tbA_Hermes.md` | Auditor (Hermes) | 3 处建议（数据迁移、匹配规则、遗漏归档），修正后通过 |

🔍 **已执行**——可进入终版。

---

## InvestmentOS v1.5.2 — 版本升级自动化

### 方案

| 文件 | 角色 | 核心内容 |
|------|:---:|------|
| `v1.5.2_版本升级自动化_R1_方案_tbd_MiMo.md` | Planner (MiMo) | pre-commit hook 自动计算版本号 + 写入 VERSION |

### 审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v1.5.2_版本升级自动化_R1_方案_tbd_MiMo.md` | Planner (MiMo) | 自动版本升级方案 |
| 2 | `v1.5.2_版本升级自动化_R1_审计_tbA_Hermes.md` | Auditor (Hermes) | 3 处修正：流程图实现矛盾、git add 通配符风险、失败回滚缺失。修正后通过。 |

🔍 **审计中**——修正后执行。

---

## InvestmentOS v1.6 longbridge + 思维模型集成

### 方案

| 文件 | 角色 | 核心内容 |
|------|:---:|------|
| `v1.6_longbridge集成_R1_方案_tbd_MiMo.md` | Planner (MiMo) | v1.6 流程模板，不做代码；v1.7 API 集成；v1.8 自动化 |

### 审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v1.6_longbridge集成_R1_方案_tbd_MiMo.md` | Planner (MiMo) | 范围控制得当，5 步评审流程清晰 |
| 2 | `v1.6_longbridge集成_R1_审计_tbA_Hermes.md` | Auditor (Hermes) | 通过。3 个建议（预期管理、触发机制、审计日志） |

🔍 **审计中**——修正后执行。

---

## InvestmentOS v1.8 — 综合改进计划

### 背景

v1.7 完成决策归档闭环和知识审计层后，v1.8 目标是补全投资组合监控能力（回撤、基准比较）和数据质量保障（schema 校验），同时引入 longbridge 作为行情备用源提升可靠性。

### 方案

| 文件 | 角色 | 核心内容 |
|------|:---:|------|
| `v1.8_综合改进计划_R1_方案_tbd_MiMo.md` | Planner (MiMo) | 三子版本发布：v1.8.1 回撤+schema、v1.8.2 基准比较、v1.8.3 longbridge 备用源 |

### 审计

| 序号 | 文件 | 角色 | 核心发现 |
|:---:|------|:---:|------|
| 1 | `v1.8_综合改进计划_R1_方案_tbd_MiMo.md` | Planner (MiMo) | 分三子版本发布，范围控制严格 |
| 2 | `v1.8_综合改进计划_R1_审计_tbA_Hermes.md` | Auditor (Hermes) | 2 个中等建议（schema 中央字典、pre-commit 验证）+ 3 个低优先级建议。无 P0 阻塞。 |

### 终版

| 序号 | 文件 | 角色 | 结果 |
|:---:|------|:---:|------|
| 3 | `v1.8_综合改进计划_终版_OK_MiMo.md` | Planner (MiMo) | ✅ 全部采纳，无异议。可进入执行。 |

### 审计建议采纳记录

| # | 审计建议 | 采纳方式 |
|:---:|------|------|
| ⚠️ 1 | schema 校验需中央字段字典 | 新增 `lib/schema.py` 定义 `ASSET_SCHEMA` |
| ⚠️ 2 | pre-commit hook 需验证结构 | 确认 hook 无 `--layer` 参数，L6 在默认模式自动包含 |
| 📝 3 | 回撤区块加数据量提示 | 快照 < 14 天时显示警告提示 |
| 📝 4 | longbridge 优先评估 CLI 方式 | 改为优先 `subprocess` 调用 CLI，API 作为 fallback |
| 📝 5 | L5/L6 加注释说明层级定位 | 代码中加注释明确层级定位差异 |

✅ **已通过**——可进入执行阶段。
