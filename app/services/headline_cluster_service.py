from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any
from urllib.parse import urlparse


STOPWORDS = {
    "오늘", "뉴스", "속보", "종합", "단독", "기자", "관련", "주요", "오전", "오후",
    "있는", "없는", "한다", "했다", "위해", "대한", "이번", "내일", "최근",
    "으로", "에서", "까지", "부터", "그리고", "하지만", "관련해", "밝혀",
}


@dataclass
class HeadlineArticle:
    category: str
    title: str
    description: str = ""
    url: str = ""
    published_at: Any = None
    source: str = ""
    query: str = ""

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        if isinstance(self.published_at, datetime):
            data["published_at"] = self.published_at.isoformat()
        return data


@dataclass
class HeadlineCluster:
    cluster_id: str
    category: str
    representative_title: str
    articles: list[dict[str, Any]]
    score: float
    keywords: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def clean_text(text: str) -> str:
    text = str(text or "")
    text = re.sub(r"<[^>]+>", "", text)
    text = text.replace("&quot;", '"').replace("&amp;", "&").replace("...", "…").replace("⋯", "…")
    text = re.sub(r"\[[^\]]{1,30}\]", "", text)
    text = re.sub(r"\([^)]{1,30}\)$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -·ㆍ|")


def tokenize(text: str) -> set[str]:
    text = clean_text(text).lower()
    raw = re.findall(r"[가-힣A-Za-z0-9]{2,}", text)
    tokens = []
    for token in raw:
        if token in STOPWORDS:
            continue
        if len(token) <= 1:
            continue
        tokens.append(token)
    return set(tokens)


def article_domain(url: str) -> str:
    if not url:
        return "news"
    try:
        host = urlparse(url).netloc or urlparse(url).path
        return host.replace("www.", "")[:32] or "news"
    except Exception:
        return "news"


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / max(1, len(a | b))


def article_similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
    a_title = tokenize(a.get("title", ""))
    b_title = tokenize(b.get("title", ""))
    a_full = tokenize((a.get("title", "") or "") + " " + (a.get("description", "") or ""))
    b_full = tokenize((b.get("title", "") or "") + " " + (b.get("description", "") or ""))

    title_score = jaccard(a_title, b_title)
    full_score = jaccard(a_full, b_full)

    category_bonus = 0.12 if a.get("category") == b.get("category") else 0.0
    domain_penalty = -0.04 if article_domain(a.get("url")) == article_domain(b.get("url")) else 0.0

    return min(1.0, max(0.0, title_score * 0.62 + full_score * 0.38 + category_bonus + domain_penalty))


def extract_keywords_from_articles(articles: list[dict[str, Any]], limit: int = 5) -> list[str]:
    counts = Counter()
    for article in articles:
        text = f"{article.get('title','')} {article.get('description','')}"
        for token in tokenize(text):
            if len(token) > 12:
                continue
            counts[token] += 1

    return [word for word, _ in counts.most_common(limit)]


def cluster_articles(
    articles: list[dict[str, Any]],
    *,
    max_clusters: int = 5,
    min_cluster_size: int = 2,
    similarity_threshold: float = 0.24,
) -> list[dict[str, Any]]:
    """
    제목/설명 기반으로 유사 기사를 묶습니다.
    - 같은 이슈의 중복 기사들을 하나의 headline cluster로 통합
    - 대표 이슈는 기사 수 + 최신성 + description 보유 여부로 정렬
    """
    normalized = []
    seen_exact = set()

    for item in articles:
        title = clean_text(item.get("title", ""))
        if not title:
            continue

        key = re.sub(r"[^0-9a-zA-Z가-힣]", "", title.lower())[:120]
        if key in seen_exact:
            continue
        seen_exact.add(key)

        normalized.append({
            **item,
            "title": title,
            "description": clean_text(item.get("description", "")),
        })

    clusters: list[list[dict[str, Any]]] = []

    for item in normalized:
        best_idx = None
        best_score = 0.0

        for idx, cluster in enumerate(clusters):
            # 대표 3개와 비교
            scores = [article_similarity(item, existing) for existing in cluster[:3]]
            score = max(scores) if scores else 0.0
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is not None and best_score >= similarity_threshold:
            clusters[best_idx].append(item)
        else:
            clusters.append([item])

    # 1개짜리 클러스터도 허용하되, 2개 이상 클러스터를 우선
    def cluster_score(cluster: list[dict[str, Any]]) -> float:
        size_score = min(len(cluster), 5) * 10
        desc_score = sum(1 for x in cluster if x.get("description")) * 0.8
        naver_score = sum(1 for x in cluster if x.get("source") == "naver") * 0.7
        recent_score = 0.0

        for x in cluster[:5]:
            published = x.get("published_at")
            if isinstance(published, datetime):
                recent_score += published.timestamp() / 10_000_000_000

        return size_score + desc_score + naver_score + recent_score

    clusters.sort(key=cluster_score, reverse=True)

    output = []
    for idx, cluster in enumerate(clusters):
        if len(output) >= max_clusters:
            break

        if len(cluster) < min_cluster_size and len(output) < max_clusters - 1:
            # 초반에는 단독 이슈보다 묶음 이슈 우선
            continue

        cluster.sort(
            key=lambda x: (
                0 if x.get("description") else 1,
                0 if x.get("source") == "naver" else 1,
                -(x.get("published_at").timestamp() if isinstance(x.get("published_at"), datetime) else 0),
            )
        )

        rep = cluster[0]
        keywords = extract_keywords_from_articles(cluster, limit=5)
        output.append(HeadlineCluster(
            cluster_id=f"headline-cluster-{len(output)+1}",
            category=rep.get("category", "주요"),
            representative_title=rep.get("title", ""),
            articles=cluster[:3],
            score=cluster_score(cluster),
            keywords=keywords,
        ).to_dict())

    # 부족하면 단독 클러스터로 보충
    if len(output) < max_clusters:
        used_titles = {x["representative_title"] for x in output}
        for cluster in clusters:
            if len(output) >= max_clusters:
                break
            cluster.sort(key=lambda x: -(x.get("published_at").timestamp() if isinstance(x.get("published_at"), datetime) else 0))
            rep = cluster[0]
            if rep.get("title") in used_titles:
                continue
            keywords = extract_keywords_from_articles(cluster, limit=5)
            output.append(HeadlineCluster(
                cluster_id=f"headline-cluster-{len(output)+1}",
                category=rep.get("category", "주요"),
                representative_title=rep.get("title", ""),
                articles=cluster[:3],
                score=cluster_score(cluster),
                keywords=keywords,
            ).to_dict())

    return output[:max_clusters]
