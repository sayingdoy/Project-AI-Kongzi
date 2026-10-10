# AGENTS.md — 开发规范

> 给所有参与 Project AI-Kongzi 开发的 Agent。
> **本文件定义多 Agent 协作规则。** 运行时使用指南见 `../LearningOS Code/AGENTS.md`。

---

## 1. 项目结构

```
Project AI Kongzi/
├── LearningOS Spec/          ← 规范。只读。不要改。
├── LearningOS Code/          ← 交付物。可迁移的代码。
│   ├── modules/              ← 每个子模块独立目录
│   ├── shared/               ← 跨模块共享代码
│   └── OS Audit/             ← 方案审计存档
├── LearningOS Users/         ← 用户数据。不要改结构。
└── Project/                  ← 开发管理（本目录）
```

---

## 2. Spec 链（开发前必读，顺序不可跳）

```
Constitution → CONTEXT → 全局 PRD → 模块 PRD → Architecture → ADR → 开始编码
```

| 读什么 | 在哪 | 为什么 |
|------|------|------|
| Constitution | `../LearningOS Spec/constitution.md` | 最高原则。12 条 MUST/MUST NOT。违反即驳回。 |
| CONTEXT | `../LearningOS Spec/CONTEXT.md` | 术语定义。确保代码中概念一致。 |
| 全局 PRD | `../LearningOS Spec/prd.md` | 产品边界。MVP 什么该做什么不该做。 |
| 模块 PRD | `../LearningOS Code/modules/{module}/Spec/prd.md` | 本模块功能范围。 |
| Architecture | `../LearningOS Code/modules/{module}/Spec/architecture.md` | 分层、数据流、文件路径。 |
| ADR | `../LearningOS Code/modules/{module}/Spec/adr.md` | 为什么这样设计。 |

**禁止跳过任何一步直接写代码。**

---

## 3. 代码规范

### 分层规则

```
Interface (CLI/Web) → Service → Repository → File System
```

- Interface 只调用 Service
- Service 只调用 Repository
- Repository 只操作文件系统
- **禁止跨层调用**

### 文件寻址

| 对象 | 路径格式 |
|------|------|
| 知识点索引 | `../LearningOS Code/shared/knowledge-points.yaml` |
| 用户数据 | `../LearningOS Users/{student}/data/{module}/` |
| 共享代码 | `modules/shared/` |

**禁止硬编码绝对路径。** 使用相对路径或配置变量。

### 数据格式

- 错题集：Markdown + YAML Frontmatter（见 Architecture §6.1）
- 复习记录：Markdown + YAML Frontmatter（见 Architecture §6.2）
- 用户画像：YAML（见 Architecture §5）

### 错误处理

- 输入校验在 Service 层，拒绝非法数据
- 文件操作失败在 Repository 层，抛明确异常
- CLI 层捕获异常，给用户可读的错误信息

---

## 4. 修改流程

1. **先读 Spec**（§2 全链）
2. **确认修改范围**：改哪层？改哪个文件？
3. **写测试**（测试意图，不测实现）
4. **写代码**（最小修改，不顺手优化）
5. **运行测试**
6. **更新 sprint-plan.md**（标记 Task 状态）

---

## 5. 禁止事项

| ❌ | 后果 |
|------|------|
| 修改 Constitution | 最高原则不可动 |
| 修改 CONTEXT.md 不通过 grill-with-docs | 术语漂移 |
| 跨层调用 | 架构腐化 |
| 硬编码绝对路径 | 不可迁移 |
| 原地修改错题数据（不通过 Repository） | 违反 A12 诚信 |
| 给答案而非引导（AI prompt 中） | 违反 A1 启发 |
| 新增 Spec 文件不通知 | 文档链断裂 |

---

## 6. 测试

```bash
cd ../LearningOS Code/modules/错题整理系统
pytest tests/ -v
```

- 使用 `tmp_path` fixture 隔离文件操作
- Mock AI 层，不实际调用外部 API
- 测试业务意图，不测试实现细节

---

## 7. 参考

- [sprint-plan.md](./sprint-plan.md) — 当前 Sprint 任务分解
- [user-stories.md](./user-stories.md) — 用户故事与验收标准
- [roadmap.md](./roadmap.md) — 里程碑与依赖关系

---

## 8. 多 Agent 协作流程

> 所有开发任务均通过 `../LearningOS Code/OS Audit/` 目录完成方案审计。
> 详细流程见 `../LearningOS Code/OS Audit/README.md`。

### 8.1 角色与职责

角色不绑定特定 Agent。任何 Agent 可担任任何角色。

| 角色 | 职责 | 要求 |
|:---:|------|------|
| **Owner** | 终裁。分歧无法达成共识时裁决。对 Constitution 有最终解释权。 | 了解项目全局。 |
| **Auditor** | 独立审计 Planner 的方案。不接受 Planner 的引导。 | 必须读完 Spec 全链后才开始审。审计报告必须引用具体依据（Constitution 编号 / Spec 段落 / Karpathy 规则编号）。 |
| **Planner** | 读 Spec → 出开发计划 → 在 Auditor 通过后执行代码。 | 必须读完 Spec 全链后才出方案。方案中每项决策必须说明依据。 |

### 8.2 流程

```
Planner 读 sprint-plan.md + 全链 Spec
    ↓
Planner 出开发计划 → 放 OS Audit/{版本}_{内容}_R{轮次}_方案_tbd_CodeWhale.md
    ↓
Auditor 审 → 审计_tbA_Hermes.md
    ↓
Planner 读审计 → 逐项标注"采纳"或"异议"
    ↓
    ├── 全部采纳 → 终版_OK → 执行 → 归档
    └── 有异议 → 异议_tbd_CodeWhale.md
                    ↓
                Auditor 复审
                    ↓
                ├── 让步 → 终版
                └── 维持 → Owner 裁决 → 终版
```

### 8.3 开发计划要求

Planner 的开发计划必须包含：

1. **垂直切片顺序**（先录入→查看，再叠加 AI 复习）
2. **每个 Task 的验收标准**（什么算"完成"）
3. **风险点**（可能出问题的地方）
4. **不做什么**（明确排除）

### 8.4 审计标准

Auditor 对照以下维度。**Karpathy 12 准则为最高审计宪法。**

| 维度 | 检查 |
|------|------|
| Constitution | 是否违反 A1-A12 任何一条？ |
| Architecture | 是否跨层调用？文件路径是否正确？ |
| Spec 合规 | 是否覆盖 PRD 的 MUST？是否超出 MVP 范围？ |
| 垂直切片 | 是否先跑通第一条完整数据流？ |
| 过度工程 | 是否有 YAGNI 抽象？是否有顺手优化？ |
| Karpathy 12 | 是否违反 R1-R12？详见 OS Audit README。 |

**分歧无法达成共识时，以 Karpathy 准则为终裁依据，引用具体规则编号。**

### 8.5 执行后

Planner 执行完代码后：

1. 运行 `pytest tests/ -v` 并附结果
2. 更新 `sprint-plan.md` 标记 Task 状态
3. 将本轮所有审计文件归档到 `OS Audit/Archive/`
