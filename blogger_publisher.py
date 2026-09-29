"""Blogger API v3 발행 모듈.

Google OAuth(refresh token) 인증을 사용합니다. wp_publisher.py와 동일한 article dict
형태({title, html, tags, category, slug, ...})를 받아 Blogger 글로 변환해 올립니다.

필요한 환경변수:
  GOOGLE_OAUTH_CLIENT_ID
  GOOGLE_OAUTH_CLIENT_SECRET
  GOOGLE_OAUTH_REFRESH_TOKEN
  BLOGGER_BLOG_ID
  BLOGGER_DEFAULT_DRAFT (선택, true면 초안으로 저장. 기본 false = 즉시 게시)
  BLOGGER_ENGLISH_PERMALINK (선택, 기본 true. article["slug"]로 영문 URL 생성)
  BLOGGER_MAX_LABELS (선택, 기본 3. 카테고리 포함 라벨 최대 개수)

애드센스 심사 대응 가드:
  - 본문에 "[... 삽입]" 같은 자리표시자가 남아 있으면 공개하지 않고 초안으로 저장합니다.
  - 한글 제목만으로 게시하면 URL이 "ai.html", "blog-post_126.html"처럼 의미 없게 생성되므로,
    영문 슬러그 제목으로 먼저 게시해 URL을 고정한 뒤 실제 한글 제목으로 바꿉니다.
  - 라벨이 글마다 10개 이상 붙으면 얇은 라벨 페이지가 대량으로 생기므로 개수를 제한합니다.
"""

import os
import re
import time

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
BLOGGER_API_BASE = "https://www.googleapis.com/blogger/v3"

_cached_token: dict = {"value": None, "expires_at": 0}

# 생성 프롬프트가 남기는 자리표시자. 공개되면 '미완성/자동 생성 글'로 보여 심사에 불리합니다.
PLACEHOLDER_PATTERNS = [
    r"\[[^\]\n]{0,60}삽입[^\]\n]{0,30}\]",
    r"\[[^\]\n]{0,60}확인 후[^\]\n]{0,30}\]",
    r"\bTODO\b",
    r"lorem ipsum",
]


def _env_true(name: str, default: str = "false") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_access_token() -> str:
    now = time.time()
    if _cached_token["value"] and now < _cached_token["expires_at"] - 60:
        return _cached_token["value"]

    client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "").strip()
    client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("GOOGLE_OAUTH_REFRESH_TOKEN", "").strip()
    if not client_id or not client_secret or not refresh_token:
        raise RuntimeError(
            "GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET, GOOGLE_OAUTH_REFRESH_TOKEN이 필요합니다."
        )

    res = requests.post(
        TOKEN_URL,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        },
        timeout=30,
    )
    if res.status_code >= 400:
        raise RuntimeError(f"Google OAuth 토큰 갱신 실패: HTTP {res.status_code}. {res.text[:300]}")

    data = res.json()
    access_token = data.get("access_token")
    if not access_token:
        raise RuntimeError(f"Google OAuth 응답에 access_token이 없습니다: {data}")

    _cached_token["value"] = access_token
    _cached_token["expires_at"] = now + int(data.get("expires_in", 3000))
    return access_token


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {_get_access_token()}", "Content-Type": "application/json"}


def _friendly_blogger_error(res: requests.Response) -> str:
    try:
        data = res.json()
        message = (data.get("error") or {}).get("message", "") if isinstance(data, dict) else ""
    except Exception:
        message = res.text[:300]

    if res.status_code in (401, 403):
        return (
            "Blogger 인증/권한 오류입니다. GOOGLE_OAUTH_REFRESH_TOKEN이 블로그 소유 계정으로 발급됐는지, "
            "Google Cloud 프로젝트에서 Blogger API가 활성화됐는지 확인해주세요. "
            f"원문: {message}"
        )
    if res.status_code == 404:
        return f"BLOGGER_BLOG_ID를 찾을 수 없습니다. 값을 다시 확인해주세요. 원문: {message}"
    return f"HTTP {res.status_code}: {message or res.reason}"


def find_placeholders(html: str) -> list:
    """본문에 남은 자리표시자 문구를 찾아 반환합니다 (없으면 빈 리스트)."""
    found = []
    for pattern in PLACEHOLDER_PATTERNS:
        for m in re.finditer(pattern, html or "", flags=re.IGNORECASE):
            found.append(m.group(0))
    return found


def _english_slug_title(slug: str) -> str:
    """영문 슬러그를 URL 생성용 임시 제목으로 바꿉니다. 영문 슬러그가 아니면 빈 문자열."""
    slug = str(slug or "").strip().lower()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or not re.search(r"[a-z]", slug):
        return ""
    return " ".join(slug.split("-")[:7])


def _build_labels(article: dict) -> list:
    max_labels = int(os.environ.get("BLOGGER_MAX_LABELS", "3"))
    labels: list = []
    for value in [article.get("category")] + list(article.get("tags") or []):
        value = str(value or "").strip()
        if value and value not in labels:
            labels.append(value)
    return labels[:max(1, max_labels)]


def list_recent_posts(blog_id: str = None, max_results: int = 15) -> list:
    blog_id = (blog_id or os.environ.get("BLOGGER_BLOG_ID", "")).strip()
    if not blog_id:
        raise RuntimeError("BLOGGER_BLOG_ID가 필요합니다.")

    url = f"{BLOGGER_API_BASE}/blogs/{blog_id}/posts"
    params = {"maxResults": max_results, "orderBy": "published", "fetchBodies": "false", "status": "live"}
    res = requests.get(url, headers=_auth_headers(), params=params, timeout=30)
    if res.status_code >= 400:
        raise RuntimeError(f"Blogger 글 목록 조회 실패: {_friendly_blogger_error(res)}")
    return res.json().get("items", []) or []


def _patch_post(blog_id: str, post_id: str, body: dict) -> dict:
    url = f"{BLOGGER_API_BASE}/blogs/{blog_id}/posts/{post_id}"
    res = requests.patch(url, headers=_auth_headers(), json=body, timeout=60)
    if res.status_code >= 400:
        raise RuntimeError(f"Blogger 글 수정 실패: {_friendly_blogger_error(res)}")
    return res.json()


def _revert_to_draft(blog_id: str, post_id: str) -> None:
    url = f"{BLOGGER_API_BASE}/blogs/{blog_id}/posts/{post_id}/revert"
    try:
        requests.post(url, headers=_auth_headers(), timeout=30)
    except Exception:
        pass


def create_blogger_post(article: dict, blog_id: str = None, is_draft: bool = None) -> dict:
    blog_id = (blog_id or os.environ.get("BLOGGER_BLOG_ID", "")).strip()
    if not blog_id:
        raise RuntimeError("BLOGGER_BLOG_ID가 필요합니다.")

    if is_draft is None:
        is_draft = _env_true("BLOGGER_DEFAULT_DRAFT", "false")

    html = article.get("html") or ""
    placeholders = find_placeholders(html)
    if placeholders and not is_draft:
        # 미완성 흔적이 있는 글은 절대 공개하지 않고 초안으로 돌립니다.
        is_draft = True

    title = article.get("title") or article.get("keyword") or "제목 없음"
    slug_title = ""
    if not is_draft and _env_true("BLOGGER_ENGLISH_PERMALINK", "true"):
        slug_title = _english_slug_title(article.get("slug"))

    payload = {
        "kind": "blogger#post",
        "title": slug_title or title,
        "content": html,
        "labels": _build_labels(article),
    }

    url = f"{BLOGGER_API_BASE}/blogs/{blog_id}/posts"
    params = {"isDraft": "true" if is_draft else "false"}
    res = requests.post(url, headers=_auth_headers(), params=params, json=payload, timeout=60)
    if res.status_code >= 400:
        raise RuntimeError(f"Blogger 글 발행 실패: {_friendly_blogger_error(res)}")
    result = res.json()

    if slug_title:
        # URL은 최초 게시 제목(영문)으로 고정됐으니 실제 한글 제목으로 교체합니다.
        try:
            result = _patch_post(blog_id, result["id"], {"title": title})
        except Exception as exc:
            # 영문 임시 제목이 공개된 채로 남지 않도록 초안으로 되돌립니다.
            _revert_to_draft(blog_id, result.get("id", ""))
            raise RuntimeError(f"제목 교체 실패로 글을 초안으로 되돌렸습니다: {exc}") from exc

    result["draft_reason"] = (
        f"자리표시자 {len(placeholders)}건 발견: {placeholders[:3]}" if placeholders else ""
    )
    return result
