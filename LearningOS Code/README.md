# 错题整理系统

> Project AI-Kongzi · 第一个子模块
> Sprint 2B — Core Engine 待实现

---

## 这是什么

一个帮你系统化记录、分析、回顾孩子错题的工具。

- **录入**：CLI 录入错题（科目、题目、错误答案、原因）
- **分析**：AI 归纳同类错误的共性，生成引导问题
- **验证**：AI 出 3 道同类题，答对才算"已复习"

系统不代替你教孩子——它帮你准备内容，你执行教学。

---

## 目录

| 目录 | 内容 |
|------|------|
| `modules/错题整理系统/Spec/` | 产品 + 架构 + 决策文档 |
| `modules/错题整理系统/src/core/` | Python Core Engine |
| `modules/错题整理系统/tests/` | 测试 |
| `../LearningOS Spec/` | 全局规范和术语 |
| `../LearningOS Users/` | 开心、开颜的错题数据 |

---

## 命令

```bash
# 录入一道错题
mkt add --student 开心 --subject 数学 --topic 分数加法 \
        --question "3/4 + 1/2 = ?" --wrong "1" --correct "5/4" \
        --reason 概念不清

# 查看分数加法的所有未复习错题
mkt list --student 开心 --topic 分数加法 --status 未复习

# 触发复习（AI 分析 + 出题）
mkt review --student 开心 --topic 分数加法

# 判练习题结果
mkt check --id ex-001 --correct

# 查看学生画像
mkt profile --student 开心
```

---

## 数据

错题数据用 Markdown + Frontmatter 存储，在 `../LearningOS Users/{学生}/` 下。Obsidian 可以直接打开浏览。

---

## 文档全览

| 文件 | 位置 | 读的人 |
|------|------|:---:|
| Constitution | `../LearningOS Spec/constitution.md` | 所有人 |
| 术语表 | `../LearningOS Spec/CONTEXT.md` | 所有人 |
| 产品规范 | `../LearningOS Spec/prd.md` + `Spec/prd.md` | Agent |
| 系统规范 | `Spec/architecture.md` | Agent |
| 决策记录 | `Spec/adr.md` | Agent |
| 工程规则 | `../Project/AGENTS.md` | Coding Agent |
| 开发计划 | `../Project/sprint-plan.md` | 你 + Agent |
