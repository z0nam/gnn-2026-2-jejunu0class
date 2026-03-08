# A7610 그래프신경망특론 자료 구조

## 폴더 규칙
- `references/books/`: 교재 원본(PDF/EPUB)
- `chapters/chXX_.../`: 챕터별 발제문 작업 폴더
- `scratch/`: 임시 추출 파일/실험 파일(버전관리 제외)

## 챕터 폴더 권장 구조
- `notes/`: 본문 요약 tex
- `slides/`: beamer/handout tex + 이미지
- `build/`: 컴파일 중간파일(aux, log, toc, nav, snm...)
- `output/`: 최종 pdf
- `scripts/`: 컴파일/정리 스크립트

## 현재 담당 반영
- 길준민: `chapters/ch01_ch02_graph_learning_and_theory/`

## 협업 권장 네이밍
- 챕터 단위 폴더: `ch03_name`, `ch04_name`, ...
- 슬라이드 메인 파일: `ch03_beamer.tex`, `ch03_handout.tex`
- 요약문 파일: `ch03_summary.tex`

## 컴파일 원칙 (상대경로)
- 각 챕터 루트 기준 상대경로만 사용
- 예시(Chapter 1-2):
  - `cd chapters/ch01_ch02_graph_learning_and_theory/scripts`
  - `powershell -ExecutionPolicy Bypass -File .\build.ps1`

위 스크립트는 결과물을 `../output`, 중간파일을 `../build`에 생성합니다.
