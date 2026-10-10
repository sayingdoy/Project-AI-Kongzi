# AGENTS.md — 运行时指南

> 给你（Hermes）和其他使用本系统的 Agent。
> 开发阶段的工程规则见 `../Project/AGENTS.md`。

---

## 1. 这是什么系统

**错题整理系统** — Project AI-Kongzi 的第一个子模块。

功能：录入错题 → AI 分析归纳 → 出同类题 → 判题 → 追踪复习进度。

当前状态：Core Engine 待实现（Sprint 2B），Spec 完整。

---

## 2. 系统地图

```
../LearningOS Spec/          ← 规范和术语（只读）
    constitution.md             最高原则
    CONTEXT.md                  领域术语
    prd.md                      全局产品定义

shared/
    knowledge-points.yaml       知识点索引

../LearningOS Users/         ← 用户数据
    {student}/
        profile.yaml            用户画像
        data/错题整理/
            错题集/             按学科/年级/知识点 .md
            复习记录/           ReviewSession .md

modules/错题整理系统/
    Spec/                       本模块规范（只读）
        prd.md
        architecture.md
        adr.md
    src/core/                   核心引擎（Python）
        models.py               数据模型
        repository.py           文件读写
        service.py              业务逻辑
        ai.py                   AI 分析+出题
        profile.py              画像管理
```

---

## 3. 可用的操作

如果你（Agent）需要操作这个系统：

| 操作 | 方式 | 说明 |
|------|------|------|
| 录入错题 | `import` Core Engine → `service.add_mistake()` | 或 CLI `mkt add` |
| 查询错题 | `service.list_mistakes()` 或直接读 `users/` 下 .md 文件 | 用 `search_files` 搜索 Frontmatter |
| 查看学生画像 | 读 `../LearningOS Users/{student}/profile.yaml` | |
| 触发复习 | `service.review()` → AI 生成归纳+题目 | |
| 了解术语 | 读 `../LearningOS Spec/CONTEXT.md` | 不确定概念时先查 |
| 了解设计意图 | 读 `modules/错题整理系统/Spec/adr.md` | |

---

## 4. 约束

### 你可以做的事

- ✅ 读取任何 Spec、Code、用户数据
- ✅ 调用 Core Engine 的函数
- ✅ 通过 `search_files` 搜索错题集 Frontmatter
- ✅ 读取 profile.yaml 了解学生学习情况
- ✅ 读写 `../LearningOS Users/` 下通过 Core Engine 管理的文件

### 你不能做的事

- ❌ 修改 `../LearningOS Spec/` 下的 Constitution / CONTEXT（最高原则不可动）
- ❌ 修改 `modules/*/Spec/` 下的 Spec 文档（规范层不可动）
- ❌ 绕过 Core Engine 直接修改用户数据（必须通过 Repository 层）
- ❌ 向孩子直接输出答案（违反 Constitution A1）
- ❌ 给用户画像加主观标签（违反 Constitution A2）

---

## 5. 路径约定

本系统所有路径为相对路径，基于 `LearningOS Code/` 目录。

如需使用绝对路径，从环境变量或配置文件读取，不硬编码。
