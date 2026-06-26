from app.services.sns_trend_service import SnsTrendService


def main():
    result = SnsTrendService().collect_trends(platforms=["google", "youtube", "naver", "tiktok"])
    print(result)


if __name__ == "__main__":
    main()
