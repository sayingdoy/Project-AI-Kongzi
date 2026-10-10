# Project AI-Kongzi · User Stories

> 按 Sprint 组织。完成后标记状态。
> 最后更新：2026-06-29

---

## Sprint 1 — Constitution ✅ 已完成

| ID | Story | 状态 |
|:---:|------|:---:|
| S1-1 | 定义最高原则（12 条） | ✅ |
| S1-2 | 定义写作规范（Constitution-Guide） | ✅ |

---

## Sprint 2A — 规范体系 ✅ 已完成

| ID | Story | 状态 |
|:---:|------|:---:|
| S2A-1 | 产出 CONTEXT.md（领域术语表） | ✅ |
| S2A-2 | 产出 knowledge-points.yaml（知识点索引） | ✅ |
| S2A-3 | 产出全局 PRD | ✅ |
| S2A-4 | 产出模块 PRD | ✅ |
| S2A-5 | 产出模块 Architecture | ✅ |
| S2A-6 | 产出模块 ADR | ✅ |

---

## Sprint 2B — Core Engine MVP ✅ 已完成

| ID | Story | 验收 | 状态 |
|:---:|------|------|:---:|
| S2B-1 | 录入错题：`mkt add` → 写入 Markdown 错题集文件 | 文件生成，Frontmatter 正确 | ✅ |
| S2B-2 | 校验输入：topic 在 knowledge-points.yaml，reason 受控词汇内 | 非法输入拒绝 | ✅ |
| S2B-3 | 查询错题：`mkt list` → 按学科/topic/状态筛选 | 匹配结果正确 | ✅ |
| S2B-4 | 查看单条错题：`mkt show --id` | 显示完整信息 | ✅ |
| S2B-5 | 复习会话：`mkt review` → AI 归纳+引导+3 题 | 输出可用复习内容 | ✅ |
| S2B-6 | 判题：`mkt check` → 全对=已复习，错题=新 Mistake | 状态正确变更 | ✅ |
| S2B-7 | 用户画像读写：profile.yaml knowledge_map 自动更新 | 数据与 source 可追溯 | ✅ |
| S2B-8 | 新知识点流程：`mkt add` 发现未知 topic 提示确认 | 提示+确认后写入 | ✅ |

**测试：** `pytest tests/ -v` → 49/49 通过

---

## Sprint 3 — 状态机闭环 ✅ 已完成

| ID | Story | 验收 | 状态 |
|:---:|------|------|:---:|
| S3-1 | 已掌握判定：`mkt verify` → AI 出 5 道间隔测试题 | 全对→已掌握，错→保持 | ✅ |
| S3-2 | 记忆曲线：knowledge_map 记录 next_review，到期可见 | `mkt profile` 显示待复测 | ✅ |
| S3-3 | 二次错误回滚：已掌握 topic 录入新错题→自动回滚 | Mistake status = 未复习 | ✅ |
| S3-4 | 根因探究：`mkt recall` → AI 分析+概念讲解 | 输出根因分析 | ✅ |
| S3-5 | AI Provider 配置化：环境变量 AI_PROVIDER/AI_API_KEY | mock 模式下有警告提示 | ✅ |
| S3-6 | 批量导入：`mkt add-raw <file> --student` → AI 提取+预览确认 | 预览后逐条录入 | ✅ |
| S3-7 | SOP 更新：批量导入 MD 格式示例 | SOP.md §2.2 补充 | ✅ |

---

## Sprint 4 — 学习仪表盘 + 多学科（待实现）

| ID | Story | 验收 | 依赖 |
|:---:|------|------|:---:|
| S4-1 | **学习概览**：`mkt dashboard --student 开心` 输出全局概况 | 活跃/已掌握/待复测/本周趋势/最薄弱点 | S2B+S3 |
| S4-2 | **知识点趋势**：`mkt trend --student 开心 --topic 分数加法` 时间线 | 录入→复习→已掌握→回滚→再复习 的历史 | S2B+S3 |
| S4-3 | **智能推荐**：`mkt recommend --student 开心` 输出 1-3 个推荐复习知识点 | 推荐理由含 evidence（待复测期/错题数/趋势） | S2B+S3 |
| S4-4 | **多学科-英语**：`mkt add/review --subject 英语` 全流程走通 | knowledge-points 含英语条目，英语错题可录入+复习 | S2B |
| S4-5 | **多学科-语文**：同上 | 同上 | S2B |

---

## 远期

| ID | Story | 预计 Sprint |
|:---:|------|:---:|
| F1 | Web UI — 浏览器操作，不再依赖 CLI | Sprint 5 |
| F2 | Obsidian vault 集成 — 数据目录可配置 | Sprint 6 |
| F3 | 知识图谱 — 知识点关系网络 | Sprint 7 |
| F4 | AI 对话辅导 — 学生直接交互 | Sprint 8+ |
| F5 | 游戏化激励 — 学习成就、里程碑 | — |
