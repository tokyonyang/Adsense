from __future__ import annotations

import asyncio
import html
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

KST = timezone(timedelta(hours=9))


def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def esc(value: Any) -> str:
    return html.escape(str(value or ""))


def domain(url: str | None) -> str:
    if not url:
        return "news"
    try:
        host = urlparse(url).netloc or urlparse(url).path
        return host.replace("www.", "")[:30] or "news"
    except Exception:
        return "news"


def slot_label(issue: dict[str, Any]) -> str:
    return str(issue.get("slot") or issue.get("category") or "주요").replace("·", "\n").replace("/", "\n")


def cat_color(category: str) -> tuple[str, str]:
    mapping = {
        "경제·금융": ("#f5b531", "#1a1f26"),
        "증권·투자": ("#f5b531", "#171d25"),
        "산업·기업": ("#f5b531", "#171d25"),
        "정책·지원금": ("#ff3131", "#151515"),
        "정책·생활": ("#ff3131", "#151515"),
        "시사·정치": ("#ff3131", "#151515"),
        "사회·사건": ("#ff3131", "#151515"),
        "국제": ("#59a9ff", "#101820"),
        "국제·안전": ("#59a9ff", "#101820"),
        "날씨·안전": ("#59a9ff", "#101820"),
        "생활·제도": ("#b7dec0", "#25362c"),
        "건강·의료": ("#b7dec0", "#25362c"),
        "교육·입시": ("#b7dec0", "#25362c"),
        "연예·문화": ("#b7dec0", "#25362c"),
        "스포츠": ("#b7dec0", "#25362c"),
    }
    return mapping.get(str(category), ("#f5b531", "#1a1f26"))


def base_css(width: int, height: int) -> str:
    return f"""
@font-face {{ font-family: NanumGothic; src: local('NanumGothic'); }}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  width: {width}px;
  height: {height}px;
  overflow: hidden;
  font-family: NanumGothic, 'Noto Sans CJK KR', 'Apple SD Gothic Neo', sans-serif;
  color: #fff;
  background:#050505;
}}
.page {{
  width:{width}px; height:{height}px; position:relative; overflow:hidden;
  background:
    radial-gradient(circle at 15% 10%, rgba(255,202,64,.20), transparent 26%),
    radial-gradient(circle at 85% 28%, rgba(255,80,60,.15), transparent 28%),
    linear-gradient(135deg, #20242a 0%, #0b0d10 48%, #050505 100%);
}}
.page::before {{
  content:""; position:absolute; inset:0;
  background-image:
    linear-gradient(rgba(255,255,255,.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px);
  background-size:42px 42px;
  opacity:.45;
}}
.bg-visual {{
  position:absolute; inset:0; overflow:hidden;
}}
.bg-visual .shape1 {{
  position:absolute; left:-80px; top:100px; width:680px; height:420px;
  background:linear-gradient(135deg, rgba(255,48,48,.78), rgba(255,177,49,.25));
  clip-path: polygon(0 15%, 70% 0, 100% 45%, 56% 70%, 70% 100%, 5% 82%);
  filter: drop-shadow(0 30px 50px rgba(0,0,0,.45));
  opacity:.72;
}}
.bg-visual .shape2 {{
  position:absolute; right:-140px; top:20px; width:620px; height:620px;
  border-radius:50%; background:radial-gradient(circle, rgba(255,209,84,.42), rgba(255,209,84,.06) 55%, transparent 70%);
  opacity:.75;
}}
.bg-visual .shape3 {{
  position:absolute; right:60px; top:160px; width:220px; height:220px;
  border:8px solid rgba(255,255,255,.16); border-radius:32px; transform:rotate(18deg);
}}
.bg-visual .zigzag {{
  position:absolute; left:80px; top:155px; font-size:190px; color:rgba(255,255,255,.18); font-weight:900; transform:rotate(-12deg);
}}
.cover-title {{
  position:absolute; left:66px; top:90px; right:80px;
  font-size:84px; line-height:1.05; font-weight:900; letter-spacing:-5px;
}}
.cover-sub {{ position:absolute; left:70px; top:300px; font-size:30px; color:#f5b531; letter-spacing:8px; }}
.cover-box {{
  position:absolute; left:60px; right:60px; bottom:140px; padding:34px;
  border:3px solid rgba(255,255,255,.75); background:rgba(0,0,0,.46);
}}
.cover-list {{ list-style:none; padding:0; margin:0; }}
.cover-list li {{ font-size:31px; line-height:1.45; margin:12px 0; }}
.ribbon {{
  position:absolute; top:0; right:60px; width:122px; min-height:204px;
  background:var(--accent); color:var(--dark); z-index:10;
  display:flex; flex-direction:column; align-items:center; justify-content:center;
  font-weight:900; text-align:center; padding:18px 10px;
}}
.ribbon .cat {{ font-size:34px; line-height:1.05; white-space:pre-line; letter-spacing:-2px; }}
.ribbon .line {{ width:70px; height:5px; background:var(--dark); margin:18px 0; }}
.ribbon .num {{ font-size:42px; letter-spacing:2px; }}
.poster-frame {{
  position:absolute; inset:28px; border:3px solid rgba(255,255,255,.65); z-index:2;
}}
.content {{
  position:absolute; left:66px; right:58px; bottom:50px; z-index:4;
}}
.quote {{
  font-size:168px; color:var(--accent); line-height:.5; font-family:Georgia, serif; opacity:.95; margin-left:-6px;
}}
.main-title {{
  margin-top:-26px; font-size:64px; line-height:1.16; font-weight:900; letter-spacing:-4px;
  text-shadow:0 4px 18px rgba(0,0,0,.55);
}}
.sub-title {{
  margin-top:26px; color:var(--accent); font-size:36px; line-height:1.26; font-weight:900; letter-spacing:-2px;
}}
.summary {{
  margin-top:18px; font-size:27px; line-height:1.43; color:#f2f2f2; letter-spacing:-1px;
}}
.summary div {{ margin:6px 0; }}
.insight {{
  margin-top:18px; border-left:5px solid var(--accent); padding-left:18px;
  font-size:28px; line-height:1.34; color:#fff; font-weight:800;
}}
.chart {{
  margin-top:20px; display:grid; grid-template-columns:1fr 300px; gap:18px; align-items:center;
  border:1px solid rgba(255,255,255,.25); background:rgba(0,0,0,.48); padding:14px 16px;
}}
.chart-title {{ color:var(--accent); font-size:22px; font-weight:900; }}
.chart-caption {{ margin-top:6px; font-size:20px; line-height:1.25; }}
.footer {{
  position:absolute; left:30px; right:30px; bottom:14px; z-index:5;
  display:flex; justify-content:space-between; font-size:20px; color:#f7f7f7; opacity:.95;
}}
.keyword-line {{ position:absolute; left:66px; right:58px; bottom:18px; z-index:4; font-size:19px; color:#f6f0d4; opacity:.95; }}
.summary-page .content {{ top:110px; bottom:auto; }}
"""


def page_shell(body: str, width: int, height: int) -> str:
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{base_css(width,height)}</style></head><body>{body}</body></html>"""


def visual_bg() -> str:
    return """
<div class="bg-visual">
  <div class="shape1"></div>
  <div class="shape2"></div>
  <div class="shape3"></div>
  <div class="zigzag">↘</div>
</div>
"""


def cover_page(issues: list[dict[str, Any]], total_pages: int, width: int, height: int) -> str:
    now = datetime.now(KST)
    top_html = "".join(f"<li>{i+1}. {esc(x.get('headline'))}</li>" for i, x in enumerate(issues[:5]))
    body = f"""
<main class="page">
  {visual_bg()}
  <div class="poster-frame"></div>
  <div class="cover-title">오늘의<br><span style="color:#f5b531;">헤드라인 뉴스</span></div>
  <div class="cover-sub">아침 브리핑 · {now:%Y.%m.%d} ({weekday_ko(now)})</div>
  <section class="cover-box">
    <ul class="cover-list">{top_html}</ul>
  </section>
  <div class="footer"><span>카카오톡 오픈채팅 “비티의 경제” 검색!</span><span>© 비티의 인사이트 노트</span></div>
</main>
"""
    return page_shell(body, width, height)


def chart_html(issue: dict[str, Any]) -> str:
    chart = issue.get("chart") or {}
    if not chart or not chart.get("available") or not chart.get("svg"):
        return ""
    return f"""
<section class="chart">
  <div>
    <div class="chart-title">관련 지표 · {esc(chart.get("title"))}</div>
    <div class="chart-caption">{esc(chart.get("caption"))}</div>
  </div>
  <div>{chart.get("svg")}</div>
</section>
"""


def issue_page(issue: dict[str, Any], page_index: int, total_pages: int, width: int, height: int) -> str:
    category = issue.get("category") or "주요"
    accent, dark = cat_color(category)
    ribbon = slot_label(issue)
    num = str(issue.get("rank", page_index - 1)).zfill(2)
    headline = esc(issue.get("headline"))
    anchor = esc(issue.get("anchor_title") or "")
    lines = [esc(x) for x in (issue.get("summary_lines") or [])[:3]]
    while len(lines) < 3:
        lines.append("")
    insight = esc(issue.get("insight") or "")
    keyword_line = " / ".join(str(k) for k in (issue.get("keywords") or [])[:4])
    source_line = " · ".join(domain(x.get("url")) for x in (issue.get("links") or [])[:3])
    chart_block = chart_html(issue)

    body = f"""
<main class="page" style="--accent:{accent};--dark:{dark};">
  {visual_bg()}
  <div class="poster-frame"></div>
  <aside class="ribbon">
    <div class="cat">{esc(ribbon)}</div>
    <div class="line"></div>
    <div class="num">{num}</div>
  </aside>
  <section class="content">
    <div class="quote">“</div>
    <div class="main-title">{headline}</div>
    <div class="sub-title">{anchor}</div>
    <div class="summary">
      <div>{lines[0]}</div>
      <div>{lines[1]}</div>
      <div>{lines[2]}</div>
    </div>
    {chart_block}
    <div class="insight">{insight}</div>
  </section>
  <div class="keyword-line">관련 키워드 · {esc(keyword_line)} &nbsp;&nbsp; | &nbsp;&nbsp; 출처 · {esc(source_line)}</div>
  <div class="footer"><span>카카오톡 오픈채팅 “비티의 경제” 검색!</span><span>© 비티의 인사이트 노트</span></div>
</main>
"""
    return page_shell(body, width, height)


def summary_page(issues: list[dict[str, Any]], page_index: int, total_pages: int, width: int, height: int) -> str:
    items = "".join(f"<li>{i+1}. {esc(x.get('headline'))}</li>" for i, x in enumerate(issues[:6]))
    body = f"""
<main class="page summary-page" style="--accent:#f5b531;--dark:#1a1f26;">
  {visual_bg()}
  <div class="poster-frame"></div>
  <section class="content">
    <div class="main-title">오늘의 흐름 요약</div>
    <div class="sub-title">중복 이슈를 제거하고 핵심 흐름만 남겼습니다</div>
    <ul class="cover-list" style="margin-top:42px;">{items}</ul>
    <div class="insight" style="margin-top:42px;">경제·금융, 증시, 산업, 정책 이슈를 중심으로 생활 영향과 시장 변수를 함께 점검하세요.</div>
  </section>
  <div class="footer"><span>카카오톡 오픈채팅 “비티의 경제” 검색!</span><span>© 비티의 인사이트 노트</span></div>
</main>
"""
    return page_shell(body, width, height)


async def render_html_to_png(html_content: str, output_path: Path, *, width: int, height: int, scale: int = 2) -> str:
    from playwright.async_api import async_playwright

    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = output_path.with_suffix(".html")
    html_path.write_text(html_content, encoding="utf-8")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=scale,
        )
        await page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        await page.screenshot(path=str(output_path), full_page=True, type="png")
        await browser.close()

    return str(output_path)


def build_cardnews_pages(issues: list[dict[str, Any]], *, output_dir: str | Path) -> list[str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    width = int(os.getenv("HEADLINE_IMAGE_WIDTH", "1080"))
    height = int(os.getenv("HEADLINE_IMAGE_HEIGHT", "1080"))
    scale = int(os.getenv("HEADLINE_IMAGE_SCALE", "2"))

    issues = issues[:5]
    total_pages = len(issues) + 2
    html_pages = [cover_page(issues, total_pages, width, height)]
    for idx, issue in enumerate(issues, start=2):
        html_pages.append(issue_page(issue, idx, total_pages, width, height))
    html_pages.append(summary_page(issues, total_pages, total_pages, width, height))

    async def run_all() -> list[str]:
        paths = []
        for i, html_content in enumerate(html_pages, start=1):
            out = output_dir / f"headline_cardnews_{i:02d}.png"
            await render_html_to_png(html_content, out, width=width, height=height, scale=scale)
            paths.append(str(out))
        return paths

    return asyncio.run(run_all())
