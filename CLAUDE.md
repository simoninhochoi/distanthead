# DistantHead — 개인 홈페이지

`https://simoninhochoi.github.io/distanthead/` 로 발행되는 Hugo 정적 사이트.
영문(`/`)과 국문(`/ko/`) 두 판을 같은 템플릿으로 찍는다.
디자인 DNA는 `Projects/circle-of-fish`(그리고 그 원본인 `complex-intelligence.github.io`)
에서 가져왔다 — 스티키 헤더, 모티프 위의 가운데 히어로, 교차 밴드 섹션, 카드 그리드,
세리프 표제 + 산세리프 본문. 팔레트만 먹빛(slate)·구릿빛(copper)으로 갈라놓았다.

## 구조

```
data/en/ · data/ko/   ← 페이지 내용의 정본. 여기만 고치면 양쪽 언어가 바뀐다
content/*.md          ← 제목·nav 순서(weight)·레이아웃만 담은 껍데기. 본문 없음
layouts/              ← Hugo 템플릿. 내용은 들어가지 않는다
static/css/style.css  ← 스타일시트 전부(단일 파일)
static/img/           ← roundabout.svg(히어로 모티프) · favicon.svg
static/files/         ← choi-cv.pdf
.github/workflows/    ← main 에 push 하면 Hugo 0.142.0 으로 빌드해 Pages 로 발행
```

**내용을 고칠 때는 `data/<lang>/*.yaml` 만 건드린다.** 템플릿을 고쳐야 한다면 그것은
새 구성요소가 필요하다는 뜻이다.

| 파일 | 담는 것 |
|---|---|
| `site.yaml` | 이름·소속·히어로 문구·소개 본문·홈 섹션 제목·UI 문자열 |
| `research.yaml` | 연구 영역 5개(본문 + 진행 중인 갈래) |
| `publications.yaml` | 게재 논문. `groups[].entries` 가 `entries[].id` 를 순서대로 참조 |
| `wip.yaml` | 진행 중인 논문과 초록 |
| `seminars.yaml` | 상설 세미나 |
| `resources.yaml` | 자료와 도구 링크 |
| `cv.yaml` | 이력서 페이지 문구 |

두 언어의 **키 구조는 반드시 같아야 한다.** 한쪽에만 키를 더하면 다른 언어에서
`StrictUndefined` 가 아니라 빈칸으로 조용히 새어 나간다.

## 빌드

Hugo 바이너리는 저장소에 없다. 로컬에서 볼 때는 내려받아 쓴다.

```bash
# 발행 경로 그대로 빌드 (GitHub Action 과 같은 결과)
hugo --gc --minify

# 로컬 미리보기 — baseURL 을 반드시 덮어쓸 것. 안 그러면 /distanthead/ 로 링크가 깨진다
hugo --gc -b "http://localhost:8099/" -d /tmp/preview
python -m http.server 8099 --directory /tmp/preview
```

## 함정

- **YAML 스칼라 안의 `: ` 는 매핑으로 읽힌다.** 논문 제목은 거의 다 콜론 이중 구조라
  이 문제를 반드시 만난다. `- "「사대의 국제정치이론: 일어난 미래로서 병자호란」"` 처럼
  **큰따옴표로 감쌀 것.** 감싸지 않으면 빌드가 `mapping values are not allowed` 로 죽는다.
- **`range` 안에서 `$` 는 반복 항목이 아니라 페이지다.** 항목의 다른 필드를 쓰려면
  `{{- $e := . }}` 로 먼저 묶는다(`layouts/_default/seminars.html` 참조).
- **`html { font-size: 150% }`** 가 걸려 있어 모든 rem 값이 1.5배로 읽힌다. circle-of-fish
  에서 그대로 가져온 것이고, 좁은 화면에서는 125% → 108% 로 내려간다. **새 규칙을 쓸 때
  보통 감각의 rem 을 쓰면 1.5배로 커진다.**
- **그리드 트랙은 `minmax(min(Xrem, 100%), 1fr)`** 로 쓴다. `min()` 없이 쓰면 트랙이
  뷰포트보다 넓어져 휴대폰에서 문서 전체가 가로로 넘친다.
- **헤드리스 크롬 스크린샷은 믿지 말 것.** 윈도우 배율 때문에 CSS 뷰포트가 최소 485px
  로 고정되고, `--window-size=390` 을 줘도 485px 로 그린 화면을 390px 로 **잘라서** 저장한다.
  잘려 보이는 것은 레이아웃 버그가 아니다. 진짜 좁은 화면을 재려면 **390px iframe**
  안에 페이지를 띄우고 `documentElement.scrollWidth` 를 읽는다.
- **언어 전환은 `.AllTranslations`** 로 돈다. 같은 페이지의 다른 언어판으로 가며
  홈으로 떨어지지 않는다. `content/x.md` 와 `content/x.ko.md` 의 **파일 이름이 짝을
  이룰 때만** 연결된다.
- `static/files/choi-cv.pdf` 는 사이트와 **따로 논다** — 소속을 바꿔도 PDF 는 그대로다.

## 표기

- 국문 소속은 **「경기대학교 정치외교학전공」**(「정치외교학과」 아님),
  영문은 "Department of Political Science and Diplomacy, Kyonggi University".
- 서지(저자·제목·게재지)는 **원어 그대로** 둔다. 국문 논문은 국문 제목이 정본이고
  영문판에서는 영문 번역 제목을 쓰되 국문 원제를 함께 보인다(`original` 필드).
- 국문 본문은 **한다체**(학술 문체)다. 슬라이드나 정책 글의 문체를 섞지 않는다.
  문체 규약은 `Projects/문체/` 와 `inho-paper-style`·`inho-english-style` 스킬에 있다.
