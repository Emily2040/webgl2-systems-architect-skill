# 06 - 상태 격리, 리소스 수명, 컨텍스트 손실 및 WebGPU 마이그레이션 (ko)

## 목적 (Purpose)

WebGL 2.0 상태 누수, VRAM 누수, 모바일 타일 GPU 대역폭 낭비, 컨텍스트 손실 복구 실패를 방지하면서 WebGPU 마이그레이션에 대비된 리소스 추상화를 유지한다. 모든 GPU 핸들을 추적하라.

## 로드 시점 (When to load)

모든 의도(`architecture`, `implementation`, `debug`, `optimize`, `review`, `migration`)에서 로드한다.

## 입력 (Inputs)

- 호스트 JS/TS 렌더러 코드, 패스 설정, 리사이즈 로직 및 이벤트 리스너
- 텍스처, 버퍼, VAO, Sampler, FBO, 프로그램 생성 및 해제 경로

## 핵심 규칙 (Rules)

### 1. 패스 상태를 격리하고 WebGL 2.0 네이티브 객체를 사용한다

- **버텍스 배열 객체 (VAO)**: 초기화 시 `gl.createVertexArray()`로 정점 속성 바인딩을 기록하고, 렌더 루프에서는 `gl.bindVertexArray(vao)`만 호출한다. `gl_VertexID` 기반 풀스크린 삼각형 패스도 비어 있지 않은 VAO 바인딩이 필수다.
- **유니폼 버퍼 객체 (UBO)**: `gl.uniformBlockBinding`과 `gl.bindBufferBase(gl.UNIFORM_BUFFER, binding, ubo)`로 `std140` 블록을 바인딩한다. `bindBufferRange` 사용 시 오프셋은 `UNIFORM_BUFFER_OFFSET_ALIGNMENT`의 배수여야 한다.
- **샘플러 객체 (Sampler)**: `gl.createSampler()`와 `gl.bindSampler(unit, sampler)`로 필터링/래핑 상태를 텍스처 스토리지와 분리한다.

### 2. 불변 텍스처 스토리지 할당 및 타일 GPU 프레임버퍼 무효화

- 드로우 시점의 밉맵 검증 오버헤드를 없애기 위해 `gl.texStorage2D` / `gl.texStorage3D` + `gl.texSubImage2D`를 사용한다.
- 모바일 타일 기반 GPU에서는 패스 종료 후 보존할 필요가 없는 깊이/스텐실 첨부물에 `gl.invalidateFramebuffer(gl.FRAMEBUFFER, [gl.DEPTH_ATTACHMENT, gl.STENCIL_ATTACHMENT])`를 호출하여 시스템 RAM 플러시를 방지한다.

### 3. 명시적 리소스 해제 및 컨텍스트 손실 복구 (`webglcontextlost` / `webglcontextrestored`)

- `gl.linkProgram(prog)` 직후 `detachShader`와 `deleteShader`로 임시 셰이더 객체를 즉시 해제한다.
- `webglcontextlost` 및 `webglcontextrestored` 리스너를 등록하고, 손실된 이전 핸들에 `delete*`를 호출하지 않고 의존성 순서대로 재구축한다:

```js
canvas.addEventListener('webglcontextlost', (e) => {
  e.preventDefault();
  cancelAnimationFrame(rafId);
}, false);

canvas.addEventListener('webglcontextrestored', () => {
  initCapabilitiesAndExtensions(gl);
  rebuildShadersVAOsUBOsSamplersTexturesAndFBOs(gl);
  rafId = requestAnimationFrame(renderFrame);
}, false);
```

### 4. WebGL 2.0에서 WebGPU(WGSL)로의 1:1 마이그레이션 매핑 표

| WebGL 2.0 개념 | WebGPU 대응 개념 | 마이그레이션 엔지니어링 규칙 |
| --- | --- | --- |
| `WebGLVertexArrayObject` (VAO) | `GPUVertexBufferLayout` | 정점 버퍼 스트라이드와 속성 오프셋을 파이프라인 디스크립터에 선언한다 |
| `std140` UBO + 텍스처 유닛 + `WebGLSampler` | `GPUBindGroupLayout` + `GPUBindGroup` | 갱신 주기별(`group(0)` 프레임, `group(1)` 패스, `group(2)` 재질)로 묶는다 |
| `useProgram` + 가변 블렌드/깊이 상태 | 불변 `GPURenderPipeline` | 셰이더·블렌드·깊이·첨부물 포맷을 키로 파이프라인을 사전 생성한다 |
| `WebGLFramebuffer` + `invalidateFramebuffer` | `GPURenderPassDescriptor` (`loadOp`/`storeOp`) | 임시 깊이 첨부물에는 `storeOp: 'discard'`를 명시한다 |
| 클립 공간 깊이 `Z in [-1, 1]`·좌하단 UV 원점 | 클립 공간 깊이 `Z in [0, 1]`·좌상단 프레임버퍼 원점 | 깊이 리매핑과 UV Y-플립을 단일 카메라/포스트프로세스 헬퍼에 격리한다 |

## 주요 실패 모드 (Failure modes)

- VAO를 바인딩하지 않고 `gl.drawArrays`를 호출하는 것
- `webglcontextlost`에서 `e.preventDefault()`를 누락하거나 손실 이전의 핸들을 재사용하는 것

## 출력 계약 기여 (Output contribution)

런타임 `decisions`, 상태/리소스 `risks`, `deliverables` (수명 주기 체크리스트 또는 WebGPU 매핑 표)를 채운다.
