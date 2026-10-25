#!/usr/bin/env python3
"""Unify visible course numbering without changing stable paths or anchors.

Run only after all content edits are complete.  The script reads those final
canonical HTML pages, stages all changes in memory, and then writes them.  It
does not build complete.html, search-data.js, or wiki; rebuild those derivatives
after this script.  A second execution is refused to prevent remapping Q labels.

Dependencies: beautifulsoup4, lxml.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup, Comment


REVISION = "2026-10-24-unified-reading-order"
IGNORE_TEXT_IN = ("script", "style", "pre", "code", "textarea")

# These old chapter numbers came from several merged books.  They therefore
# cannot be replaced by one numeric old-chapter -> new-lesson dictionary.
# Each exact phrase below is scoped to its canonical page and checked once.
SEMANTIC_REFS = {
    "chapters/09.html": [
        ("完整验证链在第22章展开", "完整验证链在第06课展开"),
    ],
    "chapters/22.html": [
        ("第27章已实测其中的陈旧验证拒绝", "第67课保留了其中陈旧验证拒绝的既有实验记录"),
    ],
    "chapters/10.html": [
        ("这与第07章教学解析器的边界一致", "这与本课教学解析器的边界一致"),
    ],
    "chapters/13.html": [
        ("第07章已证明：", "后续第60课会进一步解释："),
        ("第12章给出压缩盈亏的计算方法", "第24课给出压缩盈亏的计算方法"),
        ("第06章区分了KV状态与服务计费缓存", "第60课进一步区分KV状态与服务计费缓存"),
    ],
    "chapters/16.html": [
        ("第12章强调过，结构通过不等于语义通过", "第24课还会结合压缩验证说明，结构通过不等于语义通过"),
        ("第15章有效时间与知晓时间帮助区分这些需求", "第25课的有效时间与知晓时间帮助区分这些需求"),
    ],
    "chapters/18.html": [
        ("本书第15章的双时间与冲突模型", "本课的双时间与冲突模型"),
    ],
    "chapters/24.html": [
        ("第08章的unknown状态", "第27课的unknown状态"),
    ],
    "chapters/23.html": [
        ("第12章因此使用约束与继续执行测试", "第24课因此使用约束与继续执行测试"),
    ],
    "chapters/25.html": [
        ("第08章动作日志", "第27课的动作日志"),
    ],
    "foundations/02.html": [
        ("系统机制第04章", "第55课的系统机制"),
    ],
    "chapters/01.html": [
        ("见第07章", "见第09课"),
    ],
    "foundations/15.html": [
        ("系统机制第04章", "第55课的系统机制"),
    ],
    "chapters/04.html": [
        ("第08章继续拆解推理侧的并行", "第63课继续拆解推理侧的并行"),
        ("第06章将从roofline和带宽继续解释这些取舍", "第62—63课将从Roofline和带宽继续解释这些取舍"),
    ],
    "chapters/05.html": [
        (
            "第03章解释分布式约束，第06章解释计算/带宽，第31章进一步讨论梯度与门控边界",
            "第55课补充训练、反向传播与并行约束，第62—63课解释计算、带宽与服务调度",
        ),
    ],
    "chapters/06.html": [
        ("第19章使用按任务配对的统计方法", "第32课使用按任务配对的统计方法"),
        ("第07章给出截断SSE的真实解析测试", "第09课给出截断SSE的解析测试与既有记录"),
        (
            "第04章讲学习目标，第07—08章讲协议与执行",
            "第55—56课讲训练与后训练目标，第09课讲协议，第27课讲可靠执行",
        ),
    ],
    "chapters/08.html": [
        ("第07章例子", "第60课的例子"),
    ],
    "chapters/27.html": [
        ("第08章unknown与对账思想", "第27课的unknown与对账思想"),
    ],
    "chapters/26.html": [
        ("第13、15、20章分别提供检索、生命周期与安全基础", "第19—20课、第25课和第29—30课分别提供检索、记忆生命周期与安全基础"),
    ],
    "chapters/28.html": [
        ("专题第01—06章解释共通机制", "第35—63课解释模型输入、前向、训练、推理与服务等共通机制"),
        ("第02章的GQA公式", "第51课的GQA缓存公式"),
    ],
    "labs.html": [
        (
            "这些文件对应基础课F01—F21与系统机制第01—08章",
            "这些文件对应第35—63课的模型输入、前向、训练、推理与服务机制",
        ),
    ],
    "sources.html": [
        (
            "F01—F40与系统机制01—28的既有页面保留；编号是稳定的查找标识，不再充当首读顺序。五阶段目录、单元内顺序和“下一节”是一致的。",
            "40节基础讲解与28节系统机制已经按首读顺序统一为第01—68课；18个单元和5个作业沿用同一条主线。目录、标题、正文引用和“下一课”使用一致的可见编号，既有文件路径与书签链接继续有效。",
        ),
    ],
    "studies/code/attention_gradients.html": [
        ("对应第31章", "对应第55课"),
    ],
    "studies/code/capstone.html": [
        ("对应第18、27章", "对应第06、67课"),
    ],
    "studies/code/context_memory.html": [
        ("对应第11、12、15章", "对应第12、24—25课"),
    ],
    "studies/code/journal.html": [
        ("对应第08、20、21章", "对应第27、30、34课"),
    ],
    "studies/code/live_readonly.html": [
        ("对应第07、08章", "对应第09、27课"),
    ],
    "studies/code/numerics.html": [
        ("对应第01、02、04、05、06章", "对应第41、50—51、56、59—63课"),
    ],
    "studies/code/retrieval.html": [
        ("对应第13、14章", "对应第19—21课"),
    ],
    "studies/code/sse_protocol.html": [
        ("对应第07章", "对应第09课"),
    ],
    "studies/code/statistics_lab.html": [
        ("对应第19章", "对应第32课"),
    ],
    "studies/code/train_tiny_lm.html": [
        ("对应第03章", "对应第55课"),
    ],
}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="AI_Systems_Engineering_Textbook_ZH directory")
    ap.add_argument("--dry-run", action="store_true", help="validate and report without writing")
    args = ap.parse_args()
    root = args.root.resolve()
    curriculum = json.loads((root / "editorial/curriculum.json").read_text())
    if curriculum.get("numbering_revision") == REVISION:
        raise SystemExit("This numbering revision is already applied. Refusing to remap visible Q labels twice.")
    canonical = json.loads((root / "editorial/canonical-pages.json").read_text())
    sequence = curriculum["sequence"]
    lesson_paths = [p for p in sequence if p.startswith(("foundations/", "chapters/"))]
    assert len(lesson_paths) == len(set(lesson_paths)) == 68
    assert len(curriculum["units"]) == 18
    assert len(curriculum["assignment_pages"]) == 5
    lessons = {p: i for i, p in enumerate(lesson_paths, 1)}
    foundations = {f"F{Path(p).stem}": lessons[p] for p in lessons if p.startswith("foundations/")}
    old_titles = {e["path"]: e["title"] for e in canonical}
    new_titles = dict(old_titles)
    bare_titles = {}
    for p, n in lessons.items():
        bare = re.sub(r"^(?:F\d{2}|\d{2})[｜|]\s*", "", old_titles[p])
        bare_titles[p] = bare
        new_titles[p] = f"第{n:02d}课｜{bare}"
    assignments = {p: int(n) for n, p in curriculum["assignment_pages"].items()}
    for p, n in assignments.items():
        bare = re.sub(r"^(.+?)作业：", r"\1：", old_titles[p])
        bare_titles[p] = bare
        new_titles[p] = f"作业{n:02d}｜{bare}"
    pages = {e["path"]: BeautifulSoup((root / e["path"]).read_text(), "lxml") for e in canonical}
    stable_ids_before = {p: Counter(t["id"] for t in soup.find_all(id=True)) for p, soup in pages.items()}
    data_questions_before = {p: Counter(t["data-question"] for t in soup.select("[data-question]")) for p, soup in pages.items()}
    question_rows = []
    for p in lesson_paths:
        for h in pages[p].select("article.article h2[id]"):
            if re.fullmatch(r"Q\d{3}", h["id"]):
                question_rows.append({"path": p, "lesson": lessons[p], "stable_id": h["id"], "old_label": h["id"], "label": f"Q{len(question_rows)+1:03d}", "title_before": h.get_text(" ", strip=True)})
    assert len(question_rows) == len({q["stable_id"] for q in question_rows}) == 112
    questions = {q["stable_id"]: q["label"] for q in question_rows}
    source_titles = sorted(((old_titles[p], title) for p, title in new_titles.items() if title != old_titles[p]), key=lambda t: -len(t[0]))
    report = {"revision": REVISION, "lessons": 68, "units": 18, "assignments": 5, "questions": 112, "answers_opened": 0, "forward_prerequisites_reclassified": [], "semantic_references": [], "semantic_rules_not_found": [], "unresolved_visible_chapter_references": [], "files_changed": []}

    def resolved(page: str, href: str):
        u = urlsplit(href)
        if u.scheme or u.netloc:
            return None
        try:
            path = (((root / page).parent / unquote(u.path)) if u.path else root / page).resolve().relative_to(root).as_posix()
        except ValueError:
            return None
        return path, unquote(u.fragment)

    def lesson_range(values):
        values = sorted(set(values))
        groups = []
        for n in values:
            if groups and groups[-1][-1] + 1 == n:
                groups[-1].append(n)
            else:
                groups.append([n])
        return "第" + "、".join(f"{g[0]:02d}" if len(g) == 1 else f"{g[0]:02d}—{g[-1]:02d}" for g in groups) + "课"

    def display_text(text: str) -> str:
        for old, new in source_titles:
            text = text.replace(old, new)
        def frange(m):
            lo, hi = int(m[1]), int(m[2])
            if not 1 <= lo <= hi <= 40:
                return m[0]
            return lesson_range(foundations[f"F{i:02d}"] for i in range(lo, hi + 1))
        text = re.sub(r"\bF(\d{2})\s*[—–-]\s*F?(\d{2})(?!\d)", frange, text)
        text = re.sub(r"(?<![A-Za-z0-9_])F\d{2}(?!\d)", lambda m: f"第{foundations[m[0]]:02d}课" if m[0] in foundations else m[0], text)
        text = re.sub(r"(?<![A-Za-z0-9_])Q\d{3}(?!\d)", lambda m: questions.get(m[0], m[0]), text)
        text = re.sub(r"单元\s*0?(\d{1,2})(?!\d)", lambda m: f"单元{int(m[1]):02d}", text)
        text = re.sub(r"阶段\s*0?([1-5])(?!\d)", lambda m: f"阶段{int(m[1]):02d}", text)
        text = re.sub(r"实践作业\s*0?([1-5])(?!\d)", lambda m: f"作业{int(m[1]):02d}", text)
        return text.replace("自检答案默认收起", "自检答案默认展开，可按需收起").replace("练习答案默认隐藏", "练习答案默认展开，可按需收起").replace("答案默认收起", "答案默认展开，可按需收起")

    for page, soup in pages.items():
        article = soup.select_one("article.article")
        assert article, page
        # Apply ambiguous references before the generic visible F/Q relabelling.
        for old, new in SEMANTIC_REFS.get(page, []):
            found = 0
            for t in list(article.find_all(string=True)):
                if isinstance(t, Comment) or t.find_parent(IGNORE_TEXT_IN):
                    continue
                if old in str(t):
                    found += str(t).count(old)
                    t.replace_with(str(t).replace(old, new))
            if found:
                report["semantic_references"].append({"path": page, "old": old, "new": new, "count": found})
            else:
                report["semantic_rules_not_found"].append({"path": page, "old": old})
        # Remove four orphaned section numbers inherited from an earlier order.
        if page == "chapters/01.html":
            for h in article.select("h4"):
                if re.match(r"5\.[1-4]\s", h.get_text(" ", strip=True)):
                    h.string = re.sub(r"^5\.[1-4]\s+", "", h.get_text(" ", strip=True))

        # Forward links are useful, but cannot be called required pre-reading.
        prerequisite = next((h for h in article.select("h3") if h.get_text(strip=True) == "本章预备知识"), None)
        if prerequisite is not None and page in lessons:
            panel = prerequisite.parent
            row = panel.select_one(".pillrow")
            if row:
                earlier, later = [], []
                for a in list(row.select("a[href]")):
                    target = resolved(page, a["href"])
                    if target and target[0] in lessons and lessons[target[0]] > lessons[page]:
                        later.append(a.extract())
                        report["forward_prerequisites_reclassified"].append({"path": page, "lesson": lessons[page], "target": target[0], "target_lesson": lessons[target[0]]})
                    else:
                        earlier.append(a.extract())
                block = soup.new_tag("div", attrs={"class": "course-reading-links"})
                for label, links in [("已学回顾", earlier), ("后续深入（首次阅读无需跳读）", later)]:
                    if not links:
                        continue
                    p = soup.new_tag("p", attrs={"class": "small"})
                    strong = soup.new_tag("strong")
                    strong.string = label
                    p.append(strong)
                    block.append(p)
                    new_row = soup.new_tag("div", attrs={"class": "pillrow"})
                    for a in links:
                        new_row.append(a)
                    block.append(new_row)
                row.replace_with(block)
                prerequisite.string = "本课准备与后续联系"
                for p in panel.find_all("p", recursive=False):
                    if "本章各题列出所需基础" in p.get_text():
                        p.string = "先用下面的小检查确认当前所需概念。已学回顾帮助复习；后续深入按主线在对应课次展开，不要求现在提前完成。" if later else "先用下面的小检查确认当前所需概念；已学回顾链接可用于查漏补缺。"

        # Rewrite text, labels and tooltips, never stable IDs or program literals.
        for t in list(soup.find_all(string=True)):
            if isinstance(t, Comment) or t.find_parent(IGNORE_TEXT_IN):
                continue
            original = str(t)
            changed = display_text(original)
            if changed != original:
                t.replace_with(changed)
        for tag in soup.find_all(True):
            for attr in ("title", "aria-label", "placeholder"):
                if tag.get(attr):
                    tag[attr] = display_text(str(tag[attr]))

        if page in lessons or page in assignments:
            h1 = article.find("h1")
            assert h1, page
            h1.string = new_titles[page]
            soup.head.title.string = new_titles[page] + " — AI系统工程"

        for a in soup.select("a[data-target]"):
            target = a.get("data-target")
            if target not in new_titles:
                continue
            a["title"] = new_titles[target]
            code = a.select_one(".rail-code")
            name = a.select_one(".rail-name")
            if target in lessons:
                if code:
                    code.string = f"第{lessons[target]:02d}课"
                if name:
                    name.string = bare_titles[target]
            elif target in assignments:
                if code:
                    code.string = f"作业{assignments[target]:02d}"
                if name:
                    name.string = bare_titles[target]

        # Explicit number in the pager makes its position unambiguous.
        for a in soup.select(".pager a[href]"):
            target = resolved(page, a["href"])
            if target and target[0] in new_titles:
                direction = "上一课" if "上一" in a.get_text() else "下一课"
                a.clear()
                a.append(direction)
                a.append(soup.new_tag("br"))
                a.append(new_titles[target[0]])

        for answer in article.select("details.quiz-answer"):
            answer["open"] = ""
            report["answers_opened"] += 1
            summary = answer.find("summary", recursive=False)
            if summary:
                for t in list(summary.find_all(string=True)):
                    val = str(t).replace("查看自检参考答案", "自检参考答案").replace("查看参考答案", "参考答案")
                    if val != str(t):
                        t.replace_with(val)

        for t in article.find_all(string=True):
            if isinstance(t, Comment) or t.find_parent(IGNORE_TEXT_IN):
                continue
            # A source repository's chapter is a source locator, not our lesson.
            current_reference_text = re.sub(r"(?:Dive(?: into LLMs)?|DIVE|dive-into-llms)\s*第[\d、，—–－\s-]+章", "", str(t))
            if re.search(r"第[\d、，—–－\s-]+章", current_reference_text):
                report["unresolved_visible_chapter_references"].append({"path": page, "text": str(t)})

    assert not report["unresolved_visible_chapter_references"], json.dumps(report["unresolved_visible_chapter_references"], ensure_ascii=False)
    # New paragraphs may change the counts; an omitted baseline answer is not OK.
    assert report["answers_opened"] >= 182
    assert len(report["forward_prerequisites_reclassified"]) == 35
    for p, soup in pages.items():
        assert Counter(t["id"] for t in soup.find_all(id=True)) == stable_ids_before[p], f"Stable ids changed in {p}"
        assert Counter(t["data-question"] for t in soup.select("[data-question]")) == data_questions_before[p], f"Stable question keys changed in {p}"
        if p in lessons or p in assignments:
            assert soup.select_one("article.article h1").get_text(" ", strip=True) == new_titles[p]
    for q in question_rows:
        actual = pages[q["path"]].find("h2", id=q["stable_id"]).get_text(" ", strip=True)
        assert actual.startswith(q["label"] + "｜"), (q, actual)

    updates = {page: str(soup) for page, soup in pages.items()}
    for e in canonical:
        e["title"] = new_titles[e["path"]]
    curriculum["revision_date"] = "2026-10-24"
    curriculum["numbering_revision"] = REVISION
    curriculum["lesson_numbers"] = lessons
    curriculum["visible_numbering"] = {"lessons": "第01—68课，按sequence顺序", "units": "单元01—18", "assignments": "作业01—05", "questions": "Q001—Q112，按课次和页内顺序；内部锚点保持兼容"}
    for u in curriculum["units"]:
        u["display_number"] = f"{u['unit']:02d}"
    mapping = {"revision": REVISION, "lessons": [{"path": p, "lesson": lessons[p], "old_title": old_titles[p], "title": new_titles[p]} for p in lesson_paths], "questions": question_rows, "stable_paths_and_ids_preserved": True, "note": "可见课号与题号按当前主线重排；旧路径、HTML锚点、data-question与历史实验数据键保留。"}
    updates["editorial/canonical-pages.json"] = json.dumps(canonical, ensure_ascii=False, indent=2) + "\n"
    updates["editorial/curriculum.json"] = json.dumps(curriculum, ensure_ascii=False, indent=2) + "\n"
    updates["editorial/numbering-map.json"] = json.dumps(mapping, ensure_ascii=False, indent=2) + "\n"
    updates["assets/catalog.js"] = "window.BOOK_CATALOG=" + json.dumps(canonical, ensure_ascii=False) + ";\n"
    updates["llms.txt"] = "# AI系统工程\n\n课程只有一条从外到内的主流程，参考代码与来源不构成并行章节。课号、题号按当前阅读顺序统一。\n\n" + "".join(f"- [{new_titles[p]}]({p})\n" for p in sequence)
    readme = (root / "README.txt").read_text()
    readme = display_text(readme)
    readme += "\n课程编号：第01—68课、单元01—18、作业01—05、Q001—Q112；按主线顺序阅读。正文答案默认展开，可手动收起。\n"
    updates["README.txt"] = readme
    style = (root / "assets/style.css").read_text()
    updates["assets/style.css"] = style.replace("自检题：答案默认收起，读者主动展开", "自检题：答案默认展开，读者可主动收起")
    app = (root / "assets/app.js").read_text()
    updates["assets/app.js"] = app.replace("例如：张量、F05、Q025、unknown", "例如：张量、第39课、Q001、unknown")

    # This is a requirement change, so the old 'answers hidden' gate is obsolete.
    test_path = "validation/test_progression.py"
    tests = (root / test_path).read_text()
    old_gate = re.compile(r" def test_answers_hidden\(self\):\n.*?(?= def test_no_old_images\(self\):)", re.S)
    new_gate = ''' def test_answers_open(self):
  class Parser(HTMLParser):
   def __init__(self):super().__init__();self.bad=[];self.answers=0
   def handle_starttag(self,t,attrs):
    a=dict(attrs)
    if t=='details' and 'quiz-answer' in a.get('class',''):
     self.answers+=1
     if 'open' not in a:self.bad.append(a)
  total=0
  for e in json.loads((R/'editorial/canonical-pages.json').read_text()):
   p=R/e['path'];s=Parser();s.feed(p.read_text());total+=s.answers
   self.assertFalse(s.bad,e['path'])
  self.assertGreater(total,0)
'''
    tests, changes = old_gate.subn(lambda _: new_gate, tests)
    assert changes == 1, "The previous answer visibility gate was not found exactly once."
    updates[test_path] = tests
    report["files_changed"] = sorted(updates)
    report["requires_follow_up_build"] = ["assets/search-data.js", "complete.html (including rail, inline catalog and CSS/JS)", "wiki Markdown", "new package verification record"]
    updates["editorial/numbering-update.json"] = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    print(json.dumps({k: v if k not in ("forward_prerequisites_reclassified", "semantic_references", "files_changed") else len(v) for k, v in report.items()}, ensure_ascii=False, indent=2))
    if args.dry_run:
        print("Dry run complete: no course files written.")
        return
    for relative, contents in updates.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + ".numbering-tmp")
        temporary.write_text(contents, encoding="utf-8")
        temporary.replace(path)
    print("Visible numbering updated. Rebuild derived artifacts next.")


if __name__ == "__main__":
    main()
