# 02 - 하드웨어 프로브 및 프레임 예산 산정 (ko)

## Purpose

아키텍처 설계와 성능 최적화 결정을 실제 WebGL 2.0 기능 한계, 메모리 대역폭 수식, 실측 프레임 시간에 근거하게 한다. 기능을 줄이기 전에 먼저 측정하라.

## When to load

`architecture` 및 `optimize` 작업, 또는 FPS 저하, DPR 스케일링, 메모리 대역폭, 발열 쓰로틀링 문제를 다룰 때 로드한다.

## Inputs

- 대상 플랫폼, 뷰포트 해상도 및 목표 FPS (`30`, `60`, `90`, `120`)
- 런타임 `gl.getParameter` 및 `gl.getExtension` 조회 결과
- 기존 패스 타이밍 로그 또는 차등 기능 토글 측정값

## Rules

### 1. 실제 WebGL 2.0 하드웨어 한계를 먼저 조회한다

User-Agent 문자열로 기기 등급을 추측하지 말고 `gl.getParameter`와 `gl.getExtension`으로 직접 조회한다:

- 텍스처 한계: `MAX_TEXTURE_SIZE`, `MAX_CUBE_MAP_TEXTURE_SIZE`, `MAX_3D_TEXTURE_SIZE`, `MAX_ARRAY_TEXTURE_LAYERS`, `MAX_TEXTURE_IMAGE_UNITS`, `MAX_VERTEX_TEXTURE_IMAGE_UNITS`
- MRT 및 MSAA 한계: `MAX_COLOR_ATTACHMENTS`, `MAX_DRAW_BUFFERS`, `MAX_SAMPLES`, `MAX_RENDERBUFFER_SIZE`
- Uniform 및 UBO 한계: `MAX_VERTEX_UNIFORM_VECTORS`, `MAX_FRAGMENT_UNIFORM_VECTORS`, `MAX_UNIFORM_BUFFER_BINDINGS`, `MAX_UNIFORM_BLOCK_SIZE`, `UNIFORM_BUFFER_OFFSET_ALIGNMENT`
- 핵심 확장: `EXT_disjoint_timer_query_webgl2`, `KHR_parallel_shader_compile`, `EXT_color_buffer_float`, `OES_texture_float_linear`, `WEBGL_lose_context`

### 2. 증거 우선순위를 엄격히 준수한다

1. **링 버퍼 방식의 GPU 타이머 쿼리 (`EXT_disjoint_timer_query_webgl2`)**: 2~3 프레임 뒤에 `QUERY_RESULT_AVAILABLE`을 확인하고 `GPU_DISJOINT_EXT === false`일 때만 `QUERY_RESULT`를 신뢰한다.
2. **통제된 차등 측정**: 카메라와 씬을 고정한 상태에서 패스를 하나씩 끄거나 DPR을 변경하여 프레임 시간 차이를 측정한다.
3. **`gl.getParameter` 명시적 한계값**.
4. **기기 등급 휴리스틱 추산** (가장 낮은 순위; 반드시 `estimated` 또는 `unknown`으로 표시).

### 3. 프레임 예산, 필레이트, 대역폭 수식을 명시한다

```text
frameBudgetMs = 1000 / targetFPS
gpuBudgetMs   = frameBudgetMs - cpuMainThreadReserveMs - browserCompositorReserveMs
activePixels  = (cssWidth * targetDPR) * (cssHeight * targetDPR)
bandwidthBps  = activePixels * bytesPerPixelReadWriteAcrossPasses * targetFPS
targetDPR     = min(devicePixelRatio, maxDPRCap, sqrt(gpuBudgetMs / (cssWidth * cssHeight * 1e-6 * msPerMegapixel)))
```

### 4. 3단계 품질 티어 (`low` / `mid` / `high`) 를 정의한다

각 티어별 내부 렌더 스케일, `targetDPR` 상한, FBO 포맷(`RGBA8` 대 `EXT_color_buffer_float` 기반 `RGBA16F`), MSAA 샘플 수, 레이마칭/필터 탭 수를 명시한다.

## Failure modes

- 추정된 GPU TFLOPS 수치를 실제 브라우저 성능으로 간주하는 것
- 동일 프레임에서 타이머 쿼리를 동기 조회하거나 `GPU_DISJOINT_EXT`를 무시하는 것
- `bindBufferRange` 오프셋을 `UNIFORM_BUFFER_OFFSET_ALIGNMENT` 배수로 맞추지 않는 것

## Output contribution

`inputs.hardware_data_quality`, `derivations` (프레임 예산, DPR 클램프, 대역폭), 티어별 `decisions`, 하드웨어 `risks`를 채운다.
