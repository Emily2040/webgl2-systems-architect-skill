# 06 - 상태 격리, 리소스 수명, 컨텍스트 손실 및 WebGPU 마이그레이션 (ko)

## Purpose

WebGL 2.0 상태 누수, VRAM 누수, 모바일 타일 GPU 대역폭 낭비, 컨텍스트 손실 복구 실패를 방지하면서 WebGPU 마이그레이션에 대비된 리소스 추상화를 유지한다. 모든 GPU 핸들을 추적하라.

## When to load

모든 의도(`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`)에서 로드한다.

## Inputs

- 호스트 JS/TS 렌더러 코드, 패스 설정, 리사이즈 로직 및 이벤트 리스너
- 텍스처, 버퍼, VAO, Sampler, FBO, 프로그램 생성 및 해제 경로

## Rules

### 1. 패스 상태를 격리하고 WebGL 2.0 네이티브 객체를 사용한다

- **버텍스 배열 객체 (VAO)**: 초기화 시 `gl.createVertexArray()`로 정점 속성 바인딩을 기록하고, 렌더 루프에서는 `gl.bindVertexArray(vao)`만 호출한다. `gl_VertexID` 기반 풀스크린 삼각형 패스도 VAO 바인딩이 필수다.
- **유니폼 버퍼 객체 (UBO)**: `gl.uniformBlockBinding`과 `gl.bindBufferBase(gl.UNIFORM_BUFFER, binding, ubo)`로 `std140` 블록을 바인딩한다. `bindBufferRange` 사용 시 오프셋은 `UNIFORM_BUFFER_OFFSET_ALIGNMENT`의 배수여야 한다.
- **샘플러 객체 (Sampler)**: `gl.createSampler()`와 `gl.bindSampler(unit, sampler)`로 필터링/래핑 상태를 텍스처 스토리지와 분리한다.

### 2. 불변 텍스처 스토리지 할당 및 타일 GPU 프레임버퍼 무효화

- 드로우 시점의 밉맵 검증 오버헤드를 없애기 위해 `gl.texStorage2D` / `gl.texStorage3D` + `gl.texSubImage2D`를 사용한다.
- 모바일 타일 기반 GPU에서는 패스 종료 후 보존할 필요가 없는 깊이/스텐실 첨부물에 `gl.invalidateFramebuffer(gl.FRAMEBUFFER, [gl.DEPTH_ATTACHMENT, gl.STENCIL_ATTACHMENT])`를 호출하여 시스템 RAM 플러시를 방지한다.

### 3. 명시적 리소스 해제 및 컨텍스트 손실 복구 (`webglcontextlost` / `webglcontextrestored`)

- `gl.linkProgram(prog)` 직후 `detachShader`와 `deleteShader`로 임시 셰이더 객체를 즉시 해제한다.
- `webglcontextlost`에서 `event.preventDefault()`와 `cancelAnimationFrame`을 호출하고, `webglcontextrestored`에서 셰이더 -> VAO/UBO/Sampler -> 텍스처 -> FBO 순서로 리소스를 재구축한다.

### 4. WebGL 2.0에서 WebGPU로의 마이그레이션 매핑

- `VAO` -> `GPUVertexBufferLayout`
- `std140` UBO + 텍스처 유닛 + `WebGLSampler` -> `GPUBindGroupLayout` + `GPUBindGroup`
- `useProgram` + 가변 블렌드/깊이 상태 -> 불변 `GPURenderPipeline`
- `WebGLFramebuffer` + `invalidateFramebuffer` -> `GPURenderPassDescriptor` (`loadOp` / `storeOp`)
- 클립 공간 깊이 `Z in [-1, 1]` (좌하단 UV 원점) -> WebGPU `Z in [0, 1]` (좌상단 프레임버퍼 원점)

## Failure modes

- VAO를 바인딩하지 않고 `gl.drawArrays`를 호출하는 것
- `webglcontextlost`에서 `e.preventDefault()`를 누락하거나 손실 이전의 핸들을 재사용하는 것

## Output contribution

런타임 `decisions`, 상태/리소스 `risks`, `deliverables` (수명 주기 체크리스트 또는 WebGPU 매핑 표)를 채운다.
