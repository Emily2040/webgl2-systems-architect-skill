# 01 - 의도 분류 및 범위 설정 (ko)

## 목적 (Purpose)

셰이더 수식 유도, FBO 패스 설계 또는 성능 최적화에 착수하기 전에 사용자의 WebGL 2.0 작업을 단일 핵심 의도(Intent)와 프로젝트 분류(Project Class)로 정의하고 최소 모듈 세트를 확정한다. 분류 단계를 건너뛰고 구현부터 시작하지 마라.

## 로드 시점 (When to load)

모든 작업에서 가장 먼저 로드한다 (`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`).

## 입력 (Inputs)

- 사용자의 요구사항, 대상 플랫폼 및 목표 프레임 레이트
- 제공된 코드, 셰이더, 스크린샷, 프로파일링 로그 또는 프롬프트 단독(`prompt-only`)

## 핵심 규칙 (Rules)

### 1. 주 엔지니어링 의도를 1가지로 결정한다

- **`architecture`**: 신규 멀티패스 WebGL 2.0 렌더러, SDF 레이마칭 파이프라인, FBO 토폴로지 또는 하이브리드 아키텍처를 설계한다.
- **`implementation`**: 구체적인 `#version 300 es` 셰이더, VAO/UBO/Sampler 바인딩, FBO 구성 또는 호스트 JS/TS 렌더 코드를 작성한다.
- **`debug`**: 블랙스크린, `FRAMEBUFFER_INCOMPLETE_*`, 비균일 분기 내 미분 아티팩트, NaN 전파, `webglcontextlost` 크래시, 동기 리드백 스톨을 진단한다.
- **`optimize`**: 프레임 드롭, 고해상도 모바일 기기에서의 필레이트 과부하, 타일 메모리 대역폭 병목, CPU/GPU 동기 스톨을 해결한다.
- **`review`**: 기존 셰이더나 렌더러 코드의 수치 안정성, 매직 넘버, 상태 누수, 검증 커버리지를 감사한다.
- **`migration`**: WebGL 1.0에서 WebGL 2.0으로 업그레이드하거나, WebGL 2.0 폴백을 유지하며 WebGPU(`navigator.gpu` + WGSL) 듀얼 백엔드로 이관한다.

### 2. 프로젝트 분류를 1가지로 결정한다

```text
raster-mesh | sdf-raymarch | hybrid | postprocess | data-vis | ui
```

### 3. 입력 증거를 점검하고 하드웨어 데이터 품질을 기록한다

`inputs.hardware_data_quality`를 다음 4가지 등급 중 하나로 명시한다:
- **`measured`**: `EXT_disjoint_timer_query_webgl2` 실측값이나 통제된 패스 토글 차등 측정값이 있는 경우.
- **`partial`**: `gl.getParameter` 한계값이나 단편적인 FPS 로그는 있으나 패스별 타이밍이 없는 경우.
- **`estimated`**: 기기 등급("중급 안드로이드", "모바일 Safari" 등)만 알려진 경우 (반드시 휴리스틱 추산임을 명시).
- **`unknown`**: 대상 하드웨어 정보가 전혀 없는 경우.

### 4. `registry/module-map.json`의 최소 모듈 세트와 정확히 일치시킨다

출력의 `modules` 배열은 `registry/module-map.json[intent]`와 정확히 일치해야 한다 (불필요한 모듈을 추가하거나 필수 모듈을 누락하지 않는다).

## 주요 실패 모드 (Failure modes)

- 국소적인 `debug`나 `implementation` 작업에서 7개 모듈 전체를 로드하여 컨텍스트를 희석시키는 것
- 기기 등급에 기반한 추정치를 실측(`measured`) 하드웨어 데이터로 포장하는 것
- `registry/module-map.json`과 일치하지 않는 모듈 목록을 출력하는 것

## 출력 계약 기여 (Output contribution)

`task`(또는 최상위 `intent`, `project_class`, `subject`, `locale`), `inputs`, `modules` 및 초기 `assumptions`를 채운다.
