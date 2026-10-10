"""错题整理系统 · 数据模型

遵循 Architecture §6.1（错题集文件格式）和 §6.2（复习记录文件格式）。
"""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional

# ── 受控词汇（来自 CONTEXT） ──────────────────────────────

VALID_REASONS = frozenset({
    "概念不清", "审题错误", "计算错误", "方法错误", "粗心", "未掌握",
})

VALID_STATUSES = frozenset({
    "未复习", "已复习", "已掌握",
})

VALID_SUBJECTS = frozenset({
    "数学", "语文", "英语",
})


# ── Helper ──────────────────────────────────────────────────

def _new_id() -> str:
    """生成 8 字符短 ID — UUID4 前 8 位 hex。MVP 数据量下碰撞可忽略。"""
    return uuid.uuid4().hex[:8]


def _today() -> str:
    return date.today().isoformat()


# ── 数据类 ──────────────────────────────────────────────────

@dataclass
class Mistake:
    """单条错题记录。对应 Architecture §6.1 条目格式。"""
    id: str = field(default_factory=_new_id)
    student: str = ""
    subject: str = ""
    grade: str = ""
    topic: str = ""
    question: str = ""
    wrong_answer: str = ""
    correct_answer: str = ""
    reason: str = ""
    status: str = "未复习"
    created_at: str = field(default_factory=_today)
    source: str = "manual"   # "manual" | "system"

    # ── 序列化 ──────────────────────────────────────────

    def to_entry(self) -> str:
        """生成 Markdown 条目文本，以 '---' 结尾。"""
        lines = [
            f"## {self.created_at} · {self.question} ❌",
            "",
            f"- **id:** {self.id}",
            f"- **错误答案：** {self.wrong_answer}",
            f"- **正确答案：** {self.correct_answer}",
            f"- **原因：** {self.reason}",
            f"- **状态：** {self.status}",
            "",
            "---",
        ]
        return "\n".join(lines)

    @classmethod
    def from_entry(cls, text: str) -> Optional["Mistake"]:
        """从条目文本解析 Mistake。若解析失败返回 None。"""
        text = text.strip()
        if not text:
            return None

        # 解析 heading: ## 2026-06-28 · 题目 ❌
        # 使用 re.search 而非 re.match——body 可能以 `# 错题集` 开头
        heading_match = re.search(r"^##\s+(\S+)\s+[·.]\s+(.+?)\s*[❌✗×]\s*$", text, re.MULTILINE)
        if not heading_match:
            return None
        created_at = heading_match.group(1)
        question = heading_match.group(2).strip()

        # 解析键值行: - **key:** value
        fields = {
            "id": "",
            "错误答案": "",
            "正确答案": "",
            "原因": "",
            "状态": "未复习",
        }
        for line in text.splitlines():
            m = re.match(r'^-\s+\*\*([^:]+?)[：:]\*\*\s+(.*)', line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                if key == "id":
                    fields["id"] = val
                elif key == "错误答案":
                    fields["错误答案"] = val
                elif key == "正确答案":
                    fields["正确答案"] = val
                elif key == "原因":
                    fields["原因"] = val
                elif key == "状态":
                    fields["状态"] = val

        return cls(
            id=fields["id"],
            student="",       # 由文件上下文填充
            subject="",
            grade="",
            topic="",
            question=question,
            wrong_answer=fields["错误答案"],
            correct_answer=fields["正确答案"],
            reason=fields["原因"],
            status=fields["状态"] if fields["状态"] in VALID_STATUSES else "未复习",
            created_at=created_at,
        )

    def to_status_line(self, new_status: str) -> str:
        """生成新状态行文本，用于 update_mistake_status 原地替换。"""
        return f"- **状态：** {new_status}"


@dataclass
class Exercise:
    """练习题 — ReviewSession 的子条目。"""
    id: str = field(default_factory=_new_id)
    question: str = ""
    correct_answer: str = ""
    student_answer: str = ""       # mkt check 时填入
    passed: Optional[bool] = None  # mkt check 时填入


@dataclass
class ReviewSession:
    """复习会话记录。对应 Architecture §6.2。"""
    id: str = field(default_factory=_new_id)
    student: str = ""
    topic: str = ""
    grade: str = ""
    date: str = field(default_factory=_today)
    exercises: List[Exercise] = field(default_factory=list)
    summary: str = ""              # 错误归纳
    guiding_questions: List[str] = field(default_factory=list)
    result: str = "未通过"          # "未通过" | "通过"

    @property
    def exercises_total(self) -> int:
        return len(self.exercises)

    @property
    def exercises_passed(self) -> int:
        return sum(1 for e in self.exercises if e.passed is True)

    def to_frontmatter(self) -> str:
        """生成文件开头的 YAML Frontmatter。"""
        lines = [
            "---",
            f"id: {self.id}",
            f"student: {self.student}",
            f"topic: {self.topic}",
            f"grade: {self.grade}",
            f"date: {self.date}",
            f"exercises_total: {self.exercises_total}",
            f"exercises_passed: {self.exercises_passed}",
            f"result: {self.result}",
            "---",
        ]
        return "\n".join(lines)

    def to_body(self) -> str:
        """生成复习记录正文。"""
        lines = [
            f"# 复习：{self.topic} · {self.date}",
            "",
            "## 错误归纳",
            self.summary,
            "",
            "## 引导问题",
        ]
        for q in self.guiding_questions:
            lines.append(f"- {q}")
        lines.append("")
        lines.append("## 练习题")
        for i, ex in enumerate(self.exercises, 1):
            status = "✅" if ex.passed is True else "❌" if ex.passed is False else "⏳"
            lines.append("")
            lines.append(f"### 题 {i} · {status}")
            lines.append(ex.question)
            # 答案不显示在 mkt review 输出中，但存储在文件里供 check 判题
            lines.append(f"正确答案：{ex.correct_answer}")
            if ex.student_answer:
                lines.append(f"学生答案：{ex.student_answer}")
        return "\n".join(lines)

    def to_full(self) -> str:
        """生成完整文件内容。"""
        return self.to_frontmatter() + "\n\n" + self.to_body()

    @classmethod
    def parse_frontmatter(cls, text: str) -> dict:
        """简易 YAML Frontmatter 解析。返回 key→value 字典。"""
        result = {}
        for line in text.strip().splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                result[key.strip()] = val.strip()
        return result


@dataclass
class Profile:
    """用户画像。对应 CONTEXT Profile 结构。"""
    name: str = ""
    grade: str = ""
    subjects: List[str] = field(default_factory=list)
    knowledge_map: dict = field(default_factory=dict)
    # 格式: {topic: {mistake_count: int, last_reviewed: str, common_reason: str, mastered: bool}}
    learning_trends: List[dict] = field(default_factory=list)
    # 格式: [{pattern: str, since: str, source: [id, ...]}]

    def to_yaml_lines(self) -> List[str]:
        """生成可写入 profile.yaml 的行。"""
        lines = [
            f"name: {self.name}",
            f"grade: {self.grade}",
            f"subjects: [{', '.join(self.subjects)}]",
            "",
            "knowledge_map:",
        ]
        for topic, info in self.knowledge_map.items():
            lines.append(f"  {topic}:")
            lines.append(f"    mistake_count: {info.get('mistake_count', 0)}")
            lines.append(f"    last_reviewed: {info.get('last_reviewed', '')}")
            lines.append(f"    common_reason: {info.get('common_reason', '')}")
            lines.append(f"    mastered: {str(info.get('mastered', False)).lower()}")
        lines.append("")
        lines.append("learning_trends:")
        for trend in self.learning_trends:
            sources = ", ".join(trend.get("source", []))
            lines.append(f"  - pattern: \"{trend.get('pattern', '')}\"")
            lines.append(f"    since: {trend.get('since', '')}")
            lines.append(f"    source: [{sources}]")
        return lines
