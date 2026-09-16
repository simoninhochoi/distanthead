# DistantHead

Personal academic site of **Inho Choi** (최인호), Assistant Professor in the
Department of Political Science and Diplomacy, Kyonggi University.

Published at <https://simoninhochoi.github.io/distanthead/> · 한국어판 `/ko/`

Built with [Hugo](https://gohugo.io/) and deployed by GitHub Actions on every
push to `main`. Page content lives in `data/en/` and `data/ko/`; the templates
in `layouts/` carry no copy. See `CLAUDE.md` for the working notes.

```bash
hugo --gc --minify                                   # build as published
hugo --gc -b "http://localhost:8099/" -d /tmp/preview  # local preview build
```
