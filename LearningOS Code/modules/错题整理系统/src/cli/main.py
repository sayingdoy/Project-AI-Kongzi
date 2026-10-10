#!/usr/bin/env python3
"""错题整理系统 · CLI 入口

Architecture §3 + ADR-004：CLI 是 Core Engine 的薄壳，不做业务逻辑。
"""

import argparse
import os
import sys
from typing import List

from ..core.models import Mistake
from ..core.service import MistakeService


def _print_mistake(m: "Mistake") -> None:
    """打印单条错题详情。"""
    print(f"ID:        {m.id}")
    print(f"学生:      {m.student}")
    print(f"科目:      {m.subject}")
    print(f"年级:      {m.grade}")
    print(f"知识点:    {m.topic}")
    print(f"题目:      {m.question}")
    print(f"错误答案:  {m.wrong_answer}")
    print(f"正确答案:  {m.correct_answer}")
    print(f"原因:      {m.reason}")
    print(f"状态:      {m.status}")
    print(f"录入日期:  {m.created_at}")
    print()


def _print_mistake_compact(m: "Mistake") -> None:
    """紧凑打印错题列表行。"""
    print(f"  {m.id:10s}  {m.created_at:12s}  {m.topic:12s}  {m.status:6s}  {m.question[:40]}")


def _print_header() -> None:
    print(f"  {'ID':10s}  {'日期':12s}  {'知识点':12s}  {'状态':6s}  题目")
    print("  " + "-" * 80)


def cmd_add(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt add — 录入错题。"""
    try:
        # 先校验 topic 是否存在
        topic_err = svc.validate_topic(args.subject, args.grade, args.topic)
        auto_add = False
        if topic_err:
            # 提示用户确认新增知识点（审计 #3）
            print(topic_err)
            resp = input("是否自动添加到知识点索引？(y/n): ").strip().lower()
            if resp == "y":
                auto_add = True
            else:
                print("录入已取消。")
                sys.exit(1)

        mistake = svc.add_mistake(
            student=args.student,
            subject=args.subject,
            grade=args.grade,
            topic=args.topic,
            question=args.question,
            wrong_answer=args.wrong,
            correct_answer=args.correct,
            reason=args.reason,
            auto_add_topic=auto_add,
        )
        print(f"✅ 错题已录入，ID: {mistake.id}")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_add_raw(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt add-raw — 从 MD 文件批量导入错题。

    Sprint 3 + 审计 #4：读取 MD 文件，AI 提取字段，预览后录入。
    """
    try:
        filepath = args.file
        if not os.path.exists(filepath):
            print(f"❌ 文件不存在：{filepath}")
            sys.exit(1)

        content = open(filepath, "r", encoding="utf-8").read()
        # 调用 AI 提取
        extracted = svc.extract_from_md(content)
        if not extracted:
            print("❌ 未能从文件提取错题。请检查文件格式。")
            sys.exit(1)

        n = len(extracted)
        print(f"📄 从文件提取到 {n} 条错题：\n")
        for i, item in enumerate(extracted, 1):
            print(f"  [{i}] 题目: {item.get('question', '?')}")
            print(f"      科目: {item.get('subject', '?')} | 年级: {item.get('grade', '?')} | 知识点: {item.get('topic', '?')}")
            print(f"      错误: {item.get('wrong_answer', '?')} | 正确: {item.get('correct_answer', '?')}")
            print(f"      原因: {item.get('reason', '?')}")
            print()

        if not getattr(args, 'confirm', False):
            resp = input(f"确认录入以上 {n} 条错题？(y/n): ").strip().lower()
            if resp != "y":
                print("录入已取消。")
                sys.exit(1)

        # 逐条录入
        for item in extracted:
            try:
                m = svc.add_mistake(
                    student=args.student,
                    subject=item.get("subject", args.subject or "数学"),
                    grade=item.get("grade", args.grade or "五年级上"),
                    topic=item.get("topic", "未分类"),
                    question=item.get("question", ""),
                    wrong_answer=item.get("wrong_answer", ""),
                    correct_answer=item.get("correct_answer", ""),
                    reason=item.get("reason", "未掌握"),
                    auto_add_topic=True,
                )
                print(f"  ✅ {m.id}  {m.question[:40]}")
            except ValueError as e:
                print(f"  ❌ 录入失败: {e}")

        print(f"\n✅ 批量导入完成（{n} 条）")
    except Exception as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_list(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt list — 查询错题。"""
    try:
        mistakes = svc.list_mistakes(
            student=args.student,
            subject=args.subject,
            topic=args.topic,
            status=args.status,
            grade=args.grade,
        )
        if not mistakes:
            print("没有匹配的错题。")
            return
        print(f"共 {len(mistakes)} 条错题：\n")
        _print_header()
        for m in mistakes:
            _print_mistake_compact(m)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_show(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt show — 查看单条错题详情。"""
    try:
        mistake = svc.get_mistake(args.id)
        _print_mistake(mistake)
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


# 内存中的最后一条复习会话 — CLI 层持有，用于 check 判题
_last_session: "ReviewSession | None" = None


def cmd_review(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt review — 触发复习会话（Slice 2）。"""
    global _last_session
    try:
        session = svc.review(args.student, args.topic, args.subject)
        _last_session = session
        print(f"📝 复习会话已创建（ID: {session.id}）\n")
        print("━━━━ 错误归纳 ━━━━")
        print(session.summary)
        print("\n━━━━ 引导问题 ━━━━")
        for i, q in enumerate(session.guiding_questions, 1):
            print(f"  {i}. {q}")
        print("\n━━━━ 练习题 ━━━━")
        print("（答案不在此处显示）\n")
        for i, ex in enumerate(session.exercises, 1):
            print(f"  题 {i}: {ex.question}")
            print(f"  mkt check --id {ex.id} --correct | --wrong")
            print()
    except (ValueError, NotImplementedError) as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_recall(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt recall — 根因探究（Sprint 3）。

    分析已掌握知识点再次出错的原因，生成概念讲解。
    """
    try:
        result = svc.recall(args.student, args.topic, args.subject)
        print("\n━━━━ 根因分析 ━━━━")
        print(result.get("analysis", ""))
        print("\n━━━━ 概念讲解 ━━━━")
        print(result.get("explanation", ""))
        print("\n━━━━ 试做提示 ━━━━")
        print(result.get("practice", ""))
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_verify(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt verify — 掌握度验证（Sprint 3）。

    触发 AI 生成 5 道间隔测试题。
    Parent 用 mkt check 判题，全对→已掌握。
    """
    try:
        session = svc.verify_mastery(args.student, args.topic, args.subject)
        print(f"📝 掌握度验证已创建（ID: {session.id}）\n")
        print("━━━━ 间隔测试题（共 5 题）━━━━")
        for i, ex in enumerate(session.exercises, 1):
            print(f"\n  题 {i}: {ex.question}")
            print(f"  mkt check --id {ex.id} --correct | --wrong")
        print("\n全部判完后运行 mkt mastery-result 查看结果。")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_mastery_result(args: argparse.Namespace, svc: MistakeService) -> None:
    """对最近一条 verify 会话执行掌握度判定。"""
    global _last_session
    try:
        if _last_session is None or _last_session.summary != "掌握度验证测试":
            print("❌ 没有活跃的掌握度验证会话。请先运行 mkt verify。")
            sys.exit(1)
        result = svc.judge_mastery(_last_session)
        print(result["message"])
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_check(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt check — 判题。

    在内存中的最后一条复习会话中定位 exercise，逐题标记。
    该 topic 所有 exercise 全对 → 更新 Mistake 状态为「已复习」。
    """
    global _last_session
    try:
        if _last_session is None:
            print("❌ 没有活跃的复习会话。请先运行 mkt review。")
            sys.exit(1)

        if args.correct == args.wrong:
            print("❌ 请指定 --correct 或 --wrong（二选一）")
            sys.exit(1)

        passed = args.correct

        # 在 session 中定位 exercise
        ex = next((e for e in _last_session.exercises if e.id == args.id), None)
        if not ex:
            print(f"❌ 未找到练习题：{args.id}")
            sys.exit(1)

        # 标记
        ex.passed = passed
        ex.student_answer = "正确" if passed else "错误"
        print(f"{'✅' if passed else '❌'} 题已标记（{ex.question}）")

        # 检查是否所有 exercise 都已判完
        total = len(_last_session.exercises)
        marked = sum(1 for e in _last_session.exercises if e.passed is not None)
        if marked < total:
            print(f"进度：{marked}/{total} 题已判完。继续或输入 mkt check --next 重新开始。")
            return

        # 全部已判完 → 判定
        is_mastery = (_last_session.summary == "掌握度验证测试")
        all_passed = all(e.passed for e in _last_session.exercises)
        _last_session.result = "通过" if all_passed else "未通过"

        if is_mastery:
            # 掌握度验证 — 交给 judge_mastery 处理
            result = svc.judge_mastery(_last_session)
            print(f"\n{result['message']}")
        elif all_passed:
            # 复习判题全对 → 已复习
            mistakes = svc.repo.read_all_mistakes(_last_session.student)
            topic_mistakes = [
                m for m in mistakes
                if m.topic == _last_session.topic and m.status == "未复习"
            ]
            for m in topic_mistakes:
                svc.repo.update_mistake_status(m.id, "已复习")
            print(f"\n🎉 全部正确！「{_last_session.topic}」的错题已标记为「已复习」。")
        else:
            # 复习判题有错 → 新错题
            for e in _last_session.exercises:
                if e.passed is False:
                    new_m = Mistake(
                        student=_last_session.student,
                        subject="数学",
                        grade=_last_session.grade,
                        topic=_last_session.topic,
                        question=e.question,
                        wrong_answer=e.student_answer or "错误",
                        correct_answer=e.correct_answer,
                        reason="未掌握",
                        status="未复习",
                        source="system",
                    )
                    svc.repo.append_mistake(new_m)
            print(f"\n📖 有题目未通过，已转为新错题。")
    except (ValueError, NotImplementedError) as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_profile(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt profile — 查看学生画像。"""
    try:
        profile = svc.get_profile(args.student)
        print(f"学生: {profile.name}")
        print(f"年级: {profile.grade}")
        print(f"科目: {', '.join(profile.subjects)}")

        # 待复测知识点（审计 #1：next_review 可见性）
        from datetime import date
        today = date.today().isoformat()
        pending = [
            (t, info) for t, info in profile.knowledge_map.items()
            if info.get("mastered") and info.get("next_review", "") <= today
        ]
        if pending:
            print(f"\n⏰ 待复测知识点：")
            for topic, info in pending:
                print(f"   {topic}（上次复习: {info.get('last_reviewed', '无')}）")
                print(f"     → mkt verify --student {profile.name} --topic {topic}")

        if profile.knowledge_map:
            print("\n知识点掌握情况：")
            for topic, info in profile.knowledge_map.items():
                mastered = "✅" if info.get("mastered") else "📖"
                nxt = info.get("next_review", "")
                nxt_str = f" (复测: {nxt})" if (info.get("mastered") and nxt) else ""
                print(f"  {mastered} {topic}{nxt_str}")
                print(f"      错题数: {info.get('mistake_count', 0)}")
                print(f"      上次复习: {info.get('last_reviewed', '无')}")
                print(f"      常见原因: {info.get('common_reason', '未知')}")
        if profile.learning_trends:
            print("\n学习趋势：")
            for t in profile.learning_trends:
                print(f"  📊 {t.get('pattern', '')} (since {t.get('since', '')})")
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)


def cmd_recommend(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt recommend — 智能推荐复习内容。"""
    try:
        recs = svc.recommend(args.student, getattr(args, 'subject', ''))
        if not recs:
            print("暂无推荐，继续保持！所有知识点都在掌控中。")
            return

        print("\n今日复习推荐")
        print("\u2500" * 50)
        medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
        for i, r in enumerate(recs):
            medal = medals[i] if i < len(medals) else ""
            print(f"{medal} {r['topic']}（推荐指数：{r['score']}%）")
            print(f"   理由：{r['reason']}")
            print(f"   命令：{r['command']}")
            print()
    except ValueError as e:
        print(f"\u274c {e}")
        sys.exit(1)


def cmd_dashboard(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt dashboard — 学习概览。"""
    try:
        data = svc.get_dashboard_data(args.student)
        if not data.get("active_count") and not data.get("mastered_count"):
            print(f"📋 {data['student']} 的学习概览\n")
            print("还没有学习记录。录入错题后再来看。")
            return

        print(f"\n{data['student']} · {data.get('grade', '?')} · 学习概览")
        print("\u2500" * 40)
        print(f"\U0001f4d6 活跃知识点：{data['active_count']} 个" +
              (f"（{', '.join(data['active_topics'][:5])}）" if data['active_topics'] else ""))
        print(f"\u2705 已掌握：{data['mastered_count']} 个")
        print(f"\u23f0 待复测：{data['pending_count']} 个" +
              (f"（{', '.join(data['pending_topics'])}）" if data['pending_topics'] else ""))
        print(f"\U0001f4ca 本周新增错题：{data['week_new_mistakes']} 条")
        print(f"\U0001f4ca 本周完成复习：{data['week_reviews']} 次")
        if data['weakest_topic']:
            print(f"\u26a1 最薄弱知识点：{data['weakest_topic']}（{data['weakest_reason']}）")
            print(f"   \u2192 mkt trend --student {data['student']} --topic {data['weakest_topic']}")
    except ValueError as e:
        print(f"\u274c {e}")
        sys.exit(1)


def cmd_trend(args: argparse.Namespace, svc: MistakeService) -> None:
    """mkt trend — 知识点时间线。"""
    try:
        events = svc.get_trend(args.student, args.topic, args.subject)
        if not events:
            print(f"{args.student} 在「{args.topic}」下没有学习记录。")
            return

        print(f"\n{args.topic} · 学习趋势")
        print("\u2500" * 50)
        for e in events:
            icons = {"录入": "\U0001f4c5", "复习": "\U0001f504", "掌握度验证": "\u2705", "已掌握": "\U0001f389"}
            icon = icons.get(e["type"], "\U0001f4cb")
            print(f"{icon} {e['date']}  {e['type']}：{e['detail']}")

        # 汇总
        total = sum(1 for e in events if e["type"] == "录入")
        mastered_events = [e for e in events if e["type"] == "已掌握"]
        mastered_now = "已掌握" if mastered_events else "未掌握"
        print(f"\n\U0001f4ca 汇总：共 {total} 条错题 | 掌握状态：{mastered_now}")
    except ValueError as e:
        print(f"\u274c {e}")
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mkt",
        description="错题整理系统 — 记录、分析、复习错题",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = sub.add_parser("add", help="录入错题")
    p_add.add_argument("--student", required=True)
    p_add.add_argument("--subject", required=True)
    p_add.add_argument("--grade", required=True)
    p_add.add_argument("--topic", required=True)
    p_add.add_argument("--question", required=True)
    p_add.add_argument("--wrong", required=True)
    p_add.add_argument("--correct", required=True)
    p_add.add_argument("--reason", required=True)

    # add-raw (Sprint 3)
    p_add_raw = sub.add_parser("add-raw", help="从 MD 文件批量导入错题")
    p_add_raw.add_argument("file", help="MD 文件路径")
    p_add_raw.add_argument("--student", required=True)
    p_add_raw.add_argument("--subject", default="数学")
    p_add_raw.add_argument("--grade", default="五年级上")
    p_add_raw.add_argument("--confirm", action="store_true", help="跳过确认直接录入")

    # list
    p_list = sub.add_parser("list", help="查询错题")
    p_list.add_argument("--student", required=True)
    p_list.add_argument("--subject")
    p_list.add_argument("--topic")
    p_list.add_argument("--status")
    p_list.add_argument("--grade")

    # show
    p_show = sub.add_parser("show", help="查看错题详情")
    p_show.add_argument("--id", required=True)

    # review (Slice 2)
    p_review = sub.add_parser("review", help="触发复习会话")
    p_review.add_argument("--student", required=True)
    p_review.add_argument("--topic", required=True)
    p_review.add_argument("--subject", default="数学")

    # check (Slice 2)
    p_check = sub.add_parser("check", help="判题")
    p_check.add_argument("--id", required=True)
    p_check.add_argument("--correct", action="store_true")
    p_check.add_argument("--wrong", action="store_true")

    # profile (Slice 2)
    p_profile = sub.add_parser("profile", help="查看学生画像")
    p_profile.add_argument("--student", required=True)

    # recall (Sprint 3)
    p_recall = sub.add_parser("recall", help="根因探究 — 分析已掌握知识点再次出错的原因")
    p_recall.add_argument("--student", required=True)
    p_recall.add_argument("--topic", required=True)
    p_recall.add_argument("--subject", default="数学")

    # verify (Sprint 3)
    p_verify = sub.add_parser("verify", help="掌握度验证 — 生成 5 道间隔测试题")
    p_verify.add_argument("--student", required=True)
    p_verify.add_argument("--topic", required=True)
    p_verify.add_argument("--subject", default="数学")

    # recommend (Sprint 4)
    p_rec = sub.add_parser("recommend", help="智能推荐复习内容")
    p_rec.add_argument("--student", required=True)
    p_rec.add_argument("--subject")

    # dashboard (Sprint 4)
    p_dash = sub.add_parser("dashboard", help="学习概览")
    p_dash.add_argument("--student", required=True)

    # trend (Sprint 4)
    p_trend = sub.add_parser("trend", help="知识点学习趋势")
    p_trend.add_argument("--student", required=True)
    p_trend.add_argument("--topic", required=True)
    p_trend.add_argument("--subject", default="数学")

    # mastery-result (Sprint 3)
    p_mr = sub.add_parser("mastery-result", help="查看掌握度验证结果")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    svc = MistakeService()

    handlers = {
        "add": cmd_add,
        "add-raw": cmd_add_raw,
        "list": cmd_list,
        "show": cmd_show,
        "review": cmd_review,
        "check": cmd_check,
        "profile": cmd_profile,
        "recall": cmd_recall,
        "recommend": cmd_recommend,
        "dashboard": cmd_dashboard,
        "trend": cmd_trend,
        "verify": cmd_verify,
        "mastery-result": cmd_mastery_result,
    }

    handler = handlers.get(args.command)
    if handler:
        handler(args, svc)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
