from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


REFERENCE_SEED_PACKS = {
    "economic_newspaper": [
        ("경제·금융", "등록임대 집값 안정 전세난"),
        ("경제·금융", "전세값 상승 전세난 임대차"),
        ("산업·기업", "카카오뱅크 인수합병 종합금융플랫폼"),
        ("산업·기업", "현대차 노조 파업 임금협상"),
        ("증권·투자", "미국 증시 애플 급락 나스닥 하락"),
        ("산업·기업", "SK하이닉스 이직률 꿈의 직장 반도체 인력"),
        ("산업·기업", "마이크론 실적 반도체 업황 회복"),
        ("정책·지원금", "정부 등록임대 제도 전세난 집값 안정"),
        ("부동산·주거금융", "서울 아파트 전셋값 13년 최대 상승"),
        ("부동산·주거금융", "동탄 집값 급등 전국 상승률"),
    ],
    "stock_finance": [
        ("증권·투자", "마이크론 실적 뉴욕증시 반도체"),
        ("경제·금융", "미국 PCE 물가 인플레이션 금리"),
        ("증권·투자", "원화 약세 반도체 백화점 철강 석유화학 양극화"),
        ("증권·투자", "개인 투자자 빚투 증권사 신규 대출 중단"),
        ("경제·금융", "비은행 예금 유출 유동성 경고"),
        ("경제·금융", "은행 주택담보대출 한도 축소"),
        ("정책·지원금", "국민성장펀드 AI 전력망 반도체 지원"),
        ("증권·투자", "단일 종목 2배 레버리지 투자 위험"),
        ("경제·금융", "미실현 이익 과세 포괄 과세론"),
    ],
    "international": [
        ("국제", "베네수엘라 강진 사망 부상 도시 붕괴"),
        ("국제", "호르무즈 해협 이란 미국 긴장 화물선 피격"),
        ("국제", "미국 한국 반도체 핵심 광물 공급망 파트너"),
        ("국제", "유럽 폭염 프랑스 최고 기온 사망"),
        ("산업·기업", "애플 메모리 가격 상승 제품 가격 인상"),
    ],
    "politics_social": [
        ("시사·정치", "이재명 이재용 호남 반도체 클러스터"),
        ("시사·정치", "문재인 오찬 당내 갈등 봉합"),
        ("시사·정치", "총리 후보자 청문회 여야 공방"),
        ("시사·정치", "검찰 보완수사권 폐지 국회 입법"),
        ("시사·정치", "국민의힘 당대표 경선 내홍"),
        ("사회·사건", "리튬 배터리 지하철 반입 금지"),
        ("건강·의료", "필수의료 3.6조 MRI CT 수가 인하"),
        ("사회·사건", "AI 대포통장 유통 경찰 국세청 은행 정보 공유"),
        ("사회·사건", "불법 사채 성착취 20대 여성 사건"),
        ("사회·사건", "검찰 보완수사권 폐지 국회"),
    ],
    "it_science_life": [
        ("산업·기업", "IBM 1나노 이하 반도체 나노스택"),
        ("산업·기업", "네이버 AI탭 대화형 검색 출시"),
        ("산업·기업", "누리호 5호 발사 위성 15기"),
        ("산업·기업", "오픈AI 자체 AI 반도체 데이터센터"),
        ("산업·기업", "SKT SK하이닉스 AI 투자 법인 출자"),
        ("생활·제도", "전국 소나기 우박 장마 지연 농민 걱정"),
        ("건강·의료", "구강 건강 뇌 심장 건강"),
        ("생활·제도", "교통카드 절약 팁 생활비"),
        ("생활·제도", "전통시장 외국인 핫플 광장시장"),
    ],
}


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def enabled() -> bool:
    return env("HOT_ISSUE_USE_REFERENCE_HEADLINES", "true").lower() in {"1", "true", "yes", "y", "on"}


def parse_reference_text(text: str) -> list[tuple[str, str]]:
    """사용자가 붙여넣은 주요신문 헤드라인 텍스트를 간단히 seed로 변환합니다."""
    if not text.strip():
        return []

    current_category = "기타"
    category_map = {
        "경제": "경제·금융",
        "사회": "사회·사건",
        "국제": "국제",
        "정치": "시사·정치",
        "증권": "증권·투자",
        "금융": "경제·금융",
        "부동산": "부동산·주거금융",
        "IT": "산업·기업",
        "과학": "산업·기업",
        "생활": "생활·제도",
        "문화": "생활·제도",
        "날씨": "날씨·안전",
    }

    seeds: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip(" \t•-*")
        if not line:
            continue

        header = re.sub(r"[<>\s/]+", "", line)
        for k, v in category_map.items():
            if header == k or header.startswith(k):
                current_category = v
                break

        if len(line) < 12:
            continue
        if line.startswith("<") and line.endswith(">"):
            continue

        # 너무 긴 문장은 키워드형으로 압축
        line = re.sub(r"\s+", " ", line)
        line = re.sub(r"[\"'“”‘’]", "", line)
        words = re.findall(r"[가-힣A-Za-z0-9·.%]+", line)
        query = " ".join(words[:12])
        if query:
            seeds.append((current_category, query))

    return seeds[:60]


def load_reference_headline_seeds() -> list[tuple[str, str]]:
    if not enabled():
        return []

    seeds: list[tuple[str, str]] = []

    mode = env("HOT_ISSUE_REFERENCE_PACKS", "economic_newspaper,stock_finance,international,politics_social,it_science_life")
    for pack_name in [x.strip() for x in mode.split(",") if x.strip()]:
        seeds.extend(REFERENCE_SEED_PACKS.get(pack_name, []))

    env_text = env("HOT_ISSUE_REFERENCE_HEADLINES_TEXT", "")
    seeds.extend(parse_reference_text(env_text))

    path = Path(env("HOT_ISSUE_REFERENCE_HEADLINES_FILE", "data/morning_reference_headlines.txt"))
    if path.exists():
        try:
            seeds.extend(parse_reference_text(path.read_text(encoding="utf-8")))
        except Exception:
            pass

    # 중복 제거
    seen = set()
    unique = []
    for category, query in seeds:
        key = re.sub(r"[^0-9a-zA-Z가-힣]", "", query.lower())[:80]
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append((category, query))

    return unique
