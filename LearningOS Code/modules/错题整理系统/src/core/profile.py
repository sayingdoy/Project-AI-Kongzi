"""画像管理。

CONTEXT Profile 结构定义 + Architecture 知识更新逻辑。
"""

from __future__ import annotations

from typing import Any, Dict, List

from .models import Mistake, Profile, ReviewSession


def update_knowledge_map(
    profile: Profile,
    mistakes: List[Mistake],
    session: ReviewSession,
) -> Profile:
    """基于本次复习结果更新 knowledge_map。

    规则：
    - 该 topic 的 mistake_count 不变（原数据已录入）
    - last_reviewed 更新为 session 日期
    - common_reason 从本次错题中取最常见原因
    - mastered: 若 session.result == "通过" 设为 True
    """
    topic = session.topic
    if topic not in profile.knowledge_map:
        profile.knowledge_map[topic] = {
            "mistake_count": len(mistakes),
            "last_reviewed": session.date,
            "common_reason": "",
            "mastered": False,
        }

    profile.knowledge_map[topic]["last_reviewed"] = session.date
    profile.knowledge_map[topic]["mastered"] = session.result == "通过"

    # 统计最常见原因
    reasons = [m.reason for m in mistakes if m.reason]
    if reasons:
        from collections import Counter
        profile.knowledge_map[topic]["common_reason"] = Counter(reasons).most_common(1)[0][0]

    return profile


def detect_trends(profile: Profile, mistakes: List[Mistake]) -> List[Dict[str, Any]]:
    """分析历史错误模式，返回 learning_trends（含 source 字段指向原始 Mistake ID）。

    MVP 阶段进行简单的重复原因检测。
    """
    # 按 reason 分组
    from collections import defaultdict
    groups: Dict[str, List[str]] = defaultdict(list)
    for m in mistakes:
        groups[m.reason].append(m.id)

    trends: List[Dict[str, Any]] = []
    for reason, ids in groups.items():
        if len(ids) >= 2:
            trends.append({
                "pattern": f"连续{len(ids)}次{reason}",
                "since": min((m.created_at for m in mistakes if m.id in ids), default=""),
                "source": ids,
            })

    return trends
