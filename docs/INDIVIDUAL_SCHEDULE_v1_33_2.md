# v1.33.2 개별 workflow 자동 실행 복구

수동 실행 가능한 workflow가 정해진 시간에 자동으로도 실행되도록 각 workflow에 `workflow_dispatch`와 `schedule`을 함께 넣었습니다.

## 구조

```text
Overnight Hot Issue Report
├─ 수동 실행
└─ KST 05:30 자동 실행

Morning Headline News Report
├─ 수동 실행
└─ KST 06:10 자동 실행

Daily AdSense SEO Hot Issue Report
├─ 수동 실행
└─ KST 06:07 / 11:07 / 15:07 / 19:07 자동 실행
```

GitHub Actions의 자동 실행은 수동 버튼을 누르는 방식이 아니라, 같은 workflow를 `schedule` 이벤트로 실행하는 방식입니다.
