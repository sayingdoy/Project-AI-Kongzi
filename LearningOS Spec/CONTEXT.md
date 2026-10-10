# Project AI-Kongzi · CONTEXT（Domain Glossary）

> 本项目共享的领域术语表。不含实现细节，不含 Spec。
> 新增术语需在 grill-with-docs 中确认后写入。

---

## Core Entities

| Term | Definition |
|------|------|
| **LearningRecord / 学习记录** | 学习活动中任何值得留存的事件的持久化记录。是 Mistake、Strength、Milestone 等具体记录类型的父概念。 |
| **Mistake / 错题记录** | 学生在一次具体学习活动中，对一道具体题目给出的错误作答的完整记录。包含：题目本身、学生答了什么、正确答案是什么、为什么错了。是一次已发生的、可追溯的错误作答事件，而非"学生不会的题"或"值得记录的难题"。 |
| **Student / 学生** | 学习活动的主体，Mistake 的产生者。系统不自动检测错误。 |
| **Parent / 家长** | MVP 阶段唯一的系统直接用户，负责录入和查阅 Mistake。 |

## Controlled Vocabularies

### Reason / 错误原因

| Value | Definition |
|------|------|
| 概念不清 | 不理解题目涉及的知识概念 |
| 审题错误 | 错误理解题目要求 |
| 计算错误 | 概念和方向正确，具体计算出错 |
| 方法错误 | 用了错误的解题方法或步骤 |
| 粗心 | 本应做对但因注意力疏漏出错 |
| 未掌握 | 完全不会，没有解题思路 |

### Status / 复习状态

**证据驱动状态机。** 状态变更不由人主观判定，由系统基于证据决定。

```
[未复习] ──→ [已复习] ──→ [已掌握]
   ↑            │            │
   └── 二次错误回滚 ←── 同类型新错题录入
```

| Value | Definition | 触发条件 |
|------|------|------|
| 未复习 | 错题已录入，尚未复习 | 新录入或二次错误回滚 |
| 已复习 | 该 topic 下所有未复习错题，完成系统出题测试且全部正确 | `mkt check` 全对（MVP） |
| 已掌握 | 系统按记忆曲线出题，正确率达标 | AI 出题+间隔测试（v0.2+） |

**MVP Review 流程：**

```
Parent: mkt review --student 开心 --topic 分数加法
    ↓
系统分析该 topic 下未复习错题 → 生成错误归纳 + 引导问题 + 3 道同类题
    ↓
Parent 读给孩子 → 孩子纸面/口答
    ↓
Parent: mkt check --id <exercise_id> --correct/--wrong（逐题录入结果）
    ↓
系统判定：全对 → 已复习 | 有错 → 保持未复习
```

**Exercise / 练习题**：系统基于 Mistake 分析生成的同类测试题（含题目 + 参考答案）。Review Session 期间临时存在。答对 → 记录通过。答错 → 自动转为新 Mistake，标记来源=系统出题。

**ReviewSession / 复习会话**：一次 `mkt review` 触发的完整流程（分析→出题→判题→判定）。需持久化，可追溯。

**角色边界（MVP）：** AI 生成思考内容（归纳、引导、出题），Parent 执行面对面教学，孩子不直接操作系统。Parent 是系统唯一的直接用户。

**AI Provider（MVP）：** 不做硬编码。默认复用调用 Agent 的当前模型，预留独立 provider 配置项。MVP 以最简单透传实现。

**二次错误规则：** 已掌握的 Mistake，若同 Student + 同类型 出现新错题 → 自动回滚 → 需根因探究 + 概念讲解 → 重新测试方可闭环。

## Data References

### Subject / 科目

受控词汇。当前范围：

| Value |
|------|
| 数学 |
| 语文 |
| 英语 |

### Topic / 知识点

受控词汇。存储于独立文件 `LearningOS Code/shared/knowledge-points.yaml`，按学科 → 年级 → 章节组织，引用教参课标。系统以 YAML 解析做合法性校验。Parent 可新增，系统提示确认防重复。

### User / 用户

| Term | Definition |
|------|------|
| **Profile / 用户画像** | 学生的持久属性与基于证据的动态洞察。存储于 `users/{student}/profile.yaml`。 |

**Profile 结构规则：**

```yaml
# 静态字段 — Parent 手动维护
name: 开心
grade: 五年级
subjects: [数学, 语文, 英语]

# 动态字段 — 系统从数据计算，每次 Review 后刷新
knowledge_map:                   # 知识点掌握情况
  分数加法:
    mistake_count: 5             # 累计错题数
    last_reviewed: 2026-06-28
    common_reason: 通分错误
    mastered: false              # 证据判定（非人判定）

learning_trends:                 # 学习趋势
  - pattern: "分数连续3次通分错误"
    since: 2026-06-15
    source: [id1, id2, id3]      # 证据链，可追溯
```

**约束：** 所有 insight 必须有 `source` 指向原始数据。禁止主观标签（"数学差"等）。

### File System Convention

```
modules/{module}/     ← 代码（子模块源码、Spec、测试）
users/{student}/      ← 用户数据
  ├── profile.yaml    ← 用户画像
  └── data/{module}/  ← 按模块隔离的数据
      ├── 错题集/     ← Markdown + Frontmatter，按学科→年级→知识点
      └── 复习记录/   ← ReviewSession 独立存档

shared/              ← 跨模块共享代码
```

**错题集示例路径：** `users/开心/data/错题整理/错题集/数学/五年级上/分数加法.md`

**数据目录策略：** MVP 阶段数据存于项目内 `users/`。未来各学生独立 Obsidian vault，数据目录可配置目标路径。

**代码层与数据层严格分离。** 模块代码不直接写用户目录，通过 `users/{student}/data/{module}/` 寻址。
