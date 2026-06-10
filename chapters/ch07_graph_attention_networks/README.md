# Chapter 7: Graph Attention Networks

실습 원본:
- `practice/hands_on_gnn_examples/Chapter07/chapter7.ipynb`

산출물:
- `slides/ch07_beamer.tex`: 발표 슬라이드
- `slides/ch07_handout.tex`: handout PDF
- `slides/ch07_handout_text.tex`: 텍스트형 handout
- `notes/ch07_summary.tex`: 상세 정리 노트

핵심 흐름:
1. GAT의 attention 메시지 패싱 직관
2. 4노드 toy 예제로 attention coefficient 계산 흐름 확인
3. Cora/CiteSeer에서 GATv2 실험
4. 노드 degree별 정확도 분석으로 한계와 해석 정리

빌드:
```bash
./scripts/build.sh
```

또는 루트에서:
```bash
./scripts/build_chapter.sh chapters/ch07_graph_attention_networks
```
