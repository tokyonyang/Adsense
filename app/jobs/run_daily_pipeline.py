from app.services.keyword_service import KeywordService
from app.services.sns_trend_service import SnsTrendService


def main():
    keyword_result = KeywordService().collect_keywords()
    sns_result = SnsTrendService().collect_trends(platforms=["google", "youtube", "naver", "tiktok"])

    print({
        "keyword_result": keyword_result,
        "sns_result": sns_result,
    })


if __name__ == "__main__":
    main()
