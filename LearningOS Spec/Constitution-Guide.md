
# Constitution Writing Guide

> Version: v1.0
>
> Defines how to write, review, and evolve the Project AI-Kongzi Constitution.

---

# 1. Purpose

The Constitution defines the immutable principles of Project AI-Kongzi.

This guide defines how those principles are created, evaluated, and maintained.

The guide governs the writing process.

The Constitution governs the project.

---

# 2. Writing Philosophy

The Constitution follows **Constitution-Driven Development (CDD)**.

Every Article SHALL satisfy the following objectives:

- Long-term stable.
- Universally applicable.
- Engineering actionable.
- AI interpretable.

The Constitution is written for AI Agents first, and humans second.

---

# 3. Core Principles

## G-001｜One Article, One Principle

Each Article defines exactly one fundamental principle.

If an Article attempts to solve multiple problems, it SHALL be split.

---

## G-002｜Rule First

Each Article SHALL follow this structure:

```text
Quotation
    ↓
Principle
    ↓
MUST
    ↓
MUST NOT
    ↓
Arbitration
```

The Principle MUST be understandable without reading any other Article.

---

## G-003｜Engineering First

Every Article MUST be enforceable.

If a principle cannot influence Product, Architecture, ADR, Engineering, Prompt, or AI Agent behavior, it does not belong in the Constitution.

---

## G-004｜Decision First

Every Article MUST answer a design conflict.

It should answer the question:

> "When two reasonable designs conflict, how should Project AI-Kongzi decide?"

If an Article cannot serve as an arbitration rule, it should not be included.

---

## G-005｜Agent First

The Constitution is primarily written for AI Agents.

Writing should prioritize:

- Precision over elegance.
- Consistency over rhetoric.
- Specification over explanation.

Avoid unnecessary narrative.

Avoid philosophical essays.

Avoid ambiguous language.

---

## G-006｜Modern First

The Constitution is derived using the following process:

```text
Modern Educational Philosophy
            ↓
Software Engineering
            ↓
AI System Design
            ↓
Analects Validation
            ↓
Constitution
```

The Analects validate the principle.

They do not define the principle.

---

## G-007｜Authentic Sources

All quotations MUST satisfy:

- Authentic.
- Verifiable.
- Accurately cited.

Never fabricate quotations.

Never imitate classical Chinese.

---

# 4. Article Template

Every Article SHALL use the following template.

```md
## Article N｜中文名称（English Name）

> Quotation
>
> —— Source

### Principle

...

### MUST

- ...

### MUST NOT

- ...

### Arbitration

...
```

No additional sections should be introduced unless the Constitution itself evolves.

---

# 5. Scope

The Constitution SHOULD contain only principles that are:

- Stable for years rather than months.
- Applicable across the entire project.
- Independent from implementation details.

The following content MUST NOT appear in the Constitution:

- Product requirements
- Architecture design
- Technical implementation
- Prompt engineering
- Coding conventions
- Temporary decisions

These belong in PRD, Architecture, ADR, or Engineering documentation.

---

# 6. Review Checklist

Before accepting a new Article, verify:

- [ ] Does it define exactly one principle?
- [ ] Can it resolve a design conflict?
- [ ] Can an AI Agent directly apply it?
- [ ] Will it likely remain valid for many years?
- [ ] Does it avoid implementation details?
- [ ] Does it duplicate an existing Article?
- [ ] Is the quotation authentic and properly cited?

If any answer is "No", the Article SHOULD be revised before inclusion.

---

# 7. Amendment Policy

The Constitution evolves slowly.

Changing an existing Article is preferred over adding a new one.

Adding a new Article SHOULD be considered only when no existing Article can reasonably govern the new principle.

The Constitution is intended to remain small, stable, and authoritative.

