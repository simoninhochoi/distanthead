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
static/img/           ← network.svg(히어로 모티프) · favicon.svg · cv/page-N.png — 전부 생성물
_build/               ← 생성 스크립트 둘. 산출물을 손으로 고치지 말 것
data/cv_pages.yaml    ← 생성물. CV 지면 목록·PDF 해시
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

## 히어로 배경

`static/img/network.svg` 는 손으로 그린 것이 아니라 **`Projects/3d-network-sculpture`
의 조형물 기하에서 뽑은 것**이다. 렌더 PNG 를 따지 않고 `prims_v3_150mm.json`
(실린더 391·구 226·토러스 6)을 직접 투영해 단순화한다 — 겉껍질의 대원(大圓),
솎아낸 안쪽 가새, 마디 몇 개. 파비콘은 같은 기하를 16px 에서 읽히는 데까지 줄인 것이다.

```bash
python _build/make_hero_motif.py              # static/img/network.svg
python _build/make_hero_motif.py --favicon    # static/img/favicon.svg
python _build/make_hero_motif.py --az 40 --el 8   # 시점 바꾸기
```

- **파비콘에서 넓은 고리 셋을 고르면 안 된다** — 셋 다 정면이라 찌그러진 원 하나로 보인다.
  가장 정면인 고리 하나 + 가장 옆면인 고리 둘이라야 혼천의 형태가 된다.
- 조형물 폴더 경로가 스크립트 안에 절대경로로 박혀 있다. 그 폴더가 없으면 돌지 않지만,
  **SVG 는 저장소에 커밋되어 있으므로 빌드에는 지장이 없다.**

## 이력서 지면

브라우저 PDF 뷰어를 `iframe` 으로 끼우면 어두운 패널이 페이지와 따로 놀고, iOS 에서는
아예 아무것도 뜨지 않는다. 그래서 지면을 **미리 이미지로 렌더해** 본문에 얹는다.
JavaScript 가 필요 없고 어디서나 뜨며, PDF 는 내려받기 단추로 한 번에 간다.

```bash
python _build/make_cv_preview.py    # static/img/cv/page-N.png + data/cv_pages.yaml
```

폭 1400px 회색조 팔레트 PNG 로 뽑아 화면에서는 816px 로 보인다(약 1.7배 밀도).
3면 합계 390KB 남짓이고 둘째 면부터는 `loading="lazy"` 다.

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
- **CV PDF 를 갈면 `_build/make_cv_preview.py` 를 반드시 다시 돌린다.** 이력서 페이지는
  PDF 를 브라우저 뷰어로 끼우지 않고 **미리 렌더한 지면 이미지**로 보여주기 때문에,
  스크립트를 안 돌리면 새 PDF 를 올려도 화면에는 옛 이력서가 계속 걸려 있다.
  `data/cv_pages.yaml` 의 `source_sha` 가 현재 PDF 의 해시와 같은지로 확인할 수 있다.
- `static/files/choi-cv.pdf` 는 사이트 본문과 **따로 논다** — 소속을 바꿔도 PDF 는 그대로다.

## 표기

- 국문 소속은 **「경기대학교 정치외교학전공」**(「정치외교학과」 아님),
  영문은 "Department of Political Science and Diplomacy, Kyonggi University".
- 서지(저자·제목·게재지)는 **원어 그대로** 둔다. 국문 논문은 국문 제목이 정본이고
  영문판에서는 영문 번역 제목을 쓰되 국문 원제를 함께 보인다(`original` 필드).
- 국문 본문은 **한다체**(학술 문체)다. 슬라이드나 정책 글의 문체를 섞지 않는다.
  문체 규약은 `Projects/문체/` 와 `inho-paper-style`·`inho-english-style` 스킬에 있다.
