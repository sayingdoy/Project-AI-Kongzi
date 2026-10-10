"""数据模型测试。"""

from src.core.models import Mistake, Exercise, ReviewSession, Profile, VALID_REASONS, VALID_STATUSES


class TestMistake:
    def test_create(self, sample_mistake: Mistake):
        m = sample_mistake
        assert m.id == "abc12345"
        assert m.student == "开心"
        assert m.subject == "数学"
        assert m.status == "未复习"
        assert m.source == "manual"

    def test_to_entry_format(self, sample_mistake: Mistake):
        entry = sample_mistake.to_entry()
        assert entry.startswith("## ")
        assert "❌" in entry
        assert sample_mistake.id in entry
        assert "错误答案：" in entry
        assert "正确答案：" in entry
        assert "原因：" in entry
        assert "状态：" in entry
        assert entry.endswith("---")

    def test_from_entry_roundtrip(self, sample_mistake: Mistake, sample_mistake_lines: str):
        """双向序列化对称校验。"""
        entry = sample_mistake.to_entry()
        parsed = Mistake.from_entry(entry)
        assert parsed is not None
        assert parsed.id == sample_mistake.id
        assert parsed.question == sample_mistake.question
        assert parsed.wrong_answer == sample_mistake.wrong_answer
        assert parsed.correct_answer == sample_mistake.correct_answer
        assert parsed.reason == sample_mistake.reason
        assert parsed.status == sample_mistake.status
        assert parsed.created_at == sample_mistake.created_at

    def test_from_entry_exact_lines(self, sample_mistake_lines: str):
        """解析精确的架构示例文本。"""
        parsed = Mistake.from_entry(sample_mistake_lines)
        assert parsed is not None
        assert parsed.id == "abc12345"
        assert parsed.question == "3/4 + 1/2 = ？"
        assert parsed.wrong_answer == "1"
        assert parsed.correct_answer == "5/4"
        assert parsed.reason == "概念不清"
        assert parsed.status == "未复习"
        assert parsed.created_at == "2026-06-28"

    def test_from_entry_empty(self):
        assert Mistake.from_entry("") is None
        assert Mistake.from_entry("   ") is None

    def test_from_entry_non_mistake_text(self):
        """非条目文本应返回 None。"""
        assert Mistake.from_entry("这是一段普通文本") is None

    def test_valid_reasons(self):
        assert "概念不清" in VALID_REASONS
        assert "计算错误" in VALID_REASONS
        assert len(VALID_REASONS) == 6

    def test_valid_statuses(self):
        assert "未复习" in VALID_STATUSES
        assert "已复习" in VALID_STATUSES
        assert "已掌握" in VALID_STATUSES

    def test_to_status_line(self, sample_mistake: Mistake):
        assert sample_mistake.to_status_line("已复习") == "- **状态：** 已复习"


class TestReviewSession:
    def test_create(self):
        ex1 = Exercise(question="1+1=?", correct_answer="2")
        ex2 = Exercise(question="2+2=?", correct_answer="4", passed=True)
        session = ReviewSession(
            id="sess-001",
            student="开心",
            topic="分数加法",
            grade="五年级上",
            date="2026-06-28",
            exercises=[ex1, ex2],
            summary="通分错误",
            guiding_questions=["为什么分母不同不能直接加？"],
        )
        assert session.exercises_total == 2
        assert session.exercises_passed == 1
        assert session.result == "未通过"

    def test_to_frontmatter(self):
        session = ReviewSession(id="sess-001", student="开心")
        fm = session.to_frontmatter()
        assert fm.startswith("---")
        assert fm.endswith("---")
        assert "id: sess-001" in fm
        assert "student: 开心" in fm

    def test_to_full(self):
        session = ReviewSession(
            id="sess-002",
            student="开心",
            topic="小数乘法",
            grade="五年级上",
            date="2026-06-28",
            summary="进位错误",
            guiding_questions=["整数乘法怎么列竖式？"],
            exercises=[Exercise(question="2.5×3=?", correct_answer="7.5")],
        )
        full = session.to_full()
        assert "小数乘法" in full
        assert "进位错误" in full
        assert "2.5×3=?" in full
        # 审计 #1：答案不显示在 review 输出，但存储在文件里
        assert "7.5" in full  # 文件里存答案（给 parent check 用）


class TestProfile:
    def test_create(self, sample_profile: Profile):
        assert sample_profile.name == "开心"
        assert "数学" in sample_profile.subjects
        assert "分数加法" in sample_profile.knowledge_map
        assert len(sample_profile.learning_trends) == 1

    def test_to_yaml_lines(self, sample_profile: Profile):
        lines = sample_profile.to_yaml_lines()
        text = "\n".join(lines)
        assert "name: 开心" in text
        assert "knowledge_map:" in text
        assert "learning_trends:" in text
        assert "分数加法" in text
        assert "通分错误" in text
