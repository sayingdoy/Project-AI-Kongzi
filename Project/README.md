# Project AI-Kongzi

> AI Learning OS — 以学习者成长为核心的 AI 辅助学习系统。

---

## 项目结构

| 目录 | 用途 | 谁操作 |
|------|------|:---:|
| `LearningOS Spec/` | 规范：Constitution + CONTEXT + PRD | 人读，Agent 遵守 |
| `LearningOS Code/` | 交付物：可迁移的代码 | Agent 开发 |
| `LearningOS Users/` | 用户数据：错题集、复习记录、画像 | 系统读写 |
| `Project/` | 开发管理：AGENTS + 计划 + 故事 | 你 + Agent |

---

## 当前状态

**Sprint 2** — 错题整理系统 MVP

| Phase | 内容 | 进度 |
|:---:|------|:---:|
| 2A | 规范体系（Constitution → PRD → Architecture → ADR） | ✅ |
| 2B | Core Engine（录入、查询、AI 复习） | ⏳ |

详见 [`Project/sprint-plan.md`](Project/sprint-plan.md)

---

## 快速开始

### 给 Agent

读 `Project/AGENTS.md`。

### 给人

1. 产品愿景 → [`LearningOS Spec/prd.md`](LearningOS Spec/prd.md)
2. 术语 → [`LearningOS Spec/CONTEXT.md`](LearningOS Spec/CONTEXT.md)
3. 开发计划 → [`Project/sprint-plan.md`](Project/sprint-plan.md)

---

## 核心原则

1. **证据驱动** — 所有判定基于可追溯的学习证据
2. **家长协作** — AI 生成内容，家长执行教学
3. **过程优先** — 记录错误过程，而非仅记录答案
4. **按学生隔离** — 每个学生独立数据空间
5. **Spec 驱动开发** — Constitution → PRD → Architecture → ADR → Code
