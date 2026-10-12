# 02 - WebGL 2.0 및 GLSL ES 3.00 공식 명세 참조표 (ko)

본 스킬 패키지의 모든 핵심 불변량(Invariants)은 다음 공식 표준 문서와 하드웨어 아키텍처 명세에 근거합니다.

| 영역 | 공식 명세 / 기술 표준 | 핵심 엔지니어링 제약 및 관련 모듈 |
| --- | --- | --- |
| **WebGL 2.0 렌더링 컨텍스트 및 상태 머신** | Khronos WebGL 2.0 Specification (OpenGL ES 3.0.4 기반) | 단일 컨텍스트 직렬 명령 제출, VAO(`createVertexArray`) 상시 바인딩 필수, `texStorage2D` 불변 텍스처 스토리지, `invalidateFramebuffer` 타일 메모리 플러시 방지, `MAX_CLIENT_WAIT_TIMEOUT_WEBGL == 0` (`03`, `06`) |
| **GLSL ES 3.00 셰이더 언어 명세** | The OpenGL ES Shading Language 3.00 Specification | 0바이트 `#version 300 es`, `in`/`out` 스테이지 인터페이스, `layout(location = N)`, `layout(std140)` 16바이트 정렬 규칙, 비균일 제어 흐름 내부 암시적 미분(`texture`, `dFdx`, `dFdy`, `fwidth`) 미정의 동작 (`05`) |
| **비동기 컴파일·GPU 타이머·FBO 확장 명세** | Khronos WebGL Extension Registry (`KHR_parallel_shader_compile`, `EXT_disjoint_timer_query_webgl2`, `EXT_color_buffer_float`, `OES_texture_float_linear`, `WEBGL_lose_context`) | 프레임 간 `COMPLETION_STATUS_KHR` 비차단 폴링, `GPU_DISJOINT_EXT === false` 검증 기반 3~4프레임 지연 타이머 링 버퍼, 부동소수점 FBO 완전성 검증 및 컨텍스트 복구 훈련 (`02`, `03`, `06`, `07`) |
| **SDF 레이마칭 및 사면체 노멀 수학** | Hart (1996) *Sphere Tracing: A Geometric Method for the Antialiased Ray Tracing of Implicit Surfaces* · 사면체 유한차분법 | Lipschitz 상수에 기반한 스텝 감쇠(`stepScale = 0.65..0.85`), 6탭 중심차분을 대체하는 4탭 사면체 기울기 노멀(`k = (±1,±1,±1)`) (`05`) |
| **WebGL 2.0 -> WebGPU 이관 명세** | W3C WebGPU & WGSL Specifications | `VAO -> GPUVertexBufferLayout`, `std140 UBO -> GPUBindGroup`, `WebGLFramebuffer -> GPURenderPassDescriptor`, 클립 공간 깊이 `Z in [-1, 1] -> [0, 1]` 및 UV Y-원점 단일 헬퍼 격리 (`06`) |
