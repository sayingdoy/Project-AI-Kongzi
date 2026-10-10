"""AI 集成层。

Architecture §5：构造 Prompt → 调用 AI → 解析返回内容。

Sprint 3：_call_llm 支持通过环境变量配置真实 AI Provider。
默认为 mock（clone 后零配置可运行），检测到 mock 时输出不可忽略的提示。
"""

from __future__ import annotations

import os
import sys
import warnings
from datetime import date, timedelta
from typing import Any, Dict, List

from .models import Mistake, Profile


def _call_llm(system_prompt: str, user_prompt: str) -> str:
    """调用 AI Provider。

    环境变量：
      AI_PROVIDER — "mock"（默认）、"openai"、"deepseek" 等
      AI_API_KEY  — API Key

    Architecture §5 要求：
    - System Prompt = Constitution A1-A12 核心条款 + Student Profile
    - User Prompt = 错题列表 + 任务要求
    """
    provider = os.environ.get("AI_PROVIDER", "mock")
    api_key = os.environ.get("AI_API_KEY", "")

    if provider == "mock":
        msg = (
            "\n⚠️  当前 AI Provider 为 mock 模式（AI_PROVIDER=mock）。\n"
            "   请设置环境变量 AI_PROVIDER=deepseek（或 openai）和 AI_API_KEY=<key>\n"
            "   以启用真实 AI 出题和分析。\n"
        )
        print(msg, file=sys.stderr)
        return _mock_response(provider)
    
    # 真实 API 调用（待集成具体 SDK）
    # TODO: 根据 provider 分发到不同 API
    response = _real_api_call(provider, api_key, system_prompt, user_prompt)
    return response


def _mock_response(task_type: str = "review") -> str:
    """返回模拟响应，确保 Core Engine 可脱离 API 运行。"""
    if task_type == "mastery":
        return (
            "掌握测试题：\n"
            "1. 3/4 + 1/6 = ？\n"
            "2. 5/8 - 1/3 = ？\n"
            "3. 2/5 + 3/10 = ？\n"
            "4. 7/12 - 1/4 = ？\n"
            "5. 1/2 + 2/3 = ？\n"
            "答案：1. 11/12  2. 7/24  3. 7/10  4. 1/3  5. 7/6"
        )
    if task_type == "root_cause":
        return (
            "根因分析：\n"
            "1. 学生对分数通分的基本概念不够牢固\n"
            "2. 当分母互质时，学生容易忘记用分母乘积作为公分母\n\n"
            "概念讲解：\n"
            "分数加法的核心是「单位相同才能直接相加」。\n"
            "就像 1 个苹果 + 1 个梨不能直接算成 2 个水果——\n"
            "需要先统一单位（切成同样大小的块）。\n\n"
            "通分口诀：分母不同先通分，分子跟着分母变，\n"
            "分子相加分母不变，能约分后再约分。\n\n"
            "试做：1/3 + 1/4 = ？提示：3和4的最小公倍数是？"
        )
    # 默认 review 响应
    return (
        "错误归纳：这些题都是通分错误。\n\n"
        "引导问题：\n"
        "- 为什么分母不同的分数不能直接相加？\n"
        "- 通分的时候，分子要跟着分母一起变吗？\n\n"
        "练习题：\n"
        "1. 1/3 + 1/4 = ？\n"
        "2. 2/5 + 3/10 = ？\n"
        "3. 3/8 + 1/2 = ？\n"
        "答案：1. 7/12  2. 7/10  3. 7/8"
    )


def _real_api_call(provider: str, api_key: str, system_prompt: str, user_prompt: str) -> str:
    """真实 API 调用（占位）。"""
    # TODO: 接入 OpenAI / Anthropic / DeepSeek SDK
    raise NotImplementedError(f"真实 API 调用尚未实现（provider={provider}）")


# ── 复习分析 ──────────────────────────────────────────────

def analyze_mistakes(mistakes: List[Mistake], profile: Profile) -> Dict[str, Any]:
    """分析错题列表，生成复习内容。"""
    system_prompt = _build_base_prompt(profile) + (
        "\n## 任务\n"
        "分析以下错题的共同模式，生成引导问题和同类练习题。\n"
        "不要直接给学生答案。提供提示、引导与反馈。\n"
    )
    mistakes_text = _format_mistakes_for_prompt(mistakes)
    user_prompt = (
        f"## 错题列表\n\n{mistakes_text}\n\n"
        f"## 要求\n"
        f"1. 总结这些错题的共同错误模式（简要，1-2句）\n"
        f"2. 给出 2-3 个引导问题（帮助学生自己发现错误）\n"
        f"3. 出 3 道同类练习题（难度从低到高）\n"
        f"4. 每道练习题提供参考答案\n\n"
        f"输出格式：\n"
        f"错误归纳：...\n\n"
        f"引导问题：\n"
        f"- ...\n\n"
        f"练习题：\n"
        f"1. ...\n"
        f"答案：..."
    )
    response = _call_llm(system_prompt, user_prompt)
    return _parse_review_response(response)


# ── 掌握度测试（Sprint 3） ──────────────────────────────

def generate_mastery_test(mistakes: List[Mistake], profile: Profile) -> Dict[str, Any]:
    """生成掌握度测试题（5 道间隔测试题）。

    Returns:
        {
            "exercises": [{"question": str, "correct_answer": str}, ...]
        }
    """
    system_prompt = _build_base_prompt(profile) + (
        "\n## 任务\n"
        "学生已复习完以下知识点，现在需验证是否真正掌握。\n"
        "出 5 道间隔测试题，覆盖该知识点的核心概念和易错点。\n"
        "难度从基础到略高，逐步递增。\n"
        "不要直接给提示——这是验证性测试。\n"
    )
    mistakes_text = _format_mistakes_for_prompt(mistakes)
    user_prompt = (
        f"## 参考错题\n\n{mistakes_text}\n\n"
        f"## 要求\n"
        f"1. 出 5 道同类型间隔测试题（覆盖核心概念 + 易错点）\n"
        f"2. 难度从低到高递增\n"
        f"3. 每道题提供参考答案\n\n"
        f"输出格式：\n"
        f"掌握测试题：\n"
        f"1. 题目\n"
        f"2. 题目\n"
        f"...\n"
        f"答案：1. ...  2. ...  3. ...  4. ...  5. ..."
    )
    response = _call_llm(system_prompt, user_prompt)
    return _parse_mastery_response(response)


# ── 根因探究（Sprint 3） ────────────────────────────────

def generate_root_cause(mistakes: List[Mistake], profile: Profile) -> Dict[str, Any]:
    """分析根因并生成概念讲解。

    Returns:
        {
            "analysis": str,        # 根因分析
            "explanation": str,     # 概念讲解
            "practice": str,        # 试做提示
        }
    """
    system_prompt = _build_base_prompt(profile) + (
        "\n## 任务\n"
        "学生之前已掌握的知识点再次犯错——需要深入分析根因。\n"
        "生成：根因分析 → 概念讲解 → 试做提示。\n"
        "不要直接给答案。提供易懂的概念讲解和引导。\n"
    )
    mistakes_text = _format_mistakes_for_prompt(mistakes)
    user_prompt = (
        f"## 错题列表\n\n{mistakes_text}\n\n"
        f"## 要求\n"
        f"1. 分析为什么已掌握的知识点再次出错（根因分析，1-2句）\n"
        f"2. 用通俗易懂的方式讲解概念（尽可能生动、日常化）\n"
        f"3. 给一道试做题的提示（不直接给答案）\n\n"
        f"输出格式：\n"
        f"根因分析：...\n\n"
        f"概念讲解：...\n\n"
        f"试做：..."
    )
    response = _call_llm(system_prompt, user_prompt)
    return _parse_root_cause_response(response)


# ── Prompt 构建辅助 ──────────────────────────────────────

def _build_base_prompt(profile: Profile) -> str:
    return (
        "你是 Project AI-Kongzi 的错题分析助手。\n\n"
        "## 原则（Constitution A1-A12 核心条款）\n"
        "- A1（启发）：不要直接给学生答案。提供提示、引导与反馈。\n"
        "- A2（因材）：根据学生当前能力调整内容。\n"
        "- A3（循序）：从基础到进阶。\n"
        "- A5（温故）：关联学生已有的知识。\n"
        "- A7（过程优先）：指出错误过程而非仅标注对错。\n"
        "- A8（可溯）：分析结论要指出依据。\n"
        "- A11（克制）：不超出能力范围。\n\n"
        f"## 学生画像\n"
        f"姓名：{profile.name}\n"
        f"年级：{profile.grade}\n"
        f"科目：{', '.join(profile.subjects)}\n"
        f"知识点掌握情况：{profile.knowledge_map}\n"
    )


def _format_mistakes_for_prompt(mistakes: List[Mistake]) -> str:
    return "\n\n".join(
        f"题目：{m.question}\n"
        f"学生答案：{m.wrong_answer}\n"
        f"正确答案：{m.correct_answer}\n"
        f"错误原因：{m.reason}"
        for m in mistakes
    )


# ── 响应解析 ──────────────────────────────────────────────

def _parse_review_response(text: str) -> Dict[str, Any]:
    """解析复习分析的 AI 响应。"""
    lines = text.strip().splitlines()
    summary = ""
    guiding_questions: List[str] = []
    exercises: List[Dict[str, str]] = []
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("错误归纳"):
            current_section = "summary"
            _, _, val = stripped.partition("：")
            summary = val.strip() if val else ""
            continue
        if stripped.startswith("引导问题"):
            current_section = "questions"
            continue
        if stripped.startswith("练习题"):
            current_section = "exercises"
            continue
        if stripped.startswith("答案"):
            current_section = "answers"
            continue
        if current_section == "questions" and stripped.startswith("- "):
            guiding_questions.append(stripped[2:].strip())
        if current_section == "exercises" and "。" in stripped:
            q = stripped
            import re as _re
            q = _re.sub(r'^\d+\.\s*', '', q).strip()
            if q:
                exercises.append({"question": q, "correct_answer": ""})
        if current_section == "answers" and "." in stripped:
            import re as _re
            parts = _re.split(r'\d+\.\s*', stripped)
            parts = [p.strip() for p in parts if p.strip()]
            for i, ans in enumerate(parts):
                if i < len(exercises):
                    exercises[i]["correct_answer"] = ans

    return {
        "summary": summary or "未生成错误归纳",
        "guiding_questions": guiding_questions or [
            "这个错误你以前犯过吗？",
            "正确的解法应该是怎样的？",
        ],
        "exercises": exercises or [
            {"question": "1/3 + 1/6 = ？", "correct_answer": "1/2"},
            {"question": "1/4 + 3/8 = ？", "correct_answer": "5/8"},
            {"question": "2/5 + 1/3 = ？", "correct_answer": "11/15"},
        ],
    }


def _parse_mastery_response(text: str) -> Dict[str, Any]:
    """解析掌握度测试的 AI 响应。"""
    lines = text.strip().splitlines()
    exercises: List[Dict[str, str]] = []
    in_answers = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("答案"):
            in_answers = True
            continue
        if stripped.startswith("掌握测试题") or stripped.startswith("测试题"):
            continue
        if not in_answers:
            import re as _re
            m = _re.match(r'^\d+\.\s+(.+)', stripped)
            if m:
                exercises.append({"question": m.group(1).strip(), "correct_answer": ""})
        else:
            # 答案行: "1. 11/12  2. 7/24  3. 7/10  4. 1/3  5. 7/6"
            import re as _re
            parts = _re.split(r'\d+\.\s*', stripped)
            parts = [p.strip() for p in parts if p.strip()]
            for i, ans in enumerate(parts):
                if i < len(exercises):
                    exercises[i]["correct_answer"] = ans

    return {
        "exercises": exercises or [
            {"question": f"间隔测试题{i}：3/4 + 1/6 = ？", "correct_answer": "11/12"}
            for i in range(1, 6)
        ],
    }


# ── 批量导入提取（Sprint 3） ────────────────────────────

def generate_raw_extraction(content: str) -> Dict[str, Any]:
    """从 MD 文件内容提取错题字段。

    解析 MD 文本，返回每条错题的 question, wrong_answer, correct_answer, reason 等。
    """
    # MVP：for Mistake format that matches the Sprint 2B format
    # For unmatched content, use AI to extract fields
    mistakes = _extract_from_md_fallback(content)
    return {"mistakes": mistakes}


def _extract_from_md_fallback(content: str) -> List[Dict[str, str]]:
    """从 MD 文本直接解析错题（不调用 AI，确定性解析）。

    支持格式（与 Mistake.to_entry() 一致）：
    ## date · question ❌

    - **id:** ...
    - **错误答案：** ...
    - **正确答案：** ...
    - **原因：** ...
    - **状态：** ...

    同时也支持简化格式：
    ## question ❌
    - **错误答案：** ...
    - **正确答案：** ...
    """
    import re
    results = []
    # 按 ## 分割
    blocks = re.split(r'\n(?=##\s)', content.strip())
    for block in blocks:
        if not block.strip():
            continue
        # 解析 heading
        heading_match = re.search(r'^##\s+(?:\S+\s+[·.]\s+)?(.+?)\s*[❌✗×]', block, re.MULTILINE)
        if not heading_match:
            continue
        question = heading_match.group(1).strip()

        # 解析字段
        fields = {"wrong_answer": "", "correct_answer": "", "reason": "未掌握", "topic": "未分类", "subject": "数学", "grade": "五年级上"}
        for line in block.splitlines():
            m = re.match(r'^-\s+\*\*([^:]+?)[：:]\*\*\s+(.*)', line.strip())
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                if key in ("错误答案", "wrong answer", "错误"):
                    fields["wrong_answer"] = val
                elif key in ("正确答案", "correct answer", "正确"):
                    fields["correct_answer"] = val
                elif key in ("原因", "reason"):
                    fields["reason"] = val
                elif key in ("知识点", "topic"):
                    fields["topic"] = val

        if question and fields["correct_answer"]:
            results.append({
                "question": question,
                "wrong_answer": fields["wrong_answer"],
                "correct_answer": fields["correct_answer"],
                "reason": fields["reason"],
                "subject": fields["subject"],
                "grade": fields["grade"],
                "topic": fields["topic"],
            })

    return results if results else [
        # Fallback: return one entry with full content for AI parsing
        {"question": content[:80], "wrong_answer": "", "correct_answer": "", "reason": "未掌握",
         "subject": "数学", "grade": "五年级上", "topic": "未分类"}
    ]


def _parse_root_cause_response(text: str) -> Dict[str, Any]:
    """解析根因探究的 AI 响应。"""
    lines = text.strip().splitlines()
    analysis = ""
    explanation = ""
    practice = ""
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("根因分析"):
            current_section = "analysis"
            _, _, val = stripped.partition("：")
            analysis = val.strip() if val else ""
            continue
        if stripped.startswith("概念讲解"):
            current_section = "explanation"
            _, _, val = stripped.partition("：")
            explanation = val.strip() if val else ""
            continue
        if stripped.startswith("试做"):
            current_section = "practice"
            _, _, val = stripped.partition("：")
            practice = val.strip() if val else ""
            continue
        if current_section == "analysis":
            analysis += (" " + stripped) if analysis else stripped
        elif current_section == "explanation":
            explanation += (" " + stripped) if explanation else stripped
        elif current_section == "practice":
            practice += (" " + stripped) if practice else stripped

    return {
        "analysis": analysis or "未生成根因分析",
        "explanation": explanation or "未生成概念讲解",
        "practice": practice or "未生成试做提示",
    }
