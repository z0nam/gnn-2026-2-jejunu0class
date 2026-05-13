# Chapter 3: DeepWalk Representation Learning

실습 원본:
- `practice/hands_on_gnn_examples/Chapter03/chapter3.ipynb`

산출물:
- `slides/ch03_beamer.tex`: 발표 슬라이드
- `slides/ch03_handout.tex`: handout PDF
- `slides/ch03_handout_text.tex`: 텍스트형 handout
- `notes/ch03_summary.tex`: 상세 정리 노트

핵심 흐름:
1. `Word2Vec`로 임베딩 학습 직관 이해
2. 문장 시퀀스를 그래프 random walk 시퀀스로 치환
3. `DeepWalk`로 노드 임베딩 생성
4. Karate Club 그래프에서 시각화와 분류 성능 확인

빌드:
```bash
./scripts/build.sh
```

또는 루트에서:
```bash
./scripts/build_chapter.sh chapters/ch03_deepwalk_representation_learning
```
