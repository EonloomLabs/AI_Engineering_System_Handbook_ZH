"""Check a fully extracted textbook without third-party Python packages.
Run: python3 design/check_local_links.py
Scope: static href/src targets and HTML id anchors, not browser behavior.
"""
from __future__ import annotations
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json

class Page(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: Counter[str] = Counter()
        self.links: list[str] = []
        self.feed(text)
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if a.get("id"):
            self.ids[str(a["id"])] += 1
        for name in ("href", "src"):
            if a.get(name):
                self.links.append(str(a[name]))
    handle_startendtag = handle_starttag

def main() -> int:
    root = Path(__file__).resolve().parent.parent
    pages = {p.resolve(): Page(p.read_text(encoding="utf-8")) for p in root.rglob("*.html")}
    errors: list[dict[str, str]] = []
    checked = 0
    for path, doc in pages.items():
        for ident, count in doc.ids.items():
            if count > 1:
                errors.append({"file": str(path.relative_to(root)), "duplicate_id": ident})
        for value in doc.links:
            u = urlsplit(value)
            if u.scheme or u.netloc:
                continue
            checked += 1
            target = (path.parent / unquote(u.path)).resolve() if u.path else path
            reason = "missing_file" if not target.exists() else None
            if not reason and u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
                reason = "missing_anchor"
            if reason:
                errors.append({"file": str(path.relative_to(root)), "link": value, "reason": reason})
    report = {"html_pages": len(pages), "local_references": checked, "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
