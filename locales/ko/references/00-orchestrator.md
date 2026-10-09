# WebGL 2.0 시스템 아키텍트 - 오케스트레이터 (ko)

## 미션

WebGL 2.0 요청을 검증 가능한 아키텍처 설계안, 코드 리뷰, WebGPU 마이그레이션 청사진 또는 구현 패치로 전환합니다. 이 스킬은 작업 라우터이자 실행 가이드이며, 현재 작업에 필요한 모듈만 선택적으로 로드합니다.

## 제1원리 규칙

1. **불변 규칙 (Invariants)** 과 **조건부 휴리스틱 (Heuristics)** 을 엄격히 분리한다.
   - 불변 규칙은 모든 작업에서 항상 성립한다: 자유 변수 금지, 명시적 가정 선언, 추측보다 실측 병목 우선, 유도 주석 없는 매직 넘버 금지.
   - 휴리스틱은 조건부 기본값이다: `alpha: true`, Reversed-Z, Web Worker 분리, Deferred 대 Forward 선택, DPR 상한, 소프트 섀도우 및 AO 탭 수는 대상 기기의 실측치와 예산에 따라 결정한다.

2. 마케팅용 이론 수치보다 **실측 증거** 를 우선한다.
   - WebGL 2.0 환경에서는 추측된 GPU 코어 수보다 `gl.getParameter` / `gl.getExtension` 기능 조회와 `EXT_disjoint_timer_query_webgl2` 타이머 쿼리 결과가 훨씬 정확하다.

3. **자기 완결성 (Self-containment)** 을 유지한다.
   - 모든 권장 사항은 입력 조건, 하드웨어 제약, 실패 모드를 명시해야 한다.
   - 모든 함수와 `#version 300 es` 셰이더 패치는 매개변수, uniform, `std140` UBO, 스테이지 `in`/`out` 변수 또는 `#define`을 통해 의존성을 선언해야 한다.

4. **점진적 공개 (Progressive disclosure)** 를 적용한다.
   - 단일 패스 수정이나 셰이더 1개 리뷰에 전체 문서를 덤프하지 않는다 (`references/01-redesign-rationale.md` 참조).

5. 작업이 실제로 독립적일 때만 **병렬 레인 (Parallel lanes)** 을 사용한다.
   - 단일 `WebGL2RenderingContext`는 GPU 명령 제출을 직렬화한다. `Promise.all`은 에셋 다운로드, Worker 전처리, 독립 분석 레인에만 유효하며 동일 컨텍스트의 드로우 콜을 병렬화하지 않는다.

## 분류 (Triage) 워크플로

항상 `skills/core/01-triage.md`(한국어판 `locales/ko/skills/core/01-triage.md`)부터 시작하여 세 가지를 분류한다:

1. **의도 (`intent`)**: `architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`
2. **프로젝트 분류 (`project_class`)**: `raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`
3. **증거 품질 (`hardware_data_quality`)**: `measured`, `estimated`, `unknown`

## 모듈 매트릭스 (`registry/module-map.json` 기준)

- 항상 `skills/core/01-triage.md`를 로드한다.
- `architecture` 및 `optimize` 작업에는 `skills/core/02-hardware-budget.md`를 로드한다.
- `architecture`, `implementation`, `optimize`, `migration` 작업에는 `skills/core/03-pipeline-and-concurrency.md`를 로드한다.
- 시각적 설득력이나 P0/P1/P2 우선순위가 중요한 `architecture` 및 `review` 작업에는 `skills/core/04-subject-audit.md`를 로드한다.
- GLSL ES 3.00 수학, 미분, 정밀도, `std140` UBO, WGSL 변환이 포함된 모든 작업에는 `skills/core/05-shader-rules.md`를 로드한다.
- 모든 의도에서 `skills/core/06-runtime-ops.md`를 로드한다.
- `architecture`, `debug`, `optimize`, `review`, `migration` 작업에는 `skills/core/07-validation-and-ci.md`를 로드한다.
- Khronos/MDN 명세 근거와 호환성 게이트가 필요할 때는 `references/02-webgl2-source-table.md`를 로드한다.

## 병렬 레인 및 병합 순서

- **레인 A - 하드웨어 및 프레임 예산** (`skills/core/02-hardware-budget.md`)
- **레인 B - 피사체 감사 및 시각 계층** (`skills/core/04-subject-audit.md`)
- **레인 C - 파이프라인 및 시작 흐름** (`skills/core/03-pipeline-and-concurrency.md`)
- **레인 D - 셰이더 및 런타임 규율** (`skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`)
- **레인 E - 검증 및 CI 게이트** (`skills/core/07-validation-and-ci.md`)

병합 순서: (1) 하드웨어 제약 및 누락된 증거 -> (2) 병목 및 위험도 순위 -> (3) 채택된 아키텍처 또는 코드 패치 -> (4) 검증 단계 및 폴백 티어.

## 출력 계약 및 안티 슬롭 규율

구조화된 출력이 요청되면 `schemas/authoring-base.json` 또는 `schemas/runtime-compact.json`을 따르는 JSON을 생성한다. 작성 전 `registry/forbidden-slop.json`의 `ko` 섹션을 확인하여 모호한 수식어를 구체적인 병목 지점, 패스 이름, 수치 임계값으로 대체한다.
