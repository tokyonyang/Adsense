"""Blogger API v3 발행 모듈.

Google OAuth(refresh token) 인증을 사용합니다. wp_publisher.py와 동일한 article dict
형태({title, html, tags, category, ...})를 받아 Blogger 글로 변환해 올립니다.

필요한 환경변수:
  GOOGLE_OAUTH_CLIENT_ID
  GOOGLE_OAUTH_CLIENT_SECRET
  GOOGLE_OAUTH_REFRESH_TOKEN
  BLOGGER_BLOG_ID
  BLOGGER_DEFAULT_DRAFT (선택, true면 초안으로 저장. 기본 false = 즉시 게시)
"""

import os
import time

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
BLOGGER_API_BASE = "https://www.googleapis.com/blogger/v3"

_cached_token: dict = {"value": None, "expires_at": 0}


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


def create_blogger_post(article: dict, blog_id: str = None, is_draft: bool = None) -> dict:
    blog_id = (blog_id or os.environ.get("BLOGGER_BLOG_ID", "")).strip()
    if not blog_id:
        raise RuntimeError("BLOGGER_BLOG_ID가 필요합니다.")

    if is_draft is None:
        is_draft = _env_true("BLOGGER_DEFAULT_DRAFT", "false")

    labels: list = []
    for value in [article.get("category")] + list(article.get("tags") or []):
        value = str(value or "").strip()
        if value and value not in labels:
            labels.append(value)

    payload = {
        "kind": "blogger#post",
        "title": article.get("title") or article.get("keyword") or "제목 없음",
        "content": article.get("html") or "",
        "labels": labels[:20],
    }

    url = f"{BLOGGER_API_BASE}/blogs/{blog_id}/posts"
    params = {"isDraft": "true" if is_draft else "false"}
    res = requests.post(url, headers=_auth_headers(), params=params, json=payload, timeout=60)
    if res.status_code >= 400:
        raise RuntimeError(f"Blogger 글 발행 실패: {_friendly_blogger_error(res)}")
    return res.json()
