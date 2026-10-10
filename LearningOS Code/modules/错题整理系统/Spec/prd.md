# 错题整理系统 · PRD

> Version: v0.1
> Parent: [LearningOS PRD](../../../LearningOS Spec/prd.md) | [Constitution](../../../LearningOS Spec/constitution.md) | [CONTEXT](../../../LearningOS Spec/CONTEXT.md)

---

## 1. Product Definition

错题整理系统是 Project AI-Kongzi 的第一个落地子模块。

它解决：**家长需要系统化地记录、分析、回顾孩子的错题——并基于错题证据，由 AI 生成个性化辅导内容。**

系统不代替家长教学。系统做三件事：**记录（录入）、分析（AI）、验证（出题判题）。** 家长执行面对面教学。

---

## 2. Users

| 用户 | 角色 | 交互方式 |
|------|------|------|
| Jason（家长） | 录入者、复习触发者 | CLI 命令 |
| 开心（老大，五年级） | 数据来源、学习主体 | 不操作系统（家长转述） |
| 开颜（老二，一年级） | 数据来源、学习主体 | 不操作系统（家长转述） |
| Coding Agent | 实现者 | 读 Spec → 写代码 |

---

## 3. Core Workflow

```
┌─────────────────────────────────────────────────┐
│  录入                 复习                  回顾  │
│                                                       │
│  mkt add            mkt review            Obsidian  │
│      ↓                   ↓                    ↓    │
│  错题入库          AI分析+出题          浏览/打印     │
│      ↓                   ↓                           │
│  [未复习]          mkt check                          │
│                       ↓                              │
│                  全对→[已复习]                         │
│                  有错→新Mistake                        │
└─────────────────────────────────────────────────┘
```

---

## 4. Feature List

### F1 — 录入错题

| 项目 | 内容 |
|------|------|
| 命令 | `mkt add` |
| 参数 | `--student`, `--subject`, `--topic`, `--question`, `--wrong`, `--correct`, `--reason` |
| 校验 | `subject` 必须在科目列表内；`topic` 必须在 `knowledge-points.yaml` 内或经确认新增；`reason` 必须在受控词汇内 |
| 输出 | 追加 Mistake 到 `users/{student}/data/错题整理/错题集/{subject}/{grade}/{topic}.md` |
| 初始状态 | 未复习 |

### F2 — 查询错题

| 项目 | 内容 |
|------|------|
| 命令 | `mkt list` |
| 参数 | `--student`, `[--subject]`, `[--topic]`, `[--status]`, `[--grade]` |
| 输出 | 匹配的 Mistake 列表 |

### F3 — 复习会话

| 项目 | 内容 |
|------|------|
| 命令 | `mkt review --student <name> --topic <topic>` |
| 系统行为 | (1) 读取该 topic 下所有未复习 Mistake；(2) 读取该学生的 profile 和 knowledge_map；(3) 调用 AI 生成：错误归纳 + 引导问题 + 3 道同类题；(4) 创建 ReviewSession |
| 输出 | 错误归纳 + 引导问题 + 3 道练习题（带 exercise_id） |

### F4 — 判题

| 项目 | 内容 |
|------|------|
| 命令 | `mkt check --id <exercise_id> --correct | --wrong` |
| 系统行为 | 记录结果；若答错 → 自动转为新 Mistake（来源=系统出题） |
| 判定 | 3 题全对 → 该 topic 所有未复习 Mistake → 已复习；有错 → 保持未复习 |

---

## 5. User Stories

| ID | 场景 |
|:---:|------|
| US1 | 家长发现老大在分数加法上做错 → CLI 录入 → 错题保存在对应文件 |
| US2 | 累积了 3 道分数加法错题 → `mkt review` → AI 分析出共同通病是通分 → 出 3 道同类题 |
| US3 | 家长把 3 道题读给老大 → 老大答对 2 道、错 1 道 → 错的那道自动变成新 Mistake |
| US4 | 下次再 review 同一 topic → 上次错的题也在待复习列表中 |

---

## 6. Beyond MVP

| 优先级 | 功能 | 依赖 |
|:---:|------|------|
| P1 | 已掌握状态（AI 出题 + 记忆曲线间隔测试） | F3 稳定 |
| P1 | 二次错误回滚 + 根因探究 + 概念讲解流程 | P1 |
| P2 | 多学科支持（语文、英语知识点） | knowledge-points 扩展 |
| P2 | Web UI | Core Engine 稳定 |
| P3 | 各学生独立 Obsidian vault | 数据目录可配置 |

---

## 7. Design Constraints

| Article | 约束 | 模块实现 |
|------|------|------|
| A1 启发 | AI 生成引导问题，不给答案 | Review 分析时生成引导问题 |
| A2 因材 | 按学生隔离 | `users/{student}/` 分目录 |
| A5 温故 | 连接已有知识 | Review 分析引用该 topic 历史所有 Mistake |
| A7 过程优先 | 记录错误过程 | 每个 Mistake 含 `wrong_answer` + `reason` |
| A8 可溯 | 结论可追溯 | insight 字段含 `source` 指向原始 Mistake ID |
| A12 诚信 | 忠实记录 | 错题不可原地修改；状态变更通过新 session 记录 |
