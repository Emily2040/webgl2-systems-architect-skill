# 05 - GLSL ES 3.00 및 셰이더 수학 규율 (ko)

## Purpose

WebGL 2.0 셰이더의 이식성, 자기 완결성, 수치적 안정성을 보장하고 매직 넘버를 제거한다. 모든 셰이더는 `#version 300 es`로 시작한다.

## When to load

GLSL ES 3.00 버텍스/프래그먼트 셰이더를 작성, 리뷰, 디버그, 최적화하거나 WGSL로 마이그레이션할 때 로드한다.

## Inputs

- 셰이더 소스 코드 또는 대상 셰이딩 알고리즘
- 프로젝트 분류 및 대상 GPU 정밀도 프로필 (모바일 `mediump` FP16 대 데스크톱 `highp` FP32)

## Rules

### 1. 엄격한 GLSL ES 3.00 (`#version 300 es`) 스테이지 계약을 적용한다

- 모든 셰이더 파일의 0번째 바이트는 `#version 300 es`여야 하며, 명시적 정밀도 선언(`precision highp float; precision highp int;`)을 포함한다.
- 버텍스 입력은 `layout(location = N) in`, 스테이지 인터페이스는 `in` / `out`, 프래그먼트 출력은 `layout(location = 0) out vec4 outColor;`를 사용한다. WebGL 1.0의 `attribute`, `varying`, `texture2D`, `gl_FragColor`를 절대 혼용하지 않는다.
- 프레임/패스 공유 유니폼은 `layout(std140) uniform FrameBlock { ... };`으로 묶어 WebGPU `GPUBindGroup`과 1:1 매핑되게 한다.

### 2. 자유 변수와 설명 없는 매직 리터럴을 금지한다

모든 헬퍼 함수는 매개변수, UBO, `in` 변수 또는 명명된 상수를 통해 입력을 선언해야 하며, 모든 수치 상수에는 기하학적·물리적 유도 주석을 남긴다 (예: `SURF_HIT_EPS = 0.0042`, `NORMAL_GRAD_EPS = 0.0084`, `SKIN_F0 = 0.0255`).

### 3. 정밀도, 나눗셈, 비균일 제어 흐름 내 미분을 보호한다

- 월드/카메라 좌표, 레이 원점 및 방향, 시간 `uTime`, 깊이 연산에는 반드시 `highp`를 사용한다.
- 분모와 거듭제곱 밑을 보호한다: `inversesqrt(max(dot(v, v), 1e-12))`, `sqrt(max(x, 0.0))`, `pow(max(base, 0.0), expVal)`.
- 비균일 `if`, `for`, 레이마칭 `break` 루프에 진입하기 **전**에 `vec2 dPdx = dFdx(uv); vec2 dPdy = dFdy(uv);`를 먼저 계산하고, 분기 내부에서는 `textureGrad(uTex, uv, dPdx, dPdy)` 또는 `textureLod`를 호출한다.
- SDF 노멀 계산은 6탭 중심차분 대신 4탭 사면체 차분(Tetrahedral normal)을 사용한다.

## Failure modes

- `#version 300 es` 셰이더에 `varying`이나 `gl_FragColor`를 사용하여 컴파일 에러를 유발하는 것
- 동적 분기나 레이마칭 루프 안에서 암시적 LOD `texture(uTex, uv)`나 `fwidth()`를 호출하여 2x2 쿼드 경계 깨짐을 만드는 것
- `std140` UBO 내부에 16바이트 정렬을 고려하지 않고 `vec3` 배열을 배치하는 것

## Output contribution

`derivations` (상수 유도, 정밀도 선택, 루프 상한), 셰이더 `decisions`, 수치적 `risks`를 채운다.
