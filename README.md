# A7610 그래프신경망특론 자료 구조

## 폴더 규칙
- `references/books/`: 교재 원본(PDF/EPUB)
- `chapters/chXX_.../`: 챕터별 발제문 작업 폴더
- `practice/`: 실습 코드와 예제 저장소
- `scratch/`: 임시 추출 파일/실험 파일(버전관리 제외)

## 챕터 폴더 권장 구조
- `notes/`: 본문 요약 tex
- `slides/`: beamer/handout tex + 이미지
- `build/`: 컴파일 중간파일(aux, log, toc, nav, snm...)
- `output/`: 최종 pdf
- `scripts/`: 컴파일/정리 스크립트

## 현재 담당 반영
- 길준민: `chapters/ch01_ch02_graph_learning_and_theory/`
- Chapter 3 초안: `chapters/ch03_deepwalk_representation_learning/`
- Chapter 7 초안: `chapters/ch07_graph_attention_networks/`

## 협업 권장 네이밍
- 챕터 단위 폴더: `ch03_name`, `ch04_name`, ...
- 슬라이드 메인 파일: `ch03_beamer.tex`, `ch03_handout.tex`
- 요약문 파일: `ch03_summary.tex`

## 실습 폴더 운영
- `practice/hands_on_gnn_examples/`: 교재 예제 코드 원본 복제본
- 원본 저장소: `git@github.com:z0nam/Hands-On-Graph-Neural-Networks-Using-Python.git`
- 수업 저장소 안에서는 일반 폴더로 관리하기 위해 내부 `.git`은 제거
- 권장 원칙: 예제 원본은 `practice/`에 모아두고, 발제에 필요한 코드만 각 `chapters/chXX_.../` 아래로 가져와서 정리

이렇게 두면 `practice/`는 공용 실습 자료 보관소 역할을 하고, `chapters/`는 발표/과제 결과물 중심 구조로 유지할 수 있습니다.

## 챕터별 컴파일
루트에서 실행:

### macOS / Linux
```bash
./scripts/build_chapter.sh chapters/ch01_ch02_graph_learning_and_theory
```

다른 챕터도 같은 형식:
```bash
./scripts/build_chapter.sh chapters/ch03_xxx
./scripts/build_chapter.sh chapters/ch04_xxx
```

### Windows PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_chapter.ps1 -ChapterDir "chapters/ch01_ch02_graph_learning_and_theory"
```

다른 챕터도 같은 형식:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_chapter.ps1 -ChapterDir "chapters/ch03_xxx"
powershell -ExecutionPolicy Bypass -File .\scripts\build_chapter.ps1 -ChapterDir "chapters/ch04_xxx"
```

## Chapter 1-2 직접 빌드
챕터 루트(`chapters/ch01_ch02_graph_learning_and_theory`)에서 실행:

### macOS / Linux
```bash
./scripts/build.sh
```

### Windows PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

위 스크립트는 결과물을 `output/`, 중간파일을 `build/`에 생성합니다.
