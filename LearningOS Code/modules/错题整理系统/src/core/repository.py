"""错题整理系统 · 文件读写层

遵循 Architecture §4（数据流）和 §6（文件格式）。
Repository 层只操作文件系统，不涉及业务逻辑。
所有路径相对于可配置的 BASE_DIR（默认 `../../LearningOS Users/` 相对于模块根目录）。
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .models import Mistake, Profile, ReviewSession

# ── 路径常量 ──────────────────────────────────────────────

# 模块根目录 = modules/错题整理系统/
_MODULE_DIR = Path(__file__).resolve().parent.parent.parent  # up from core/ to modules/错题整理系统/

# 默认用户数据目录（相对于项目根目录 LearningOS Code/）
_USERS_DIR = (_MODULE_DIR / "../../LearningOS Users").resolve()

# 知识点索引路径
_KNOWLEDGE_POINTS_PATH = (_MODULE_DIR / "../../shared/knowledge-points.yaml").resolve()


class MistakeRepository:
    """错题与画像的文件读写操作。"""

    def __init__(self, users_base: Optional[str] = None):
        self._users_base = Path(users_base) if users_base else _USERS_DIR

    # ── 路径解析 ──────────────────────────────────────────

    def _mistake_file(self, student: str, subject: str, grade: str, topic: str) -> Path:
        return self._users_base / student / "data" / "错题整理" / "错题集" / subject / grade / f"{topic}.md"

    def _review_session_file(self, student: str, subject: str, grade: str, date: str, topic: str, session_id: str = "") -> Path:
        """复习记录文件路径。含 session_id 避免同 topic 同天覆盖。"""
        suffix = f"_{session_id}" if session_id else ""
        return self._users_base / student / "data" / "错题整理" / "复习记录" / subject / grade / f"{date}_{topic}{suffix}.md"

    def _profile_file(self, student: str) -> Path:
        return self._users_base / student / "profile.yaml"

    def _all_mistake_dirs(self, student: str) -> List[Path]:
        """遍历该学生所有错题集文件所在的目录。"""
        base = self._users_base / student / "data" / "错题整理" / "错题集"
        if not base.exists():
            return []
        return sorted(base.rglob("*.md"))

    # ── Frontmatter 解析 ──────────────────────────────────

    def _parse_frontmatter(self, content: str) -> Tuple[dict, str]:
        """解析 YAML Frontmatter，返回 (fields, body)。"""
        content = content.strip()
        if not content.startswith("---"):
            return {}, content
        # 找到第二个 '---'
        end_idx = content.find("---", 3)
        if end_idx == -1:
            return {}, content
        fm_block = content[3:end_idx].strip()
        body = content[end_idx + 3:].strip()
        fields = {}
        for line in fm_block.splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                fields[key.strip()] = val.strip()
        return fields, body

    def _build_frontmatter(self, topic: str, student: str, subject: str, grade: str, mistake_count: int) -> str:
        return (
            "---\n"
            f"topic: {topic}\n"
            f"student: {student}\n"
            f"subject: {subject}\n"
            f"grade: {grade}\n"
            f"mistake_count: {mistake_count}\n"
            f"last_updated: {Mistake().created_at}\n"
            "---"
        )

    def _read_file_safe(self, path: Path) -> str:
        """安全读取文件，不存在时返回空字符串。统一换行符为 \n。"""
        if not path.exists():
            return ""
        content = path.read_bytes()
        # 统一 \r\n → \n（Windows 兼容）
        return content.replace(b"\r\n", b"\n").decode("utf-8")

    # ── Mistake CRUD ──────────────────────────────────────

    def read_mistakes(self, student: str, subject: str, grade: str, topic: str) -> List[Mistake]:
        """读取指定知识点文件中的所有 Mistake。"""
        path = self._mistake_file(student, subject, grade, topic)
        content = self._read_file_safe(path)
        _, body = self._parse_frontmatter(content)
        return self._parse_entry_blocks(body, student, subject, grade, topic)

    def read_all_mistakes(self, student: str) -> List[Mistake]:
        """读取该学生所有知识点文件中的 Mistake。用于跨文件搜索。"""
        results: List[Mistake] = []
        for md_path in self._all_mistake_dirs(student):
            rel = md_path.relative_to(self._users_base / student / "data" / "错题整理" / "错题集")
            parts = rel.parts  # (subject, grade, topic.md)
            if len(parts) < 3:
                continue
            subject, grade = parts[0], parts[1]
            topic = parts[2].replace(".md", "")
            results.extend(self.read_mistakes(student, subject, grade, topic))
        return results

    def find_mistake_by_id(self, mistake_id: str) -> Optional[Mistake]:
        """跨所有学生/knowledge-point 文件按 ID 搜索 Mistake。"""
        # 搜索 LearningOS Users/ 下所有错题集文件
        for student_dir in (d for d in self._users_base.iterdir() if d.is_dir()):
            student = student_dir.name
            for md_path in self._all_mistake_dirs(student):
                rel = md_path.relative_to(self._users_base / student / "data" / "错题整理" / "错题集")
                parts = rel.parts
                if len(parts) < 3:
                    continue
                subject, grade = parts[0], parts[1]
                topic = parts[2].replace(".md", "")
                content = self._read_file_safe(md_path)
                _, body = self._parse_frontmatter(content)
                entries = self._parse_entry_blocks(body, student, subject, grade, topic)
                for m in entries:
                    if m.id == mistake_id:
                        return m
        return None

    def append_mistake(self, mistake: Mistake) -> None:
        """追加一条 Mistake 到对应文件。文件不存在时创建含 Frontmatter 的文件。"""
        path = self._mistake_file(mistake.student, mistake.subject, mistake.grade, mistake.topic)
        path.parent.mkdir(parents=True, exist_ok=True)

        content = self._read_file_safe(path)
        if not content:
            # 新文件：写入 Frontmatter + 标题 + 条目
            fm = self._build_frontmatter(
                topic=mistake.topic,
                student=mistake.student,
                subject=mistake.subject,
                grade=mistake.grade,
                mistake_count=1,
            )
            body = (
                f"\n\n# {mistake.topic} · 错题集\n\n"
                f"{mistake.to_entry()}\n"
            )
            path.write_text(fm + body, encoding="utf-8")
        else:
            # 已有文件：更新 Frontmatter 计数 + 追加条目
            fields, body = self._parse_frontmatter(content)
            count = int(fields.get("mistake_count", "0")) + 1
            new_fm = self._build_frontmatter(
                topic=mistake.topic,
                student=mistake.student,
                subject=mistake.subject,
                grade=mistake.grade,
                mistake_count=count,
            )
            # 保留原标题行 + 已有条目，末尾追加新条目
            path.write_text(new_fm + "\n\n" + body.rstrip() + "\n\n" + mistake.to_entry() + "\n", encoding="utf-8")

    def update_mistake_status(self, mistake_id: str, new_status: str) -> bool:
        """原地修改指定 Mistake 的状态行。返回是否找到并修改。"""
        for student_dir in (d for d in self._users_base.iterdir() if d.is_dir()):
            student = student_dir.name
            for md_path in self._all_mistake_dirs(student):
                content = self._read_file_safe(md_path)
                if not content:
                    continue
                # 在条目中搜索该 ID
                pattern = rf"(- \*\*id:\*\* {re.escape(mistake_id)}\s*\n.*?)(- \*\*状态：\*\* )(\S+)"
                replacement = rf"\1\2{new_status}"
                if re.search(pattern, content, re.DOTALL):
                    updated = re.sub(pattern, replacement, content, count=1, flags=re.DOTALL)
                    md_path.write_text(updated, encoding="utf-8")
                    return True
        return False

    # ── Profile ────────────────────────────────────────────

    def read_profile(self, student: str) -> Profile:
        """读取 student 的 profile.yaml。文件不存在时返回默认 Profile。"""
        path = self._profile_file(student)
        if not path.exists():
            return Profile(name=student)
        content = path.read_text(encoding="utf-8")
        return self._parse_profile_yaml(content, student)

    def write_profile(self, student: str, profile: Profile) -> None:
        """写入 profile.yaml。"""
        path = self._profile_file(student)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = profile.to_yaml_lines()
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _parse_profile_yaml(self, content: str, student: str) -> Profile:
        """简易 profile.yaml 解析。"""
        profile = Profile(name=student)
        current_topic: Optional[str] = None
        topic_info: dict = {}
        in_knowledge_map = False
        in_trends = False
        current_trend: dict = {}

        for line in content.splitlines():
            stripped = line.strip()

            if stripped == "knowledge_map:":
                in_knowledge_map = True
                in_trends = False
                continue
            if stripped == "learning_trends:":
                in_knowledge_map = False
                in_trends = True
                continue

            if in_knowledge_map:
                # 检测缩进判断层级
                if line.startswith("  ") and not line.startswith("    "):
                    # 知识点名: 比如 "  分数加法:"
                    if current_topic and topic_info:
                        profile.knowledge_map[current_topic] = dict(topic_info)
                    topic_match = re.match(r"\s{2}(\S+?):", line)
                    if topic_match:
                        current_topic = topic_match.group(1)
                        topic_info = {}
                    continue
                if line.startswith("    ") and current_topic:
                    m = re.match(r"\s{4}(\w+):\s*(.*)", line)
                    if m:
                        key = m.group(1)
                        val = m.group(2).strip()
                        if key == "mistake_count":
                            topic_info[key] = int(val)
                        elif key == "mastered":
                            topic_info[key] = val.lower() == "true"
                        else:
                            topic_info[key] = val
                    continue

            if in_trends:
                if line.startswith("  - pattern:"):
                    if current_trend:
                        profile.learning_trends.append(dict(current_trend))
                    m = re.match(r'\s{2}-\s+pattern:\s+"(.+)"', line)
                    if m:
                        current_trend = {"pattern": m.group(1), "since": "", "source": []}
                elif line.startswith("    since:"):
                    m = re.match(r"\s{4}since:\s+(.*)", line)
                    if m:
                        current_trend["since"] = m.group(1).strip()
                elif line.startswith("    source:"):
                    m = re.match(r"\s{4}source:\s+\[(.*)\]", line)
                    if m:
                        src_str = m.group(1).strip()
                        current_trend["source"] = [s.strip() for s in src_str.split(",") if s.strip()]

            if ":" in stripped:
                key, _, val = stripped.partition(":")
                k = key.strip()
                v = val.strip()
                if k == "name":
                    profile.name = v
                elif k == "grade":
                    profile.grade = v
                elif k == "subjects":
                    v_clean = v.strip("[]").replace(", ", ",")
                    profile.subjects = [s.strip() for s in v_clean.split(",") if s.strip()]

        # Flush last topic
        if current_topic and topic_info:
            profile.knowledge_map[current_topic] = dict(topic_info)
        if current_trend:
            profile.learning_trends.append(dict(current_trend))

        return profile

    # ── ReviewSession ─────────────────────────────────────

    def create_review_session(self, session: ReviewSession, student: str, subject: str) -> None:
        """将 ReviewSession 写入复习记录文件。"""
        path = self._review_session_file(student, subject, session.grade, session.date, session.topic, session.id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(session.to_full() + "\n", encoding="utf-8")

    # ── 帮助方法 ──────────────────────────────────────────

    @staticmethod
    def _parse_entry_blocks(body: str, student: str, subject: str, grade: str, topic: str) -> List[Mistake]:
        """将文件正文解析为 Mistake 列表。"""
        results: List[Mistake] = []
        # 按 '---' 分割条目（兼容末尾无 \n 的情形）
        blocks = re.split(r'\n---(?:\n|$)', body)
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            mistake = Mistake.from_entry(block)
            if mistake:
                mistake.student = student
                mistake.subject = subject
                mistake.grade = grade
                mistake.topic = topic
                results.append(mistake)
        return results

    # ── 知识点索引 ────────────────────────────────────────

    @staticmethod
    def load_knowledge_points() -> dict:
        """加载 knowledge-points.yaml，返回 {subject: {grade: [topics...]}} 结构。"""
        path = _KNOWLEDGE_POINTS_PATH
        if not path.exists():
            return {}
        content = path.read_text(encoding="utf-8")
        return _parse_knowledge_points_yaml(content)

    @staticmethod
    def append_knowledge_point(subject: str, grade: str, topic: str) -> None:
        """向 knowledge-points.yaml 追加一个知识点。"""
        path = _KNOWLEDGE_POINTS_PATH
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.exists():
            content = path.read_text(encoding="utf-8")
        else:
            content = ""

        # 查找学科/年级位置插入
        # 如果年级已存在，在年级下追加知识点
        pattern = rf"({re.escape(subject)}:\s*\n\s+{re.escape(grade)}:.*?)(?=\n\s+\w+:|$)"
        grade_pattern = re.compile(pattern, re.DOTALL)
        match = grade_pattern.search(content)
        if match:
            # 在年级下追加知识点
            insert = match.group(1)
            new_block = insert.rstrip() + f"\n    {topic}:\n"
            content = content[:match.start(1)] + new_block + content[match.end(1):]
        else:
            # 追加新学科/年级
            content += f"\n{subject}:\n  {grade}:\n    {topic}:\n"

        path.write_text(content, encoding="utf-8")

    @staticmethod
    def topic_exists(subject: str, grade: str, topic: str) -> bool:
        """检查知识点是否已存在于索引中。"""
        kp = MistakeRepository.load_knowledge_points()
        return subject in kp and grade in kp[subject] and topic in kp[subject][grade]


def _parse_knowledge_points_yaml(content: str) -> dict:
    """简易知识点 YAML 解析。返回 {subject: {grade: [topic, ...]}}。

    缩进层级：0 空格=学科，2 空格=年级，4 空格及以上=知识点。
    使用前导空格数量判断层级，避免 4 空格行被误判为 2 空格层级。
    """
    result: dict = {}
    current_subject: Optional[str] = None
    current_grade: Optional[str] = None

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if ":" not in stripped:
            continue

        # 计算前导空格数
        indent = len(line) - len(line.lstrip())

        # 用 partition 提取冒号前的键名（兼容 key: value 格式）
        key = stripped.partition(":")[0].strip()
        if not key:
            continue

        if indent == 0:
            # 学科级
            current_subject = key
            if current_subject not in result:
                result[current_subject] = {}
            current_grade = None
        elif indent == 2 and current_subject:
            # 年级级
            current_grade = key
            if current_grade not in result[current_subject]:
                result[current_subject][current_grade] = []
        elif indent >= 4 and current_subject and current_grade:
            # 知识点级（含带引号的值行）
            result[current_subject][current_grade].append(key)

    return result
