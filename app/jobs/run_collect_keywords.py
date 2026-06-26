from app.services.keyword_service import KeywordService


def main():
    result = KeywordService().collect_keywords()
    print(result)


if __name__ == "__main__":
    main()
