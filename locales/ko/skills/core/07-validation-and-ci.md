# 07 - 검증 사다리, 프로파일링 및 CI 게이트 (ko)

## 목적 (Purpose)

WebGL 2.0 렌더러나 스킬 패키지가 정상 컴파일되고, 비자명한 픽셀을 렌더링하며, 컨텍스트 손실에서 복구되고, 불변 규칙 위반 시 즉시 실패하는지 검증한다. 컴파일 성공만으로 배포하지 마라.

## 로드 시점 (When to load)

`architecture`, `debug`, `optimize`, `review`, `migration` 작업에서 로드한다.

## 입력 (Inputs)

- 검증 대상 셰이더, JS/TS 런타임 코드 또는 구조화된 아키텍처 설계안
- 테스트 환경 (로컬 브라우저, 헤드리스 Chromium/Playwright 또는 CI 러너)

## 핵심 규칙 (Rules)

### 1. 5단계 WebGL 2.0 검증 사다리를 실행한다

1. **셰이더 컴파일 및 링크 게이트**: 0바이트 위치의 `#version 300 es`와 `COMPILE_STATUS` / `LINK_STATUS`를 확인한다.
2. **프레임버퍼 완전성 및 상태 게이트**: 모든 커스텀 FBO에서 `gl.checkFramebufferStatus(gl.FRAMEBUFFER) === gl.FRAMEBUFFER_COMPLETE`를 확인하고, `EXT_color_buffer_float` 미지원 시 발생하는 `FRAMEBUFFER_INCOMPLETE_ATTACHMENT`와 다중 샘플 수 불일치로 인한 `FRAMEBUFFER_INCOMPLETE_MULTISAMPLE`을 검사한다.
3. **픽셀 및 다중 프레임 PBO + Fence 비차단 리드백 게이트**: 결정론적 프레임을 렌더링하여 중심 픽셀 RGBA 값을 검증하고(`fixtures/webgl2-smoke/index.html` 참조), `gl.PIXEL_PACK_BUFFER` + `gl.fenceSync`를 프레임 간 폴링하여 신호 완료 후 `getBufferSubData`로 검증한다.
4. **컨텍스트 손실 복구 훈련**: `WEBGL_lose_context.loseContext()` 및 `restoreContext()`를 실행하여 `gl.getError() === gl.NO_ERROR` 상태로 복구되는지 확인한다.
5. **차등 성능 및 시각적 회귀 게이트**: 고정된 OS/브라우저/DPR 환경에서 스크린샷을 비교하고 패스별 개별 토글 및 `EXT_disjoint_timer_query_webgl2`로 프레임 시간 차이를 측정한다.

### 2. 진단용 셰이더 출력 모드 (`uDebugMode`)

원인 격리를 위해 셰이더 내부에 4가지 진단 출력 모드를 제공한다:

```glsl
if (uDebugMode == 1) { outColor = vec4(N * 0.5 + 0.5, 1.0); return; }           // 사면체 노멀 시각화
if (uDebugMode == 2) { outColor = vec4(vec3(float(steps) / float(MAX_STEPS)), 1.0); return; } // 레이마칭 스텝 히트맵
if (uDebugMode == 3) { outColor = vec4(dPdx * 16.0, length(dPdy) * 16.0, 1.0); return; }      // UV 미분 불연속성 검사
if (isnan(col.r) || isnan(col.g) || isnan(col.b) || isinf(col.r)) {
  outColor = vec4(1.0, 0.0, 1.0, 1.0); return; // NaN / Inf 마젠타 경고 출력
}
```

### 3. 저장소 검증 및 네거티브 셀프 테스트

`python scripts/validate_repo.py` 및 `python scripts/verify_browser.py`를 실행하여 JSON 스키마, 모듈 집합 일치, 전체 8개 SVG XML 정합성 및 텍스트 박스 여백, 4개 언어(`en`, `zh-CN`, `ja`, `ko`) 패리티, `registry/forbidden-slop.json` 4개 국어 금지어 검사, 그리고 잘못된 입력을 거부하는 네거티브 셀프 테스트를 통과시킨다.

## 주요 실패 모드 (Failure modes)

- `gl.checkFramebufferStatus`를 확인하지 않고 멀티패스 FBO 파이프라인을 배포하는 것
- 프로덕션 렌더 루프 안에서 매 프레임 `gl.getError()`나 동기 `gl.readPixels`를 호출하여 CPU/GPU 동기화 스톨을 유발하는 것

## 출력 계약 기여 (Output contribution)

`deliverables` (검증 매트릭스), `risks`, `validation_gates` 및 최종 신뢰도 등급을 채운다.
