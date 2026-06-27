from __future__ import annotations

import html
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

KST = timezone(timedelta(hours=9))


def _weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def _domain(url: str | None) -> str:
    if not url:
        return "news"
    try:
        host = urlparse(url).netloc or urlparse(url).path
        host = host.replace("www.", "")
        return host[:28] or "news"
    except Exception:
        return "news"


def _category_color(category: str) -> str:
    return {
        "경제": "#f4c542",
        "증시": "#ff7a45",
        "정치": "#4d96ff",
        "사회": "#00c389",
        "국제": "#a66bff",
        "산업": "#ffb020",
        "생활": "#00b8d9",
        "IT": "#7a5af8",
        "스포츠": "#22c55e",
    }.get(category, "#f4c542")


def _icon(category: str) -> str:
    return {
        "경제": "₩",
        "증시": "↘",
        "정치": "🏛",
        "사회": "⚖",
        "국제": "🌐",
        "산업": "🏭",
        "생활": "☀",
        "IT": "AI",
        "스포츠": "⚽",
    }.get(category, "•")


def _clean(value: Any, limit: int | None = None) -> str:
    text = str(value or "").replace("...", "…").replace("⋯", "…")
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return html.escape(text)


def _keywords(items: list[dict[str, Any]], limit: int = 8) -> list[str]:
    result = []
    for item in items:
        for k in item.get("keywords") or []:
            k = str(k).strip()
            if k and k not in result:
                result.append(k)
            if len(result) >= limit:
                return result
    return result


def build_premium_headline_html(items: list[dict[str, Any]]) -> str:
    """
    v1.22:
    Pillow 직접 드로잉 대신 HTML/CSS로 고품질 카드 이미지를 구성합니다.
    Playwright가 이 HTML을 고해상도 PNG로 캡처합니다.
    """
    now = datetime.now(KST)
    cards = []
    for idx, item in enumerate(items[:8], start=1):
        category = str(item.get("category") or "주요")
        color = _category_color(category)
        headline = _clean(item.get("headline_text") or item.get("title"), 52)
        summaries = [s for s in (item.get("summaries") or []) if str(s).strip()]
        summaries = summaries[:2]
        while len(summaries) < 2:
            summaries.append("관련 이슈 확인 필요")

        source = _domain(item.get("url"))
        link_text = "원문 링크" if item.get("url") else "링크 없음"
        icon = item.get("icon") or _icon(category)

        card = f"""
        <section class="card" style="--accent:{color}">
          <div class="card-top">
            <div class="num">{idx}</div>
            <div class="pill">{html.escape(category)}</div>
          </div>
          <div class="card-body">
            <div class="headline">{headline}</div>
            <ul>
              <li>{_clean(summaries[0], 42)}</li>
              <li>{_clean(summaries[1], 42)}</li>
            </ul>
          </div>
          <div class="visual">
            <div class="orb">{html.escape(str(icon)[:3])}</div>
          </div>
          <div class="source">
            <span>출처: {html.escape(source)}</span>
            <span class="divider"></span>
            <span>{link_text} ↗</span>
          </div>
        </section>
        """
        cards.append(card)

    kws = _keywords(items)
    if not kws:
        kws = ["경제", "증시", "정책", "산업", "국제", "IT"]

    keyword_html = "".join(f"<span>{html.escape(k)}</span>" for k in kws[:8])

    return f"""
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<style>
  @font-face {{
    font-family: 'NanumGothic';
    src: local('NanumGothic');
  }}

  * {{
    box-sizing: border-box;
  }}

  body {{
    margin: 0;
    width: 1400px;
    height: 1980px;
    background:
      radial-gradient(circle at 20% 4%, rgba(246,197,66,0.18), transparent 23%),
      radial-gradient(circle at 83% 20%, rgba(255,122,69,0.12), transparent 23%),
      linear-gradient(180deg, #050505 0%, #0a0a0a 45%, #050505 100%);
    font-family: NanumGothic, 'Noto Sans CJK KR', 'Apple SD Gothic Neo', sans-serif;
    color: #f8f8f8;
    overflow: hidden;
  }}

  .page {{
    width: 1400px;
    height: 1980px;
    padding: 42px 42px 34px;
    position: relative;
  }}

  .page::before {{
    content: "";
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px);
    background-size: 48px 48px;
    mask-image: linear-gradient(180deg, rgba(0,0,0,0.6), transparent 80%);
    pointer-events: none;
  }}

  .header {{
    position: relative;
    display: grid;
    grid-template-columns: 1fr 330px;
    align-items: start;
    margin-bottom: 34px;
  }}

  .brand {{
    display: flex;
    align-items: center;
    gap: 24px;
  }}

  .newspaper {{
    width: 88px;
    height: 88px;
    border: 5px solid #f4c542;
    border-radius: 16px;
    transform: rotate(-9deg);
    position: relative;
    box-shadow: 0 0 28px rgba(246,197,66,0.25);
  }}

  .newspaper::before {{
    content: "";
    position: absolute;
    left: 16px;
    top: 18px;
    width: 46px;
    height: 8px;
    background: #f4c542;
    box-shadow: 0 18px 0 #f4c542, 0 36px 0 #f4c542;
  }}

  .title-main {{
    font-size: 76px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -4px;
  }}

  .title-main .gold {{
    color: #f4c542;
    text-shadow: 0 0 24px rgba(246,197,66,0.22);
  }}

  .subtitle {{
    margin-top: 14px;
    font-size: 28px;
    color: #f1d57b;
    letter-spacing: 8px;
    display: flex;
    align-items: center;
    gap: 22px;
  }}

  .subtitle::before,
  .subtitle::after {{
    content: "";
    display: block;
    width: 210px;
    height: 2px;
    background: linear-gradient(90deg, transparent, #f4c542, transparent);
  }}

  .date {{
    justify-self: end;
    border: 2px solid #f4c542;
    border-radius: 18px;
    padding: 22px 30px;
    color: #fff1b8;
    font-size: 34px;
    font-weight: 800;
    box-shadow: inset 0 0 22px rgba(246,197,66,0.08), 0 0 18px rgba(246,197,66,0.13);
  }}

  .grid {{
    position: relative;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 22px;
  }}

  .card {{
    height: 385px;
    position: relative;
    background:
      radial-gradient(circle at 82% 50%, color-mix(in srgb, var(--accent), transparent 83%), transparent 34%),
      linear-gradient(145deg, rgba(255,255,255,0.045), rgba(255,255,255,0.012));
    border: 2.5px solid rgba(246,197,66,0.88);
    border-radius: 24px;
    padding: 24px 26px 70px;
    overflow: hidden;
    box-shadow:
      0 24px 50px rgba(0,0,0,0.55),
      inset 0 0 0 1px rgba(255,255,255,0.055);
  }}

  .card::after {{
    content: "";
    position: absolute;
    left: 24px;
    right: 24px;
    bottom: 58px;
    height: 1px;
    background: linear-gradient(90deg, rgba(246,197,66,0.85), transparent);
  }}

  .card-top {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 26px;
  }}

  .num {{
    width: 78px;
    height: 78px;
    border: 2px solid #f4c542;
    border-radius: 14px;
    display: grid;
    place-items: center;
    font-size: 50px;
    font-weight: 900;
    color: #f4c542;
    font-family: Georgia, serif;
    background: rgba(0,0,0,0.25);
    box-shadow: 0 0 18px rgba(246,197,66,0.2);
  }}

  .pill {{
    border: 2px solid var(--accent);
    color: var(--accent);
    border-radius: 999px;
    padding: 7px 28px;
    font-size: 23px;
    font-weight: 900;
    background: rgba(0,0,0,0.24);
  }}

  .headline {{
    width: 475px;
    min-height: 94px;
    font-size: 37px;
    line-height: 1.32;
    letter-spacing: -1.8px;
    font-weight: 900;
    text-shadow: 0 2px 8px rgba(0,0,0,0.65);
  }}

  ul {{
    margin: 18px 0 0;
    padding: 0;
    list-style: none;
    width: 480px;
  }}

  li {{
    position: relative;
    margin: 12px 0;
    padding-left: 23px;
    font-size: 22px;
    line-height: 1.35;
    color: rgba(255,255,255,0.86);
    letter-spacing: -0.7px;
  }}

  li::before {{
    content: "";
    position: absolute;
    left: 0;
    top: 11px;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #f4c542;
    box-shadow: 0 0 12px rgba(246,197,66,0.55);
  }}

  .visual {{
    position: absolute;
    right: 38px;
    bottom: 112px;
  }}

  .orb {{
    width: 112px;
    height: 112px;
    border: 3px solid var(--accent);
    border-radius: 999px;
    display: grid;
    place-items: center;
    color: var(--accent);
    font-size: 42px;
    font-weight: 900;
    background:
      radial-gradient(circle, color-mix(in srgb, var(--accent), transparent 72%), transparent 68%),
      rgba(0,0,0,0.35);
    box-shadow: 0 0 26px color-mix(in srgb, var(--accent), transparent 55%);
  }}

  .source {{
    position: absolute;
    left: 28px;
    right: 28px;
    bottom: 20px;
    height: 32px;
    display: flex;
    align-items: center;
    gap: 18px;
    color: rgba(255,255,255,0.82);
    font-size: 20px;
    font-weight: 700;
  }}

  .divider {{
    width: 1px;
    height: 22px;
    background: rgba(246,197,66,0.7);
  }}

  .footer {{
    position: absolute;
    left: 42px;
    right: 42px;
    bottom: 34px;
    height: 92px;
    border: 2px solid #f4c542;
    border-radius: 20px;
    background: rgba(10,10,10,0.82);
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 0 22px;
    box-shadow: inset 0 0 20px rgba(246,197,66,0.05);
  }}

  .footer-label {{
    flex: 0 0 auto;
    border: 2px solid #f4c542;
    border-radius: 14px;
    padding: 14px 22px;
    font-size: 26px;
    font-weight: 900;
    color: #f4c542;
  }}

  .keywords {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }}

  .keywords span {{
    font-size: 22px;
    color: #f5f5f5;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(246,197,66,0.22);
  }}
</style>
</head>
<body>
  <main class="page">
    <header class="header">
      <div>
        <div class="brand">
          <div class="newspaper"></div>
          <div>
            <div class="title-main"><span>오늘의</span> <span class="gold">헤드라인 뉴스</span></div>
            <div class="subtitle">아침 브리핑</div>
          </div>
        </div>
      </div>
      <div class="date">📅 {now:%Y.%m.%d} ({_weekday_ko(now)})</div>
    </header>

    <section class="grid">
      {''.join(cards)}
    </section>

    <footer class="footer">
      <div class="footer-label">🔎 핵심 키워드</div>
      <div class="keywords">{keyword_html}</div>
    </footer>
  </main>
</body>
</html>
"""


async def _render_with_playwright(html_content: str, output_path: str | Path, *, scale: int = 2) -> str:
    from playwright.async_api import async_playwright

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_path = output_path.with_suffix(".html")
    html_path.write_text(html_content, encoding="utf-8")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": 1400, "height": 1980},
            device_scale_factor=scale,
        )
        await page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        await page.screenshot(path=str(output_path), full_page=True, type="png")
        await browser.close()

    return str(output_path)


def render_headline_news_image(
    headlines: list[dict[str, Any]],
    *,
    output_path: str | Path,
    title: str = "오늘의 헤드라인 뉴스",
) -> str:
    """
    고품질 HTML/CSS 기반 렌더링.
    Playwright가 없으면 명확히 실패시켜 workflow 로그에서 원인을 확인합니다.
    """
    import asyncio

    html_content = build_premium_headline_html(headlines)
    scale = 2
    try:
        scale = int(str(__import__("os").getenv("HEADLINE_IMAGE_SCALE", "2")))
    except Exception:
        scale = 2

    return asyncio.run(_render_with_playwright(html_content, output_path, scale=scale))
