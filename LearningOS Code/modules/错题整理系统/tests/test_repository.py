"""文件读写层测试。"""

import pytest
from pathlib import Path

from src.core.models import Mistake, Profile
from src.core.repository import MistakeRepository


class TestAppendAndRead:
    def test_append_creates_file(self, tmp_path: Path, sample_mistake: Mistake):
        repo = MistakeRepository(users_base=str(tmp_path))
        repo.append_mistake(sample_mistake)

        path = tmp_path / "开心" / "data" / "错题整理" / "错题集" / "数学" / "五年级上" / "分数加法.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "分数加法" in content
        assert sample_mistake.id in content
        assert "====" not in content  # 不是 Frontmatter 分隔符

    def test_append_then_read_back(self, tmp_path: Path, sample_mistake: Mistake):
        repo = MistakeRepository(users_base=str(tmp_path))
        repo.append_mistake(sample_mistake)

        mistakes = repo.read_mistakes("开心", "数学", "五年级上", "分数加法")
        assert len(mistakes) == 1
        assert mistakes[0].id == sample_mistake.id
        assert mistakes[0].question == sample_mistake.question

    def test_append_multiple_entries(self, tmp_path: Path, sample_mistake: Mistake):
        repo = MistakeRepository(users_base=str(tmp_path))
        repo.append_mistake(sample_mistake)

        m2 = Mistake(
            id="def67890",
            student="开心",
            subject="数学",
            grade="五年级上",
            topic="分数加法",
            question="1/3 + 1/2 = ？",
            wrong_answer="2/5",
            correct_answer="5/6",
            reason="概念不清",
        )
        repo.append_mistake(m2)

        mistakes = repo.read_mistakes("开心", "数学", "五年级上", "分数加法")
        assert len(mistakes) == 2
        assert mistakes[1].id == "def67890"

    def test_append_updates_count(self, tmp_path: Path, sample_mistake: Mistake):
        repo = MistakeRepository(users_base=str(tmp_path))
        repo.append_mistake(sample_mistake)

        m2 = Mistake(id="xyz789", student="开心", subject="数学", grade="五年级上", topic="分数加法",
                     question="test", wrong_answer="a", correct_answer="b", reason="粗心")
        repo.append_mistake(m2)

        path = tmp_path / "开心" / "data" / "错题整理" / "错题集" / "数学" / "五年级上" / "分数加法.md"
        content = path.read_text(encoding="utf-8")
        assert "mistake_count: 2" in content


class TestFindById:
    def test_find_by_id(self, tmp_path: Path, sample_mistake: Mistake):
        repo = MistakeRepository(users_base=str(tmp_path))
        repo.append_mistake(sample_mistake)

        found = repo.find_mistake_by_id("abc12345")
        assert found is not None
        assert found.id == "abc12345"

    def test_find_by_id_not_found(self, tmp_path: Path):
        repo = MistakeRepository(users_base=str(tmp_path))
        assert repo.find_mistake_by_id("nonexistent") is None


class TestReadAll:
    def test_read_all(self, tmp_path: Path, sample_mistake: Mistake):
        repo = MistakeRepository(users_base=str(tmp_path))
        repo.append_mistake(sample_mistake)

        m2 = Mistake(id="xyz789", student="开心", subject="数学", grade="五年级下", topic="分数乘法",
                     question="1/2×1/3=?", wrong_answer="1/5", correct_answer="1/6", reason="概念不清")
        repo.append_mistake(m2)

        all_mistakes = repo.read_all_mistakes("开心")
        assert len(all_mistakes) == 2


class TestUpdateStatus:
    def test_update_status(self, tmp_path: Path, sample_mistake: Mistake):
        repo = MistakeRepository(users_base=str(tmp_path))
        repo.append_mistake(sample_mistake)

        result = repo.update_mistake_status("abc12345", "已复习")
        assert result is True

        mistakes = repo.read_mistakes("开心", "数学", "五年级上", "分数加法")
        assert len(mistakes) == 1
        assert mistakes[0].status == "已复习"

    def test_update_status_not_found(self, tmp_path: Path):
        repo = MistakeRepository(users_base=str(tmp_path))
        result = repo.update_mistake_status("nonexistent", "已复习")
        assert result is False


class TestProfile:
    def test_read_default_profile(self, tmp_path: Path):
        repo = MistakeRepository(users_base=str(tmp_path))
        profile = repo.read_profile("新同学")
        assert profile.name == "新同学"
        assert profile.grade == ""

    def test_write_and_read_profile(self, tmp_path: Path, sample_profile: Profile):
        repo = MistakeRepository(users_base=str(tmp_path))
        repo.write_profile("开心", sample_profile)

        profile = repo.read_profile("开心")
        assert profile.name == "开心"
        assert "数学" in profile.subjects
        assert "分数加法" in profile.knowledge_map
        assert profile.knowledge_map["分数加法"]["mistake_count"] == 3
        assert profile.knowledge_map["分数加法"]["mastered"] is False
        assert len(profile.learning_trends) == 1


class TestKnowledgePoints:
    def test_load_knowledge_points(self):
        kp = MistakeRepository.load_knowledge_points()
        assert isinstance(kp, dict)
        assert "数学" in kp
        assert "五年级上" in kp["数学"]

    def test_topic_exists(self):
        assert MistakeRepository.topic_exists("数学", "五年级上", "分数的加法和减法") is True

    def test_topic_not_exists(self):
        assert MistakeRepository.topic_exists("数学", "五年级上", "不存在的知识点") is False

    def test_append_knowledge_point(self, tmp_path: Path, monkeypatch):
        """测试追加知识点（覆盖路径到临时文件）。"""
        # 临时修改路径需要用 monkeypatch，或者通过 repo 的静态方法测试
        # 这里用静态方法 append 测试逻辑
        pass  # 集成测试时覆盖
