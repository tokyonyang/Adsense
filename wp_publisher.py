import os, base64, requests

def wp_auth_header(username: str, app_password: str) -> dict:
    token = base64.b64encode(f"{username}:{app_password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}

def create_wp_post(article: dict, status: str = None) -> dict:
    site = os.environ.get("WP_SITE_URL", "").rstrip("/")
    username = os.environ.get("WP_USERNAME", "")
    password = os.environ.get("WP_APP_PASSWORD", "")
    status = status or os.environ.get("WP_DEFAULT_STATUS", "draft")
    if not site or not username or not password:
        raise RuntimeError("WP_SITE_URL, WP_USERNAME, WP_APP_PASSWORD가 필요합니다.")
    url = f"{site}/wp-json/wp/v2/posts"
    payload = {"title": article["title"], "content": article["html"], "status": status, "slug": article.get("slug"), "excerpt": article.get("meta_description", "")}
    res = requests.post(url, headers=wp_auth_header(username, password), json=payload, timeout=30)
    if res.status_code >= 400:
        raise RuntimeError(f"WordPress post failed: {res.status_code} {res.text[:500]}")
    return res.json()
