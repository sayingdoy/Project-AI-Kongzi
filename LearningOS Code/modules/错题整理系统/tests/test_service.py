"""业务逻辑层测试。"""

import pytest

from src.core.models import Mistake
from src.core.repository import MistakeRepository
from src.core.service import MistakeService


class TestAddMistake:
    def test_add_valid_mistake(self, tmp_path):
        repo = MistakeRepository(users_base=str(tmp_path))
        svc = MistakeService(repo)

        m = svc.add_mistake(
            student="开心",
            subject="数学",
            grade="五年级上",
            topic="小数乘法",
            question="2.5×3=?",
            wrong_answer="7.5",
            correct_answer="7.5",
            reason="计算错误",
            auto_add_topic=True,
        )
        assert m.id
        assert m.status == "未复习"
        assert m.subject == "数学"

        # 验证文件写入
        mistakes = repo.read_mistakes("开心", "数学", "五年级上", "小数乘法")
        assert len(mistakes) == 1

    def test_add_invalid_subject(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        with pytest.raises(ValueError, match="无效科目"):
            svc.add_mistake(
                student="开心", subject="物理", grade="五年级上",
                topic="test", question="?", wrong_answer="a",
                correct_answer="b", reason="粗心",
            )

    def test_add_invalid_reason(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        with pytest.raises(ValueError, match="无效错误原因"):
            svc.add_mistake(
                student="开心", subject="数学", grade="五年级上",
                topic="test", question="?", wrong_answer="a",
                correct_answer="b", reason="随便说说",
            )

    def test_add_unknown_topic_without_auto(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        with pytest.raises(ValueError, match="未知知识点"):
            svc.add_mistake(
                student="开心", subject="数学", grade="五年级上",
                topic="超级难的题目", question="?", wrong_answer="a",
                correct_answer="b", reason="粗心",
            )

    def test_add_unknown_topic_with_auto(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        m = svc.add_mistake(
            student="开心", subject="数学", grade="五年级上",
            topic="新知识点001", question="?", wrong_answer="a",
            correct_answer="b", reason="粗心",
            auto_add_topic=True,
        )
        assert m is not None


class TestListMistakes:
    def test_list_empty(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        mistakes = svc.list_mistakes("开心")
        assert mistakes == []

    def test_list_with_filter(self, tmp_path):
        repo = MistakeRepository(users_base=str(tmp_path))
        svc = MistakeService(repo)

        svc.add_mistake("开心", "数学", "五年级上", "小数乘法",
                        "2.5×3=?", "7.0", "7.5", "计算错误", auto_add_topic=True)
        svc.add_mistake("开心", "数学", "五年级上", "小数乘法",
                        "1.2×4=?", "4.0", "4.8", "计算错误", auto_add_topic=True)

        all_m = svc.list_mistakes("开心")
        assert len(all_m) == 2

        filtered = svc.list_mistakes("开心", status="未复习")
        assert len(filtered) == 2

        filtered2 = svc.list_mistakes("开心", status="已复习")
        assert len(filtered2) == 0

    def test_list_invalid_status(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        with pytest.raises(ValueError, match="无效状态"):
            svc.list_mistakes("开心", status="未知状态")


class TestGetMistake:
    def test_get_by_id(self, tmp_path):
        repo = MistakeRepository(users_base=str(tmp_path))
        svc = MistakeService(repo)
        m = svc.add_mistake("开心", "数学", "五年级上", "小数乘法",
                            "2.5×3=?", "7.0", "7.5", "计算错误", auto_add_topic=True)

        found = svc.get_mistake(m.id)
        assert found.id == m.id
        assert found.question == "2.5×3=?"

    def test_get_nonexistent(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        with pytest.raises(ValueError, match="未找到错题"):
            svc.get_mistake("nonexistent")


class TestValidate:
    def test_validate_reason(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        assert svc.validate_reason("粗心") is None
        assert svc.validate_reason("不存在的理由") is not None

    def test_validate_subject(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        assert svc.validate_subject("数学") is None
        assert svc.validate_subject("物理") is not None


class TestMaybeAddTopic:
    def test_topic_already_exists(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        result = svc._maybe_add_topic("数学", "五年级上", "分数的加法和减法", confirmed=True)
        assert result is True  # 已有，直接返回 True

    def test_topic_confirmed(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        result = svc._maybe_add_topic("数学", "五年级上", "全新知识点001", confirmed=True)
        assert result is True

    def test_topic_not_confirmed(self, tmp_path):
        svc = MistakeService(MistakeRepository(users_base=str(tmp_path)))
        result = svc._maybe_add_topic("数学", "五年级上", "全新知识点002", confirmed=False)
        assert result is False
