# Project AI-Kongzi · Roadmap

> 冲刺路径图。里程碑 + 时间线 + 依赖关系。
> 最后更新：2026-06-29

---

## 总览

```
Sprint 1           Sprint 2                 Sprint 3                 Sprint 4
Constitution   →   规范体系 + Core MVP   →   状态机闭环           →   仪表盘 + 多学科
   ✅               ✅✅                    ✅                        📋
```

---

## 已完成 Sprint

### Sprint 1 · Constitution（已归档）

| 里程碑 | 产出 | 状态 |
|------|------|:---:|
| 最高原则 | constitution.md（12 条） | ✅ |
| 编写规范 | Constitution-Guide.md | ✅ |

### Sprint 2 · 错题整理 MVP（已归档）

| Phase | 里程碑 | 产出 | 状态 |
|:---:|------|------|:---:|
| 2A | 规范体系 | CONTEXT + knowledge-points + PRD + Architecture + ADR | ✅ |
| 2B | Core Engine MVP | 录入、查询、Review（AI 分析+出题）、判题、用户画像 | ✅ |

**交付物：** `src/core/models.py` `repository.py` `service.py` `ai.py` `profile.py` `cli/main.py` + 5 个测试文件。`pytest` 49/49 通过。

### Sprint 3 · 状态机闭环（已归档）

| 里程碑 | 产出 | 状态 |
|------|------|:---:|
| 已掌握判定 | `mkt verify` — AI 出 5 道间隔测试题，全对→已掌握 | ✅ |
| 记忆曲线 | knowledge_map 新增 `next_review` 字段，`mkt profile` 显示待复测知识点 | ✅ |
| 二次错误回滚 | `add_mistake` 自动检测已掌握→回滚为未复习；`mkt recall` 根因探究 | ✅ |
| AI Provider | `_call_llm` 支持环境变量配置；mock 默认保留零配置兼容 | ✅ |
| 批量导入 | `mkt add-raw` — MD 文件 AI 提取+预览确认 | ✅ |
| SOP 更新 | 补充 MD 文件格式示例 | ✅ |

---

## 即将开始的 Sprint

### Sprint 4 · 学习仪表盘 + 多学科

| 里程碑 | 产出 | 依赖 |
|------|------|:---:|
| 学习概览 | `mkt dashboard --student` — 整体学习概况 | Sprint 2B + 3 |
| 知识点趋势 | `mkt trend --student --topic` — 知识点时间线 | Sprint 2B + 3 |
| 智能推荐 | `mkt recommend --student` — 最优复习顺序推荐 | Sprint 2B + 3 |
| 多学科支持 | `mkt add/review --subject 英语/语文` 全流程走通 | knowledge-points 扩展 |

**目标：** 从"操作工具"升级为"学习洞察引擎"。家长不再需要思考"今天该复习什么"。

---

## 史诗级故事（用户价值组织，非 Sprint 粒度）

> 史诗是跨越多个 Sprint 的用户价值主线。不绑定 Sprint 编号。

### Epic 1：错题管理闭环 ✅ 已交付（Sprint 2B + 3）

| 能力 | 交付 Sprint |
|------|:---:|
| 录入错题 + 校验 + 文件存储 | 2B |
| 查询/筛选/查看 | 2B |
| AI 复习（归纳+引导+出题） | 2B |
| 判题 + 状态变更（未复习→已复习） | 2B |
| 已掌握判定（5 题间隔测试） | 3 |
| 二次错误回滚 + 根因探究 | 3 |
| 批量导入（MD 文件 AI 提取） | 3 |
| 用户画像（knowledge_map + trends + next_review） | 2B + 3 |

**现状：** 核心闭环完成。家长可完整操作一条错题从录入到掌握的全生命周期。

### Epic 2：学习洞察 📋 Sprint 4

| 能力 | 说明 |
|------|------|
| 学习概览仪表盘 | 一眼看清全局：活跃/已掌握/待复测/趋势 |
| 知识点历史趋势 | 单个知识点随时间的变化：从录入到掌握再到回滚 |
| 智能复习推荐 | 系统主动建议"今天该复习什么" |
| 协作阅读（仪表盘） | CLI 输出可打印、可分享的概览报告 |

**启动条件：** Sprint 2B + 3 已交付，数据积累中。

### Epic 3：多学科覆盖 📋 Sprint 4+

| 能力 | 说明 |
|------|------|
| 英语知识点 | knowledge-points.yaml 扩展 + `mkt add/review --subject 英语` |
| 语文知识点 | 同上 |
| 跨学科统一画像 | profile.yaml 支持多学科 knowledge_map |

**启动条件：** 知识点索引扩展 + 基础流程验证。可与 Epic 2 并行。

### Epic 4：家长体验升级 🔭 规划中

| 能力 | 预计版本 |
|------|:---:|
| Web UI（浏览器操作，不再依赖 CLI） | v0.4 |
| 各学生独立 Obsidian vault（数据目录可配置） | v0.5 |
| 多家长协作（多 Agent 同时操作） | 待定 |

**启动条件：** Core Engine 稳定 + 仪表盘验证通过。

### Epic 5：学生自主学习 🚀 v1.0

| 能力 | 说明 |
|------|------|
| AI 对话辅导 | 学生直接与 AI 交互，不再需要家长转述 |
| 自适应学习路径 | 系统根据掌握情况自动规划学习路线 |
| 游戏化激励 | 学习成就、里程碑、排行榜（可选） |

**启动条件：** v0.x 系列验证 AI 出题质量 + 家长接受度。

---

## 中期路线图（v0.3 → v1.0）

| 版本 | Sprint | 内容 | Epic |
|:---:|:---:|------|:---:|
| **v0.3** | **Sprint 4** | **学习仪表盘（CLI）+ 多学科扩展** | 🏠 Epic 2 + Epic 3 |
| v0.4 | Sprint 5 | Web UI MVP（Flask/FastAPI 薄壳） | 🖥️ Epic 4 |
| v0.5 | Sprint 6 | Obsidian vault 集成 + 数据目录可配置 | 🗂️ Epic 4 |
| v0.6 | Sprint 7 | 知识图谱（知识点关系网络） | 🧠 待定 |
| **v1.0** | Sprint 8 | **AI 对话辅导（学生直接交互）** | 🤖 Epic 5 |

### 依赖链

```
Constitution  →  PRD  →  Architecture  →  Core Engine  →  仪表盘  →  Web UI  →  AI 对话
     │               │          │                              │
     └── CONTEXT  ───→  ADR  ───→                              │
                                                                   ↓
                                                        多学科扩展（并行）
```

---

## 版本号对照

| 版本 | Sprint | 实际交付内容 |
|:---:|:---:|------|
| v0.1 | Sprint 1 + 2 | Constitution + 规范体系 + Core Engine MVP |
| v0.2 | Sprint 3 | 状态机闭环（已掌握 + 二次错误回滚 + AI Provider + 批量导入） |
| v0.3 | Sprint 4 | 学习仪表盘 + 多学科（规划中） |
| v0.4 | Sprint 5 | Web UI（规划中） |
| v0.5+ | Sprint 6+ | Obsidian vault + 知识图谱 |
| v1.0 | Sprint 8+ | AI 对话辅导（规划中） |
