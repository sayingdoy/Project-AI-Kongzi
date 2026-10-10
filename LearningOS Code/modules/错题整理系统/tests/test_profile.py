"""画像管理测试。"""

from src.core.models import Mistake, Profile, ReviewSession, Exercise
from src.core.profile import update_knowledge_map, detect_trends


class TestUpdateKnowledgeMap:
    def test_new_topic(self):
        profile = Profile(name="开心")
        mistakes = [
            Mistake(id="m1", topic="分数加法", reason="通分错误"),
            Mistake(id="m2", topic="分数加法", reason="通分错误"),
        ]
        session = ReviewSession(topic="分数加法", date="2026-06-29", result="通过",
                                exercises=[Exercise(question="1+1=?", correct_answer="2", passed=True)])

        updated = update_knowledge_map(profile, mistakes, session)
        assert "分数加法" in updated.knowledge_map
        assert updated.knowledge_map["分数加法"]["last_reviewed"] == "2026-06-29"
        assert updated.knowledge_map["分数加法"]["mastered"] is True
        assert updated.knowledge_map["分数加法"]["common_reason"] == "通分错误"
        assert updated.knowledge_map["分数加法"]["mistake_count"] == 2

    def test_existing_topic(self):
        profile = Profile(
            name="开心",
            knowledge_map={
                "分数加法": {
                    "mistake_count": 5,
                    "last_reviewed": "2026-06-01",
                    "common_reason": "通分错误",
                    "mastered": False,
                }
            },
        )
        mistakes = [Mistake(id="m3", topic="分数加法", reason="计算错误")]
        session = ReviewSession(topic="分数加法", date="2026-06-29", result="通过",
                                exercises=[Exercise(question="test", correct_answer="a", passed=True)])

        updated = update_knowledge_map(profile, mistakes, session)
        assert updated.knowledge_map["分数加法"]["last_reviewed"] == "2026-06-29"
        assert updated.knowledge_map["分数加法"]["mastered"] is True
        # mistake_count 不变（原数据已录入）
        assert updated.knowledge_map["分数加法"]["mistake_count"] == 5

    def test_not_passed(self):
        profile = Profile(name="开心")
        mistakes = [Mistake(id="m4", topic="小数乘法", reason="粗心")]
        session = ReviewSession(topic="小数乘法", date="2026-06-29", result="未通过",
                                exercises=[Exercise(question="test", correct_answer="a", passed=False)])

        updated = update_knowledge_map(profile, mistakes, session)
        assert updated.knowledge_map["小数乘法"]["mastered"] is False


class TestDetectTrends:
    def test_detect_trend(self):
        mistakes = [
            Mistake(id="m1", topic="分数加法", reason="通分错误", created_at="2026-06-01"),
            Mistake(id="m2", topic="分数加法", reason="通分错误", created_at="2026-06-15"),
            Mistake(id="m3", topic="分数减法", reason="粗心", created_at="2026-06-20"),
        ]
        trends = detect_trends(None, mistakes)
        assert len(trends) >= 1
        trend = next(t for t in trends if "通分错误" in t["pattern"])
        assert "m1" in trend["source"]
        assert "m2" in trend["source"]

    def test_no_trend_single_instance(self):
        mistakes = [Mistake(id="m1", topic="分数加法", reason="粗心")]
        trends = detect_trends(None, mistakes)
        assert len(trends) == 0
