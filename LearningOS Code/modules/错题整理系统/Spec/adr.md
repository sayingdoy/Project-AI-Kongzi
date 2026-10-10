# 错题整理系统 · ADR

> Version: v0.1
> Parent: [Architecture](./architecture.md)

---

## ADR-001：证据驱动的状态机

> Status: Accepted | Date: 2026-06-28

### Context

错题的复习状态（未复习/已复习/已掌握）如何判定？两种路径：(A) 家长主观判定，(B) 系统基于证据判定。

### Decision

**基于证据判定。** 状态变更不由人主观决定。

```
录入 → [未复习]
    ↓ mkt check 3题全对
[已复习]
    ↓ AI 出题 + 记忆曲线测试正确率达标 (v0.2+)
[已掌握]
    ↓ 同类型新错题
[未复习] ← 二次错误回滚
```

### Alternatives

| 方案 | 优点 | 缺点 | 判定 |
|------|------|------|:---:|
| 证据驱动 | 客观、可追溯、Constitution 一致 | 需要系统支持判定逻辑 | ✅ |
| 家长主观 | 简单 | 不可靠、不可追溯、违反 A8 | ❌ |

### Consequences

- 每个状态变更有可审计的证据链
- v0.2+ 需要记忆曲线调度逻辑
- 系统复杂度高于简单标记

---

## ADR-002：Markdown + Frontmatter 作为数据存储

> Status: Accepted | Date: 2026-06-28

### Context

错题数据需要满足：(1) 人类可读可编辑 (2) Agent 可查询 (3) Obsidian 兼容 (4) 可打印。备选方案：JSONL、SQLite、纯 Markdown。

### Decision

**Markdown 文件 + YAML Frontmatter。**

- 每个知识点一个 .md 文件（非每题一个）
- Frontmatter 存机器可解析的元数据（`topic`, `student`, `mistake_count`, `last_updated`）
- 正文是人类可读的错题列表
- Agent 通过 `search_files` 按 Frontmatter 字段查询

### Alternatives

| 方案 | 可读 | 可查询 | Obsidian | 判定 |
|------|:---:|:---:|:---:|:---:|
| Markdown+Frontmatter | ✅ | ✅ rg/grep | ✅ | ✅ |
| JSONL | ❌ | ✅ | ❌ | ❌ |
| SQLite | ❌ | ✅✅ | ❌ | ❌ MVP 过度 |

### Consequences

- Obsidian 直接浏览 / Dataview 查询 / 打印
- Agent 精确按需读取，不烧 token
- 追加新 Mistake 需解析文件结构后写入（比 JSONL 稍复杂）

---

## ADR-003：知识点系统（knowledge-points.yaml）

> Status: Accepted | Date: 2026-06-28

### Context

Topic 字段需要受控词汇，否则"同类型"无法被系统识别。备选：自由文本、预定义列表、混合方案。

### Decision

**YAML 文件预定义 + Parent 可扩展。** 按学科 → 年级 → 章节组织，引用教参课标。Parent 录入新知识点时系统提示确认防重复。

### Alternatives

| 方案 | 校验 | 扩展 | 判断 |
|------|:---:|:---:|:---:|
| 预定义+YAML+可扩展 | ✅ | ✅ | ✅ |
| 纯自由文本 | ❌ | ✅ | ❌ 无校验 |
| 硬编码 | ✅ | ❌ | ❌ 无法扩展 |

### Consequences

- `knowledge-points.yaml` 需持续维护
- 系统通过 `yaml.load()` 校验 Topic 合法性
- 错题集文件路径与知识点层级一致

---

## ADR-004：Core Engine 中心化架构

> Status: Accepted | Date: 2026-06-28

### Context

系统需要支持多种调用方式：CLI（MVP）、Web UI（后续）、Agent 直接调用。是否为每种方式独立实现？

### Decision

**单一 Core Engine（Python 包），所有接口通过它调用。** CLI 只是 Core 的薄壳。后续 Web UI 通过 import Core 调用相同函数。

### Alternatives

| 方案 | 复用 | 维护 |
|------|:---:|:---:|
| Core Engine 中心化 | ✅ | 低 |
| 独立实现 | ❌ | 高（逻辑分叉） |

### Consequences

- CLI 代码极简（解析参数 → 调用 Core → 打印结果）
- 后续 Web UI 只需加 HTTP 层，Core 不变
- Agent 可直接 `import` Core 模块操作数据
