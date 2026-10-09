# WebGL 2.0 시스템 아키텍트 스킬 (WebGL 2.0 Systems Architect Skill)

[English](./README.md) · [简体中文](./README.zh-CN.md) · [日本語](./README.ja.md) · **한국어**

[![Validate Skill Repository](https://github.com/Emily2040/webgl2-systems-architect-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/Emily2040/webgl2-systems-architect-skill/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-38bdf8.svg)](./LICENSE)
[![Version](https://img.shields.io/badge/version-2.0.0-2dd4bf.svg)](./CHANGELOG.md)
[![Locales](https://img.shields.io/badge/locales-EN%20%7C%20zh--CN%20%7C%20ja%20%7C%20ko-f59e0b.svg)](./locales)

![WebGL 2.0 Systems Architect 6대 엔지니어링 기둥 개요](./docs/assets/skill-infographic.svg)

`webgl2-systems-architect-skill`은 **WebGL 2.0 렌더러 아키텍처 설계, GLSL ES 3.00 (`#version 300 es`) 셰이더 규율, GPU 프레임 예산 수식 유도, 비차단 `PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync` 파이프라인, 컨텍스트 손실 복구 및 WebGL 2.0에서 WebGPU로의 마이그레이션**을 위한 라우팅 기반 멀티 에이전트 엔지니어링 스킬입니다.

이 패키지는 **영어 (`en`)**, **중국어 간체 (`zh-CN`)**, **일본어 (`ja`)**, **한국어 (`ko`)** 4개 언어의 네이티브 문서, 로컬라이즈된 스킬 모듈 및 안티 슬롭(Anti-Slop) 검증 규칙을 기본 제공합니다.

- **GitHub 저장소**: <https://github.com/Emily2040/webgl2-systems-architect-skill>
- **대화형 WebGL 2.0 워크벤치 (`docs/index.html`)**: [로컬 워크벤치 열기](./docs/index.html?lang=ko)
- **실시간 WebGL 2.0 스모크 테스트 픽스처**: [`fixtures/webgl2-smoke/index.html`](./fixtures/webgl2-smoke/index.html)
- **작성자**: **Iamemily2050** (`Emily2040`) · [웹사이트](https://Iamemily2050.com) · [X](https://x.com/iamemily2050) · [Instagram](https://instagram.com/iamemily2050)

---

## 왜 라우팅 아키텍처인가

대부분의 그래픽스 프롬프트는 방대한 교과서 분량의 텍스트를 컨텍스트 창에 한꺼번에 쏟아붓습니다. 이는 토큰을 낭비할 뿐 아니라 인스턴싱 기반 래스터 메시 파이프라인에 SDF 레이마칭 규칙을 섞어버리는 등 작업 의도와 맞지 않는 지시를 유발합니다.

이 저장소는 WebGL 2.0 그래픽스 시스템 엔지니어링을 선택적 라우팅 워크플로로 구성합니다:

1. **초소형 라우터 진입점**: 루트 [`SKILL.md`](./SKILL.md)는 800자 미만으로 유지되며 [`references/00-orchestrator.md`](./references/00-orchestrator.md)(한국어 세션에서는 [`locales/ko/references/00-orchestrator.md`](./locales/ko/references/00-orchestrator.md))로 즉시 연결됩니다.
2. **분류(Triage) 우선 모듈 선택**: [`skills/core/01-triage.md`](./locales/ko/skills/core/01-triage.md)가 6가지 작업 의도(`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`)와 6가지 프로젝트 분류(`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`)를 판별하여 [`registry/module-map.json`](./registry/module-map.json)에 매핑된 필수 모듈만 로드합니다.
3. **불변 규칙과 조건부 휴리스틱 분리**: 불변 규칙(자유 변수 금지, 명시적 가정, 유도 주석이 포함된 상수, VAO 바인딩 필수, FBO 완전성 검증)은 항상 적용되며, 조건부 휴리스틱(`alpha: false`, Reversed-Z, Deferred/Forward 선택, DPR 상한, 탭 수)은 실측 프레임 예산에 따라 결정됩니다.
4. **정직한 WebGL 2.0 동시성 모델**: Web Worker는 에셋 다운로드, glTF/Draco 디코딩, KTX2 트랜스코딩, 컬링을 병렬화하고 `KHR_parallel_shader_compile`과 `gl.PIXEL_PACK_BUFFER` + `gl.fenceSync`는 프레임 간 비차단 폴링을 수행하지만, 단일 `WebGL2RenderingContext`의 드로우 콜 제출은 직렬로 다룹니다.
5. **실행 가능한 검증 게이트**: [`scripts/validate_repo.py`](./scripts/validate_repo.py)가 JSON 스키마, 모듈 집합 일치, SVG XML 정합성 및 텍스트 박스 여백, 4개 언어 패리티, 금지 수식어 검사, 네거티브 셀프 테스트를 자동으로 수행합니다.

---

## 아키텍처 청사진

![WebGL 2.0 Systems Architect 라우팅 레인 및 동시성 청사진](./docs/assets/architecture.svg)

---

## 4개 언어 네이티브 지원 (`en`, `zh-CN`, `ja`, `ko`)

| 언어 (Locale) | 루트 README | 로컬라이즈 SKILL | 로컬라이즈 Orchestrator | 코어 모듈 (`01`..`07`) |
|---|---|---|---|---|
| **English (`en`)** | [`README.md`](./README.md) | [`SKILL.md`](./SKILL.md) | [`references/00-orchestrator.md`](./references/00-orchestrator.md) | [`skills/core/`](./skills/core) |
| **简体中文 (`zh-CN`)** | [`README.zh-CN.md`](./README.zh-CN.md) | [`locales/zh-CN/SKILL.md`](./locales/zh-CN/SKILL.md) | [`locales/zh-CN/references/00-orchestrator.md`](./locales/zh-CN/references/00-orchestrator.md) | [`locales/zh-CN/skills/core/`](./locales/zh-CN/skills/core) |
| **日本語 (`ja`)** | [`README.ja.md`](./README.ja.md) | [`locales/ja/SKILL.md`](./locales/ja/SKILL.md) | [`locales/ja/references/00-orchestrator.md`](./locales/ja/references/00-orchestrator.md) | [`locales/ja/skills/core/`](./locales/ja/skills/core) |
| **한국어 (`ko`)** | [`README.ko.md`](./README.ko.md) | [`locales/ko/SKILL.md`](./locales/ko/SKILL.md) | [`locales/ko/references/00-orchestrator.md`](./locales/ko/references/00-orchestrator.md) | [`locales/ko/skills/core/`](./locales/ko/skills/core) |

[`registry/forbidden-slop.json`](./registry/forbidden-slop.json)은 4개 언어 모두에서 "압도적인 퀄리티", "극한의 성능", "시네마틱한 느낌" 같은 모호한 과장 표현을 차단하고 구체적인 병목 원인, 렌더 패스 이름, 수치 임계값으로 대체하도록 강제합니다.

---

## 코어 모듈 및 의도별 라우팅 매트릭스

[`registry/module-map.json`](./registry/module-map.json)에 정의된 작업 의도별 로드 모듈:

| 작업 의도 (`intent`) | 로드되는 모듈 | 주요 산출물 |
|---|---|---|
| `architecture` | `01-triage`, `02-hardware-budget`, `03-pipeline-and-concurrency`, `04-subject-audit`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | 티어별 시스템 아키텍처, 패스 그래프, 프레임 예산 수식, P0/P1/P2 시각 계층 |
| `implementation` | `01-triage`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops` | 자기 완결형 `#version 300 es` 셰이더, VAO/`std140` UBO 바인딩, 패스 구현 코드 |
| `debug` | `01-triage`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | FBO 불완전 오류, `mediump` 정밀도 깨짐, 2x2 쿼드 미분 경계, 컨텍스트 손실 원인 격리 |
| `optimize` | `01-triage`, `02-hardware-budget`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | 패스별 차등 타이밍 측정 계획, 동적 `targetDPR` 클램프 수식, `invalidateFramebuffer`, 대역폭 절감 |
| `review` | `01-triage`, `04-subject-audit`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | 코드 품질, 상태 격리, P0/P1/P2 시각적 설득력 및 배포 준비 감사 |
| `migration` | `01-triage`, `03-pipeline-and-concurrency`, `05-shader-rules`, `06-runtime-ops`, `07-validation-and-ci` | WebGL 1 -> WebGL 2.0 업그레이드 또는 WebGL 2.0 -> WebGPU(`GPUBindGroup`, WGSL, 클립 공간 `Z in [0, 1]`) 전환 청사진 |

---

## 구조화된 출력 스키마 및 예제

- [`schemas/authoring-base.json`](./schemas/authoring-base.json) — 전체 아키텍처 및 마이그레이션 스키마 (`skill`, `task`, `inputs`, `modules`, `assumptions`, `decisions`, `derivations`, `parallel_plan`, `deliverables`, `risks`, `validation_gates`).
  - 예제 (`architecture` / `sdf-raymarch`): [`examples/face-raymarch.output.json`](./examples/face-raymarch.output.json)
  - 예제 (`migration` / `hybrid`): [`examples/webgpu-migration-hybrid.output.json`](./examples/webgpu-migration-hybrid.output.json)
- [`schemas/runtime-compact.json`](./schemas/runtime-compact.json) — 컴팩트 응답 스키마 (`intent`, `project_class`, `subject`, `locale`, `modules`, `assumptions`, `derivations`, `key_decisions`, `parallel_tasks`, `risks`, `next_steps`, `validation_gates`).
  - 예제 (`optimize` / `raster-mesh`): [`examples/terrain-midrange.output.json`](./examples/terrain-midrange.output.json)
  - 예제 (`debug` / `postprocess`): [`examples/postprocess-context-loss.output.json`](./examples/postprocess-context-loss.output.json)

---

## 설치 및 검증 방법

```bash
git clone https://github.com/Emily2040/webgl2-systems-architect-skill.git
cd webgl2-systems-architect-skill
python scripts/validate_repo.py
```

정적 서버를 실행하여 4개 언어 대화형 워크벤치(`docs/index.html?lang=ko`) 또는 스모크 테스트(`fixtures/webgl2-smoke/index.html`)를 브라우저에서 확인할 수 있습니다:

```bash
python -m http.server 8080
```

---

## 릴리스 및 작성자 정보

- **패키지 이름**: `webgl2-systems-architect-skill`
- **버전**: `2.0.0`
- **라이선스**: [MIT](./LICENSE)
- **작성자**: **Iamemily2050** (`Emily2040`)
- **Git 커밋 이메일**: `191656017+Emily2040@users.noreply.github.com`
- **링크**: [GitHub 저장소](https://github.com/Emily2040/webgl2-systems-architect-skill) · [웹사이트](https://Iamemily2050.com) · [X (@iamemily2050)](https://x.com/iamemily2050) · [Instagram (@iamemily2050)](https://instagram.com/iamemily2050)
