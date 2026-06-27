from __future__ import annotations

import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

KST = timezone(timedelta(hours=9))


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
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


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int, max_lines: int) -> list[str]:
    words = str(text).split()
    if not words:
        return []

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

    if len(lines) < max_lines:
        lines.append(current)

    if len(lines) > max_lines:
        lines = lines[:max_lines]

    # 한국어처럼 띄어쓰기 단위가 부족할 때 대비
    fixed = []
    for line in lines:
        if draw.textbbox((0, 0), line, font=font)[2] <= max_width:
            fixed.append(line)
            continue

        buf = ""
        for ch in line:
            candidate = buf + ch
            if draw.textbbox((0, 0), candidate, font=font)[2] <= max_width:
                buf = candidate
            else:
                fixed.append(buf)
                buf = ch
                if len(fixed) >= max_lines:
                    break
        if len(fixed) < max_lines and buf:
            fixed.append(buf)

    lines = fixed[:max_lines]
    if lines:
        last = lines[-1]
        while draw.textbbox((0, 0), last + "…", font=font)[2] > max_width and len(last) > 1:
            last = last[:-1]
        lines[-1] = last + ("…" if last != str(text) and not str(text).startswith(last) else "")
    return lines[:max_lines]


def _draw_round_rect(draw, box, radius, outline, fill, width=2):
    draw.rounded_rectangle(box, radius=radius, outline=outline, fill=fill, width=width)


def _weekday_ko(dt: datetime) -> str:
    return "월화수목금토일"[dt.weekday()]


def _category_color(category: str) -> str:
    mapping = {
        "경제": "#F6C344",
        "증시": "#FF7A45",
        "정치": "#4D96FF",
        "사회": "#00C389",
        "국제": "#A66BFF",
        "산업": "#FFB020",
        "생활": "#00B8D9",
        "IT": "#7A5AF8",
        "스포츠": "#22C55E",
    }
    return mapping.get(category, "#F6C344")


def render_headline_news_image(
    headlines: list[dict[str, Any]],
    *,
    output_path: str | Path,
    title: str = "오늘의 헤드라인 뉴스",
) -> str:
    output_path = str(output_path)
    W, H = 1400, 2100
    bg = "#090909"
    gold = "#F6C344"
    panel = "#101010"
    white = "#F7F7F7"
    muted = "#D2D2D2"

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    title_font = _font(74, bold=True)
    title_font_y = _font(74, bold=True)
    sub_font = _font(30, bold=False)
    date_font = _font(34, bold=True)
    tile_num_font = _font(42, bold=True)
    tile_title_font = _font(30, bold=True)
    tile_summary_font = _font(21, bold=False)
    keyword_title_font = _font(28, bold=True)
    keyword_font = _font(24, bold=False)

    pad = 28
    # Header
    draw.text((pad, 30), "오늘의 ", font=title_font, fill=white)
    x2 = draw.textbbox((pad, 30), "오늘의 ", font=title_font)[2]
    draw.text((x2, 30), "헤드라인 뉴스", font=title_font_y, fill=gold)
    draw.text((740, 52), "아침 브리핑", font=sub_font, fill=white)

    now = datetime.now(KST)
    date_box = (980, 26, W - pad, 102)
    _draw_round_rect(draw, date_box, 20, gold, "#111111", 3)
    draw.text((1005, 44), f"📅 {now:%Y.%m.%d} ({_weekday_ko(now)})", font=date_font, fill=white)

    # Grid
    start_y = 120
    footer_h = 120
    grid_h = H - start_y - footer_h - 30
    gap = 18
    cols = 2
    rows = 5
    tile_w = (W - pad * 2 - gap) // 2
    tile_h = (grid_h - gap * (rows - 1)) // rows

    max_items = min(10, len(headlines))
    items = headlines[:max_items]

    for idx, item in enumerate(items):
        row = idx // 2
        col = idx % 2
        x = pad + col * (tile_w + gap)
        y = start_y + row * (tile_h + gap)
        box = (x, y, x + tile_w, y + tile_h)
        _draw_round_rect(draw, box, 18, gold, panel, 3)

        # number badge
        num_box = (x + 16, y + 16, x + 74, y + 74)
        _draw_round_rect(draw, num_box, 12, gold, "#161616", 2)
        n_text = str(idx + 1)
        nb = draw.textbbox((0, 0), n_text, font=tile_num_font)
        draw.text((num_box[0] + (58 - (nb[2]-nb[0]))/2, num_box[1] + 6), n_text, font=tile_num_font, fill=gold)

        category = item.get("category", "주요")
        cat_color = _category_color(category)
        cat_box = (x + tile_w - 130, y + 18, x + tile_w - 18, y + 56)
        _draw_round_rect(draw, cat_box, 16, cat_color, "#151515", 2)
        cb = draw.textbbox((0, 0), category, font=_font(20, bold=True))
        draw.text((cat_box[0] + (112 - (cb[2]-cb[0]))/2, cat_box[1] + 7), category, font=_font(20, bold=True), fill=cat_color)

        title_text = item.get("short_title") or item.get("title") or ""
        title_lines = _wrap_text(draw, title_text, tile_title_font, tile_w - 44, 2)
        title_y = y + 88
        for line in title_lines:
            draw.text((x + 22, title_y), line, font=tile_title_font, fill=gold if len(title_lines)==1 else white)
            title_y += 36

        # emphasis line
        if item.get("highlight"):
            hi_lines = _wrap_text(draw, item["highlight"], _font(24, bold=True), tile_w - 44, 2)
            for line in hi_lines:
                draw.text((x + 22, title_y), line, font=_font(24, bold=True), fill=gold)
                title_y += 30

        # simple icon circle
        circle_color = cat_color
        cx, cy = x + tile_w - 110, y + tile_h - 82
        draw.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), outline=circle_color, fill="#151515", width=3)
        icon = item.get("icon", "•")
        ibox = draw.textbbox((0,0), icon, font=_font(44, bold=True))
        draw.text((cx - (ibox[2]-ibox[0])/2, cy - 28), icon, font=_font(44, bold=True), fill=circle_color)

        # summary bullets
        bullet_y = y + 150
        if item.get("highlight"):
            bullet_y += 40
        bullet_max_y = y + tile_h - 30
        for summary in item.get("summaries", [])[:3]:
            lines = _wrap_text(draw, summary, tile_summary_font, tile_w - 160, 2)
            if not lines:
                continue
            if bullet_y + len(lines) * 28 > bullet_max_y:
                break
            draw.ellipse((x + 24, bullet_y + 9, x + 32, bullet_y + 17), fill=gold)
            ly = bullet_y
            for li, line in enumerate(lines):
                draw.text((x + 42, ly), line, font=tile_summary_font, fill=muted)
                ly += 25
            bullet_y = ly + 10

    # footer keywords
    foot_box = (pad, H - footer_h, W - pad, H - 24)
    _draw_round_rect(draw, foot_box, 16, gold, "#0E0E0E", 3)
    tag_box = (pad + 18, H - footer_h + 18, pad + 230, H - 42)
    _draw_round_rect(draw, tag_box, 14, gold, "#151515", 2)
    draw.text((tag_box[0] + 16, tag_box[1] + 12), "🏷 핵심 키워드", font=keyword_title_font, fill=gold)

    kw = []
    for item in items:
        for k in item.get("keywords", []):
            if k not in kw:
                kw.append(k)
    kw_text = " / ".join(kw[:10]) if kw else "주요 이슈 / 경제 / 증시 / 산업 / 정책"
    kw_lines = _wrap_text(draw, kw_text, keyword_font, W - 330, 3)
    y0 = H - footer_h + 22
    for line in kw_lines:
        draw.text((pad + 260, y0), line, font=keyword_font, fill=white)
        y0 += 28

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, format="PNG", optimize=True)
    return output_path
