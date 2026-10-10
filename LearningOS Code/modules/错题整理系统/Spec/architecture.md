# 错题整理系统 · Architecture

> Version: v0.1
> Parent: [PRD](./prd.md) | [Constitution](../../../LearningOS Spec/constitution.md) | [CONTEXT](../../../LearningOS Spec/CONTEXT.md)

---

## 1. Design Philosophy

**Core Engine 中心化。** 所有功能通过 Python Core Engine 实现。CLI 是调用入口之一，后续 Web UI、Agent 调用都走同一套 Python API。

**证据驱动。** 所有分析结论可追溯至源文件（Mistake ID / ReviewSession ID）。

**文件系统即数据库。** Markdown + Frontmatter 文件既是人类可读写的数据，也是系统的数据源。不引入数据库。

---

## 2. Layer Architecture

```
┌──────────────────────────────────────┐
│         Interface Layer              │  CLI（argparse）→ 调用 Core Engine
│         (modules/.../src/cli/)       │
├──────────────────────────────────────┤
│         Service Layer                │  业务逻辑：校验、编排、调用 AI
│         (modules/.../src/core/)      │
├──────────────────────────────────────┤
│         Repository Layer             │  文件读写：Markdown 解析/生成
│         (modules/.../src/core/)      │
├──────────────────────────────────────┤
│         File System                  │  users/ + LearningOS Spec/
└──────────────────────────────────────┘
```

### 层间规则

- Interface 只能调用 Service
- Service 只能调用 Repository + AI Provider
- Repository 只能读写文件系统
- **禁止跨层访问**

---

## 3. Module Structure

```
modules/错题整理系统/
├── Spec/                          # 本模块的规范（只读，Coding Agent 遵守）
│   ├── prd.md
│   ├── architecture.md
│   └── adr.md
├── src/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py               # CLI 入口（argparse）
│   └── core/
│       ├── __init__.py
│       ├── models.py             # 数据类：Mistake, ReviewSession, Profile
│       ├── repository.py         # 文件读写：Markdown ⇄ 数据类
│       ├── service.py            # 业务逻辑：add_mistake, review, check
│       ├── ai.py                 # AI Provider：错误分析 + 出题 + 引导
│       └── profile.py            # 画像管理：读写、更新 knowledge_map
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # 共享 fixture
│   ├── test_models.py
│   ├── test_repository.py
│   └── test_service.py
└── README.md
```

---

## 4. Data Flow

### 4.1 录入流

```
CLI: mkt add --student 开心 --subject 数学 --topic 分数加法 ...
    ↓
Service.add_mistake():
  1. 校验 topic 在 knowledge-points.yaml 中存在
  2. 校验 reason 在受控词汇内
  3. 生成 mistake_id (UUID8)
  4. 查找目标文件: users/开心/data/错题整理/错题集/数学/五年级上/分数加法.md
  5. 文件不存在 → 创建（含 Frontmatter 头）
  6. 追加 Mistake 条目（## 日期 · 题目 ❌ + 字段）
  7. 更新 Frontmatter: mistake_count += 1, last_updated
```

### 4.2 复习流

```
CLI: mkt review --student 开心 --topic 分数加法
    ↓
Service.review():
  1. 读取 users/开心/data/错题整理/错题集/数学/*/分数加法.md
  2. 提取所有 status=未复习 的 Mistake
  3. 读取 users/开心/profile.yaml 的 knowledge_map
  4. 调用 AI：错误归纳 + 引导问题 + 3 道同类题
  5. 创建 ReviewSession → users/开心/data/错题整理/复习记录/数学/五年级上/2026-06-28_分数加法.md
  6. 输出到终端
```

### 4.3 判题流

```
CLI: mkt check --id ex-001 --correct
    ↓
Service.check():
  1. 查找 ReviewSession，找到 Exercise
  2. 标记结果
  3. 如果是最后一次 check → 判定 3 题结果
  4. 全对 → 更新所有相关 Mistake: status=已复习 → 重写对应 .md 文件
  5. 有错 → 错误的 Exercise 转为新 Mistake → 追加到错题集
```

---

## 5. AI Integration

```
Core Engine (service.py)
    ↓
ai.py: analyze_mistakes(mistakes, knowledge_map) → ReviewContent
    ↓
AI Provider（默认透传当前 Agent 的模型）
    ↓
System Prompt = Constitution A1-A12 + Student Profile
User Prompt = 错题列表 + 要求（归纳 → 引导 → 出题）
    ↓
返回结构化文本 → 解析为 ReviewContent
```

| 调用点 | 触发 | AI 任务 |
|------|------|------|
| `mkt review` | 一次 API call | 分析错题共性 + 生成引导问题 + 出 3 道同类题 |

---

## 6. File Format Specification

### 6.1 错题集文件

```markdown
---
topic: 分数加法
student: 开心
subject: 数学
grade: 五年级上
mistake_count: 5
last_updated: 2026-06-28
---

# 分数加法 · 错题集

## 2026-06-28 · 3/4 + 1/2 = ？❌

- **id:** abc123
- **错误答案：** 1
- **正确答案：** 5/4
- **原因：** 概念不清
- **状态：** 未复习

---
```

### 6.2 复习记录文件

```markdown
---
id: sess-001
student: 开心
topic: 分数加法
grade: 五年级上
date: 2026-06-28
exercises_total: 3
exercises_passed: 2
result: 未通过
---

# 复习：分数加法 · 2026-06-28

## 错误归纳
3 次分数加法错的共同点：通分。

## 引导问题
为什么 1/3 + 1/2 不能直接等于 2/5？

## 练习题

### 题 1 · ❌
1/4 + 1/3 = ？
学生答案：2/7
正确答案：7/12

### 题 2 · ✅
...
```

---

## 7. Constitution Alignment

| Article | 架构决策 | 实现方式 |
|------|------|------|
| A1 启发 | AI 生成引导问题，不给答案 | AI prompt 约束 |
| A2 因材 | 按学生隔离 + 个性化出题 | `users/{student}/` + profile 注入 AI |
| A5 温故 | Review 读取所有历史 Mistake | Service 层全量读取该 topic |
| A7 过程优先 | 记录错误过程 | wrong_answer + reason 字段 |
| A8 可溯 | 结论可追溯 | insight 含 source 字段 |
| A11 克制 | AI 不超出能力 | 只做小学数学分析 + 出题 |
| A12 诚信 | 错题不原地修改 | 状态变更通过 ReviewSession 记录，不覆写原内容 |

---

## 8. Open Questions

| # | 问题 | 应解决于 |
|:---:|------|------|
| Q1 | 多 Agent 同时操作同一文件？ | 后续 ADR |
| Q2 | 错题集文件过大时的分页策略？ | 后续 ADR |
| Q3 | AI 出题质量的验证机制？ | 需要验证后决定 |
