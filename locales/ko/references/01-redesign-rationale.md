# 01 - 재설계 배경 및 아키텍처 트레이드오프 (ko)

## 1. 단일 프롬프트를 모듈형 스킬 패키지로 분리한 이유

기존의 단일 파일 WebGL 2.0 프롬프트는 안면 해부학 비례, SDF 레이마칭 스텝 제어, FBO 첨부물 상태, 모바일 대역폭 추정, CI 검증 규칙을 하나의 거대한 문서에 혼합했습니다. 이러한 구조는 세 가지 엔지니어링 문제를 일으켰습니다.

1. **컨텍스트 희석(Context Dilution)**: 개발자가 `webglcontextlost` 블랙스크린이나 `EXT_color_buffer_float` 미지원 FBO만 디버깅하려 해도 불필요한 해부학 규칙이나 지형 노이즈 규칙까지 함께 로드되었습니다.
2. **유사 정밀도와 매직 넘버(Pseudo-Precision)**: 상수 유도 과정을 기록하는 계약이 없다 보니 기하학적·물리적 근거가 없는 임의의 리터럴(`0.003`, `1.42` 등)이 셰이더에 유입되었습니다.
3. **검증 없는 완료 선언(Unverified Claims)**: 단순히 "셰이더가 컴파일됨" 또는 주관적인 과장 수식어만으로 완료를 선언하고, FBO 완전성 검사, 비차단 PBO 픽셀 리드백, 컨텍스트 손실 복구 훈련을 생략했습니다.

## 2. 핵심 엔지니어링 개선 사항

- **의도 기반 최소 모듈 라우팅(`registry/module-map.json`)**: `01-triage.md`를 통해 작업을 6가지 의도(`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`)와 6가지 프로젝트 분류로 나누고 필요한 최소 모듈만 로드합니다.
- **실측 하드웨어 데이터와 휴리스틱 추산의 엄격한 분리(`02-hardware-budget.md`)**: `EXT_disjoint_timer_query_webgl2` 링 버퍼 계측과 `gl.getParameter` 런타임 한계 조회를 최우선으로 삼고, 카탈로그상의 TFLOPS 추정치를 배제합니다.
- **단일 컨텍스트 직렬 제출과 비동기 파이프라인 분리(`03-pipeline-and-concurrency.md`)**: Web Worker CPU 병렬 처리, 프레임 간 파이프라인 작업(`KHR_parallel_shader_compile` 폴링, 다중 프레임 `PIXEL_PACK_BUFFER` + `gl.fenceSync` 비차단 리드백), 그리고 단일 `WebGL2RenderingContext` 직렬 명령 큐를 명확히 구분합니다.
- **5단계 관찰 레이어와 예산 축소 순서(`04-subject-audit.md`)**: 피사체를 5개 관찰 레이어와 P0/P1/P2 우선순위로 분해하고, 프레임 시간이 `gpuBudgetMs`를 초과할 때 P2 폴리시 -> 0.5x 보조 패스 -> DPR 클램프 -> P1 샘플 수 순서로 부하를 줄여 P0 실루엣을 보존합니다.
- **GLSL ES 3.00 수치 및 미분 규율(`05-shader-rules.md`)**: 0바이트 위치의 `#version 300 es`, `std140` 16바이트 정렬 UBO, Lipschitz 유계 SDF 스텝, 4탭 사면체 노멀, 비균일 분기 진입 전 `dFdx`/`dFdy` 사전 계산 및 `textureGrad` 호출을 강제합니다.
- **이중 JSON 출력 계약 및 슬롭 차단 게이트(`schemas/` + `registry/forbidden-slop.json`)**: `authoring-base.json`과 `runtime-compact.json` 스키마 검증과 더불어 한·영·중·일 4개 국어 금지 구문을 `scripts/validate_repo.py`로 자동 차단합니다.
