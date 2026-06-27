from __future__ import annotations

import asyncio
import html
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

KST = timezone(timedelta(hours=9))


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def esc(x: Any) -> str:
    return html.escape(str(x or ""))


def short(x: Any, n: int = 60) -> str:
    s = str(x or "").strip()
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def css(width: int, height: int) -> str:
    return f"""
@font-face {{ font-family: NanumGothic; src: local('NanumGothic'); }}
* {{ box-sizing:border-box; }}
html, body {{
  margin:0; width:{width}px; height:{height}px; overflow:hidden;
  background:#03060a; color:#f7f8fb;
  font-family:NanumGothic, 'Noto Sans CJK KR', 'Apple SD Gothic Neo', sans-serif;
}}
.page {{
  width:{width}px; height:{height}px; position:relative; overflow:hidden;
  padding:52px 58px 48px;
  background:
    radial-gradient(circle at 78% 16%, rgba(244,183,64,.22), transparent 28%),
    radial-gradient(circle at 14% 80%, rgba(92,150,255,.14), transparent 30%),
    linear-gradient(145deg, #08131e 0%, #050910 54%, #020306 100%);
}}
.page::before {{
  content:""; position:absolute; inset:0; pointer-events:none;
  background-image:
    linear-gradient(rgba(255,255,255,.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,.03) 1px, transparent 1px);
  background-size:46px 46px; opacity:.44;
}}
.top {{
  position:relative; z-index:2; display:flex; justify-content:space-between; align-items:center;
  font-size:24px; color:rgba(247,248,251,.86);
}}
.badge {{
  border:1.7px solid #f4b740; color:#ffd27a; border-radius:999px;
  padding:8px 18px; font-weight:900; background:rgba(244,183,64,.12);
}}
.title {{
  position:relative; z-index:2; margin-top:48px;
  font-size:82px; line-height:1.08; font-weight:900; letter-spacing:-5px;
}}
.title .gold {{ color:#f4b740; display:block; }}
.subtitle {{
  position:relative; z-index:2; margin-top:24px;
  width:720px; color:rgba(247,248,251,.80); font-size:28px; line-height:1.48;
}}
.panel {{
  position:relative; z-index:3; border:1.3px solid rgba(244,183,64,.42); border-radius:26px;
  background:linear-gradient(145deg, rgba(8,19,30,.86), rgba(3,8,13,.75));
  box-shadow:0 22px 70px rgba(0,0,0,.34), inset 0 0 0 1px rgba(255,255,255,.035);
}}
.cover-list {{
  margin-top:42px; padding:28px 34px;
}}
.cover-list h2 {{
  margin:0 0 18px; color:#f4b740; font-size:34px;
}}
.cover-list ol {{
  margin:0; padding-left:36px;
}}
.cover-list li {{
  font-size:30px; line-height:1.48; margin:11px 0; font-weight:800;
}}
.section-title {{
  position:relative; z-index:2; margin-top:38px;
  display:flex; align-items:center; gap:16px;
}}
.section-icon {{
  width:62px; height:62px; border-radius:18px; background:linear-gradient(180deg,#ffd27a,#f4b740);
  color:#07111a; display:grid; place-items:center; font-size:34px; font-weight:900;
}}
.section-title h1 {{
  margin:0; font-size:54px; line-height:1.08; letter-spacing:-3px;
}}
.issue-list {{
  margin-top:28px; padding:28px 32px;
}}
.issue {{
  padding:18px 0; border-bottom:1px solid rgba(255,255,255,.09);
}}
.issue:last-child {{ border-bottom:none; }}
.issue-head {{
  color:#f4b740; font-size:29px; font-weight:900; line-height:1.28; letter-spacing:-1.2px;
}}
.issue-lines {{
  margin-top:10px; color:rgba(247,248,251,.90); font-size:22px; line-height:1.46;
}}
.insight {{
  margin-top:12px; border-left:5px solid #f4b740; padding-left:16px;
  font-size:22px; line-height:1.42; font-weight:800;
}}
.market-grid {{
  margin-top:28px; display:grid; grid-template-columns:1fr 1fr; gap:16px;
}}
.market-card {{
  padding:20px 22px; min-height:128px;
}}
.market-name {{ color:#f4b740; font-size:24px; font-weight:900; }}
.market-value {{ margin-top:10px; font-size:34px; font-weight:900; }}
.market-change {{ margin-top:5px; font-size:21px; color:rgba(247,248,251,.82); }}
.keyword-grid {{
  margin-top:28px; display:grid; grid-template-columns:1fr 1fr; gap:18px;
}}
.keybox {{ padding:24px 26px; min-height:390px; }}
.keybox h2 {{ margin:0 0 18px; color:#f4b740; font-size:31px; }}
.keybox ol {{ margin:0; padding-left:33px; }}
.keybox li {{ font-size:26px; line-height:1.55; margin:7px 0; }}
.weather-grid {{
  margin-top:28px; display:grid; grid-template-columns:repeat(2, 1fr); gap:14px;
}}
.weather-card {{ padding:17px 20px; min-height:98px; }}
.weather-region {{ color:#f4b740; font-size:24px; font-weight:900; }}
.weather-line {{ margin-top:8px; font-size:21px; color:rgba(247,248,251,.9); }}
.quote-box {{
  margin-top:34px; padding:36px; min-height:280px;
}}
.quote-text {{ font-size:38px; line-height:1.38; font-weight:900; }}
.quote-author {{ margin-top:22px; color:#f4b740; font-size:25px; text-align:right; }}
.footer {{
  position:absolute; left:58px; right:58px; bottom:22px; z-index:5;
  display:flex; align-items:center; justify-content:center; gap:14px;
  color:#f4b740; font-size:27px; font-weight:900;
}}
.footer::before, .footer::after {{
  content:""; height:1px; flex:1;
  background:linear-gradient(90deg, transparent, rgba(244,183,64,.58), transparent);
}}
"""


def shell(body: str, width: int, height: int) -> str:
    return f"<!doctype html><html lang='ko'><head><meta charset='utf-8'><style>{css(width,height)}</style></head><body>{body}</body></html>"


def topbar(label: str = "05:30 KST") -> str:
    now = datetime.now(KST)
    return f"""
<div class="top">
  <div>🌙 간밤의 핫이슈 · {now:%Y.%m.%d} ({weekday_ko(now)})</div>
  <div class="badge">{esc(label)}</div>
</div>
"""


def footer() -> str:
    return '<div class="footer"><span>gooddaynews.store</span></div>'


def cover_page(payload: dict[str, Any], width: int, height: int) -> str:
    topics = []
    for item in payload.get("us_news", [])[:1]:
        topics.append(item.get("headline"))
    topics.append((payload.get("us_market") or {}).get("headline"))
    for item in payload.get("korea_news", [])[:2]:
        topics.append(item.get("headline"))
    topics = [x for x in topics if x][:4]

    rows = "".join(f"<li>{esc(short(t, 38))}</li>" for t in topics)
    body = f"""
<main class="page">
  {topbar()}
  <section class="title">간밤의<br><span class="gold">핫이슈</span></section>
  <section class="subtitle">
    미국뉴스, 미증시, 국내 아침뉴스, 인기 키워드와 날씨까지<br>
    하루를 시작하기 전 확인할 핵심 흐름만 모았습니다.
  </section>
  <section class="panel cover-list">
    <h2>오늘 아침 먼저 볼 것</h2>
    <ol>{rows}</ol>
  </section>
  {footer()}
</main>
"""
    return shell(body, width, height)


def issue_page(title: str, icon: str, issues: list[dict[str, Any]], width: int, height: int) -> str:
    cards = []
    for issue in issues[:4]:
        lines = "".join(f"<div>• {esc(short(x, 68))}</div>" for x in (issue.get("summary_lines") or [])[:2])
        cards.append(f"""
<div class="issue">
  <div class="issue-head">{esc(short(issue.get("headline"), 46))}</div>
  <div class="issue-lines">{lines}</div>
  <div class="insight">{esc(short(issue.get("insight"), 82))}</div>
</div>
""")
    body = f"""
<main class="page">
  {topbar()}
  <section class="section-title"><div class="section-icon">{esc(icon)}</div><h1>{esc(title)}</h1></section>
  <section class="panel issue-list">{''.join(cards)}</section>
  {footer()}
</main>
"""
    return shell(body, width, height)


def market_page(payload: dict[str, Any], width: int, height: int) -> str:
    market = payload.get("us_market") or {}
    rows = []
    for r in market.get("indices", [])[:6]:
        change = r.get("change_pct")
        arrow = "▲" if r.get("change", 0) >= 0 else "▼"
        rows.append(f"""
<section class="panel market-card">
  <div class="market-name">{esc(r.get("name"))}</div>
  <div class="market-value">{esc(r.get("value"))}</div>
  <div class="market-change">{arrow} {abs(change) if change is not None else "-"}%</div>
</section>
""")
    if not rows:
        rows.append("<section class='panel market-card'><div class='market-name'>미증시</div><div class='market-value'>데이터 대기</div><div class='market-change'>뉴스 흐름 중심 확인</div></section>")

    body = f"""
<main class="page">
  {topbar()}
  <section class="section-title"><div class="section-icon">📈</div><h1>미증시 요약</h1></section>
  <section class="subtitle">{esc(short(market.get("insight"), 120))}</section>
  <section class="market-grid">{''.join(rows)}</section>
  {footer()}
</main>
"""
    return shell(body, width, height)



def keyword_label(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("keyword") or "-")
    return str(item or "-")


def keyword_source_domains(item: Any) -> str:
    if not isinstance(item, dict):
        return "관련 기사 확인"
    articles = item.get("articles") or []
    domains = []
    for article in articles[:2]:
        domain = article.get("domain")
        if domain and domain not in domains:
            domains.append(domain)
    if domains:
        return " · ".join(domains)
    if item.get("source"):
        return str(item.get("source"))
    return "관련 기사 확인"


def keyword_page(payload: dict[str, Any], width: int, height: int) -> str:
    kw = payload.get("keywords") or {}
    realtime = kw.get("realtime_keywords_detailed") or kw.get("realtime_keywords") or []
    popular = kw.get("popular_keywords_detailed") or kw.get("popular_keywords") or []

    realtime_rows = "".join(
        f"<li><span>{esc(short(keyword_label(x), 22))}</span><small>{esc(short(keyword_source_domains(x), 34))}</small></li>"
        for x in realtime[:8]
    )
    popular_rows = "".join(
        f"<li><span>{esc(short(keyword_label(x), 22))}</span><small>{esc(short(keyword_source_domains(x), 34))}</small></li>"
        for x in popular[:8]
    )
    body = f"""
<main class="page">
  {topbar()}
  <section class="section-title"><div class="section-icon">🔥</div><h1>키워드 & 트렌드</h1></section>
  <section class="keyword-grid">
    <div class="panel keybox"><h2>실시간 급상승</h2><ol>{realtime_rows}</ol></div>
    <div class="panel keybox"><h2>간밤 인기 키워드</h2><ol>{popular_rows}</ol></div>
  </section>
  {footer()}
</main>
"""
    return shell(body, width, height)


def sns_page(payload: dict[str, Any], width: int, height: int) -> str:
    kw = payload.get("keywords") or {}
    sns_items = kw.get("sns_trends") or []
    cards = []
    for item in sns_items[:6]:
        articles = item.get("articles") or []
        domains = " · ".join(
            a.get("domain") for a in articles[:2] if a.get("domain")
        ) or "뉴스/검색 기반 보조 수집"
        cards.append(f"""
<div class="issue">
  <div class="issue-head">[{esc(short(item.get("platform"), 18))}] {esc(short(item.get("headline"), 44))}</div>
  <div class="issue-lines"><div>• {esc(short(item.get("summary"), 76))}</div></div>
  <div class="insight">근거: {esc(short(domains, 70))}</div>
</div>
""")
    if not cards:
        cards.append("""
<div class="issue">
  <div class="issue-head">SNS 트렌드 후보 없음</div>
  <div class="issue-lines"><div>• 이번 실행에서는 SNS별 보조 트렌드 후보를 찾지 못했습니다.</div></div>
  <div class="insight">공식 SNS API 연동 시 더 정확한 플랫폼별 랭킹을 제공할 수 있습니다.</div>
</div>
""")
    body = f"""
<main class="page">
  {topbar()}
  <section class="section-title"><div class="section-icon">📱</div><h1>SNS별 트렌드</h1></section>
  <section class="panel issue-list">{''.join(cards)}</section>
  {footer()}
</main>
"""
    return shell(body, width, height)


def weather_page(payload: dict[str, Any], width: int, height: int) -> str:
    rows = []
    for w in (payload.get("weather") or [])[:12]:
        temp = ""
        if w.get("temp_min") is not None and w.get("temp_max") is not None:
            temp = f"{w.get('temp_min')}~{w.get('temp_max')}℃"
        rows.append(f"""
<section class="panel weather-card">
  <div class="weather-region">{esc(w.get("region"))}</div>
  <div class="weather-line">{esc(w.get("weather"))} {esc(temp)} · 자외선 {esc(w.get("uv_label"))} · 미세먼지 {esc(w.get("pm_label"))}</div>
</section>
""")
    body = f"""
<main class="page">
  {topbar()}
  <section class="section-title"><div class="section-icon">☀</div><h1>오늘의 지역별 날씨</h1></section>
  <section class="weather-grid">{''.join(rows)}</section>
  {footer()}
</main>
"""
    return shell(body, width, height)


def quote_page(payload: dict[str, Any], width: int, height: int) -> str:
    q = payload.get("quote") or {}
    body = f"""
<main class="page">
  {topbar()}
  <section class="section-title"><div class="section-icon">✦</div><h1>오늘의 명언</h1></section>
  <section class="panel quote-box">
    <div class="quote-text">“{esc(q.get("text"))}”</div>
    <div class="quote-author">— {esc(q.get("author"))}</div>
  </section>
  {footer()}
</main>
"""
    return shell(body, width, height)


async def render_html_to_png(html_content: str, output_path: Path, *, width: int, height: int, scale: int = 2) -> str:
    from playwright.async_api import async_playwright
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = output_path.with_suffix(".html")
    html_path.write_text(html_content, encoding="utf-8")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=scale)
        await page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        await page.screenshot(path=str(output_path), full_page=True, type="png")
        await browser.close()
    return str(output_path)


def build_overnight_cardnews_pages(payload: dict[str, Any], *, output_dir: str | Path) -> list[str]:
    output_dir = Path(output_dir)
    width = int(env("OVERNIGHT_IMAGE_WIDTH", "1080"))
    height = int(env("OVERNIGHT_IMAGE_HEIGHT", "1080"))
    scale = int(env("OVERNIGHT_IMAGE_SCALE", "2"))

    html_pages = [
        cover_page(payload, width, height),
        issue_page("미국뉴스 주요 이슈", "🇺🇸", payload.get("us_news") or [], width, height),
        market_page(payload, width, height),
        issue_page("국내뉴스 아침 이슈", "🇰🇷", payload.get("korea_news") or [], width, height),
        keyword_page(payload, width, height),
        sns_page(payload, width, height),
        weather_page(payload, width, height),
        quote_page(payload, width, height),
    ]

    async def run_all() -> list[str]:
        paths = []
        for idx, html_content in enumerate(html_pages, start=1):
            out = output_dir / f"overnight_hotissue_{idx:02d}.png"
            await render_html_to_png(html_content, out, width=width, height=height, scale=scale)
            paths.append(str(out))
        return paths

    return asyncio.run(run_all())
