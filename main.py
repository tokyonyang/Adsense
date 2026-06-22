import os, argparse, json
from pathlib import Path
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from trend_sources import collect_keywords
from content_generator import generate_article
from wp_publisher import create_wp_post
from telegram_notify import send_telegram

def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--geo", default=os.environ.get("GOOGLE_TRENDS_GEO","KR"))
    parser.add_argument("--max-keywords", type=int, default=int(os.environ.get("MAX_KEYWORDS","10")))
    parser.add_argument("--max-posts", type=int, default=int(os.environ.get("MAX_POSTS_PER_RUN","3")))
    parser.add_argument("--no-wordpress", action="store_true")
    args = parser.parse_args()

    Path("reports").mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    keywords = collect_keywords(args.geo, args.max_keywords, os.environ.get("BLOCKED_KEYWORDS",""))
    keywords.to_csv(f"reports/trend_keywords_{today}.csv", index=False, encoding="utf-8-sig")

    results = []
    for _, row in keywords.head(args.max_posts).iterrows():
        keyword = row["keyword"]
        try:
            article = generate_article(keyword, os.environ.get("SITE_DESCRIPTION","생활 정보 블로그"))
            Path(f"reports/article_{today}_{len(results)+1}.json").write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
            wp_result = {}
            if not args.no_wordpress:
                wp_result = create_wp_post(article, status=os.environ.get("WP_DEFAULT_STATUS","draft"))
            results.append({"keyword": keyword, "title": article.get("title"), "status": "draft" if not args.no_wordpress else "local_only", "wp_link": wp_result.get("link",""), "review_checklist": " | ".join(article.get("review_checklist", []))})
        except Exception as exc:
            print(f"[ERROR] {keyword}: {exc}")
            results.append({"keyword": keyword, "error": str(exc)})

    pd.DataFrame(results).to_csv(f"reports/generated_posts_{today}.csv", index=False, encoding="utf-8-sig")

    lines = ["📝 <b>AdSense SEO 초안 생성 리포트</b>"]
    for i, r in enumerate(results, 1):
        if r.get("error"):
            lines.append(f"{i}. ❌ {r['keyword']} - {r['error'][:80]}")
        else:
            lines.append(f"{i}. {r['title']}\n키워드: {r['keyword']}\n{r.get('wp_link') or '(로컬 저장)'}")
    send_telegram("\\n\\n".join(lines))

if __name__ == "__main__":
    main()
