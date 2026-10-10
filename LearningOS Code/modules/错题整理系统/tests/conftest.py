"""共享测试 fixture。"""

from __future__ import annotations

import pytest

from src.core.models import Mistake, Profile, ReviewSession


@pytest.fixture
def sample_mistake() -> Mistake:
    return Mistake(
        id="abc12345",
        student="开心",
        subject="数学",
        grade="五年级上",
        topic="分数加法",
        question="3/4 + 1/2 = ？",
        wrong_answer="1",
        correct_answer="5/4",
        reason="概念不清",
        status="未复习",
        created_at="2026-06-28",
    )


@pytest.fixture
def sample_mistake_lines() -> str:
    return """## 2026-06-28 · 3/4 + 1/2 = ？❌

- **id:** abc12345
- **错误答案：** 1
- **正确答案：** 5/4
- **原因：** 概念不清
- **状态：** 未复习

---"""


@pytest.fixture
def sample_profile() -> Profile:
    return Profile(
        name="开心",
        grade="五年级",
        subjects=["数学", "语文", "英语"],
        knowledge_map={
            "分数加法": {
                "mistake_count": 3,
                "last_reviewed": "2026-06-28",
                "common_reason": "通分错误",
                "mastered": False,
            }
        },
        learning_trends=[
            {
                "pattern": "分数连续3次通分错误",
                "since": "2026-06-15",
                "source": ["abc123", "def456"],
            }
        ],
    )
