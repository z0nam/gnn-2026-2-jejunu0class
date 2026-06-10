# Ch10 슬라이드 작업 문서 (md 초안)

> 목적: 현재 beamer 슬라이드(`slides/ch10_link_prediction_beamer_frames.tex`)를 md로 펼쳐놓고,
> 논의된 내용을 여기서 먼저 구성한 뒤 **한꺼번에 tex에 반영**한다.
>
> 표기 규칙:
> - `[NEW]` = 새로 추가할 슬라이드 (논의 반영)
> - `[수정]` = 기존 슬라이드에 내용 추가/변경
> - 표기 없음 = 기존 슬라이드 유지
> - 이미지/코드는 참조만 적음

---

## Section 1. 링크 예측 문제 개관

### 1. Link Prediction이란?
- 그래프 $G=(V,E)$에서 **관측되지 않은 엣지** $(u,v) \notin E$의 존재 가능성 추정
- 입력: $V$, 관측 엣지 $E_{obs}$, (선택) 노드 특징 $X$ / 출력: 연결 점수 $s(u,v) \in [0,1]$
- 응용: 친구 추천, 추천 시스템, 단백질 상호작용, 지식 그래프 완성

### 2. [NEW] 암묵적 전제: 지금 보이는 그래프는 표본이다
> 출처: understanding.md §1.4 (2026-06-10 논의)
- 참 엣지 집합 $E^*$가 있고, $E_{obs} \subset E^*$는 **부분 관측** — population은 모르고 표본만 있다
- "관측 안 됨"의 두 의미:
  - **결측 설정**: 참 그래프 존재, 관측 불완전 (단백질 상호작용, KG 완성)
  - **미래 설정**: 그래프가 자라는 중 (친구 추천) — population = 미래 그래프
- 노드 집합 $V$는 **완전 관측 전제** (transductive). 새 노드 등장은 별도 설정 → SEAL 복선
- 벤치마크의 뒤틀림: 정답 그래프를 알면서 `RandomLinkSplit`으로 **일부러 숨김** = MCAR 가정.
  현실 결측은 MNAR(편향) → 벤치마크가 실전을 과대평가할 수 있음
- 음성 라벨도 사실 없음: 비관측 쌍 = 진짜 비엣지 or 결측 엣지 (**PU-learning** 구조)

### 3. 전통적 휴리스틱과 학습 기반의 차이
- 표: CN / Jaccard / Adamic-Adar / Katz·PageRank vs GAE·VGAE($\sigma(z_u^\top z_v)$) / SEAL(서브그래프 분류)
- 휴리스틱은 정해진 가정 위에서만 작동, GNN 기반은 데이터로부터 학습

### 4. Chapter 10에서 다루는 두 가지 모델
- VGAE: 임베딩을 확률분포로 학습, 내적 디코더, 전체 그래프 수준 한 번에
- SEAL: 후보 링크별 enclosing subgraph + DRNL → 서브그래프 분류
- 한 줄 비교: VGAE는 *한 그래프 = 한 예제*, SEAL은 *한 후보 링크 = 한 예제*

### 5. 데이터 분할: RandomLinkSplit
- 엣지를 train/val/test로 분할 + 음성 엣지 샘플링
- 코드: `RandomLinkSplit(num_val=0.05, num_test=0.1, ...)`
- pos/neg_edge_label_index, 평가지표 AUC·AP
- [수정 후보] "test 엣지는 메시지 패싱 그래프에서도 빠진다 (누설 방지)" 한 줄 명시
- [수정 후보] 음성 = 전수 라벨링이 아니라 **샘플링** (understanding.md §1.6):
  - 개념: 암묵적 완전그래프에서 관측 엣지=양성, 나머지=음성 — 단 Cora만 해도 쌍 366만 vs 엣지 1만
  - 구현: val/test 음성은 양성과 같은 수로 뽑아 **고정**, train 음성은 **매 epoch 재샘플링**
  - "없는 엣지의 바다에서 양성과 같은 수만큼 떠서 음성 대표로 쓴다"

### 5b. [NEW 후보] 평가지표: AUC와 AP
> 출처: understanding.md §1.7
- 왜 순위 기반 지표인가: 확정 음성 라벨이 없고(PU), 임계값은 응용마다 다름
- AUC = $P(s(\text{무작위 양성}) > s(\text{무작위 음성}))$ — 양성·음성 쌍 대결에서 양성이 이길 확률. 0.5=무작위, 1.0=완벽
- AP = 점수순으로 읽어내려가며 양성을 만날 때마다 그 시점 precision을 평균 — 상위권 오염에 민감
- 손계산 예시(양성3·음성3): AUC=7/9≈0.78, AP≈0.81
- 1:1 균형 평가셋에선 둘이 비슷 (본 실행 0.87/0.87) / top-k 추천 실전에선 AP·precision@k가 더 정렬됨

---

## Section 2. Graph Autoencoder (GAE)

### 6. GAE의 아이디어
- 인코더 $Z = \mathrm{GCN}(X,A)$, 디코더 $\hat{A} = \sigma(ZZ^\top)$
- 이미지: `ch10_fig02_gae_decoder_AeqZTZ.png`

### 7. GAE의 재구성 손실
- BCE 형태: 양성 엣지 → 1, 음성 엣지 → 0
- 클래스 불균형 때문에 양/음 같은 수로 샘플링
- 단점: 임베딩이 결정적 — 불확실성 표현 못함

### 8. [NEW 후보] 내적 디코더가 강제하는 가정
> 출처: understanding.md §2.1 — "디코더가 단순한 게 아니라 가정을 강제한다"
- $\sigma(z_u^\top z_v)$ 한 줄 = **homophily 가설** ("가까우면 연결된다")
- 깨지는 곳: heterophily(사기 탐지), 방향 그래프(항상 대칭이라 표현 불가), 글로벌 구조
- Cora(인용 네트워크)는 homophily 강함 → 잘 맞는 무대

---

## Section 3. Variational Graph Autoencoder (VGAE)

### 9. VGAE: 확률적 인코더
- $q(z_i|X,A) = \mathcal{N}(\mu_i, \mathrm{diag}(\sigma_i^2))$, GCN 두 개로 $\mu$, $\log\sigma$
- Reparameterization: $z = \mu + \sigma \odot \epsilon$
- [수정 후보] §1.4 연결: "관측 그래프 = 생성 모델의 표본" 관점 한 줄 ($A_{uv} \sim \mathrm{Bernoulli}(\sigma(z_u^\top z_v))$)

### 10. VGAE 손실
- $\mathcal{L} = \mathcal{L}_{recon} + \frac{1}{N}\mathrm{KL}[q\|p]$
- KL = 정규화, 1/N = 노드당 평균 (β-VAE 관점: recon 우선)

### 11. PyG VGAE 인코더 구현 (코드)
### 12. VGAE 학습 루프 (코드)
- recon_loss가 음성 엣지를 매 epoch 자동 샘플링

### 13. Cora 결과 + Ahat 히트맵
- 책 0.88/0.90 vs 본 실행 0.869/0.872
- 블록 구조 = homophily 학습됨 (이미지: `ch10_runtime_vgae_ahat_heatmap.png`)

### 14. t-SNE 시각화
- 링크 예측만 학습했는데 클래스 군집이 드러남 (이미지: `ch10_runtime_vgae_embedding_tsne.png`)

---

## Section 4. SEAL

### 15. [NEW 후보] 왜 GNN은 링크 예측이 어려운가 (4-cycle 반례)
> 출처: understanding.md §3.3 — VGAE→SEAL 전환의 논리적 다리
- 4-cycle: 모든 노드 차수 2, feature 같으면 $z_1 = z_2 = z_3 = z_4$
- 내적: $(1,2)$ 엣지와 $(1,3)$ 비엣지를 **구분 불가** — 학습 부족이 아니라 1-WL 표현력의 구조적 한계
- 처방: "타깃이 누구인지" feature에 박아넣기 = labeling trick → SEAL 도입

### 16. SEAL의 출발점
- 이미지: `ch10_fig03_seal_pipeline.png`
- 휴리스틱(CN, AA, Katz)이 모두 enclosing subgraph의 함수 → 이진 그래프 분류로 환원

### 17. k-hop 이웃 개념
- 이미지: `ch10_fig01_khop_neighborhood.png`, $k=2$ 표준

### 18. Enclosing Subgraph 추출
- tikz 그림: 타깃 링크 점선 제거
- 타깃 링크 자체는 서브그래프에서 제거 (정답 보고 학습 금지)

### 19. 타깃 엣지 제거 코드
- 양방향 제거, 양성/음성 동일 절차

### 20. DRNL: Double-Radius Node Labeling
- $z(x) = 1 + \min(d_x,d_y) + d(d+r-1)$, 타깃은 1, 도달불가 0
- GNN은 누가 타깃인지 모름 → 라벨로 명시

### 21. DRNL 예시 (실제 Cora 서브그래프)
- 이미지: `ch10_runtime_drnl_example.png`, $z=2$ = 공통 이웃

### 22. SEAL Cora 실행 결과
- 책 0.89/0.90 vs 본 실행 0.786/0.802 + 차이 원인 3가지

### 23. DRNL 라벨 계산 코드
- dst 빼고 d_src, src 빼고 d_dst — 경로 누설 방지

### 24. DGCNN: SEAL의 분류기
- 4-layer GCN → SortPooling(k=30) → Conv1D → Dense

### 25. DGCNN 코드 (요지)

### 26. 트레이드오프
- SEAL 장점: 표현력, inductive / 단점: 쌍마다 전처리, 대규모 불가

---

## Section 5. 정리 및 비교

### 27. VGAE vs SEAL 한눈에 보기 (표)
- [수정 후보] 행 추가: **transductive vs inductive** (새 노드/새 그래프 일반화)
- [수정 후보] 행 추가: 숨은 가정 (homophily·대칭 vs 구조 라벨링)

### 28. 발제 마무리
- [수정 후보] 한 줄 핵심 교체: "링크 예측은 GNN이 자연스럽게 풀 수 없는 anchored 과제다.
  VGAE는 노드 feature에 그 일을 떠넘기고, SEAL은 라벨링으로 직접 해결한다."

### 29. Q&A
- 기존 질문 3개 + [추가 후보] understanding.md §6 질문들 (heterophily에서 내적 디코더, DRNL 3-노드 일반화 등)
- [예상 질문 대비] "왜 AUC와 AP를 둘 다 보나?" → AUC는 클래스 비율에 둔감해 모델 비교 안정적, AP는 top-k 사용 시나리오에 가까움 (§1.7)

---

## 작업 메모

**2026-06-10 오후: 전부 채택되어 tex 일괄 반영 + 빌드 완료** (발제 시간 40분 이상 확인됨)

- [x] 슬라이드 2 (표본 프레이밍)
- [x] 슬라이드 5 수정 + 5b (AUC/AP)
- [x] 슬라이드 8 (내적 디코더 가정)
- [x] 슬라이드 15 (4-cycle/1-WL) — tikz 4-cycle 그림 포함
- [x] 비교표 행 추가 (숨은 가정 / transductive vs inductive)
- [x] 추가 반영분 (understanding.md §7 대기 목록): 휴리스틱 표기 설명($\Gamma$ 등) + AA 직관, 인코더-디코더 계보, 점수함수 형태 대비
- [x] 오늘 DRNL 논의분: "DRNL 공식 음미" 슬라이드 (좌표 접기 표, labeling trick 본질, z=2→CN 포섭)
- [x] 실습 노트북 안내 슬라이드 (책 vs 본 실행 결과 표)
- [x] tex 일괄 반영 + 빌드 — **36페이지, overfull 0건** (기존 DRNL 예시·k-hop 프레임 넘침도 수정)
