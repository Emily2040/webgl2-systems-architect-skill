# 03 - 파이프라인 토폴로지 및 동시성 설계 (ko)

## 목적 (Purpose)

CPU 스레드와 단일 GPU 큐에서 WebGL 2.0이 실제로 실행되는 방식에 맞춰 렌더 패스 그래프, 시작 흐름, 비동기 파이프라인을 설계한다. 단일 컨텍스트는 드로우 콜을 직렬화한다.

## 로드 시점 (When to load)

`architecture`, `implementation`, `optimize`, `migration` 작업에서 패스 그래프, FBO 체인, Web Worker, 셰이더 컴파일, 리드백을 다룰 때 로드한다.

## 입력 (Inputs)

- 프로젝트 분류 (`raster-mesh`, `sdf-raymarch`, `hybrid`, `postprocess`, `data-vis`, `ui`)
- 대상 패스 체인, 에셋 크기 및 첫 프레임 지연 시간 예산
- `OffscreenCanvas`, Web Worker, `KHR_parallel_shader_compile` 지원 여부

## 핵심 규칙 (Rules)

### 1. 관성이 아니라 요구사항에 따라 컨텍스트 속성을 선택한다

불투명 캔버스는 `alpha: false`로 설정하여 브라우저 컴포지터 블렌딩 비용을 제거한다. 오프스크린 FBO나 SDF 레이마칭에서는 `antialias: false`로 설정하고, 필요한 경우에만 `renderbufferStorageMultisample` + `blitFramebuffer`를 사용한다.

### 2. 진짜 병렬 작업, 프레임 간 파이프라인, 단일 컨텍스트 직렬 제출을 구분한다

- **CPU / Web Worker 병렬 가능**: 네트워크 `fetch`, glTF/Draco 압축 해제, KTX2/Basis 트랜스코딩, BVH 구축, 절두체 컬링, 지형 청크 생성, `createImageBitmap` 디코딩.
- **프레임 간 파이프라인 처리 가능 (비차단 GPU/CPU 오버랩)**:
  - `KHR_parallel_shader_compile`: 프레임 간에 `ext.COMPLETION_STATUS_KHR`를 폴링한 뒤 완료되었을 때만 `gl.LINK_STATUS`를 조회한다:

```js
function pollProgramLink(gl, ext, prog) {
  if (ext && !gl.getProgramParameter(prog, ext.COMPLETION_STATUS_KHR)) return null;
  return gl.getProgramParameter(prog, gl.LINK_STATUS);
}
```

  - `gl.PIXEL_PACK_BUFFER` (PBO) + `gl.fenceSync`: 프레임 $N$에서 비동기 `readPixels`와 펜스를 생성하고, 이후 프레임에서 `clientWaitSync(fence, 0, 0)`를 폴링하여 신호가 완료된 뒤에만 `getBufferSubData`를 호출한다:

```js
// 프레임 N: 비동기 PBO 패킹 시작 및 GPU 펜스 삽입
gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbo);
gl.readPixels(x, y, w, h, gl.RGBA, gl.UNSIGNED_BYTE, 0);
gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
const fence = gl.fenceSync(gl.SYNC_GPU_COMMANDS_COMPLETE, 0);
gl.flush();
// 프레임 N+k: timeout = 0 비차단 폴링 후 완료 시에만 리드백
const status = gl.clientWaitSync(fence, 0, 0);
if (status === gl.ALREADY_SIGNALED || status === gl.CONDITION_SATISFIED) {
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, pbo);
  gl.getBufferSubData(gl.PIXEL_PACK_BUFFER, 0, dstPixels);
  gl.bindBuffer(gl.PIXEL_PACK_BUFFER, null);
  gl.deleteSync(fence);
}
```

- **단일 `WebGL2RenderingContext`에서 직렬 실행**: 상태 전환, 버퍼/텍스처 업로드, 드로우 콜.

### 3. 첫 프레임 부트 시퀀스 단계화 및 상태 정렬

프레임 1에서는 부트스트랩 셰이더와 1×1 플레이스홀더 텍스처(`texStorage2D`)만으로 즉시 첫 화면을 그리고, 고해상도 텍스처와 보조 셰이더는 이후 프레임에서 비동기로 준비한다. 패스 내부는 **FBO -> Program -> UBO/텍스처 -> VAO -> Draw Call** 순서로 정렬한다.

## 주요 실패 모드 (Failure modes)

- 순차적인 `gl.*` 호출을 `async`/`await`로 감싸고 병렬 GPU 실행이라고 주장하는 것
- `COMPLETION_STATUS_KHR`가 `false`인 상태에서 `LINK_STATUS`를 조회하여 메인 스레드를 멈추게 하는 것
- `readPixels`와 동일한 프레임에서 `TIMEOUT_EXPIRED`를 무시하고 `getBufferSubData`를 즉시 호출하여 파이프라인 스톨을 유발하는 것

## 출력 계약 기여 (Output contribution)

`decisions` (컨텍스트 속성, 패스 그래프, 시작 흐름), `parallel_plan` (또는 `parallel_tasks`), 동시성 `risks`를 채운다.
