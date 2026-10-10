# Sprint 2 · 任务分解

> 错题整理系统 MVP
> Sprint 状态：Phase 2A ✅ | 2B ✅

---

## Phase 2A：规范体系 ✅ 已完成

| # | 任务 | 产出 | 状态 |
|:---:|------|------|:---:|
| 1 | 领域术语定义 | CONTEXT.md | ✅ |
| 2 | 知识点索引 | knowledge-points.yaml | ✅ |
| 3 | 全局产品规范 | LearningOS Spec/prd.md | ✅ |
| 4 | 模块产品规范 | modules/错题整理/Spec/prd.md | ✅ |
| 5 | 系统规范 | modules/错题整理/Spec/architecture.md | ✅ |
| 6 | 决策记录 | modules/错题整理/Spec/adr.md | ✅ |

---

## Phase 2B：Core Engine MVP ✅ 已完成

### 任务概览

| # | 任务 | 文件 | 状态 |
|:---:|------|------|:---:|
| T1 | 数据模型定义 | `core/models.py` | ✅ |
| T2 | 文件读写层 | `core/repository.py` | ✅ |
| T3 | 知识点校验（内联到 service） | `core/service.py` | ✅ |
| T4 | 业务逻辑层 | `core/service.py` | ✅ |
| T5 | AI 集成层 | `core/ai.py` | ✅ |
| T6 | 画像管理 | `core/profile.py` | ✅ |
| T7 | CLI 入口 | `cli/main.py` | ✅ |
| T8 | 测试 | `tests/`（5 个文件） | ✅ |

### 交付物清单

```
modules/错题整理系统/src/
├── cli/main.py            # mkt add/list/show/review/check/profile
├── core/models.py         # Mistake / ReviewSession / Exercise / Profile
├── core/repository.py     # 文件读写
├── core/service.py        # 业务逻辑 + 校验 + 新 Topic 流程
├── core/ai.py             # AI 分析+出题
└── core/profile.py        # 画像管理

modules/错题整理系统/tests/
├── conftest.py
├── test_models.py
├── test_repository.py
├── test_service.py
├── test_cli.py            # Slice 1 端到端
└── test_profile.py
```

### 审计路径

```
CodeWhale (Planner) → Hermes (Auditor) → 分歧清零 → 终版_OK
详见 OS Audit/Archive/
```

### 测试结果

```
pytest tests/ -v → 49/49 通过
```

---

## 实施顺序（垂直切片优先）

```
Slice 1：录入 → 查看
  T1 → T2(读+追加+ID查询) → T3+T4(add+list+get) → T7(add+list+show) → T8(前4个测试)

Slice 2：复习
  T2(update+session) → T5 → T4(review+check) → T6 → T7(review+check+profile) → T8(全部)
```

**原则：** 先跑通第一条完整数据流（录入→查看），再叠加 AI 功能。
