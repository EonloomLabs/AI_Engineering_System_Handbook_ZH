
"""Synchronize edited independent pages into local search, Markdown and a standalone book.
No network; no edits to the model, experiment data, or chapter sequence."""
from pathlib import Path
from bs4 import BeautifulSoup
import json, posixpath, hashlib, base64, mimetypes, copy, re, sys
import markdownify
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT.parents[1]/"source"/ROOT.name
CAT=json.loads((ROOT/"editorial/canonical-pages.json").read_text())
PAGES={x["path"]:x for x in CAT}

def source_page(path):return BeautifulSoup((ROOT/path).read_text(encoding="utf-8"),"lxml")
def normalize_svg(s):
    for a,b in [("viewbox=","viewBox="),("preserveaspectratio=","preserveAspectRatio="),
                ("markerwidth=","markerWidth="),("markerheight=","markerHeight="),
                ("refx=","refX="),("refy=","refY=")]:
        s=s.replace(a,b)
    return s
def resolve_path(src,href):
    from urllib.parse import urlsplit,unquote
    u=urlsplit(href)
    if u.scheme or u.netloc or href.startswith("//"):return None
    target=posixpath.normpath(posixpath.join(posixpath.dirname(src),unquote(u.path))) if u.path else src
    return target,unquote(u.fragment)
def searchable(art):
    n=copy.deepcopy(art)
    for e in n.select("script,style,svg,button,nav,details.quiz-answer,.mobile-outline,.reading-meta,.progress-row,.breadcrumb,.d-caption .d-source-note"):
        e.decompose()
    return n
# Normalize structure and independent-page metadata, then build clean search excerpts.
if "--only-complete" not in sys.argv:
    search=[]
    for rec in CAT:
        path=rec["path"];sp=source_page(path)
        for e in sp.select("p.d-source-note"):
            # Keep paragraph children valid rather than a nested <p>.
            if e.find(["p","div"]):e.name="div"
        for d in sp.select("details.quiz-answer"):d.attrs.pop("open",None)
        for h in sp.select("h1,h2,h3,h4,h5,h6"):
            for figure in h.find_all("figure",recursive=False):
                h.insert_after(figure.extract())
        art=sp.select_one("main article") or sp.select_one("article")
        if not art:continue
        for toc in sp.select(".mobile-outline nav, nav.toc"):
            for link in toc.select("a[href^='#']"):
                head=sp.find(id=link["href"][1:])
                if head and re.fullmatch("h[1-6]",head.name or ""):
                    clean=copy.deepcopy(head)
                    for fig in clean.select("figure,button"):fig.decompose()
                    title=clean.get_text(" ",strip=True)
                    if title:link.string=title
        for count in sp.select(".reading-meta span"):
            if re.search(r"\d+\s*组分步图解",count.get_text()):
                n=len(sp.select(".vb-player"))
                count.string=f"{n} 组可控演示" if n else "图表与逐项说明"
        (ROOT/path).write_text(normalize_svg(str(sp)),encoding="utf-8")
        clean=searchable(art)
        search.append(dict(id=rec["id"],path=path,title=rec["title"],kind=rec["kind"],
                           text=clean.get_text(" ",strip=True)[:22000]))
        headings=clean.find_all(["h2","h3"])
        for h in headings:
            if not h.get("id"):continue
            title=h.get_text(" ",strip=True)
            if not title or len(title)>200:continue
            parts=[title]
            # Following siblings at the local level; a hit always lands at a concrete section.
            for sibling in h.next_siblings:
                if getattr(sibling,"name",None) in ("h1","h2","h3"):break
                if hasattr(sibling,"get_text"):parts.append(sibling.get_text(" ",strip=True))
                elif str(sibling).strip():parts.append(str(sibling).strip())
            text=" ".join(parts)
            if len(text)>60:
                search.append(dict(id=rec["id"]+"--"+h["id"],path=path+"#"+h["id"],title=title,
                                   kind=rec["kind"],text=text[:16000]))
    (ROOT/"assets/search-data.js").write_text("window.COURSE_SEARCH="+json.dumps(search,ensure_ascii=False,separators=(",",":"))+";",encoding="utf-8")

    print("Search rebuilt", len(search), flush=True)
    # Markdown: meaningful diagrams reference their own local SVG, not a duplicated screenshot.
    svg_dir=ROOT/"wiki/figures";svg_dir.mkdir(exist_ok=True)
    wiki_count=0
    for rec in CAT:
        path=rec["path"];sp=source_page(path);art=sp.select_one("main article") or sp.select_one("article")
        if not art:continue
        art=copy.deepcopy(art)
        mdfile=ROOT/"wiki"/Path(path).with_suffix(".md")
        mdfile.parent.mkdir(parents=True,exist_ok=True)
        for e in art.select("script,style,nav,.mobile-outline,.progress-row,.reading-meta,.breadcrumb,button"):
            e.decompose()
        anchor_placeholders={}
        for j,el in enumerate(art.select("[id]")):
            if el.name=="svg" or el.find_parent("svg") or el.find_parent("details",class_="quiz-answer"):
                continue
            token=f"WIKIPRESERVEDANCHOR{j:05d}END"
            anchor_placeholders[token]='<span id="'+str(el["id"])+'"></span>'
            el.insert_before(token)
        details={}
        for j,d in enumerate(art.select("details.quiz-answer")):
            token=f"WIKIHIDDENANSWER{j:04d}END"
            details[token]=str(d)
            d.replace_with(token)
        for sv in art.find_all("svg"):
            raw=normalize_svg(str(sv));key=hashlib.sha256(raw.encode()).hexdigest()[:16]
            target=svg_dir/(key+".svg");target.write_text(raw,encoding="utf-8")
            img=sp.new_tag("img");img["src"]=posixpath.relpath(target.relative_to(ROOT).as_posix(),mdfile.parent.relative_to(ROOT).as_posix())
            img["alt"]=sv.get("aria-label") or (sv.title.get_text() if sv.title else "技术图解")
            sv.replace_with(img)
        for a in art.find_all("a",href=True):
            resolved=resolve_path(path,a["href"])
            if resolved:
                target,frag=resolved
                if target in PAGES:dest=(ROOT/"wiki"/Path(target).with_suffix(".md"))
                else:dest=ROOT/target
                a["href"]=posixpath.relpath(dest.relative_to(ROOT).as_posix(),mdfile.parent.relative_to(ROOT).as_posix())+("#"+frag if frag else "")
        text=markdownify.markdownify(str(art),heading_style="ATX",bullets="-")
        for token,anchor in anchor_placeholders.items():
            text=text.replace(token,"\n"+anchor+"\n")
        for token,raw in details.items():
            # Links in raw answers resolve from the actual Markdown page.
            ds=BeautifulSoup(raw,"lxml")
            for a in ds.find_all("a",href=True):
                r=resolve_path(path,a["href"])
                if r:
                    target,frag=r;dest=ROOT/"wiki"/Path(target).with_suffix(".md") if target in PAGES else ROOT/target
                    a["href"]=posixpath.relpath(dest.relative_to(ROOT).as_posix(),mdfile.parent.relative_to(ROOT).as_posix())+("#"+frag if frag else "")
            text=text.replace(token,str(ds.body.decode_contents()))
        mdfile.write_text("---\ntitle: "+json.dumps(rec["title"],ensure_ascii=False)+"\ndescription: \"AI系统工程：本地教学正文与可追溯图表\"\n---\n\n"+text,encoding="utf-8")
        wiki_count+=1

    print("Markdown rebuilt", wiki_count, flush=True)
else:
    s=(ROOT/"assets/search-data.js").read_text()
    search=json.loads(s.split("=",1)[1].strip().rstrip(";"))
    wiki_count=len(CAT)
# Use the existing complete-reader shell. Rebuild only its teaching article.
full=BeautifulSoup((ROOT/"diagrams/reader-shell.template").read_text(encoding="utf-8"),"lxml")
article=full.select_one("main article")
article.clear()
h=full.new_tag("h1",id="book-start");h.string="AI系统工程：从基础到内部";article.append(h)
lead=full.new_tag("p");lead["class"]="lead";lead.string="沿基础课程与系统机制连续阅读：共通计算、训练和验证、训练后推理，再进入Agent与工程。图解解释关系，原生表格保留数据。";article.append(lead)
toc=full.new_tag("nav",id="book-toc");toc["class"]="toc";toc["aria-label"]="全书目录"
for r in CAT:
    a=full.new_tag("a",href="#"+r["id"]);a.string=r["title"];toc.append(a)
article.append(toc)
resources={}
def standalone_href(src,href):
    resolved=resolve_path(src,href)
    if not resolved:return href,None
    target,frag=resolved
    if target=="complete.html":return "#"+(frag or "book-start"),None
    if target in PAGES:
        return "#"+PAGES[target]["id"]+("--"+frag if frag else ""),None
    p=ROOT/target
    if p.is_file():
        key="resource--"+hashlib.sha256(target.encode()).hexdigest()[:12]
        resources[key]=(target,p)
        return "#"+key,None
    return href,"missing:"+target
missing=[]
for r in CAT:
    path=r["path"];slug=r["id"];sp=source_page(path);art=sp.select_one("main article") or sp.select_one("article")
    sec=full.new_tag("section",id=slug);sec["class"]="standalone-section";sec["data-book-page"]=path
    for child in list(art.children):sec.append(child.extract())
    # Remove per-page dialogs/shell bits, but preserve pedagogical collapses.
    for e in sec.select("script,style,.mobile-outline,.breadcrumb,.reading-meta"):e.decompose()
    ids={el["id"]:slug+"--"+el["id"] for el in sec.select("[id]")}
    for el in sec.select("[id]"):el["id"]=ids[el["id"]]
    for el in sec.find_all(True):
        for attr in ("aria-labelledby","aria-describedby","aria-controls","for","headers"):
            if el.has_attr(attr):el[attr]=" ".join(ids.get(t,t) for t in str(el[attr]).split())
        for attr in ("href","xlink:href"):
            if not el.has_attr(attr):continue
            original=el[attr]
            if original.startswith("#") and original[1:] in ids:el[attr]="#"+ids[original[1:]]
            else:
                el[attr],err=standalone_href(path,original)
                if err:missing.append((path,original,err))
        for attr in ("fill","stroke","filter","clip-path","mask","marker-end","marker-start","marker-mid","style"):
            if el.has_attr(attr):
                el[attr]=re.sub(r"url\(#([^)]+)\)",lambda m:"url(#"+ids.get(m.group(1),m.group(1))+")",el[attr])
        if el.name=="img" and el.get("src") and not el["src"].startswith("data:"):
            resolved=resolve_path(path,el["src"])
            if resolved and (ROOT/resolved[0]).is_file():
                p=ROOT/resolved[0];mime=mimetypes.guess_type(p.name)[0] or "application/octet-stream"
                el["src"]="data:"+mime+";base64,"+base64.b64encode(p.read_bytes()).decode()
    article.append(sec)
# Every non-HTML local source remains available inside the single file.
ressec=full.new_tag("section",id="embedded-resources");ressec["class"]="standalone-section"
h=full.new_tag("h1");h.string="本地源文件";ressec.append(h)
for key,(target,p) in resources.items():
    wrap=full.new_tag("section",id=key);h=full.new_tag("h2");h.string=target;wrap.append(h)
    raw=p.read_bytes();mime=mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    a=full.new_tag("a",href="data:"+mime+";base64,"+base64.b64encode(raw).decode());a["download"]=p.name;a.string="保存此源文件";wrap.append(a)
    if p.suffix.lower()==".svg":
        img=full.new_tag("img",src="data:image/svg+xml;base64,"+base64.b64encode(raw).decode());img["alt"]=p.stem;wrap.append(img)
    elif p.suffix.lower() in (".py",".json",".mmd",".txt",".md",".log",".js",".css"):
        detail=full.new_tag("details");summ=full.new_tag("summary");summ.string="查看完整源文件";detail.append(summ)
        pre=full.new_tag("pre");code=full.new_tag("code");code.string=raw.decode("utf-8",errors="replace");pre.append(code);detail.append(pre);wrap.append(detail)
    ressec.append(wrap)
article.append(ressec)
# Replace old data and preserve adapted complete-page reader logic.
for sc in full.find_all("script"):
    st=sc.string or sc.get_text()
    if st.startswith("window.COURSE_SEARCH"):
        values=copy.deepcopy(search)
        for x in values:
            x["path"]=standalone_href(x["path"].split("#")[0],x["path"] if not x["path"].startswith("#") else x["path"])[0] if False else (
                "#"+PAGES[x["path"].split("#")[0]]["id"]+("--"+x["path"].split("#",1)[1] if "#" in x["path"] else ""))
        sc.string="window.COURSE_SEARCH="+json.dumps(values,ensure_ascii=False,separators=(",",":"))+";"
    elif st.startswith("window.VISUAL_LESSONS"):
        sc.string=(ROOT/"assets/visual-data.js").read_text()
# New shared graph style and viewer; all existing reader scripts retained.
style=full.new_tag("style");style.string=(ROOT/"assets/diagrams.css").read_text();full.head.append(style)
sc=full.new_tag("script");sc.string=(ROOT/"assets/diagrams.js").read_text();full.body.append(sc)
# Eliminate external runtime dependencies; sources are explicit external links only.
for lk in full.select("link[rel=stylesheet]"):lk.decompose()
fulltext=normalize_svg(str(full))
(ROOT/"complete.html").write_text(fulltext,encoding="utf-8")
(ROOT/"diagrams/export-report.json").write_text(json.dumps({"pages":len(CAT),"markdown_pages":wiki_count,
 "search_entries":len(search),"embedded_resources":len(resources),"unresolved":missing,
 "standalone_bytes":len(fulltext.encode())},ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"pages":len(CAT),"markdown":wiki_count,"search":len(search),"resources":len(resources),"unresolved":missing[:10],"standalone_MiB":len(fulltext.encode())/2**20},ensure_ascii=False))
