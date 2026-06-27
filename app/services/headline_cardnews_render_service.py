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


def normalize_category(category: str) -> str:
    category = str(category or "주요").strip()
    aliases = {
        "경제": "경제·금융",
        "증시": "증권·투자",
        "산업": "산업·기업",
        "정책": "정책·지원금",
        "생활": "생활·제도",
        "정치": "시사·정치",
        "사회": "사회·사건",
        "IT": "산업·기업",
    }
    return aliases.get(category, category)


def cat_color(category: str) -> str:
    category = normalize_category(category)
    return {
        "경제·금융": "#f4c542",
        "증권·투자": "#ff7a45",
        "산업·기업": "#ffb020",
        "정책·지원금": "#4d96ff",
        "부동산·주거금융": "#d6a64f",
        "생활·제도": "#00b8d9",
        "국제": "#a66bff",
        "시사·정치": "#4d96ff",
        "사회·사건": "#00c389",
        "날씨·안전": "#38bdf8",
        "건강·의료": "#22c55e",
        "교육·입시": "#f59e0b",
        "연예·문화": "#ec4899",
        "스포츠": "#22c55e",
        "기타": "#cbd5e1",
    }.get(category, "#f4c542")


def cat_icon(category: str) -> str:
    category = normalize_category(category)
    return {
        "경제·금융": "₩",
        "증권·투자": "↗",
        "산업·기업": "AI",
        "정책·지원금": "🏛",
        "부동산·주거금융": "🏠",
        "생활·제도": "☀",
        "국제": "🌐",
        "시사·정치": "🏛",
        "사회·사건": "⚖",
        "날씨·안전": "☔",
        "건강·의료": "＋",
        "교육·입시": "✎",
        "연예·문화": "★",
        "스포츠": "⚽",
        "기타": "•",
    }.get(category, "•")


def base_css() -> str:
    return """
@font-face { font-family: NanumGothic; src: local('NanumGothic'); }
* { box-sizing: border-box; }
body {
  margin: 0;
  width: 1080px;
  height: 1350px;
  overflow: hidden;
  font-family: NanumGothic, 'Noto Sans CJK KR', 'Apple SD Gothic Neo', sans-serif;
  color: #f7f7f7;
  background:
    radial-gradient(circle at 20% 4%, rgba(246,197,66,.18), transparent 25%),
    radial-gradient(circle at 88% 28%, rgba(255,122,69,.11), transparent 26%),
    linear-gradient(180deg, #050505 0%, #101010 45%, #050505 100%);
}
.page {
  width: 1080px;
  height: 1350px;
  position: relative;
  padding: 42px 46px 38px;
}
.page::before {
  content: "";
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,.026) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.026) 1px, transparent 1px);
  background-size: 44px 44px;
  opacity: .75;
  pointer-events: none;
}
.header {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 255px;
  align-items: start;
  margin-bottom: 36px;
}
.brand { display: flex; align-items: center; gap: 18px; }
.menu-icon {
  width: 74px; height: 74px; border: 3px solid #f4c542; border-radius: 17px;
  display: grid; place-items: center; color: #f4c542; font-size: 42px; font-weight: 900;
  box-shadow: 0 0 22px rgba(246,197,66,.18);
}
.title { font-size: 54px; line-height: 1; font-weight: 900; letter-spacing: -3px; }
.title .gold { color: #f4c542; text-shadow: 0 0 22px rgba(246,197,66,.23); }
.sub { margin-top: 12px; font-size: 22px; color: #f1d57b; letter-spacing: 7px; }
.date {
  justify-self: end; border: 2px solid #f4c542; border-radius: 17px; padding: 16px 20px;
  font-size: 25px; font-weight: 900; color: #fff1b8; text-align: center;
  box-shadow: inset 0 0 20px rgba(246,197,66,.07), 0 0 20px rgba(246,197,66,.13);
}
.page-no {
  position: absolute; top: 112px; left: 0; right: 0; text-align: center;
  font-size: 24px; color: #e9d38b; letter-spacing: 5px;
}
.page-no::before, .page-no::after {
  content: ""; display: inline-block; width: 135px; height: 1px; background: linear-gradient(90deg, transparent, #f4c542, transparent);
  vertical-align: middle; margin: 0 18px;
}
.gold { color: #f4c542; }
.card {
  position: relative; border: 2px solid rgba(246,197,66,.9); border-radius: 26px;
  background: linear-gradient(145deg, rgba(255,255,255,.045), rgba(255,255,255,.012));
  box-shadow: 0 25px 55px rgba(0,0,0,.55), inset 0 0 0 1px rgba(255,255,255,.05);
  overflow: hidden;
}
.card::before {
  content: ""; position:absolute; left: 24px; right:24px; top:0; height:2px;
  background: linear-gradient(90deg, transparent, rgba(246,197,66,.95), transparent);
}
.badge-num {
  width: 88px; height: 88px; border: 2px solid #f4c542; border-radius: 15px;
  display: grid; place-items:center; color:#f4c542; font-size:58px; font-weight:900; font-family: Georgia, serif;
  background: rgba(0,0,0,.25); box-shadow:0 0 20px rgba(246,197,66,.18);
}
.pill {
  border: 2px solid var(--accent); color: var(--accent); border-radius:999px;
  padding:8px 28px; font-size:24px; font-weight:900; background:rgba(0,0,0,.24);
}
.section-label {
  display:flex; align-items:center; gap:12px; color:#f4c542; font-size:27px; font-weight:900;
  margin: 28px 0 18px;
}
.section-label::after {
  content:""; height:1px; flex:1; background: linear-gradient(90deg, rgba(246,197,66,.85), transparent);
}
.bullets { list-style:none; padding:0; margin:0; }
.bullets li {
  position:relative; padding-left:28px; margin:18px 0; font-size:28px; line-height:1.42; color:rgba(255,255,255,.92); letter-spacing:-.9px;
}
.bullets li::before {
  content:""; position:absolute; left:0; top:17px; width:9px; height:9px; border-radius:50%; background:#f4c542;
  box-shadow:0 0 12px rgba(246,197,66,.65);
}
.footer-row {
  position:absolute; left:0; right:0; bottom:0; height:84px; border-top:1px solid rgba(246,197,66,.45);
  display:flex; align-items:center; gap:18px; padding:0 28px; color:#f7f0d1; font-size:23px; font-weight:800;
  background:rgba(0,0,0,.22);
}
.divider { width:1px; height:32px; background:rgba(246,197,66,.55); }
.keyword-chip {
  display:inline-block; margin:6px 7px 0 0; padding:8px 14px; border:1px solid rgba(246,197,66,.35);
  border-radius:999px; background:rgba(255,255,255,.06); font-size:21px;
}
"""


def page_shell(body: str) -> str:
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{base_css()}</style></head><body>{body}</body></html>"""


def header_html(page_no: str = "", subtitle: str = "아침 브리핑") -> str:
    now = datetime.now(KST)
    page = f'<div class="page-no">{esc(page_no)}</div>' if page_no else ""
    return f"""
<header class="header">
  <div>
    <div class="brand">
      <div class="menu-icon">☰</div>
      <div>
        <div class="title">오늘의 <span class="gold">헤드라인 뉴스</span></div>
        <div class="sub">{esc(subtitle)}</div>
      </div>
    </div>
  </div>
  <div class="date">📅 {now:%Y.%m.%d}<br>({weekday_ko(now)})</div>
</header>
{page}
"""


def cover_page(issues: list[dict[str, Any]], total_pages: int) -> str:
    keywords = []
    for issue in issues:
        for k in issue.get("keywords") or []:
            if k not in keywords:
                keywords.append(k)
    keywords = keywords[:8] or ["경제", "증시", "정치", "사회", "국제", "산업"]

    top3 = issues[:3]
    top3_html = "".join(
        f'<li><b>{i+1}</b> {esc(x.get("headline"))}</li>'
        for i, x in enumerate(top3)
    )
    keyword_html = "".join(f"<span class='keyword-chip'>{esc(k)}</span>" for k in keywords)

    body = f"""
<main class="page">
  {header_html("", "아침 브리핑")}
  <section style="position:relative; margin-top:90px;">
    <div style="font-size:90px; font-weight:900; letter-spacing:-5px; line-height:1.05;">
      중복 이슈는 <span class="gold">하나로</span><br>
      유사 기사 3건은 <span class="gold">3줄로</span>
    </div>
    <p style="margin-top:28px; font-size:30px; line-height:1.55; color:#eee;">
      오늘 아침 주요 기사를 유사 이슈별로 묶어<br>
      카드뉴스형 브리핑으로 정리했습니다.
    </p>
  </section>
  <section class="card" style="height:360px; padding:36px; margin-top:46px;">
    <div class="section-label">📌 오늘 TOP 이슈</div>
    <ul class="bullets" style="margin-top:10px;">{top3_html}</ul>
  </section>
  <section class="card" style="height:230px; padding:34px; margin-top:28px;">
    <div style="font-size:34px; font-weight:900; color:#f4c542;">핵심 키워드</div>
    <div style="margin-top:24px;">{keyword_html}</div>
  </section>
  <div style="position:absolute; left:46px; right:46px; bottom:42px; font-size:25px; color:#e8d48a; text-align:center;">
    총 {total_pages}장 구성 · 원문 링크는 마지막 텍스트 메시지에서 제공
  </div>
</main>
"""
    return page_shell(body)


def issue_page(issue: dict[str, Any], page_index: int, total_pages: int) -> str:
    category = issue.get("category") or "주요"
    accent = cat_color(category)
    keywords = issue.get("keywords") or []
    keyword_line = " / ".join(str(k) for k in keywords[:4]) or "주요 이슈"
    links = issue.get("links") or []
    source_line = " · ".join(domain(x.get("url")) for x in links[:3]) or "관련 기사 묶음"

    bullets = "".join(f"<li>{esc(line)}</li>" for line in (issue.get("summary_lines") or [])[:3])
    insight = issue.get("insight") or "유사 기사 흐름을 하나의 이슈로 정리했습니다."

    body = f"""
<main class="page">
  {header_html(f"{page_index} / {total_pages}", "아침 브리핑")}
  <section class="card" style="--accent:{accent}; height:1030px; padding:42px; margin-top:92px;">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
      <div class="badge-num">{issue.get("rank", page_index-1)}</div>
      <div class="pill">{esc(category)}</div>
    </div>
    <div style="margin-top:42px; font-size:50px; line-height:1.26; letter-spacing:-2.8px; font-weight:900;">
      {esc(issue.get("headline"))}
    </div>
    <div class="section-label">▤ 유사 기사 3건 핵심 요약</div>
    <ul class="bullets">{bullets}</ul>
    <section style="margin-top:36px; border:1px solid rgba(246,197,66,.5); border-radius:18px; padding:24px 26px; background:rgba(0,0,0,.22);">
      <div style="font-size:25px; color:#f4c542; font-weight:900;">한줄 인사이트</div>
      <div style="margin-top:12px; font-size:29px; line-height:1.45;">{esc(insight)}</div>
    </section>
    <div class="footer-row">
      <span style="color:#f4c542;">🏷 관련 키워드</span>
      <span>{esc(keyword_line)}</span>
      <span class="divider"></span>
      <span style="color:#f4c542;">🔗 출처</span>
      <span>{esc(source_line)}</span>
    </div>
  </section>
</main>
"""
    return page_shell(body)


def summary_page(issues: list[dict[str, Any]], page_index: int, total_pages: int) -> str:
    cats = {}
    for issue in issues:
        cats[issue.get("category", "주요")] = cats.get(issue.get("category", "주요"), 0) + 1
    top_cat = sorted(cats.items(), key=lambda x: x[1], reverse=True)
    top_cat_text = " / ".join(f"{c} {n}건" for c, n in top_cat[:4]) or "주요 이슈"

    issue_list = "".join(
        f"<li><b>{esc(issue.get('category'))}</b> · {esc(issue.get('headline'))}</li>"
        for issue in issues[:5]
    )

    body = f"""
<main class="page">
  {header_html(f"{page_index} / {total_pages}", "마무리 요약")}
  <section style="position:relative; margin-top:96px;">
    <div style="font-size:84px; font-weight:900; letter-spacing:-5px; color:#f4c542;">오늘의 흐름 요약</div>
  </section>
  <section class="card" style="height:440px; padding:38px; margin-top:42px;">
    <div class="section-label">📊 카테고리 흐름</div>
    <div style="font-size:34px; line-height:1.5; margin-top:22px;">{esc(top_cat_text)}</div>
    <div style="font-size:25px; line-height:1.6; color:#e7e7e7; margin-top:30px;">
      중복 기사를 하나로 묶어 실제로 반복 노출되는 핵심 이슈만 남겼습니다.
    </div>
  </section>
  <section class="card" style="height:500px; padding:38px; margin-top:28px;">
    <div class="section-label">✅ 오늘 체크 포인트</div>
    <ul class="bullets">{issue_list}</ul>
  </section>
  <div style="position:absolute; left:46px; right:46px; bottom:42px; font-size:25px; color:#e8d48a; text-align:center;">
    원문 링크는 함께 전송되는 텍스트 메시지에서 확인할 수 있습니다.
  </div>
</main>
"""
    return page_shell(body)


async def render_html_to_png(html_content: str, output_path: Path, *, scale: int = 2) -> str:
    from playwright.async_api import async_playwright

    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = output_path.with_suffix(".html")
    html_path.write_text(html_content, encoding="utf-8")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 1080, "height": 1350},
            device_scale_factor=scale,
        )
        await page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        await page.screenshot(path=str(output_path), full_page=True, type="png")
        await browser.close()

    return str(output_path)


def build_cardnews_pages(issues: list[dict[str, Any]], *, output_dir: str | Path) -> list[str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # cover + max 5 issue pages + summary = up to 7 pages
    issues = issues[:5]
    total_pages = len(issues) + 2
    scale = int(os.getenv("HEADLINE_IMAGE_SCALE", "2"))

    html_pages = [cover_page(issues, total_pages)]
    for idx, issue in enumerate(issues, start=2):
        html_pages.append(issue_page(issue, idx, total_pages))
    html_pages.append(summary_page(issues, total_pages, total_pages))

    async def run_all() -> list[str]:
        paths = []
        for i, html_content in enumerate(html_pages, start=1):
            out = output_dir / f"headline_cardnews_{i:02d}.png"
            await render_html_to_png(html_content, out, scale=scale)
            paths.append(str(out))
        return paths

    return asyncio.run(run_all())
