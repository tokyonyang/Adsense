from __future__ import annotations

import asyncio
import html
import os
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

KST = timezone(timedelta(hours=9))


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def esc(value: Any) -> str:
    return html.escape(str(value or ""))


def domain(url: str | None) -> str:
    if not url:
        return "news"
    try:
        host = urlparse(url).netloc or urlparse(url).path
        return host.replace("www.", "")[:32] or "news"
    except Exception:
        return "news"


def clean_text(value: Any, limit: int = 80) -> str:
    text = str(value or "")
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def split_title(title: str, limit: int = 24) -> str:
    title = re.sub(r"\s+", " ", str(title or "")).strip()
    if len(title) <= limit:
        return title
    mid = len(title) // 2
    spaces = [i for i, ch in enumerate(title) if ch == " "]
    if spaces:
        cut = min(spaces, key=lambda i: abs(i - mid))
        if 8 <= cut <= len(title) - 8:
            return title[:cut].strip() + "<br>" + title[cut:].strip()
    return title[:limit].rstrip() + "<br>" + title[limit:limit*2].strip()


def category_theme(category: str) -> dict[str, str]:
    category = str(category or "")
    if category in {"경제·금융", "증권·투자", "산업·기업", "정책·지원금", "정책·생활", "부동산·주거금융", "생활·제도"}:
        return {"accent": "#f4b740", "accent2": "#ffd27a", "chip_bg": "rgba(244,183,64,.12)", "chip_border": "rgba(244,183,64,.76)"}
    if category in {"시사·정치", "사회·사건"}:
        return {"accent": "#ff5a4d", "accent2": "#ffb4a8", "chip_bg": "rgba(255,90,77,.12)", "chip_border": "rgba(255,90,77,.72)"}
    if category in {"국제", "국제·안전", "날씨·안전"}:
        return {"accent": "#64b5ff", "accent2": "#b5dbff", "chip_bg": "rgba(100,181,255,.12)", "chip_border": "rgba(100,181,255,.72)"}
    if category in {"건강·의료", "교육·입시", "연예·문화", "스포츠"}:
        return {"accent": "#9bd7b0", "accent2": "#d6f2df", "chip_bg": "rgba(155,215,176,.12)", "chip_border": "rgba(155,215,176,.72)"}
    return {"accent": "#f4b740", "accent2": "#ffd27a", "chip_bg": "rgba(244,183,64,.12)", "chip_border": "rgba(244,183,64,.76)"}


def base_css(width: int, height: int) -> str:
    return f"""
@font-face {{ font-family: NanumGothic; src: local('NanumGothic'); }}
@font-face {{ font-family: NotoKR; src: local('Noto Sans CJK KR'); }}
* {{ box-sizing: border-box; }}
html, body {{
  margin: 0;
  width: {width}px;
  height: {height}px;
  overflow: hidden;
  font-family: NanumGothic, NotoKR, 'Noto Sans KR', 'Apple SD Gothic Neo', sans-serif;
  color: #f7f8fb;
  background: #02070d;
}}
.page {{
  position: relative;
  width: {width}px;
  height: {height}px;
  overflow: hidden;
  padding: 54px 56px 42px;
  background:
    radial-gradient(circle at 80% 18%, rgba(244,183,64,.20), transparent 27%),
    radial-gradient(circle at 18% 5%, rgba(100,181,255,.08), transparent 28%),
    linear-gradient(145deg, #08131d 0%, #050a10 48%, #020407 100%);
}}
.page::before {{
  content: "";
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
  background-size: 46px 46px;
  opacity: .42;
  pointer-events: none;
}}
.bg-orb {{
  position:absolute;
  right:-110px;
  top:55px;
  width:520px;
  height:520px;
  border-radius:50%;
  background:radial-gradient(circle, rgba(244,183,64,.28) 0%, rgba(244,183,64,.10) 38%, transparent 70%);
  opacity:.9;
}}
.bg-globe {{
  position:absolute;
  right:56px;
  top:64px;
  width:360px;
  height:300px;
  opacity:.58;
  background:radial-gradient(circle at 50% 50%, rgba(244,183,64,.22), rgba(244,183,64,.03) 60%, transparent 72%);
  border-radius:50%;
}}
.bg-globe::before {{
  content:"";
  position:absolute;
  inset:22px;
  border-radius:50%;
  background-image: radial-gradient(rgba(244,183,64,.55) 1.4px, transparent 1.4px);
  background-size:12px 12px;
  mask-image: radial-gradient(circle, black 0 58%, transparent 72%);
}}
.bg-chart {{
  position:absolute;
  right:64px;
  top:250px;
  width:360px;
  height:210px;
  opacity:.82;
}}
.brand-footer {{
  position:absolute;
  left:56px;
  right:56px;
  bottom:24px;
  display:flex;
  align-items:center;
  justify-content:center;
  gap:14px;
  font-size:28px;
  font-weight:800;
  letter-spacing:.2px;
  color:#f4b740;
}}
.brand-footer::before,
.brand-footer::after {{
  content:"";
  height:1px;
  flex:1;
  background:linear-gradient(90deg, transparent, rgba(244,183,64,.58), transparent);
}}
.brand-dot {{
  width:36px;
  height:36px;
  display:inline-grid;
  place-items:center;
  border:1.6px solid rgba(244,183,64,.7);
  border-radius:50%;
  font-size:20px;
}}
.topbar {{
  position:relative;
  z-index:3;
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:18px;
  font-size:25px;
  color:#f7f8fb;
  letter-spacing:-.4px;
}}
.topbar .left {{
  display:flex;
  align-items:center;
  gap:14px;
}}
.sun {{
  color:#f4b740;
  font-size:37px;
  transform:translateY(-1px);
}}
.badges {{
  display:flex;
  align-items:center;
  gap:14px;
}}
.badge {{
  border:1.8px solid var(--accent);
  background:var(--chip-bg);
  color:var(--accent2);
  border-radius:999px;
  padding:9px 20px 8px;
  font-size:23px;
  font-weight:900;
  letter-spacing:-.8px;
}}
.page-badge {{
  min-width:70px;
  text-align:center;
  border-radius:17px;
  padding:9px 17px;
  background:linear-gradient(180deg, var(--accent2), var(--accent));
  color:#07111a;
  font-size:29px;
  font-weight:900;
  letter-spacing:1px;
}}
.cover-title {{
  position:relative;
  z-index:2;
  margin-top:54px;
  font-size:86px;
  line-height:1.08;
  font-weight:900;
  letter-spacing:-5.6px;
}}
.cover-title .gold {{
  display:block;
  color:#f4b740;
  text-shadow:0 0 30px rgba(244,183,64,.25);
}}
.cover-dek {{
  position:relative;
  z-index:2;
  margin-top:28px;
  width:610px;
  font-size:28px;
  line-height:1.55;
  color:rgba(247,248,251,.82);
  letter-spacing:-.8px;
}}
.gold-line {{
  position:relative;
  z-index:2;
  width:510px;
  height:1px;
  margin-top:30px;
  background:linear-gradient(90deg, rgba(244,183,64,.0), rgba(244,183,64,.96), rgba(244,183,64,.0));
}}
.gold-line::after {{
  content:"";
  position:absolute;
  left:50%;
  top:-4px;
  width:10px;
  height:10px;
  border-radius:50%;
  background:#f4b740;
  box-shadow:0 0 22px #f4b740;
}}
.summary-card {{
  position:relative;
  z-index:3;
  margin-top:38px;
  border:1.4px solid rgba(244,183,64,.45);
  border-radius:26px;
  padding:30px 36px 28px;
  background:linear-gradient(145deg, rgba(7,18,28,.82), rgba(3,8,13,.72));
  box-shadow:0 22px 70px rgba(0,0,0,.38), inset 0 0 0 1px rgba(255,255,255,.035);
}}
.summary-head {{
  display:grid;
  grid-template-columns:62px 1fr;
  gap:20px;
  align-items:center;
  padding-bottom:22px;
  border-bottom:1px solid rgba(244,183,64,.25);
}}
.icon-circle {{
  width:62px;
  height:62px;
  border:2px solid #f4b740;
  border-radius:50%;
  display:grid;
  place-items:center;
  color:#f4b740;
  font-size:31px;
}}
.summary-title {{
  font-size:34px;
  font-weight:900;
  color:#f4b740;
  letter-spacing:-1.5px;
}}
.summary-sub {{
  margin-top:7px;
  font-size:22px;
  color:rgba(247,248,251,.74);
}}
.agenda {{
  list-style:none;
  margin:18px 0 0;
  padding:0;
}}
.agenda li {{
  display:grid;
  grid-template-columns:58px 1fr 54px;
  gap:18px;
  align-items:center;
  min-height:78px;
  border-bottom:1px solid rgba(255,255,255,.08);
}}
.agenda li:last-child {{ border-bottom:none; }}
.num {{
  width:48px;
  height:48px;
  border-radius:50%;
  display:grid;
  place-items:center;
  background:linear-gradient(180deg, #ffd27a, #f4b740);
  color:#07111a;
  font-size:29px;
  font-weight:900;
}}
.agenda-text {{
  font-size:32px;
  font-weight:900;
  letter-spacing:-1.6px;
  color:#f8f9fb;
}}
.agenda-icon {{
  font-size:30px;
  color:#f4b740;
  text-align:center;
}}
.issue-title-wrap {{
  position:relative;
  z-index:3;
  margin-top:54px;
  display:grid;
  grid-template-columns: 1fr 300px;
  gap:28px;
  align-items:start;
}}
.title-accent {{
  width:6px;
  height:96px;
  background:linear-gradient(180deg, var(--accent2), var(--accent));
  border-radius:999px;
  float:left;
  margin:12px 26px 0 0;
}}
.issue-title {{
  font-size:74px;
  line-height:1.08;
  letter-spacing:-5px;
  font-weight:900;
  color:#f8f9fb;
  text-shadow:0 8px 32px rgba(0,0,0,.42);
}}
.keyword-chip {{
  display:inline-block;
  margin-top:22px;
  padding:8px 22px;
  border:1.5px solid var(--accent);
  color:var(--accent2);
  border-radius:999px;
  background:var(--chip-bg);
  font-size:24px;
  font-weight:900;
}}
.hero-mini {{
  position:relative;
  height:210px;
  opacity:.95;
}}
.hero-mini .coin {{
  position:absolute;
  right:100px;
  top:8px;
  width:120px;
  height:120px;
  border-radius:50%;
  border:3px solid rgba(244,183,64,.8);
  display:grid;
  place-items:center;
  color:#f4b740;
  font-size:56px;
  font-weight:900;
  background:rgba(0,0,0,.22);
  box-shadow:0 0 40px rgba(244,183,64,.22);
}}
.hero-mini .mini-bars {{
  position:absolute;
  right:14px;
  bottom:0;
  width:240px;
  height:150px;
  opacity:.72;
}}
.content-grid {{
  position:relative;
  z-index:4;
  margin-top:34px;
  display:grid;
  grid-template-columns:1fr;
  gap:18px;
}}
.panel {{
  border:1.3px solid rgba(244,183,64,.38);
  border-radius:22px;
  background:linear-gradient(145deg, rgba(7,18,28,.84), rgba(3,8,13,.74));
  box-shadow:0 18px 60px rgba(0,0,0,.32), inset 0 0 0 1px rgba(255,255,255,.035);
}}
.bullet-panel {{
  padding:24px 30px 24px;
}}
.panel-heading {{
  display:flex;
  align-items:center;
  gap:16px;
  color:var(--accent);
  font-size:29px;
  font-weight:900;
  letter-spacing:-1.1px;
  margin-bottom:15px;
}}
.bullets {{
  list-style:none;
  margin:0;
  padding:0;
}}
.bullets li {{
  position:relative;
  padding-left:26px;
  margin:12px 0;
  font-size:25px;
  line-height:1.42;
  color:rgba(248,249,251,.92);
  letter-spacing:-.8px;
}}
.bullets li::before {{
  content:"";
  position:absolute;
  left:0;
  top:16px;
  width:8px;
  height:8px;
  border-radius:50%;
  background:var(--accent);
  box-shadow:0 0 14px var(--accent);
}}
.lower-grid {{
  display:grid;
  grid-template-columns:1.12fr .88fr;
  gap:18px;
}}
.chart-panel {{
  padding:23px 25px 22px;
  min-height:260px;
}}
.chart-title {{
  color:var(--accent);
  font-size:26px;
  font-weight:900;
  letter-spacing:-1px;
}}
.chart-caption {{
  margin-top:7px;
  font-size:20px;
  color:rgba(248,249,251,.78);
}}
.chart-svg {{
  margin-top:12px;
  width:100%;
  height:160px;
  overflow:hidden;
}}
.insight-panel {{
  padding:25px 28px;
  background:radial-gradient(circle at 90% 0%, rgba(244,183,64,.18), transparent 45%), linear-gradient(145deg, rgba(244,183,64,.18), rgba(8,14,20,.84));
}}
.insight-heading {{
  display:flex;
  align-items:center;
  gap:14px;
  color:var(--accent2);
  font-size:31px;
  font-weight:900;
  letter-spacing:-1px;
}}
.quote-icon {{
  width:48px;
  height:48px;
  border:1.8px solid var(--accent);
  border-radius:50%;
  display:grid;
  place-items:center;
  font-family:Georgia, serif;
  font-size:34px;
  color:var(--accent);
}}
.insight-text {{
  margin-top:18px;
  font-size:25px;
  line-height:1.48;
  font-weight:800;
  color:#fff;
  letter-spacing:-.9px;
}}
.meta-strip {{
  display:grid;
  grid-template-columns:1fr 1.55fr;
  gap:18px;
  padding:18px 24px 17px;
  min-height:86px;
}}
.meta-block {{
  display:grid;
  grid-template-columns:34px 1fr;
  gap:12px;
  align-items:start;
  color:rgba(248,249,251,.82);
  font-size:19px;
  line-height:1.35;
}}
.meta-label {{
  color:var(--accent);
  font-size:22px;
  font-weight:900;
  margin-bottom:4px;
}}
.summary-big {{
  position:relative;
  z-index:3;
  margin-top:52px;
  font-size:70px;
  line-height:1.08;
  font-weight:900;
  letter-spacing:-4px;
}}
.summary-note {{
  position:relative;
  z-index:3;
  margin-top:28px;
  color:#f4b740;
  font-size:33px;
  font-weight:900;
  letter-spacing:-1.5px;
}}
.final-list {{
  position:relative;
  z-index:3;
  margin-top:34px;
  padding:0;
  list-style:none;
}}
.final-list li {{
  font-size:32px;
  line-height:1.45;
  margin:15px 0;
  color:#f7f8fb;
  letter-spacing:-1.3px;
}}
.final-insight {{
  position:relative;
  z-index:3;
  margin-top:34px;
  border-left:6px solid #f4b740;
  padding-left:23px;
  font-size:31px;
  line-height:1.45;
  font-weight:900;
  color:#fff;
}}
"""


def rising_chart_svg(width: int = 360, height: int = 210, color: str = "#f4b740") -> str:
    bars = []
    vals = [28, 42, 56, 68, 84, 104, 126, 150]
    x0 = 24
    for i, h in enumerate(vals):
        bars.append(f'<rect x="{x0 + i*38}" y="{height-h}" width="22" height="{h}" rx="3" fill="{color}" opacity="{0.18+i*0.06:.2f}"/>')
    line = f"""
    <polyline points="0,{height-22} 55,{height-82} 100,{height-70} 152,{height-120} 205,{height-104} 260,{height-154} 330,{height-42}"
      fill="none" stroke="{color}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
    <path d="M330 {height-42} l-30 -8 l18 -24 z" fill="{color}"/>
    """
    return f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">{"".join(bars)}{line}</svg>'


def default_chart_svg(width: int = 360, height: int = 160, accent: str = "#f4b740") -> str:
    points = "0,126 32,112 58,122 90,96 120,103 150,75 178,84 210,60 245,72 275,45 312,30 352,18"
    return f"""
<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <line x1="0" y1="130" x2="{width}" y2="130" stroke="rgba(255,255,255,.22)" stroke-width="1"/>
  <line x1="0" y1="90" x2="{width}" y2="90" stroke="rgba(255,255,255,.12)" stroke-width="1" stroke-dasharray="4 6"/>
  <line x1="0" y1="50" x2="{width}" y2="50" stroke="rgba(255,255,255,.12)" stroke-width="1" stroke-dasharray="4 6"/>
  <polyline points="{points}" fill="none" stroke="{accent}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="352" cy="18" r="8" fill="{accent}"/>
</svg>
""".strip()


def chart_block(issue: dict[str, Any], theme: dict[str, str]) -> str:
    chart = issue.get("chart") or {}
    title = chart.get("title") or "관련 지표"
    caption = chart.get("caption") or "최근 흐름"
    svg = chart.get("svg") if chart.get("available") else ""
    if not svg:
        svg = default_chart_svg(accent=theme["accent"])
    return f"""
<section class="panel chart-panel">
  <div class="chart-title">최근 {esc(title)} 추이</div>
  <div class="chart-caption">{esc(caption)}</div>
  <div class="chart-svg">{svg}</div>
</section>
"""


def page_shell(body: str, width: int, height: int) -> str:
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>{base_css(width, height)}</style></head><body>{body}</body></html>"""


def global_background() -> str:
    return f"""
<div class="bg-orb"></div>
<div class="bg-globe"></div>
<div class="bg-chart">{rising_chart_svg()}</div>
"""


def footer() -> str:
    return '<div class="brand-footer"><span class="brand-dot">◎</span><span>gooddaynews.store</span></div>'


def header_html(theme: dict[str, str], page_no: str | None = None, category: str | None = None) -> str:
    now = datetime.now(KST)
    badge_html = ""
    if category or page_no:
        badge_html = f"""
        <div class="badges">
          {f'<div class="badge">{esc(category)}</div>' if category else ''}
          {f'<div class="page-badge">{esc(page_no)}</div>' if page_no else ''}
        </div>
        """
    return f"""
<div class="topbar" style="--accent:{theme['accent']};--accent2:{theme['accent2']};--chip-bg:{theme['chip_bg']};">
  <div class="left"><span class="sun">☼</span><span>아침 브리핑 · {now:%Y.%m.%d} ({weekday_ko(now)})</span></div>
  {badge_html}
</div>
"""


def cover_page(issues: list[dict[str, Any]], total_pages: int, width: int, height: int) -> str:
    theme = category_theme("경제·금융")
    agenda = list(issues[:4])
    while len(agenda) < 4:
        agenda.append({"headline": "주요 이슈 업데이트"})
    icons = ["₩", "🏦", "▥", ""]
    rows = []
    for i, issue in enumerate(agenda[:4], start=1):
        rows.append(
            f"""
            <li>
              <div class="num">{i}</div>
              <div class="agenda-text">{esc(clean_text(issue.get("headline"), 34))}</div>
              <div class="agenda-icon">{icons[i-1]}</div>
            </li>
            """
        )
    body = f"""
<main class="page">
  {global_background()}
  {header_html(theme)}
  <section class="cover-title">
    <span>오늘의</span>
    <span class="gold">헤드라인 뉴스</span>
  </section>
  <div class="gold-line"></div>
  <section class="cover-dek">
    경제·금융, 증시, 산업 이슈를 중심으로<br>
    오늘 시장의 핵심 변수만 빠르게 정리했습니다.
  </section>
  <section class="summary-card">
    <div class="summary-head">
      <div class="icon-circle">↗</div>
      <div>
        <div class="summary-title">오늘의 흐름 요약</div>
        <div class="summary-sub">중복 이슈를 제거하고 핵심 흐름만 남겼습니다</div>
      </div>
    </div>
    <ul class="agenda">{''.join(rows)}</ul>
  </section>
  {footer()}
</main>
"""
    return page_shell(body, width, height)


def issue_page(issue: dict[str, Any], page_index: int, total_pages: int, width: int, height: int) -> str:
    category = str(issue.get("category") or "주요")
    theme = category_theme(category)
    title = str(issue.get("headline") or issue.get("anchor_title") or "주요 이슈")
    anchor = str(issue.get("anchor_title") or "")
    keywords = issue.get("keywords") or []
    links = issue.get("links") or []

    bullet_lines = [clean_text(x, 82) for x in (issue.get("summary_lines") or [])[:3]]
    while len(bullet_lines) < 3:
        bullet_lines.append("관련 기사 흐름을 추가 확인할 필요가 있습니다.")

    insight = clean_text(issue.get("insight") or "시장 영향과 후속 변수를 함께 확인해야 합니다.", 110)
    source_line = " · ".join(domain(x.get("url")) for x in links[:3]) or "경제 기사 종합"
    keyword_line = " · ".join(str(k) for k in keywords[:5]) or str(issue.get("anchor_title") or title)

    body = f"""
<main class="page" style="--accent:{theme['accent']};--accent2:{theme['accent2']};--chip-bg:{theme['chip_bg']};">
  {global_background()}
  {header_html(theme, str(issue.get("rank", page_index-1)).zfill(2), category)}
  <section class="issue-title-wrap">
    <div>
      <div class="title-accent"></div>
      <div class="issue-title">{split_title(esc(title), 20)}</div>
      <div class="keyword-chip">{esc(clean_text(anchor or title, 18))}</div>
    </div>
    <div class="hero-mini">
      <div class="coin">₩</div>
      <div class="mini-bars">{rising_chart_svg(240, 150, theme["accent"])}</div>
    </div>
  </section>

  <section class="content-grid">
    <section class="panel bullet-panel">
      <div class="panel-heading"><span>▤</span><span>유사 기사 3건 핵심 요약</span></div>
      <ul class="bullets">
        <li>{esc(bullet_lines[0])}</li>
        <li>{esc(bullet_lines[1])}</li>
        <li>{esc(bullet_lines[2])}</li>
      </ul>
    </section>

    <section class="lower-grid">
      {chart_block(issue, theme)}
      <section class="panel insight-panel">
        <div class="insight-heading"><span class="quote-icon">“</span><span>한줄 인사이트</span></div>
        <div class="insight-text">{esc(insight)}</div>
      </section>
    </section>

    <section class="panel meta-strip">
      <div class="meta-block">
        <div>🏷</div>
        <div>
          <div class="meta-label">관련 키워드</div>
          <div>{esc(keyword_line)}</div>
        </div>
      </div>
      <div class="meta-block">
        <div>📄</div>
        <div>
          <div class="meta-label">출처</div>
          <div>{esc(source_line)}</div>
        </div>
      </div>
    </section>
  </section>
  {footer()}
</main>
"""
    return page_shell(body, width, height)


def summary_page(issues: list[dict[str, Any]], page_index: int, total_pages: int, width: int, height: int) -> str:
    theme = category_theme("경제·금융")
    rows = []
    for i, issue in enumerate(issues[:5], start=1):
        rows.append(f"<li>{i}. {esc(clean_text(issue.get('headline'), 38))}</li>")
    body = f"""
<main class="page">
  {global_background()}
  {header_html(theme)}
  <section class="summary-big">오늘의 흐름 요약</section>
  <section class="summary-note">중복 이슈를 제거하고 핵심 흐름만 남겼습니다</section>
  <ul class="final-list">{''.join(rows)}</ul>
  <section class="final-insight">
    경제·금융, 증시, 산업 이슈를 중심으로 생활 영향과 시장 변수를 함께 점검하세요.
  </section>
  {footer()}
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

    width = int(env("HEADLINE_IMAGE_WIDTH", "1080"))
    height = int(env("HEADLINE_IMAGE_HEIGHT", "1080"))
    scale = int(env("HEADLINE_IMAGE_SCALE", "2"))

    issues = issues[: int(env("HEADLINE_CARDNEWS_ISSUES", "5"))]
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
