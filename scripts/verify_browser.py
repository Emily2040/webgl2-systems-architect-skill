#!/usr/bin/env python3
"""Zero-dependency headless browser verifier using Chrome DevTools Protocol (CDP).

Starts a local HTTP server from the repository root, launches headless Chrome/Edge,
and verifies:
  1. fixtures/webgl2-smoke/index.html (offscreen FBO completeness, VAO, std140 UBO,
     multi-frame non-blocking PBO + fenceSync, and WEBGL_lose_context recovery).
  2. docs/index.html across all 4 locales (en, zh-CN, ja, ko), including localized
     select options, links, live JSON contract synthesis, 4-locale anti-slop linter,
     and 5 WebGL 2.0 diagnostic shader modes.
"""
from __future__ import annotations

import argparse
import base64
import functools
import http.server
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED_LOCALES = ("en", "zh-CN", "ja", "ko")


def find_browser_binary() -> str:
    env_bin = os.environ.get("CHROME_BIN")
    if env_bin and os.path.exists(env_bin):
        return env_bin

    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome", "msedge"):
        found = shutil.which(name)
        if found:
            candidates.insert(0, found)

    for path in candidates:
        if path and os.path.exists(path):
            return path
    raise RuntimeError("No Chrome, Chromium, or Edge binary found. Set CHROME_BIN to your browser executable.")


def get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass


class CDPClient:
    """Minimal RFC 6455 WebSocket client for Chrome DevTools Protocol using Python stdlib."""

    def __init__(self, ws_url: str) -> None:
        parsed = urlparse(ws_url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or 80
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        self.sock = socket.create_connection((host, port), timeout=15.0)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        handshake = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(handshake.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("WebSocket handshake closed unexpectedly")
            response += chunk
        header_end = response.index(b"\r\n\r\n") + 4
        self._buffer = response[header_end:]
        self._msg_id = 0
        self.console_errors: list[str] = []

    def _recv_exact(self, n: int) -> bytes:
        while len(self._buffer) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("WebSocket connection closed while reading frame")
            self._buffer += chunk
        out = self._buffer[:n]
        self._buffer = self._buffer[n:]
        return out

    def _read_frame(self) -> str:
        while True:
            b1, b2 = self._recv_exact(2)
            opcode = b1 & 0x0F
            masked = bool(b2 & 0x80)
            length = b2 & 0x7F
            if length == 126:
                (length,) = struct.unpack("!H", self._recv_exact(2))
            elif length == 127:
                (length,) = struct.unpack("!Q", self._recv_exact(8))
            mask_key = self._recv_exact(4) if masked else b""
            payload = self._recv_exact(length)
            if masked:
                payload = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
            if opcode == 0x8:
                raise RuntimeError("WebSocket closed by peer")
            if opcode == 0x9:  # Ping -> send Pong
                self._send_frame(payload, opcode=0xA)
                continue
            if opcode == 0x1:
                return payload.decode("utf-8", errors="replace")

    def _send_frame(self, payload: bytes, opcode: int = 0x1) -> None:
        mask_key = os.urandom(4)
        header = bytearray([0x80 | opcode])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        header.extend(mask_key)
        masked = bytes(b ^ mask_key[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._msg_id += 1
        target_id = self._msg_id
        msg = {"id": target_id, "method": method, "params": params or {}}
        self._send_frame(json.dumps(msg).encode("utf-8"))
        while True:
            raw = self._read_frame()
            data = json.loads(raw)
            if "method" in data:
                ev = data["method"]
                p = data.get("params", {})
                if ev == "Runtime.exceptionThrown":
                    details = p.get("exceptionDetails", {})
                    self.console_errors.append(f"Uncaught exception: {details.get('text', details)}")
                elif ev == "Runtime.consoleAPICalled" and p.get("type") == "error":
                    args = [a.get("value", a.get("description", "")) for a in p.get("args", [])]
                    self.console_errors.append("console.error: " + " ".join(str(x) for x in args))
                continue
            if data.get("id") == target_id:
                if "error" in data:
                    raise RuntimeError(f"CDP {method} error: {data['error']}")
                return data.get("result", {})

    def eval(self, expression: str) -> Any:
        res = self.call(
            "Runtime.evaluate",
            {
                "expression": expression,
                "returnByValue": True,
                "awaitPromise": True,
            },
        )
        if "exceptionDetails" in res:
            raise RuntimeError(f"JS eval exception in {expression!r}: {res['exceptionDetails']}")
        return res.get("result", {}).get("value")

    def close(self) -> None:
        try:
            self.sock.close()
        except Exception:
            pass


def wait_until(cdp: CDPClient, js_expr: str, timeout_s: float = 8.0) -> Any:
    deadline = time.time() + timeout_s
    last_val = None
    while time.time() < deadline:
        last_val = cdp.eval(js_expr)
        if last_val:
            return last_val
        time.sleep(0.1)
    raise RuntimeError(f"Timed out waiting for {js_expr!r} (last={last_val!r})")


def save_screenshot(cdp: CDPClient, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    res = cdp.call("Page.captureScreenshot", {"format": "png", "fromSurface": True})
    out_path.write_bytes(base64.b64decode(res["data"]))


def verify_smoke_fixture(cdp: CDPClient, base_url: str, screenshot_dir: Path | None) -> None:
    cdp.console_errors.clear()
    cdp.call("Page.navigate", {"url": f"{base_url}/fixtures/webgl2-smoke/index.html"})
    wait_until(cdp, "Boolean(window.__WEBGL2_SMOKE_RESULT__ && window.__WEBGL2_SMOKE_RESULT__.pass === true)")
    res = cdp.eval("window.__WEBGL2_SMOKE_RESULT__")
    if not isinstance(res, dict) or not res.get("pass") or not res.get("ok"):
        raise RuntimeError(f"Smoke fixture did not pass: {res}")
    if not res.get("fboComplete") or not res.get("pboAsyncSignaled"):
        raise RuntimeError(f"Smoke fixture FBO or async PBO check failed: {res}")
    if res.get("glError") != 0:
        raise RuntimeError(f"Smoke fixture reported WebGL error: {res}")

    # Drill WEBGL_lose_context recovery
    cdp.eval("document.getElementById('btn-lose-context').click()")
    wait_until(
        cdp,
        "Boolean(window.__WEBGL2_SMOKE_RESULT__ && window.__WEBGL2_SMOKE_RESULT__.contextRestoredCount >= 1 && window.__WEBGL2_SMOKE_RESULT__.pass === true)",
        timeout_s=8.0,
    )
    after_restore = cdp.eval("window.__WEBGL2_SMOKE_RESULT__")
    if cdp.console_errors:
        raise RuntimeError("Console errors on smoke fixture: " + "; ".join(cdp.console_errors))
    if screenshot_dir is not None:
        save_screenshot(cdp, screenshot_dir / "smoke_fixture_verified.png")
    print(
        f"[OK] Smoke fixture verified: FBO complete, PBO status={after_restore['pboWaitStatus']}, "
        f"RGBA={after_restore['centerPixelRGBA']}, contextRestoredCount={after_restore['contextRestoredCount']}"
    )


def verify_workbench_locales(cdp: CDPClient, base_url: str, screenshot_dir: Path | None) -> None:
    expected_skill_href = {
        "en": "../SKILL.md",
        "zh-CN": "../locales/zh-CN/SKILL.md",
        "ja": "../locales/ja/SKILL.md",
        "ko": "../locales/ko/SKILL.md",
    }
    expected_paradigm = {
        "en": "en-5lane-swimlane",
        "zh-CN": "zh-dual-ring-5phase",
        "ja": "ja-pokayoke-shedding",
        "ko": "ko-hbm-high-refresh",
    }
    expected_info_png = {
        "en": "assets/webgl2-systems-infographic.png",
        "zh-CN": "assets/zh-CN/webgl2-systems-infographic.png",
        "ja": "assets/ja/webgl2-systems-infographic.png",
        "ko": "assets/ko/webgl2-systems-infographic.png",
    }
    for loc in SUPPORTED_LOCALES:
        cdp.console_errors.clear()
        cdp.call("Page.navigate", {"url": f"{base_url}/docs/index.html?lang={loc}"})
        wait_until(
            cdp,
            f"document.documentElement.getAttribute('data-locale-theme') === '{loc}' && Boolean(document.getElementById('contract-json-preview').textContent)",
        )
        time.sleep(0.35)

        state = cdp.eval(
            """(() => {
              const contractRaw = document.getElementById('contract-json-preview').textContent;
              const contract = JSON.parse(contractRaw);
              const intentOpt0 = document.querySelector('#sel-intent option[value="architecture"]').textContent;
              const classOpt0 = document.querySelector('#sel-class option[value="sdf-raymarch"]').textContent;
              const bppOpt0 = document.querySelector('#calc-bpp option[value="8"]').textContent;
              const skillHref = document.getElementById('cta-skill').getAttribute('href');
              const heroImg = document.getElementById('hero-img');
              const infoPngImg = document.getElementById('infographic-png-img');
              const heroSrc = heroImg.getAttribute('src');
              const infoPngSrc = infoPngImg.getAttribute('src');
              const archSrc = document.getElementById('arch-svg-img').getAttribute('src');
              const wfStudio = document.getElementById('locale-workflow-studio');
              const wfParadigm = wfStudio ? wfStudio.getAttribute('data-workflow-paradigm') : '';
              const wfTabCount = wfStudio ? wfStudio.querySelectorAll('.wf-tab-btn').length : 0;

              // Click second tab in locale workflow studio to verify interactivity
              const secondTab = wfStudio ? wfStudio.querySelector('.wf-tab-btn[data-wf-idx="1"]') : null;
              if (secondTab) secondTab.click();

              // Test anti-slop sample detection
              document.getElementById('btn-slop-sample').click();
              const slopSampleBadge = document.getElementById('slop-badge').textContent;
              document.getElementById('btn-slop-clean').click();
              const slopCleanBadge = document.getElementById('slop-badge').textContent;

              // Cycle all 5 diagnostic shader modes
              for (let m = 0; m < 5; m++) {
                const btn = document.querySelector(`.mode-btn[data-mode="${m}"]`);
                if (btn) btn.click();
              }
              const mode0 = document.querySelector('.mode-btn[data-mode="0"]');
              if (mode0) mode0.click();

              return {
                theme: document.documentElement.getAttribute('data-locale-theme'),
                lang: document.documentElement.getAttribute('lang'),
                contractLocale: contract.locale,
                contractModulesCount: contract.modules.length,
                intentOpt0,
                classOpt0,
                bppOpt0,
                skillHref,
                heroSrc,
                infoPngSrc,
                heroNaturalWidth: heroImg.naturalWidth,
                infoPngNaturalWidth: infoPngImg.naturalWidth,
                archSrc,
                wfParadigm,
                wfTabCount,
                slopSampleBadge,
                slopCleanBadge,
                glStatus: document.getElementById('gl-status-pill').textContent,
                scrollWidth: document.documentElement.scrollWidth,
                innerWidth: window.innerWidth,
                selClassRight: Math.round(document.getElementById('sel-class').getBoundingClientRect().right),
                panel1Right: Math.round(document.getElementById('sel-class').closest('.panel').getBoundingClientRect().right)
              };
            })()"""
        )

        if state["scrollWidth"] > state["innerWidth"]:
            raise RuntimeError(f"Locale {loc} has horizontal overflow: scrollWidth={state['scrollWidth']} > innerWidth={state['innerWidth']}")
        if state["selClassRight"] > state["panel1Right"]:
            raise RuntimeError(f"Locale {loc} #sel-class overflows parent .panel: selClassRight={state['selClassRight']} > panel1Right={state['panel1Right']}")
        if state["theme"] != loc or state["lang"] != loc or state["contractLocale"] != loc:
            raise RuntimeError(f"Locale {loc} state mismatch: {state}")
        if state["skillHref"] != expected_skill_href[loc]:
            raise RuntimeError(f"Locale {loc} #cta-skill href mismatch: expected {expected_skill_href[loc]}, got {state['skillHref']}")
        if state["wfParadigm"] != expected_paradigm[loc] or state["wfTabCount"] < 4:
            raise RuntimeError(f"Locale {loc} workflow studio mismatch: paradigm={state['wfParadigm']}, tabs={state['wfTabCount']}")
        if state["infoPngSrc"] != expected_info_png[loc] or state["infoPngNaturalWidth"] != 1376 or state["heroNaturalWidth"] != 1376:
            raise RuntimeError(f"Locale {loc} PNG plate mismatch: {state}")
        if loc != "en" and state["intentOpt0"].startswith("architecture — Full"):
            raise RuntimeError(f"Locale {loc} #sel-intent option was not localized: {state['intentOpt0']}")
        if loc != "en" and state["bppOpt0"].startswith("8 B/px — RGBA8 read"):
            raise RuntimeError(f"Locale {loc} #calc-bpp option was not localized: {state['bppOpt0']}")
        if "0" in state["slopSampleBadge"]:
            raise RuntimeError(f"Locale {loc} anti-slop linter failed to flag sample slop: {state['slopSampleBadge']}")
        if "0" not in state["slopCleanBadge"]:
            raise RuntimeError(f"Locale {loc} anti-slop linter failed to clear clean spec: {state['slopCleanBadge']}")
        if cdp.console_errors:
            raise RuntimeError(f"Console errors on docs/index.html?lang={loc}: " + "; ".join(cdp.console_errors))

        if screenshot_dir is not None:
            cdp.eval("window.scrollTo(0, 0)")
            time.sleep(0.15)
            save_screenshot(cdp, screenshot_dir / f"workbench_{loc}.png")
            cdp.eval("document.getElementById('bp-heading').scrollIntoView({block: 'start'})")
            time.sleep(0.2)
            save_screenshot(cdp, screenshot_dir / f"workbench_{loc}_workflow.png")

        print(
            f"[OK] Workbench locale {loc} verified: theme={state['theme']}, paradigm={state['wfParadigm']}, "
            f"infoPng={state['infoPngSrc']}, slopSample={state['slopSampleBadge']!r}, glStatus={state['glStatus']!r}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify WebGL2 smoke fixture and 4-locale workbench in headless Chrome.")
    parser.add_argument("--screenshot-dir", type=Path, default=None, help="Optional directory to save PNG screenshots.")
    args = parser.parse_args()

    browser_bin = find_browser_binary()
    http_port = get_free_port()
    cdp_port = get_free_port()

    handler = functools.partial(QuietHTTPRequestHandler, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", http_port), handler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    temp_profile = tempfile.mkdtemp(prefix="webgl2_skill_cdp_")
    proc = subprocess.Popen(
        [
            browser_bin,
            "--headless=new",
            "--disable-gpu-sandbox",
            "--enable-webgl",
            "--ignore-gpu-blocklist",
            "--use-angle=default",
            "--no-first-run",
            "--no-default-browser-check",
            "--window-size=1440,1080",
            "--force-device-scale-factor=2",
            f"--remote-debugging-port={cdp_port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={temp_profile}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    cdp: CDPClient | None = None
    try:
        ws_url = None
        deadline = time.time() + 10.0
        while time.time() < deadline:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{cdp_port}/json", timeout=1.0) as resp:
                    targets = json.loads(resp.read().decode("utf-8"))
                    page_targets = [t for t in targets if t.get("type") == "page" and "webSocketDebuggerUrl" in t]
                    if page_targets:
                        ws_url = page_targets[0]["webSocketDebuggerUrl"]
                        break
            except Exception:
                time.sleep(0.15)
        if not ws_url:
            raise RuntimeError("Failed to connect to headless browser DevTools endpoint")

        cdp = CDPClient(ws_url)
        cdp.call("Page.enable")
        cdp.call("Runtime.enable")
        cdp.call(
            "Emulation.setDeviceMetricsOverride",
            {"width": 1440, "height": 1080, "deviceScaleFactor": 2, "mobile": False},
        )

        base_url = f"http://127.0.0.1:{http_port}"
        verify_smoke_fixture(cdp, base_url, args.screenshot_dir)
        verify_workbench_locales(cdp, base_url, args.screenshot_dir)
        print("[OK] Headless browser verification succeeded across smoke fixture and all 4 locales")
    finally:
        if cdp is not None:
            cdp.close()
        proc.terminate()
        try:
            proc.wait(timeout=5.0)
        except Exception:
            proc.kill()
        httpd.shutdown()
        shutil.rmtree(temp_profile, ignore_errors=True)


if __name__ == "__main__":
    main()
