"""错题整理系统 · 业务逻辑层

遵循 Architecture §4（数据流）和 ADR-004（Core Engine 中心化）。
Service 层编排 Repository + AI Provider，不做文件直接操作。
"""

from __future__ import annotations

from typing import List, Optional

from .models import (
    VALID_REASONS,
    VALID_STATUSES,
    VALID_SUBJECTS,
    Exercise,
    Mistake,
    Profile,
    ReviewSession,
)
from .repository import MistakeRepository


class MistakeService:
    """错题业务逻辑。"""

    def __init__(self, repo: Optional[MistakeRepository] = None):
        self.repo = repo or MistakeRepository()

    # ── 校验 ──────────────────────────────────────────────

    def validate_subject(self, subject: str) -> Optional[str]:
        """校验科目。返回错误信息或 None。"""
        if subject not in VALID_SUBJECTS:
            return f"无效科目：{subject}。允许值：{', '.join(sorted(VALID_SUBJECTS))}"
        return None

    def validate_topic(self, subject: str, grade: str, topic: str) -> Optional[str]:
        """校验知识点。返回错误信息或 None。"""
        if self.repo.topic_exists(subject, grade, topic):
            return None
        # topic 不存在 — 非错误，让调用方决定是否新增
        return f"未知知识点：{topic}（{subject} {grade}）。是否添加到知识点索引？"

    def validate_reason(self, reason: str) -> Optional[str]:
        """校验错误原因。返回错误信息或 None。"""
        if reason not in VALID_REASONS:
            return f"无效错误原因：{reason}。允许值：{', '.join(sorted(VALID_REASONS))}"
        return None

    def _validate_grade(self, grade: str) -> Optional[str]:
        """年级格式校验（基本格式检查）。"""
        if not grade or not grade.strip():
            return "年级不能为空"
        return None

    # ── 录入 ──────────────────────────────────────────────

    def add_mistake(
        self,
        student: str,
        subject: str,
        grade: str,
        topic: str,
        question: str,
        wrong_answer: str,
        correct_answer: str,
        reason: str,
        auto_add_topic: bool = False,
    ) -> Mistake:
        """录入一条错题。

        依次校验：subject → grade → reason → topic。
        topic 不存在时：若 auto_add_topic=True 自动追加到知识点索引；
        否则校验失败，由调用方（CLI）提示用户确认。
        """
        # 校验
        err = self.validate_subject(subject)
        if err:
            raise ValueError(err)
        err = self._validate_grade(grade)
        if err:
            raise ValueError(err)
        err = self.validate_reason(reason)
        if err:
            raise ValueError(err)

        # topic 校验
        topic_err = self.validate_topic(subject, grade, topic)
        if topic_err and not auto_add_topic:
            raise ValueError(topic_err)
        if topic_err and auto_add_topic:
            self.repo.append_knowledge_point(subject, grade, topic)

        # 构造 Mistake
        mistake = Mistake(
            student=student,
            subject=subject,
            grade=grade,
            topic=topic,
            question=question,
            wrong_answer=wrong_answer,
            correct_answer=correct_answer,
            reason=reason,
            status="未复习",
            source="manual",
        )

        self.repo.append_mistake(mistake)

        # Sprint 3：检测二次错误回滚
        rollback_info = self._check_rollback(mistake)
        if rollback_info:
            print(f"⏪ 注意：已标记为「已掌握」的知识点「{mistake.topic}」再次出错，自动回滚为「未复习」。")
            print(f"   建议运行 mkt recall --student {mistake.student} --topic {mistake.topic} 进行根因分析。")

        return mistake

    def _check_rollback(self, mistake: Mistake) -> bool:
        """检测二次错误回滚。

        若该 student + topic 下有 Mistake 处于「已掌握」状态，自动回滚为「未复习」。
        """
        all_mistakes = self.repo.read_all_mistakes(mistake.student)
        mastered = [
            m for m in all_mistakes
            if m.topic == mistake.topic and m.status == "已掌握"
        ]
        if not mastered:
            return False

        for m in mastered:
            self.repo.update_mistake_status(m.id, "未复习")

        # 同时清理 profile 中的 mastered 标记
        profile = self.repo.read_profile(mistake.student)
        if mistake.topic in profile.knowledge_map:
            profile.knowledge_map[mistake.topic]["mastered"] = False
            profile.knowledge_map[mistake.topic].pop("next_review", None)
            self.repo.write_profile(mistake.student, profile)

        return True

    def _maybe_add_topic(self, subject: str, grade: str, topic: str, confirmed: bool) -> bool:
        """新增 Topic 流程（审计 #3 采纳）。confirmed=True 时写入索引。"""
        if self.repo.topic_exists(subject, grade, topic):
            return True
        if confirmed:
            self.repo.append_knowledge_point(subject, grade, topic)
            return True
        return False

    # ── 查询 ──────────────────────────────────────────────

    def list_mistakes(
        self,
        student: str,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        status: Optional[str] = None,
        grade: Optional[str] = None,
    ) -> List[Mistake]:
        """查询错题。返回过滤后的 Mistake 列表。"""
        all_mistakes = self.repo.read_all_mistakes(student)

        results = all_mistakes
        if subject:
            results = [m for m in results if m.subject == subject]
        if grade:
            results = [m for m in results if m.grade == grade]
        if topic:
            results = [m for m in results if m.topic == topic]
        if status:
            if status not in VALID_STATUSES:
                raise ValueError(f"无效状态：{status}。允许值：{', '.join(sorted(VALID_STATUSES))}")
            results = [m for m in results if m.status == status]

        return results

    def get_mistake(self, mistake_id: str) -> Mistake:
        """按 ID 查询单个错题。"""
        mistake = self.repo.find_mistake_by_id(mistake_id)
        if not mistake:
            raise ValueError(f"未找到错题：{mistake_id}")
        return mistake

    # ── 掌握度验证（Sprint 3） ─────────────────────────────

    def verify_mastery(self, student: str, topic: str, subject: str = "数学") -> ReviewSession:
        """触发掌握度验证（mkt verify）。

        条件：该 topic 下所有 Mistake 均为「已复习」状态。
        操作：AI 生成 5 道间隔测试题 → 逐题判题 → 全对则标记「已掌握」。
        """
        all_mistakes = self.repo.read_all_mistakes(student)
        target = [
            m for m in all_mistakes
            if m.topic == topic and m.subject == subject
        ]
        unreviewed = [m for m in target if m.status == "未复习"]
        if unreviewed:
            raise ValueError(
                f"「{topic}」下还有 {len(unreviewed)} 条错题未复习。"
                f"请先运行 mkt review --student {student} --topic {topic}"
            )

        if not target:
            raise ValueError(f"{student} 在「{topic}」下没有错题记录")

        profile = self.repo.read_profile(student)
        grade = target[0].grade

        # 调用 AI 生成掌握度测试题
        from .ai import generate_mastery_test
        content = generate_mastery_test(target, profile)

        # 构造 ReviewSession（类型="mastery"）
        session = ReviewSession(
            student=student,
            topic=topic,
            grade=grade,
            summary="掌握度验证测试",
            exercises=[
                Exercise(
                    question=ex.get("question", ""),
                    correct_answer=ex.get("correct_answer", ""),
                )
                for ex in content.get("exercises", [])
            ],
        )

        self.repo.create_review_session(session, student, subject)
        return session

    def judge_mastery(self, session: ReviewSession) -> dict:
        """判定掌握度测试结果。

        全对 → 该 topic 所有 Mistake →「已掌握」，更新 knowledge_map。
        有错 → 保持「已复习」，错题转为新 Mistake。
        """
        all_passed = all(e.passed for e in session.exercises if e.passed is not None)
        marked = sum(1 for e in session.exercises if e.passed is not None)
        total = len(session.exercises)

        if marked < total:
            return {"result": "incomplete", "message": f"进度：{marked}/{total}，请先完成所有判题"}

        if all_passed:
            # 标记该 topic 下所有 Mistake → 已掌握
            mistakes = self.repo.read_all_mistakes(session.student)
            topic_mistakes = [m for m in mistakes if m.topic == session.topic]
            for m in topic_mistakes:
                self.repo.update_mistake_status(m.id, "已掌握")

            # 更新 profile：mastered + next_review
            profile = self.repo.read_profile(session.student)
            from datetime import date, timedelta
            next_review = (date.today() + timedelta(days=7)).isoformat()
            if session.topic not in profile.knowledge_map:
                profile.knowledge_map[session.topic] = {}
            profile.knowledge_map[session.topic]["mastered"] = True
            profile.knowledge_map[session.topic]["last_reviewed"] = session.date
            profile.knowledge_map[session.topic]["next_review"] = next_review
            self.repo.write_profile(session.student, profile)

            return {"result": "mastered", "message": f"🎉 「{session.topic}」已标记为「已掌握」，{next_review} 后复测"}
        else:
            # 有错 → 错的题转为新 Mistake
            from .models import Mistake as MistakeModel
            for e in session.exercises:
                if e.passed is False:
                    new_m = MistakeModel(
                        student=session.student,
                        subject="数学",
                        grade=session.grade,
                        topic=session.topic,
                        question=e.question,
                        wrong_answer=e.student_answer or "错误",
                        correct_answer=e.correct_answer,
                        reason="未掌握",
                        status="未复习",
                        source="system",
                    )
                    self.repo.append_mistake(new_m)

            return {"result": "failed", "message": f"有题目未通过，已转为新错题，请重新复习"}

    # ── 批量导入（Sprint 3） ──────────────────────────────

    def extract_from_md(self, content: str) -> List[dict]:
        """从 MD 文件内容提取错题字段。

        调用 AI 解析 MD 文本，返回 [{question, wrong_answer, correct_answer, reason, subject, grade, topic}, ...]。
        """
        from .ai import generate_raw_extraction
        result = generate_raw_extraction(content)
        return result.get("mistakes", [])

    # ── 仪表盘（Sprint 4） ─────────────────────────────────

    def get_dashboard_data(self, student: str) -> dict:
        """生成学习概览数据。"""
        from datetime import date, timedelta

        mistakes = self.repo.read_all_mistakes(student)
        profile = self.repo.read_profile(student)
        today = date.today()
        monday = today - timedelta(days=today.weekday())

        # 活跃知识点：有任意 Mistake 的 topic
        active_topics = sorted(set(m.topic for m in mistakes))
        active_count = len(active_topics)

        # 已掌握数
        mastered = [t for t, info in profile.knowledge_map.items() if info.get("mastered")]
        mastered_count = len(mastered)

        # 待复测
        pending = [
            t for t, info in profile.knowledge_map.items()
            if info.get("mastered") and info.get("next_review", "") <= today.isoformat()
        ]
        pending_count = len(pending)

        # 本周新增错题
        week_new = sum(1 for m in mistakes if m.created_at >= monday.isoformat())

        # 本周完成复习 — 通过 ReviewSession 文件
        week_review = self._count_weekly_reviews(student, monday)

        # 最薄弱知识点 — 错题最多的 topic
        topic_counts = {}
        for m in mistakes:
            topic_counts[m.topic] = topic_counts.get(m.topic, 0) + 1
        weakest = max(topic_counts, key=topic_counts.get) if topic_counts else ""
        weakest_count = topic_counts.get(weakest, 0)
        # 如果有趋势数据，优先用趋势描述
        from .profile import detect_trends
        trends = detect_trends(None, mistakes)
        weakest_reason = ""
        if weakest and trends:
            matching = [t for t in trends if weakest in t.get("pattern", "")]
            if matching:
                weakest_reason = matching[0].get("pattern", "")
            else:
                weakest_reason = f"共 {weakest_count} 条错题"

        return {
            "student": student,
            "grade": profile.grade,
            "active_count": active_count,
            "active_topics": active_topics,
            "mastered_count": mastered_count,
            "mastered_topics": mastered,
            "pending_count": pending_count,
            "pending_topics": pending,
            "week_new_mistakes": week_new,
            "week_reviews": week_review,
            "weakest_topic": weakest,
            "weakest_reason": weakest_reason or (f"共 {weakest_count} 条错题" if weakest else "暂无数据"),
        }

    def _count_weekly_reviews(self, student: str, monday: "date") -> int:
        """统计本周的复习次数 — 从 ReviewSession 文件名提取日期。"""
        import re
        base = self.repo._users_base / student / "data" / "错题整理" / "复习记录"
        if not base.exists():
            return 0
        count = 0
        monday_str = monday.isoformat()
        for f in base.rglob("*.md"):
            # 文件名格式: {date}_{topic}_{session_id}.md
            m = re.match(r"(\d{4}-\d{2}-\d{2})_", f.name)
            if m and m.group(1) >= monday_str:
                count += 1
        return count

    def get_trend(self, student: str, topic: str, subject: str = "数学") -> list:
        """获取知识点的时间线事件列表。"""
        from datetime import date
        mistakes = self.repo.read_all_mistakes(student)
        topic_mistakes = sorted(
            [m for m in mistakes if m.topic == topic and m.subject == subject],
            key=lambda m: m.created_at,
        )

        if not topic_mistakes:
            return []

        events = []
        # Mistake 录入事件
        for m in topic_mistakes:
            events.append({
                "date": m.created_at,
                "type": "录入",
                "detail": f"{m.question} ({m.reason})",
            })

        # 复习记录事件 — 从 session 文件解析
        import re
        base = self.repo._users_base / student / "data" / "错题整理" / "复习记录"
        if base.exists():
            for f in sorted(base.rglob("*.md")):
                if topic not in f.name:
                    continue
                content = f.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
                fm = self.repo._parse_frontmatter(content)[0]
                s_date = fm.get("date", "")
                s_result = fm.get("result", "")
                s_ex_total = fm.get("exercises_total", "0")
                s_ex_pass = fm.get("exercises_passed", "0")
                if s_date:
                    if "verify" in content or "mastery" in content or "掌握度验证" in content:
                        events.append({
                            "date": s_date,
                            "type": "掌握度验证",
                            "detail": f"{s_ex_pass}/{s_ex_total} 通过",
                        })
                    else:
                        events.append({
                            "date": s_date,
                            "type": "复习",
                            "detail": f"{s_ex_pass}/{s_ex_total} 通过 → {'通过' if s_result == '通过' else '有错'}",
                        })

        # 回滚事件 — 从 mistake status 推断（已掌握→未复习 的变化）
        mastered_before = False
        for m in topic_mistakes:
            # 如果遇到从已掌握变回未复习, 说明发生了回滚
            pass  # status 只存当前值, 不存历史, 这里需要 profile 辅助

        # profile 知识图谱变化
        profile = self.repo.read_profile(student)
        if topic in profile.knowledge_map:
            km = profile.knowledge_map[topic]
            if km.get("mastered") and km.get("last_reviewed"):
                events.append({
                    "date": km.get("last_reviewed"),
                    "type": "已掌握",
                    "detail": "通过间隔测试",
                })

        # 按日期排序、去重
        events.sort(key=lambda e: e["date"])
        seen = set()
        unique_events = []
        for e in events:
            key = (e["date"], e["type"], e["detail"][:30])
            if key not in seen:
                seen.add(key)
                unique_events.append(e)

        return unique_events

    # ── 智能推荐（Sprint 4） ──────────────────────────────

    def recommend(self, student: str, subject: str = "") -> list:
        """生成复习推荐列表。

        5 因子加权评分，阈值 30%。返回 [{topic, score, reason, command}, ...]。
        """
        from datetime import date, timedelta

        mistakes = self.repo.read_all_mistakes(student)
        profile = self.repo.read_profile(student)
        today = date.today()

        # 收集所有 topic
        all_topics = sorted(set(m.topic for m in mistakes))
        if subject:
            all_topics = [t for t in all_topics
                          if any(m.subject == subject and m.topic == t for m in mistakes)]

        scored = []
        for topic in all_topics:
            topic_mistakes = [m for m in mistakes if m.topic == topic]
            km = profile.knowledge_map.get(topic, {})

            # 因子 1: 待复测天数 (30%)
            next_review = km.get("next_review", "")
            days_overdue = 0
            if next_review and km.get("mastered"):
                try:
                    overdue = today - date.fromisoformat(next_review)
                    days_overdue = max(0, overdue.days)
                except ValueError:
                    days_overdue = 0
            score1 = min(days_overdue / 14, 1.0) * 30  # 14天以上满分

            # 因子 2: 未复习错题数 (25%)
            unreviewed = sum(1 for m in topic_mistakes if m.status == "未复习")
            # 有未复习错题即获得 > 30% 基准线
            if unreviewed > 0:
                score2 = 20 + min(unreviewed / 3, 1.0) * 5  # 20~25
            else:
                score2 = 0

            # 因子 3: 二次错误标记 (20%)
            has_rollback = any(m.status == "未复习" for m in topic_mistakes)
            # 如果 knowledge_map 显示 mastered=False 且曾经 mastered=True
            was_mastered = km.get("mastered") is False and km.get("last_reviewed", "")
            score3 = 20 if (was_mastered and has_rollback) else 0

            # 因子 4: 趋势严重度 (15%)
            from .profile import detect_trends
            trends = detect_trends(None, topic_mistakes)
            trend_score = 0
            for t in trends:
                if topic in t.get("pattern", ""):
                    trend_score = min(trend_score + 5, 15)
            score4 = trend_score

            # 因子 5: 距上次复习天数 (10%)
            last_reviewed = km.get("last_reviewed", "")
            days_since_review = 0
            if last_reviewed:
                try:
                    days_since = (today - date.fromisoformat(last_reviewed)).days
                    days_since_review = max(0, days_since)
                except ValueError:
                    days_since_review = 0
            score5 = min(days_since_review / 60, 1.0) * 10  # 60天以上满分

            total = score1 + score2 + score3 + score4 + score5
            if total < 20:
                continue

            # 生成 reason
            reasons = []
            if days_overdue > 0:
                reasons.append(f"已过复测期 {days_overdue} 天")
            if unreviewed > 0:
                reasons.append(f"{unreviewed} 条错题未复习")
            if has_rollback and was_mastered:
                reasons.append("有二次错误需要根因分析")
            if days_since_review > 30:
                reasons.append(f"已 {days_since_review} 天未复习")

            # 生成 command
            if unreviewed > 0:
                cmd = f"mkt review --student {student} --topic {topic}"
            else:
                cmd = f"mkt verify --student {student} --topic {topic}"

            scored.append({
                "topic": topic,
                "score": round(total),
                "reason": " | ".join(reasons) if reasons else "待复测",
                "command": cmd,
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:3]

    # ── 根因探究（Sprint 3） ──────────────────────────────

    def recall(self, student: str, topic: str, subject: str = "数学") -> dict:
        """根因探究（mkt recall）。

        读取该 topic 下所有 Mistake → 调用 AI 生成根因分析和概念讲解。
        """
        all_mistakes = self.repo.read_all_mistakes(student)
        target = [
            m for m in all_mistakes
            if m.topic == topic and m.subject == subject
        ]
        if not target:
            raise ValueError(f"{student} 在「{topic}」下没有错题记录")

        profile = self.repo.read_profile(student)

        from .ai import generate_root_cause
        result = generate_root_cause(target, profile)
        return result

    # ── 复习（Slice 2） ────────────────────────────────────

    def review(self, student: str, topic: str, subject: str = "数学") -> ReviewSession:
        """触发复习会话。

        读取该 topic 下未复习 Mistake → 读取 Profile → 调用 AI → 创建 Session。
        """
        # 查找该 topic 在各年级的文件
        all_mistakes = self.repo.read_all_mistakes(student)
        target = [
            m for m in all_mistakes
            if m.topic == topic and m.subject == subject and m.status == "未复习"
        ]

        if not target:
            raise ValueError(f"{student} 在「{topic}」下没有待复习的错题")

        # 读取 profile
        profile = self.repo.read_profile(student)

        # 调用 AI（由 ai.py 实现）
        from .ai import analyze_mistakes  # 延迟导入，避免 Slice 2 前报错
        review_content = analyze_mistakes(target, profile)

        # 构造 ReviewSession
        grade = target[0].grade if target else ""
        session = ReviewSession(
            student=student,
            topic=topic,
            grade=grade,
            summary=review_content.get("summary", ""),
            guiding_questions=review_content.get("guiding_questions", []),
            exercises=[
                Exercise(
                    question=ex.get("question", ""),
                    correct_answer=ex.get("correct_answer", ""),
                )
                for ex in review_content.get("exercises", [])
            ],
        )

        self.repo.create_review_session(session, student, subject)
        return session

    def check(self, session_id: str, exercise_id: str, passed: bool) -> ReviewSession:
        """判题。

        判单个 Exercise。若该 session 的所有 exercise 都已判完：
        - 全对 → 该 topic 所有未复习 Mistake → status=已复习
        - 有错 → 保持未复习
        """
        # 查找 ReviewSession 文件
        # MVP：搜索所有 ReviewSession 文件，按 ID 匹配
        # 更完善的实现需索引，MVP 线性扫描
        raise NotImplementedError("check 的完整实现需要会话文件搜索逻辑，将在 CLI 层直接处理")

    # ── 画像（Slice 2） ────────────────────────────────────

    def get_profile(self, student: str) -> Profile:
        """读取学生画像。"""
        return self.repo.read_profile(student)
