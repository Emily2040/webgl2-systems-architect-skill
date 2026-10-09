# 01 - 작업 분류 및 의도 판별 (ko)

## Purpose

WebGL 2.0 요청을 정확히 분류하여 필요한 모듈만 로드하고 불필요한 규칙 덤프를 방지한다. 모든 작업은 이 모듈에서 시작한다.

## When to load

모든 요청에서 다른 모듈보다 먼저 로드한다.

## Inputs

- 사용자 프롬프트 및 대상 언어 (`en`, `zh-CN`, `ja`, `ko`)
- 기존 셰이더, JS/TS 코드, 패스 그래프 또는 저장소 파일 (제공된 경우)
- 스크린샷, 캡처 영상, GPU 프로파일러 로그 또는 런타임 에러 로그 (제공된 경우)
- 대상 기기, 브라우저 및 목표 FPS 제약 조건 (알려진 경우)

## Rules

### 1. 네 가지 축으로 요청을 분류한다

1. **의도 (`intent`)**
   - `architecture`: 시스템 설계, 패스 그래프, 하드웨어 티어 구성, 시작 오케스트레이션
   - `implementation`: 신규 `#version 300 es` 셰이더, FBO 패스, VAO/UBO 파이프라인 또는 런타임 기능 구현
   - `debug`: 렌더링 깨짐, `NaN`/정밀도 아티팩트, 불완전한 FBO, 상태 누수, 컨텍스트 손실 버그 수정
   - `optimize`: FPS 저하, 필레이트 병목, 메모리 대역폭 압박, 셰이더 스톨, 동기식 리드백 병목 해결
   - `review`: 코드 감사, 시각적 설득력 평가, 이식성 점검, 배포 준비 상태 검증
   - `migration`: WebGL 1에서 WebGL 2.0으로 업그레이드하거나 WebGL 2.0에서 WebGPU/WGSL로 전환

2. **프로젝트 분류 (`project_class`)**
   - `raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`

3. **피사체/주제 (`subject`)**
   - `human face bust`, `terrain flyover`, `HDR bloom chain`, `WebGPU bind-group migration` 등 구체적인 대상을 명시한다.

4. **증거 품질 (`hardware_data_quality`)**
   - `measured` (타이머 쿼리 및 캡처 존재), `estimated` (기기 등급은 알지만 패스 비용은 추산), `unknown` (프롬프트만 존재; 가정 명시 필수).

### 2. 변경안을 제시하기 전에 제공된 아티팩트를 먼저 검사한다

- 셰이더나 코드가 제공된 경우 `#version 300 es` 선언, VAO/UBO 바인딩, FBO 상태, 드로우 루프를 먼저 확인한다.

### 3. 의도별 모듈 선택 (`registry/module-map.json`과 정확히 일치)

- `architecture`: `skills/core/01-triage.md`, `skills/core/02-hardware-budget.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/04-subject-audit.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `implementation`: `skills/core/01-triage.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`
- `debug`: `skills/core/01-triage.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `optimize`: `skills/core/01-triage.md`, `skills/core/02-hardware-budget.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `review`: `skills/core/01-triage.md`, `skills/core/04-subject-audit.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`
- `migration`: `skills/core/01-triage.md`, `skills/core/03-pipeline-and-concurrency.md`, `skills/core/05-shader-rules.md`, `skills/core/06-runtime-ops.md`, `skills/core/07-validation-and-ci.md`

## Failure modes

- 한 줄짜리 셰이더 수정을 위해 모든 모듈을 로드하는 것
- 래스터 메시 파이프라인에 SDF 레이마칭 규칙을 강제하는 것
- 병목 원인을 분류하기 전에 시각적 기능부터 삭제하는 것

## Output contribution

`task.intent`, `task.project_class`, `task.subject`, `inputs.hardware_data_quality`, `modules` 및 초기 `assumptions`를 채운다.
