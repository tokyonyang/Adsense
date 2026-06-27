from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

KST = timezone(timedelta(hours=9))


def _font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf" if bold else "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap_text(draw, text: str, font, max_width: int, max_lines: int):
    text = str(text or "").strip()
    if not text:
        return []
    words = text.split()
    if not words:
        words = [text]

    lines = []
    current = words[0]

    for word in words[1:]:
        candidate = current + " " + word
        if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
            if len(lines) >= max_lines:
                break

    if len(lines) < max_lines and current:
        lines.append(current)

    fixed = []
    for line in lines[:max_lines]:
        if draw.textbbox((0, 0), line, font=font)[2] <= max_width:
            fixed.append(line)
        else:
            buf = ""
            for ch in line:
                cand = buf + ch
                if draw.textbbox((0, 0), cand, font=font)[2] <= max_width:
                    buf = cand
                else:
                    if buf:
                        fixed.append(buf)
                    buf = ch
                    if len(fixed) >= max_lines:
                        break
            if buf and len(fixed) < max_lines:
                fixed.append(buf)
    return fixed[:max_lines]


def _draw_round_rect(draw, box, radius, outline, fill, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def _weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def _category_color(category: str) -> str:
    return {
        "경제": "#F6C344",
        "증시": "#FF7A45",
        "정치": "#4D96FF",
        "사회": "#00C389",
        "국제": "#A66BFF",
        "산업": "#FFB020",
        "생활": "#00B8D9",
        "IT": "#7A5AF8",
        "스포츠": "#22C55E",
    }.get(category, "#F6C344")


def _clean_card_summary(text: str) -> str:
    text = str(text or "").strip()
    ban = [
        "세부 내용 확인 필요",
        "후속 기사 확인 필요",
        "분야 주요 이슈",
        "주요 이슈",
        "상세 내용은 본문 기사 확인 필요",
    ]
    for b in ban:
        text = text.replace(b, "")
    text = text.strip(" -·ㆍ|")
    return text


def _fallback_card_summaries(item: dict[str, Any]) -> list[str]:
    category = item.get("category", "주요")
    source = item.get("source", "")
    published_at = item.get("published_at")

    lines = []
    if item.get("description"):
        lines.append(str(item["description"])[:26].rstrip("…") + ("…" if len(str(item["description"])) > 26 else ""))

    keywords = item.get("keywords") or []
    if keywords:
        lines.append("핵심: " + ", ".join(str(k) for k in keywords[:3]))

    if published_at:
        try:
            time_text = published_at.strftime("%m/%d %H:%M")
            lines.append(f"{category} · {time_text}")
        except Exception:
            pass

    if source:
        lines.append(f"출처: {source}")

    result = []
    for line in lines:
        line = _clean_card_summary(line)
        if line and line not in result:
            result.append(line)

    if not result:
        result = [f"{category} 핵심 이슈", "관련 기사 확인"]

    return result[:3]


def render_headline_news_image(headlines: list[dict[str, Any]], *, output_path: str | Path, title: str = "오늘의 헤드라인 뉴스") -> str:
    W, H = 1400, 2100
    bg = "#090909"
    gold = "#F6C344"
    panel = "#101010"
    white = "#F7F7F7"
    muted = "#D2D2D2"

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    title_font = _font(74, bold=True)
    sub_font = _font(30, bold=False)
    date_font = _font(34, bold=True)
    tile_num_font = _font(42, bold=True)
    tile_title_font = _font(30, bold=True)
    tile_summary_font = _font(21, bold=False)
    keyword_title_font = _font(28, bold=True)
    keyword_font = _font(24, bold=False)

    pad = 28
    draw.text((pad, 30), "오늘의 ", font=title_font, fill=white)
    x2 = draw.textbbox((pad, 30), "오늘의 ", font=title_font)[2]
    draw.text((x2, 30), "헤드라인 뉴스", font=title_font, fill=gold)
    draw.text((740, 52), "아침 브리핑", font=sub_font, fill=white)

    now = datetime.now(KST)
    date_box = (980, 26, W - pad, 102)
    _draw_round_rect(draw, date_box, 20, gold, "#111111", 3)
    draw.text((1005, 44), f"📅 {now:%Y.%m.%d} ({_weekday_ko(now)})", font=date_font, fill=white)

    start_y = 120
    footer_h = 120
    grid_h = H - start_y - footer_h - 30
    gap = 18
    rows = 5
    tile_w = (W - pad * 2 - gap) // 2
    tile_h = (grid_h - gap * (rows - 1)) // rows

    items = headlines[:10]
    for idx, item in enumerate(items):
        row = idx // 2
        col = idx % 2
        x = pad + col * (tile_w + gap)
        y = start_y + row * (tile_h + gap)
        box = (x, y, x + tile_w, y + tile_h)
        _draw_round_rect(draw, box, 18, gold, panel, 3)

        num_box = (x + 16, y + 16, x + 74, y + 74)
        _draw_round_rect(draw, num_box, 12, gold, "#161616", 2)
        n_text = str(idx + 1)
        nb = draw.textbbox((0, 0), n_text, font=tile_num_font)
        draw.text((num_box[0] + (58 - (nb[2]-nb[0]))/2, num_box[1] + 6), n_text, font=tile_num_font, fill=gold)

        category = item.get("category", "주요")
        cat_color = _category_color(category)
        cat_box = (x + tile_w - 130, y + 18, x + tile_w - 18, y + 56)
        _draw_round_rect(draw, cat_box, 16, cat_color, "#151515", 2)
        draw.text((cat_box[0] + 18, cat_box[1] + 7), category, font=_font(20, bold=True), fill=cat_color)

        headline = item.get("headline_text") or item.get("short_title") or item.get("title") or ""
        title_lines = _wrap_text(draw, headline, tile_title_font, tile_w - 44, 2)
        ty = y + 88
        for line in title_lines:
            draw.text((x + 22, ty), line, font=tile_title_font, fill=white)
            ty += 36

        highlight = str(item.get("highlight") or "").strip()
        if highlight:
            hi_lines = _wrap_text(draw, highlight, _font(24, bold=True), tile_w - 44, 2)
            for line in hi_lines:
                draw.text((x + 22, ty), line, font=_font(24, bold=True), fill=gold)
                ty += 30

        cx, cy = x + tile_w - 110, y + tile_h - 82
        draw.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), outline=cat_color, fill="#151515", width=3)
        icon = item.get("icon", "•")
        draw.text((cx - 22, cy - 26), icon, font=_font(36, bold=True), fill=cat_color)

        raw_summaries = item.get("summaries") or []
        summaries = []
        for s in raw_summaries:
            cleaned = _clean_card_summary(s)
            if cleaned and cleaned not in summaries:
                summaries.append(cleaned)

        if not summaries:
            summaries = _fallback_card_summaries(item)

        bullet_y = y + 150 + (40 if highlight else 0)
        max_y = y + tile_h - 30
        for summary in summaries[:3]:
            lines = _wrap_text(draw, summary, tile_summary_font, tile_w - 160, 2)
            if not lines or bullet_y + len(lines) * 28 > max_y:
                break
            draw.ellipse((x + 24, bullet_y + 9, x + 32, bullet_y + 17), fill=gold)
            ly = bullet_y
            for line in lines:
                draw.text((x + 42, ly), line, font=tile_summary_font, fill=muted)
                ly += 25
            bullet_y = ly + 10

    foot_box = (pad, H - footer_h, W - pad, H - 24)
    _draw_round_rect(draw, foot_box, 16, gold, "#0E0E0E", 3)
    tag_box = (pad + 18, H - footer_h + 18, pad + 230, H - 42)
    _draw_round_rect(draw, tag_box, 14, gold, "#151515", 2)
    draw.text((tag_box[0] + 16, tag_box[1] + 12), "🏷 핵심 키워드", font=keyword_title_font, fill=gold)

    kw = []
    for item in items:
        for k in item.get("keywords", []):
            if k and k not in kw:
                kw.append(k)
    kw_text = " / ".join(kw[:10]) if kw else "경제 / 증시 / 정책 / 산업 / 국제 / IT"
    for i, line in enumerate(_wrap_text(draw, kw_text, keyword_font, W - 330, 3)):
        draw.text((pad + 260, H - footer_h + 22 + i * 28), line, font=keyword_font, fill=white)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", optimize=True)
    return str(output_path)
