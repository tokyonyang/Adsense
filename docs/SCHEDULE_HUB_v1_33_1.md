# v1.33.1 Schedule Hub 안정화

## 문제

`Overnight Hot Issue Report`, `Morning Headline News Report`의 수동 실행은 되지만 schedule 실행 이력이 없었습니다.

## 수정 방향

새로 추가된 workflow 각각의 schedule에 의존하지 않고, 기존에 계속 사용해온 `Daily AdSense SEO Hot Issue Report`를 스케줄 허브로 사용합니다.

## 스케줄 허브 구조

```text
Daily AdSense SEO Hot Issue Report
├─ 05:30 KST → 간밤의 핫이슈 실행
├─ 06:07 KST → 기존 Daily HOT Issue 실행
├─ 06:10 KST → 아침 헤드라인 카드뉴스 실행
├─ 11:07 KST → 기존 Daily HOT Issue 실행
├─ 15:07 KST → 기존 Daily HOT Issue 실행
└─ 19:07 KST → 기존 Daily HOT Issue 실행
```

## 중복 전송 방지

아래 workflow는 수동 실행 전용으로 변경했습니다.

```text
Overnight Hot Issue Report
Morning Headline News Report
```

따라서 자동 발송은 `Daily AdSense SEO Hot Issue Report` 한 곳에서만 일어나고, 필요할 때는 각 workflow를 수동 실행할 수 있습니다.

## 확인 방법

자동 실행 이력은 앞으로 아래 workflow에 남습니다.

```text
Actions → Daily AdSense SEO Hot Issue Report
```

05:30 자동 발송도 `Overnight Hot Issue Report`가 아니라 `Daily AdSense SEO Hot Issue Report` 실행 이력으로 표시됩니다.
