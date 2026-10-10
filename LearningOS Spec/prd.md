# Project AI-Kongzi · PRD（全局产品规范）

> Version: v0.1
> Parent: [Constitution](./constitution.md) | [CONTEXT](./CONTEXT.md)

---

## 1. Product Vision

**Project AI-Kongzi 是一个以学习者成长为核心的 AI Learning OS。**

它帮助家长系统化地参与孩子的学习过程——记录学习证据、分析薄弱环节、生成个性化辅导。AI 的角色是辅助家长进行有质量的学习陪伴，而非替代家长或孩子思考。

---

## 2. Target Users

| 用户 | 角色 | 系统关系 |
|------|------|------|
| **Parent（家长）** | 系统直接用户 | 录入学习记录、触发复习、阅读分析 |
| **Student（学生）** | 学习数据来源 | 不直接操作系统（MVP）；v0.2+ 可参与 AI 对话 |
| **Coding Agent** | 系统构建者 | 依据 Spec 编码，遵循 Constitution |

---

## 3. Core Principles（从 Constitution 提取）

| # | 原则 | 产品影响 |
|:---:|------|------|
| P1 | **证据驱动** | 所有判定（能力、进度、掌握）必须基于可追溯的学习证据 |
| P2 | **家长协作** | AI 生成思考内容，家长执行面对面教学 |
| P3 | **过程优先** | 记录错误过程（怎么错的），而非仅记录正确答案 |
| P4 | **按学生隔离** | 每个学生独立的数据空间，禁止标签化 |
| P5 | **克制设计** | 系统不声称理解学生、不做情感化交互、能力边界透明 |

---

## 4. Module Map

```
Project AI-Kongzi
├── 错题整理系统          ← Sprint 2 MVP
├── 知识点系统            ← 支撑模块（knowledge-points.yaml）
├── 知识图谱              ← 未来：知识点关系网络
├── AI 对话辅导            ← 未来：学生直接交互
└── 学习仪表盘            ← 未来：统计可视化
```

**MVP 交付物：** 错题整理系统 + 知识点系统（支撑）。

---

## 5. MVP Scope（Sprint 2-3）

### MUST

| # | 功能 | 模块 |
|:---:|------|------|
| F1 | 录入错题 | 错题整理 |
| F2 | 按学生、学科、知识点、状态筛选错题 | 错题整理 |
| F3 | 触发复习会话：AI 分析错题 + 生成引导问题 + 出同类题 | 错题整理 |
| F4 | 判练习题结果，全对→已复习 | 错题整理 |
| F5 | 知识点合法性校验（基于 knowledge-points.yaml） | 知识点系统 |
| F6 | 用户画像（静态 + 动态洞察，证据可追溯） | 共享 |

### MUST NOT

- 不做 Web UI（MVP 命令行为主，后续加）
- 不做孩子直接交互
- 不做 AI 对话辅导
- 不做学习仪表盘
- 不做多设备同步

---

## 6. Cross-Module Conventions

| 规则 | 说明 |
|------|------|
| **Spec 层级** | Constitution（最高）→ PRD → Architecture → ADR → 代码 |
| **文件寻址** | `modules/{module}/` 放代码，`users/{student}/data/{module}/` 放数据 |
| **术语统一** | 所有文档和代码使用 [CONTEXT.md](./CONTEXT.md) 定义的术语 |
| **证据链** | 任何分析结论必须引用源 Mistake/ReviewSession ID |
| **Agent 规范** | Coding Agent 遵循 `AGENTS.md` 的工程规则 |

---

## 7. Long-term Roadmap

| 版本 | 模块 | 内容 |
|------|------|------|
| v0.1 | 错题整理 | 录入、查询、Review（MVP） |
| v0.2 | 错题整理 | 已掌握状态（AI 出题 + 记忆曲线）、二次错误回滚 |
| v0.3 | 学习仪表盘 | 学习趋势可视化 |
| v1.0 | AI 对话辅导 | 学生直接与 AI 交互复习 |
| v1.x | 多模块集成 | 知识图谱、多学科覆盖 |

---

## 8. Beyond This Document

- 各模块的产品细节见各自 `modules/{module}/Spec/prd.md`
- 工程规则见 `AGENTS.md`
- 术语定义见 `CONTEXT.md`
