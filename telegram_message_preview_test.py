from telegram_notify import format_hot_issues_report


sample_issues = [
    {
        "category": "경제·금융",
        "headline": "정부, 하반기 전기·가스요금 동결…석유 최고가도 낮춘다",
        "evidence": [
            {
                "title": "정부, 하반기 전기·가스요금 동결…7차 석유최고가격도 내린다",
                "source_name": "smedaily.co.kr",
                "published_at": "06-26 13:58",
                "url": "https://www.smedaily.co.kr/example",
            },
            {
                "title": "물가 3%선 방어 총력전…석유최고가격 인하·공공요금 동결",
                "source_name": "naeilecon",
                "published_at": "06-26 13:04",
                "url": "https://www.naeilecon.com/example",
            },
            {
                "title": "1조 투입해 8월 고비 정조준…정부, 하반기 물가 방어 총력",
                "source_name": "newspim.com",
                "published_at": "06-26 11:39",
                "url": "https://www.newspim.com/example",
            },
        ],
    },
    {
        "category": "경제·금융",
        "headline": "日 기준금리가 35년 만에 1%대로 올랐다",
        "evidence": [
            {
                "title": "日 기준금리 35년 만에 1%대로 올라",
                "source_name": "경제뉴스",
                "published_at": "06-26 10:20",
                "url": "",
            }
        ],
    },
]

print(format_hot_issues_report(sample_issues))
