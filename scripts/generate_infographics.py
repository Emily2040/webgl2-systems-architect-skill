#!/usr/bin/env python3
"""Composite the 8 AI-generated studio hardware plates (4 Hero + 4 Infographic)
with razor-sharp native EN / zh-CN / ja / ko typography, pixel-verified text bounds,
and unique per-locale visual and workflow designs."""

from __future__ import annotations

import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
BRAIN_DIR = Path(r"C:\Users\emily\.gemini\antigravity\brain\502cb686-82c3-4add-b18d-3043507784a3")
PLATES_DIR = ROOT / "docs" / "assets" / "plates"

RAW_SOURCES = {
    "hero_en": BRAIN_DIR / "hero_en_clean_studio_1791705251993.jpg",
    "hero_zh": BRAIN_DIR / "hero_zh_clean_studio_1791705267408.jpg",
    "hero_ja": BRAIN_DIR / "hero_ja_clean_studio_1791705282251.jpg",
    "hero_ko": BRAIN_DIR / "hero_ko_clean_studio_1791705299329.jpg",
    "info_en": BRAIN_DIR / "info_en_swiss_plate_1791705397933.jpg",
    "info_zh": BRAIN_DIR / "info_zh_jade_plate_1791705410952.jpg",
    "info_ja": BRAIN_DIR / "info_ja_sumi_plate_1791705423740.jpg",
    "info_ko": BRAIN_DIR / "info_ko_celadon_plate_1791705435802.jpg",
}


def ensure_plates() -> dict[str, Path]:
    PLATES_DIR.mkdir(parents=True, exist_ok=True)
    local_plates: dict[str, Path] = {}
    for key, src in RAW_SOURCES.items():
        dst = PLATES_DIR / f"{key}.jpg"
        if src.exists():
            shutil.copy2(src, dst)
        if not dst.exists():
            raise FileNotFoundError(f"Missing generated base plate: {dst}")
        local_plates[key] = dst
    return local_plates


def get_font_candidates(locale: str) -> tuple[list[str], list[str]]:
    if locale == "zh-CN":
        return ["msyhbd.ttc", "simhei.ttf", "msyh.ttc"], ["msyh.ttc", "simsun.ttc"]
    if locale == "ja":
        return ["YuGothB.ttc", "meiryob.ttc", "msgothic.ttc"], ["YuGothM.ttc", "meiryo.ttc", "msgothic.ttc"]
    if locale == "ko":
        return ["malgunbd.ttf", "malgun.ttf"], ["malgun.ttf"]
    return ["segoeuib.ttf", "arialbd.ttf", "calibrib.ttf"], ["segoeui.ttf", "arial.ttf", "calibri.ttf"]


def load_font(candidates: list[str], size: int) -> ImageFont.FreeTypeFont:
    win_fonts = Path(r"C:\Windows\Fonts")
    for name in candidates:
        p = win_fonts / name
        if p.exists():
            return ImageFont.truetype(str(p), size)
    return ImageFont.load_default()


def get_fonts(locale: str) -> dict[str, ImageFont.FreeTypeFont]:
    sans_b, sans_r = get_font_candidates(locale)
    # Use locale-capable font for mono in CJK so CJK labels never render as missing-glyph boxes
    mono = ["consolab.ttf", "consola.ttf"] if locale == "en" else sans_b
    return {
        "locale": locale,  # type: ignore[dict-item]
        "h1": load_font(sans_b, 36),
        "h2": load_font(sans_b, 23),
        "h3": load_font(sans_b, 16),
        "card_title": load_font(sans_b, 15),
        "body": load_font(sans_r, 13),
        "small": load_font(sans_r, 12),
        "tiny": load_font(sans_b, 11),
        "mono_b": load_font(mono, 13),
        "mono_s": load_font(mono, 11),
        "seal": load_font(sans_b, 14),
    }


def draw_fitted_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    max_width: int,
    locale: str = "en",
    bold: bool = False,
) -> None:
    """Ensure text fits strictly within max_width by stepping down font size if needed."""
    w = draw.textlength(text, font=font)
    cur_font = font
    if w > max_width:
        sans_b, sans_r = get_font_candidates(locale)
        cands = sans_b if bold else sans_r
        orig_size = getattr(font, "size", 14)
        for sz in range(orig_size - 1, 8, -1):
            test_f = load_font(cands, sz)
            if draw.textlength(text, font=test_f) <= max_width:
                cur_font = test_f
                break
    draw.text(xy, text, font=cur_font, fill=fill)


def draw_glass_panel(
    base: Image.Image,
    box: tuple[int, int, int, int],
    fill_rgba: tuple[int, int, int, int],
    border_rgba: tuple[int, int, int, int],
    radius: int = 8,
    border_width: int = 1,
    blur_px: int = 5,
) -> None:
    x0, y0, x1, y1 = box
    crop = base.crop((max(0, x0), max(0, y0), min(base.width, x1), min(base.height, y1)))
    if blur_px > 0:
        crop = crop.filter(ImageFilter.GaussianBlur(blur_px))
    base.paste(crop, (max(0, x0), max(0, y0)))

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    if radius > 0:
        od.rounded_rectangle(box, radius=radius, fill=fill_rgba, outline=border_rgba, width=border_width)
    else:
        od.rectangle(box, fill=fill_rgba, outline=border_rgba, width=border_width)
    base.alpha_composite(overlay)


def draw_callout_pin(
    base: Image.Image,
    target_xy: tuple[int, int],
    box: tuple[int, int, int, int],
    anchor_xy: tuple[int, int],
    accent_rgba: tuple[int, int, int, int],
    fill_rgba: tuple[int, int, int, int],
    title: str,
    subtitle: str,
    fonts: dict[str, ImageFont.FreeTypeFont],
    radius: int = 6,
) -> None:
    loc = str(fonts.get("locale", "en"))
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.line([target_xy, anchor_xy], fill=accent_rgba, width=2)
    tx, ty = target_xy
    od.ellipse((tx - 9, ty - 9, tx + 9, ty + 9), fill=(accent_rgba[0], accent_rgba[1], accent_rgba[2], 70), outline=accent_rgba, width=2)
    od.ellipse((tx - 4, ty - 4, tx + 4, ty + 4), fill=accent_rgba)
    base.alpha_composite(overlay)

    draw_glass_panel(base, box, fill_rgba=fill_rgba, border_rgba=accent_rgba, radius=radius, border_width=2, blur_px=7)
    d = ImageDraw.Draw(base)
    x0, y0, x1, _ = box
    max_w = (x1 - x0) - 28
    draw_fitted_text(d, (x0 + 14, y0 + 10), title, fonts["card_title"], (248, 250, 252, 255), max_w, loc, bold=True)
    draw_fitted_text(d, (x0 + 14, y0 + 34), subtitle, fonts["small"], (203, 213, 225, 255), max_w, loc, bold=False)


# ==============================================================================
# 1. FOUR UNIQUE HERO COMPOSITIONS (1376 x 768)
# ==============================================================================

def build_hero_en(plate_path: Path, out_path: Path) -> None:
    """EN: Swiss-Industrial Telemetry HUD + 5-Lane Dispatch Callouts."""
    img = Image.open(plate_path).convert("RGBA").resize((1376, 768), Image.Resampling.LANCZOS)
    f = get_fonts("en")

    draw_glass_panel(img, (34, 32, 560, 736), fill_rgba=(8, 13, 21, 184), border_rgba=(56, 189, 248, 210), radius=10, border_width=2, blur_px=4)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((34, 32, 40, 736), radius=3, fill=(56, 189, 248, 255))

    d.rounded_rectangle((58, 52, 490, 82), radius=5, fill=(14, 28, 46, 220), outline=(56, 189, 248, 180), width=1)
    draw_fitted_text(d, (70, 59), "KHRONOS WEBGL 2.0  ·  GLSL ES 3.00  ·  SWISS TELEMETRY v2.0.0", f["tiny"], (56, 189, 248, 255), 408, "en", True)

    d.text((58, 96), "WEBGL 2.0 SYSTEMS", font=f["h1"], fill=(248, 250, 252, 255))
    d.text((58, 140), "ARCHITECT SKILL", font=f["h1"], fill=(56, 189, 248, 255))
    d.text((58, 192), "5-Lane parallel worker dispatch, single-context serial GL core,", font=f["body"], fill=(203, 213, 225, 255))
    d.text((58, 212), "12.67ms @ 60Hz budget math & multi-frame PBO fenceSync.", font=f["body"], fill=(203, 213, 225, 255))

    lanes = [
        ("LANE 01 · SHADER & VAO CONTRACT", "#version 300 es · Dedicated VAO · Pre-branch dFdx/dFdy", (56, 189, 248, 255)),
        ("LANE 02 · UNIFORM BLOCK BUS", "layout(std140) 16-Byte Aligned UBO · Zero Per-Draw Links", (45, 212, 191, 255)),
        ("LANE 03 · 12.67ms FRAME & DPR GATE", "60Hz GPU Window · Dynamic targetDPR <= 2.0 · TBDR Invalidate", (245, 158, 11, 255)),
        ("LANE 04 · MULTI-FRAME PBO PROBE", "gl.PIXEL_PACK_BUFFER + gl.fenceSync (timeout = 0ns across RAF)", (129, 140, 248, 255)),
        ("LANE 05 · 24 CI GATES & 6 SELF-TESTS", "8 Golden Examples · 4 Locales · Headless Chrome CDP Verified", (52, 211, 153, 255)),
    ]
    y = 248
    for title, desc, col in lanes:
        draw_glass_panel(img, (58, y, 540, y + 82), fill_rgba=(12, 20, 32, 208), border_rgba=(col[0], col[1], col[2], 145), radius=7, border_width=1, blur_px=2)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((58, y, 64, y + 82), radius=3, fill=col)
        draw_fitted_text(d, (78, y + 14), title, f["card_title"], (248, 250, 252, 255), 446, "en", True)
        draw_fitted_text(d, (78, y + 44), desc, f["small"], (180, 196, 216, 255), 446, "en", False)
        y += 94

    draw_callout_pin(
        img,
        target_xy=(735, 445),
        box=(595, 48, 1035, 114),
        anchor_xy=(765, 114),
        accent_rgba=(56, 189, 248, 240),
        fill_rgba=(8, 14, 24, 215),
        title="SINGLE-CONTEXT SERIAL GL CORE",
        subtitle="Dedicated VAO + 16B std140 UBO + immutable texStorage2D",
        fonts=f,
        radius=8,
    )
    draw_callout_pin(
        img,
        target_xy=(1135, 465),
        box=(855, 658, 1344, 724),
        anchor_xy=(1095, 658),
        accent_rgba=(45, 212, 191, 240),
        fill_rgba=(8, 14, 24, 215),
        title="4-TAP TETRAHEDRAL SDF & LASER GRID",
        subtitle="Pre-branch dFdx/dFdy · Bounded steps · Zero magic literals",
        fonts=f,
        radius=8,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG", optimize=True)


def build_hero_zh(plate_path: Path, out_path: Path) -> None:
    """ZH-CN: 玄玉金枢 · 双环五阶主从闭环面板 (Jade-Gold Dual-Ring & Imperial Seal)."""
    img = Image.open(plate_path).convert("RGBA").resize((1376, 768), Image.Resampling.LANCZOS)
    f = get_fonts("zh-CN")

    draw_glass_panel(img, (32, 30, 562, 738), fill_rgba=(4, 12, 9, 180), border_rgba=(245, 158, 11, 220), radius=8, border_width=2, blur_px=4)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((38, 36, 556, 732), radius=6, outline=(16, 185, 129, 140), width=1)

    d.rounded_rectangle((56, 52, 432, 82), radius=4, fill=(8, 26, 20, 225), outline=(245, 158, 11, 190), width=1)
    draw_fitted_text(d, (68, 59), "玄玉金枢 · 双环五阶图形架构蓝图 · v2.0.0", f["tiny"], (245, 158, 11, 255), 352, "zh-CN", True)

    d.rectangle((446, 50, 538, 84), fill=(180, 38, 30, 235), outline=(245, 158, 11, 245), width=2)
    d.text((462, 58), "玄玉金枢", font=f["seal"], fill=(255, 248, 235, 255))

    d.text((56, 96), "WebGL 2.0 系统架构师", font=f["h1"], fill=(248, 250, 252, 255))
    d.text((56, 142), "双环五阶 · 主从闭环引擎", font=f["h1"], fill=(16, 185, 129, 255))
    draw_fitted_text(d, (56, 194), "外环 Worker 异步预备 <-> 内环单上下文 GL 串行核心：", f["body"], (209, 250, 229, 255), 480, "zh-CN", False)
    draw_fitted_text(d, (56, 214), "守住 12.67ms 帧预算红线、移动端高 DPR 钳制与零阻塞验证。", f["body"], (167, 243, 208, 255), 480, "zh-CN", False)

    phases = [
        ("第一阶 · 6×6 意图分诊与最小模块收敛", "精准区分架构/实现/调试/优化/审查/迁移，拒绝全量上下文污染", (16, 185, 129, 255)),
        ("第二阶 · 12.67ms 帧预算红线与高 DPR 钳制", "移动端 TBDR 显存带宽精算 · 动态 targetDPR <= 2.0 · 瞬态附件失效", (245, 158, 11, 255)),
        ("第三阶 · 外环并发：Worker 解码与 KHR 轮询", "KTX2/Draco 零拷贝传输 · COMPLETION_STATUS_KHR 跨帧非阻塞链接", (16, 185, 129, 255)),
        ("第四阶 · 内环串行：VAO + 16B std140 + 六通道", "强制专属 VAO · 16字节对齐 UBO · texStorage2D 不可变 FBO 拓扑", (245, 158, 11, 255)),
        ("第五阶 · 跨帧 PBO fenceSync(0ns) 与 6 项逆测", "杜绝同帧 getBufferSubData 停顿 · 24项仓库门禁与无头 Chrome 实证", (16, 185, 129, 255)),
    ]
    y = 248
    for title, desc, col in phases:
        draw_glass_panel(img, (56, y, 540, y + 82), fill_rgba=(6, 20, 15, 212), border_rgba=(col[0], col[1], col[2], 160), radius=6, border_width=1, blur_px=2)
        d = ImageDraw.Draw(img)
        d.rectangle((56, y, 62, y + 82), fill=col)
        draw_fitted_text(d, (76, y + 13), title, f["card_title"], (248, 250, 252, 255), 450, "zh-CN", True)
        draw_fitted_text(d, (76, y + 43), desc, f["small"], (186, 230, 211, 255), 450, "zh-CN", False)
        y += 94

    draw_callout_pin(
        img,
        target_xy=(990, 480),
        box=(610, 44, 1085, 110),
        anchor_xy=(920, 110),
        accent_rgba=(16, 185, 129, 245),
        fill_rgba=(5, 16, 12, 220),
        title="玄玉八角光学核心 · 四面体 SDF 晶格",
        subtitle="4采样四面体法线 · 分支前预计算 dFdx/dFdy 与 textureGrad",
        fonts=f,
        radius=6,
    )
    draw_callout_pin(
        img,
        target_xy=(855, 565),
        box=(820, 656, 1344, 722),
        anchor_xy=(940, 656),
        accent_rgba=(245, 158, 11, 245),
        fill_rgba=(5, 16, 12, 220),
        title="金枢双环交汇 · 内环串行提交与外环 PBO 回读",
        subtitle="专属 VAO + 16B std140 UBO + texStorage2D · 跨帧 fenceSync",
        fonts=f,
        radius=6,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG", optimize=True)


def build_hero_ja(plate_path: Path, out_path: Path) -> None:
    """JA: 墨朱精密 · 厳守/指針二元規律＆三段ポカヨケ仕様盤 (Sumi-Shu Monograph & Hanko Stamps)."""
    img = Image.open(plate_path).convert("RGBA").resize((1376, 768), Image.Resampling.LANCZOS)
    f = get_fonts("ja")

    draw_glass_panel(img, (32, 30, 566, 738), fill_rgba=(8, 9, 14, 188), border_rgba=(255, 77, 46, 225), radius=2, border_width=2, blur_px=4)
    d = ImageDraw.Draw(img)
    for cx, cy, dx, dy in [(32, 30, 18, 18), (566, 30, -18, 18), (32, 738, 18, -18), (566, 738, -18, -18)]:
        d.line([(cx, cy), (cx + dx, cy)], fill=(248, 250, 252, 255), width=3)
        d.line([(cx, cy), (cx, cy + dy)], fill=(248, 250, 252, 255), width=3)

    d.rectangle((54, 50, 470, 80), fill=(18, 14, 20, 230), outline=(255, 77, 46, 200), width=1)
    draw_fitted_text(d, (66, 58), "墨朱精密仕様書 · KHRONOS WEBGL 2.0 · v2.0.0", f["tiny"], (255, 110, 84, 255), 392, "ja", True)
    d.rectangle((482, 48, 542, 82), fill=(220, 48, 32, 240), outline=(255, 160, 140, 255), width=2)
    d.text((496, 56), "検済", font=f["seal"], fill=(255, 250, 245, 255))

    d.text((54, 96), "WebGL 2.0 システム", font=f["h1"], fill=(248, 250, 252, 255))
    d.text((54, 142), "アーキテクト設計規範", font=f["h1"], fill=(255, 77, 46, 255))
    draw_fitted_text(d, (54, 194), "ハードウェア不変条件［厳守］と適応型削減［指針］を峻別し、", f["body"], (226, 232, 240, 255), 488, "ja", False)
    draw_fitted_text(d, (54, 214), "三段ポカヨケ品質ゲートでフレーム予算と描画完全性を保証する。", f["body"], (203, 213, 225, 255), 488, "ja", False)

    specs = [
        ("［厳守 01］ GLSL ES 3.00 ＆ 専用 VAO 必須", "先頭バイト #version 300 es · 分岐前 dFdx/dFdy 計算と textureGrad", (255, 77, 46, 255)),
        ("［厳守 02］ std140 UBO 16B 境界整列", "vec3 配列の 16B パディング厳守 · 描画ループ内の linkProgram 禁止", (56, 189, 248, 255)),
        ("［厳守 03］ 複数フレーム非同期 PBO リードバック", "PIXEL_PACK_BUFFER + fenceSync(0ns) · 同フレーム読戻し禁止", (255, 77, 46, 255)),
        ("［指針 04］ 12.67ms 予算 ＆ 5層被写体削減順序", "P2 微細模様 -> 0.5x 半解像度 -> targetDPR -> P1 -> P0 輪郭死守", (56, 189, 248, 255)),
        ("［検証 05］ 三段ポカヨケ自動品質ゲート ＆ 6種逆テスト", "24項目 validate_repo + コンテキスト喪失復旧 + ヘッドレス Chrome 実証", (245, 158, 11, 255)),
    ]
    y = 248
    for title, desc, col in specs:
        draw_glass_panel(img, (54, y, 544, y + 82), fill_rgba=(14, 16, 24, 214), border_rgba=(col[0], col[1], col[2], 165), radius=2, border_width=1, blur_px=2)
        d = ImageDraw.Draw(img)
        d.rectangle((54, y, 60, y + 82), fill=col)
        draw_fitted_text(d, (74, y + 13), title, f["card_title"], (248, 250, 252, 255), 456, "ja", True)
        draw_fitted_text(d, (74, y + 43), desc, f["small"], (190, 202, 218, 255), 456, "ja", False)
        y += 94

    draw_callout_pin(
        img,
        target_xy=(945, 378),
        box=(600, 44, 1088, 110),
        anchor_xy=(840, 110),
        accent_rgba=(255, 77, 46, 245),
        fill_rgba=(10, 12, 18, 225),
        title="光学断面 · 4タップ四面体 SDF 法線＆レイマーチ収束",
        subtitle="有界 MAX_STEPS · 0.65..0.85 安全係数 · 分岐前 textureGrad",
        fonts=f,
        radius=3,
    )
    draw_callout_pin(
        img,
        target_xy=(1040, 585),
        box=(810, 658, 1344, 724),
        anchor_xy=(1040, 658),
        accent_rgba=(56, 189, 248, 245),
        fill_rgba=(10, 12, 18, 225),
        title="シリコンウェハ直列提出 · ポカヨケ PBO 非同期検査",
        subtitle="不変 texStorage2D FBO (0x8CD5) · 複数フレーム fenceSync",
        fonts=f,
        radius=3,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG", optimize=True)


def build_hero_ko(plate_path: Path, out_path: Path) -> None:
    """KO: 청자-인디고 파운드리 · 60Hz/120Hz 고주사율 텔레메트리 & HBM 인터포저 워크스테이션."""
    img = Image.open(plate_path).convert("RGBA").resize((1376, 768), Image.Resampling.LANCZOS)
    f = get_fonts("ko")

    draw_glass_panel(img, (32, 30, 562, 738), fill_rgba=(6, 10, 22, 184), border_rgba=(45, 212, 191, 220), radius=10, border_width=2, blur_px=4)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((32, 30, 38, 738), radius=3, fill=(45, 212, 191, 255))

    d.rounded_rectangle((54, 50, 444, 80), radius=6, fill=(11, 20, 42, 230), outline=(45, 212, 191, 190), width=1)
    draw_fitted_text(d, (66, 58), "CELADON-INDIGO HBM FOUNDRY · WEBGL 2.0 · v2.0.0", f["tiny"], (45, 212, 191, 255), 370, "ko", True)
    d.rounded_rectangle((454, 50, 540, 80), radius=6, fill=(49, 46, 129, 230), outline=(129, 140, 248, 220), width=1)
    d.text((466, 58), "60 / 120Hz", font=f["tiny"], fill=(224, 231, 255, 255))

    d.text((54, 96), "WebGL 2.0 시스템", font=f["h1"], fill=(248, 250, 252, 255))
    d.text((54, 142), "아키텍트 파운드리", font=f["h1"], fill=(45, 212, 191, 255))
    draw_fitted_text(d, (54, 194), "60Hz(12.67ms) / 120Hz(5.33ms) 고주사율 프레임 예산 텔레메트리,", f["body"], (203, 213, 225, 255), 486, "ko", False)
    draw_fitted_text(d, (54, 214), "HBM급 직렬 상태 버스 및 무재패킹 WebGPU 1:1 브릿지 패키지.", f["body"], (165, 243, 252, 255), 486, "ko", False)

    stages = [
        ("01 · GLSL ES 3.00 & 전용 VAO 불변 계약", "0바이트 #version 300 es · 전용 VAO 상시 바인딩 · 분기 전 dFdx/dFdy", (45, 212, 191, 255)),
        ("02 · 16바이트 정렬 std140 UBO 직렬 버스", "드로우별 유니폼 링크 제거 · vec3->vec4 패딩 · 256B 동적 오프셋", (129, 140, 248, 255)),
        ("03 · 60Hz / 120Hz 고주사율 프레임 예산 & DPR 클램프", "60Hz(12.67ms) / 120Hz(5.33ms) · 동적 targetDPR <= 2.0 · TBDR 대역폭", (245, 158, 11, 255)),
        ("04 · 다중 프레임 비차단 PBO + fenceSync (0ns)", "PIXEL_PACK_BUFFER 스테이징 · 다음 RAF 틱 폴링으로 스톨 완벽 제거", (45, 212, 191, 255)),
        ("05 · 24개 CI 게이트 & WebGPU 1:1 듀얼 백엔드", "6종 네거티브 자체 테스트 · 컨텍스트 복구 훈련 · 무재패킹 WGSL 매핑", (129, 140, 248, 255)),
    ]
    y = 248
    for title, desc, col in stages:
        draw_glass_panel(img, (54, y, 540, y + 82), fill_rgba=(10, 17, 36, 212), border_rgba=(col[0], col[1], col[2], 160), radius=7, border_width=1, blur_px=2)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((54, y, 60, y + 82), radius=3, fill=col)
        draw_fitted_text(d, (74, y + 13), title, f["card_title"], (248, 250, 252, 255), 454, "ko", True)
        draw_fitted_text(d, (74, y + 43), desc, f["small"], (186, 204, 232, 255), 454, "ko", False)
        y += 94

    draw_callout_pin(
        img,
        target_xy=(1045, 375),
        box=(605, 44, 1085, 110),
        anchor_xy=(920, 110),
        accent_rgba=(45, 212, 191, 245),
        fill_rgba=(7, 12, 26, 222),
        title="광학 SDF 크리스탈 큐브 · 4-탭 사면체 노멀",
        subtitle="유계 레이마칭 루프 · 매직 리터럴 제로 · 분기 전 미분 고정",
        fonts=f,
        radius=8,
    )
    draw_callout_pin(
        img,
        target_xy=(790, 495),
        box=(810, 658, 1344, 724),
        anchor_xy=(920, 658),
        accent_rgba=(129, 140, 248, 245),
        fill_rgba=(7, 12, 26, 222),
        title="3D HBM 인터포저 코어 · 단일 컨텍스트 직렬 제출",
        subtitle="전용 VAO + 16B std140 UBO + 불변 texStorage2D + 다중 프레임 PBO",
        fonts=f,
        radius=8,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG", optimize=True)


# ==============================================================================
# 2. FOUR UNIQUE WORKFLOW INFOGRAPHIC PLATES (1376 x 768)
# ==============================================================================

def build_infographic_en(plate_path: Path, out_path: Path) -> None:
    """EN Unique Workflow: Swiss 5-Lane Parallel Swimlane & 6-Intent Dispatch Board."""
    img = Image.open(plate_path).convert("RGBA").resize((1376, 768), Image.Resampling.LANCZOS)
    f = get_fonts("en")

    draw_glass_panel(img, (42, 28, 1334, 740), fill_rgba=(7, 11, 18, 210), border_rgba=(56, 189, 248, 190), radius=10, border_width=2, blur_px=3)
    d = ImageDraw.Draw(img)

    draw_fitted_text(d, (68, 44), "SWISS-INDUSTRIAL WORKFLOW · 5-LANE DISPATCH & 6×6 TRIAGE MATRIX", f["h2"], (248, 250, 252, 255), 985, "en", True)
    draw_fitted_text(d, (68, 76), "Progressive-disclosure routing (registry/module-map.json) feeding parallel Worker lanes and a single-context serial WebGL 2.0 bus.", f["body"], (148, 163, 184, 255), 985, "en", False)
    d.rounded_rectangle((1075, 44, 1308, 82), radius=6, fill=(14, 30, 48, 235), outline=(56, 189, 248, 220), width=1)
    draw_fitted_text(d, (1090, 56), "EN · SWISS TELEMETRY GRID", f["tiny"], (56, 189, 248, 255), 205, "en", True)

    intents = [
        ("1. architecture", "Mods 01..07 (7)", "Full multi-pass system", (56, 189, 248, 255)),
        ("2. implementation", "Mods 01,03,05,06 (4)", "Write GLSL & GL state", (45, 212, 191, 255)),
        ("3. debug", "Mods 01,05,06,07 (4)", "Fix FBO / seams / loss", (245, 158, 11, 255)),
        ("4. optimize", "Mods 01..03,05..07 (6)", "12.67ms & DPR clamp", (56, 189, 248, 255)),
        ("5. review", "Mods 01,04..07 (5)", "Audit math & lifecycles", (45, 212, 191, 255)),
        ("6. migration", "Mods 01,03,05..07 (5)", "WebGL1->2 / WebGPU", (129, 140, 248, 255)),
    ]
    ix = 68
    for name, mods, sub, col in intents:
        draw_glass_panel(img, (ix, 108, ix + 198, 186), fill_rgba=(13, 21, 34, 228), border_rgba=col, radius=6, border_width=1, blur_px=0)
        d = ImageDraw.Draw(img)
        draw_fitted_text(d, (ix + 10, 116), name, f["card_title"], (248, 250, 252, 255), 178, "en", True)
        draw_fitted_text(d, (ix + 10, 140), mods, f["mono_s"], col, 178, "en", True)
        draw_fitted_text(d, (ix + 10, 160), sub, f["small"], (160, 174, 192, 255), 178, "en", False)
        ix += 208

    draw_fitted_text(d, (68, 202), "STAGE II · 5-LANE CONCURRENT PIPELINE (WORKER PREP vs SERIAL GL)", f["h3"], (56, 189, 248, 255), 775, "en", True)
    swimlanes = [
        ("LANE A · SUBJECT HIERARCHY (04)", "5 Observation Layers · P0 Silhouette Lock · Shed: P2 -> 0.5x Vol -> targetDPR -> P1 -> P0", "CPU / SPEC", (56, 189, 248, 255)),
        ("LANE B · SHADER & UBO MATH (05)", "#version 300 es byte 0 · 16B std140 UBO · 4-tap tetrahedral normal · Pre-branch dFdx/dFdy", "GLSL / UBO", (45, 212, 191, 255)),
        ("LANE C · 6-PASS FBO TOPOLOGY (06)", "Shadow/SDF -> G-Buffer -> Lighting -> Transparent -> Post -> Present · texStorage2D + invalidate", "SERIAL GL", (245, 158, 11, 255)),
        ("LANE D · HARDWARE BUDGET (02)", "gpuBudgetMs = (1000/fps) - cpuMs - 1.5ms · Dynamic targetDPR <= 2.0 · KTX2 Worker Transcode", "WORKER + GL", (129, 140, 248, 255)),
        ("LANE E · ASYNC PBO & CI GATES (07)", "Multi-frame PIXEL_PACK_BUFFER + fenceSync(timeout=0) · WEBGL_lose_context drill · 6 Self-Tests", "ASYNC VERIFY", (52, 211, 153, 255)),
    ]
    sy = 232
    for title, desc, badge, col in swimlanes:
        draw_glass_panel(img, (68, sy, 845, sy + 74), fill_rgba=(11, 18, 29, 228), border_rgba=(col[0], col[1], col[2], 175), radius=6, border_width=1, blur_px=0)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((68, sy, 75, sy + 74), radius=3, fill=col)
        draw_fitted_text(d, (88, sy + 12), title, f["card_title"], (248, 250, 252, 255), 620, "en", True)
        draw_fitted_text(d, (88, sy + 42), desc, f["small"], (190, 205, 222, 255), 742, "en", False)
        d.rounded_rectangle((718, sy + 10, 832, sy + 34), radius=4, fill=(16, 28, 44, 240), outline=col, width=1)
        draw_fitted_text(d, (728, sy + 15), badge, f["tiny"], col, 96, "en", True)
        sy += 84

    draw_fitted_text(d, (868, 202), "STAGE III · EQUATIONS & WEBGPU 1:1 BRIDGE", f["h3"], (45, 212, 191, 255), 435, "en", True)
    draw_glass_panel(img, (868, 232, 1308, 428), fill_rgba=(11, 18, 29, 228), border_rgba=(56, 189, 248, 180), radius=7, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (884, 246), "FRAME-BUDGET & BANDWIDTH EQUATIONS (MOD 02)", f["card_title"], (56, 189, 248, 255), 410, "en", True)
    eqs = [
        "gpuBudgetMs = (1000 / fps) - cpuMs - 1.5ms",
        "  -> 60Hz: 16.67 - 2.5 - 1.5 = 12.67 ms window",
        "  -> 120Hz: 8.33 - 1.5 - 1.5 = 5.33 ms window",
        "targetDPR = min(deviceDPR, 2.0, sqrt(gpuMs/(Mpx*cost)))",
        "bandwidthGBps = W * H * dpr^2 * bpp * passes * fps / 1e9",
        "Poll timer ring (3..4 frames) when GPU_DISJOINT_EXT == 0",
    ]
    ey = 276
    for line in eqs:
        draw_fitted_text(d, (884, ey), line, f["mono_s"], (226, 232, 240, 255), 410, "en", False)
        ey += 23

    draw_glass_panel(img, (868, 444, 1308, 642), fill_rgba=(11, 18, 29, 228), border_rgba=(45, 212, 191, 180), radius=7, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (884, 458), "WEBGL 2.0 -> WEBGPU (WGSL) 1:1 BRIDGE (MOD 06)", f["card_title"], (45, 212, 191, 255), 410, "en", True)
    wgpu = [
        "VAO (createVertexArray)  -> GPUVertexBufferLayout",
        "std140 UBO + Samplers    -> GPUBindGroup (group 0..2)",
        "useProgram + blend/depth -> Immutable GPURenderPipeline",
        "invalidateFramebuffer    -> storeOp: 'discard' attachment",
        "PIXEL_PACK_BUFFER + sync -> GPUBuffer.mapAsync(READ)",
        "Clip Z [-1,1] & BL UV    -> Clip Z [0,1] & TL UV helper",
    ]
    wy = 488
    for line in wgpu:
        draw_fitted_text(d, (884, wy), line, f["mono_s"], (203, 213, 225, 255), 410, "en", False)
        wy += 23

    draw_glass_panel(img, (68, 658, 1308, 722), fill_rgba=(9, 22, 28, 235), border_rgba=(52, 211, 153, 210), radius=6, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (86, 668), "DETERMINISTIC VERIFICATION HARNESS:  python scripts/validate_repo.py (24 Checks + 6 Self-Tests)  |  python scripts/verify_browser.py (Headless Chrome CDP)", f["card_title"], (52, 211, 153, 255), 1200, "en", True)
    draw_fitted_text(d, (86, 694), "Verified Invariants:  FBO COMPLETE (0x8CD5)  ·  Multi-Frame PBO fenceSync CONDITION_SATISFIED  ·  WEBGL_lose_context Restored  ·  0 Console Errors  ·  0 Forbidden Slop", f["small"], (226, 232, 240, 255), 1200, "en", False)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG", optimize=True)


def build_infographic_zh(plate_path: Path, out_path: Path) -> None:
    """ZH-CN Unique Workflow: 玄玉金枢 · 双环五阶主从闭环图谱 (Concentric Dual-Ring Master-Worker Topology)."""
    img = Image.open(plate_path).convert("RGBA").resize((1376, 768), Image.Resampling.LANCZOS)
    f = get_fonts("zh-CN")

    draw_glass_panel(img, (54, 34, 1322, 734), fill_rgba=(4, 11, 8, 198), border_rgba=(245, 158, 11, 215), radius=8, border_width=2, blur_px=2)
    d = ImageDraw.Draw(img)

    draw_fitted_text(d, (78, 48), "玄玉金枢 · WebGL 2.0 双环五阶主从闭环工作流与决策图谱 (zh-CN)", f["h2"], (248, 250, 252, 255), 1020, "zh-CN", True)
    draw_fitted_text(d, (78, 80), "外环 CPU/Worker 异步预备环 <-> 内环单上下文 GL 串行提交核心 · 严守 12.67ms 帧预算红线与跨帧 PBO 零阻塞验证", f["body"], (167, 243, 208, 255), 1020, "zh-CN", False)
    d.rectangle((1120, 48, 1296, 84), fill=(165, 34, 28, 235), outline=(245, 158, 11, 245), width=2)
    draw_fitted_text(d, (1134, 57), "玄玉金枢 · 工业规约", f["seal"], (255, 248, 235, 255), 150, "zh-CN", True)

    draw_fitted_text(d, (78, 114), "一、双环五阶闭环演进轨 (01..07)", f["h3"], (245, 158, 11, 255), 390, "zh-CN", True)
    phases = [
        ("第一阶 · 6×6 意图分诊 (01-triage)", "识别 6 大工程意图 × 6 类项目形态，", "锁定最小模块集与硬件证据等级(A/B/C)。", (16, 185, 129, 255)),
        ("第二阶 · 帧预算与 DPR 红线 (02-budget)", "60Hz 留出 12.67ms GPU 净执行窗口，", "动态钳制移动端 targetDPR <= 2.0。", (245, 158, 11, 255)),
        ("第三阶 · 外环异步预备 (03-concurrency)", "Worker 解码 KTX2/Draco 零拷贝传输，", "跨帧轮询 KHR_parallel_shader_compile。", (16, 185, 129, 255)),
        ("第四阶 · 内环六通道串行提交 (04/05/06)", "专属 VAO + 16B std140 UBO 绑定，", "texStorage2D 不可变 FBO 与瞬态附件失效。", (245, 158, 11, 255)),
        ("第五阶 · 跨帧 PBO 回读与双后端 (06/07)", "PIXEL_PACK_BUFFER + fenceSync(0ns)", "跨帧非阻塞回读 + WebGPU 1:1 零重排映射。", (16, 185, 129, 255)),
    ]
    py = 142
    for title, l1, l2, col in phases:
        draw_glass_panel(img, (78, py, 470, py + 92), fill_rgba=(6, 19, 14, 224), border_rgba=col, radius=6, border_width=1, blur_px=0)
        d = ImageDraw.Draw(img)
        d.rectangle((78, py, 84, py + 92), fill=col)
        draw_fitted_text(d, (96, py + 10), title, f["card_title"], (248, 250, 252, 255), 362, "zh-CN", True)
        draw_fitted_text(d, (96, py + 38), l1, f["small"], (209, 250, 229, 255), 362, "zh-CN", False)
        draw_fitted_text(d, (96, py + 60), l2, f["small"], (167, 243, 208, 255), 362, "zh-CN", False)
        py += 100

    draw_fitted_text(d, (492, 114), "二、外环并发预备 <-> 内环串行提交双生模型", f["h3"], (16, 185, 129, 255), 390, "zh-CN", True)
    draw_glass_panel(img, (492, 142, 884, 422), fill_rgba=(7, 22, 17, 198), border_rgba=(245, 158, 11, 230), radius=12, border_width=2, blur_px=2)
    draw_glass_panel(img, (514, 226, 862, 350), fill_rgba=(5, 16, 12, 236), border_rgba=(16, 185, 129, 235), radius=10, border_width=2, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (512, 152), "【外环 · CPU / Web Worker 异步预备环】", f["card_title"], (245, 158, 11, 255), 356, "zh-CN", True)
    draw_fitted_text(d, (516, 178), "• Draco/glTF 网格解压与 BVH 构建 (Transferable)", f["small"], (248, 250, 252, 255), 352, "zh-CN", False)
    draw_fitted_text(d, (516, 199), "• KTX2 BasisU 压缩纹理转码 · KHR 异步着色器轮询", f["small"], (248, 250, 252, 255), 352, "zh-CN", False)

    draw_fitted_text(d, (532, 236), "【内环 · 单上下文 GL 串行提交核心】", f["card_title"], (16, 185, 129, 255), 314, "zh-CN", True)
    draw_fitted_text(d, (536, 264), "• 专属 VAO 绑定 + 16B 对齐 std140 UBO 批量更新", f["small"], (248, 250, 252, 255), 310, "zh-CN", False)
    draw_fitted_text(d, (536, 288), "• texStorage2D 六通道不可变 FBO 确定性串行提交", f["small"], (209, 250, 229, 255), 310, "zh-CN", False)
    draw_fitted_text(d, (536, 312), "• 移动端瓦片 GPU 瞬态附件即时 invalidateFramebuffer", f["small"], (245, 158, 11, 255), 310, "zh-CN", False)

    draw_fitted_text(d, (516, 364), "• 跨帧状态机：Frame N 触发 readPixels -> fenceSync", f["small"], (167, 243, 208, 255), 352, "zh-CN", False)
    draw_fitted_text(d, (516, 388), "• Frame N+k 轮询 clientWaitSync(0) 后 getBufferSubData", f["small"], (167, 243, 208, 255), 352, "zh-CN", False)

    draw_glass_panel(img, (492, 434, 884, 636), fill_rgba=(6, 19, 14, 226), border_rgba=(16, 185, 129, 195), radius=8, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (510, 446), "帧预算红线公式与 WebGPU 1:1 零重排映射", f["card_title"], (16, 185, 129, 255), 360, "zh-CN", True)
    zh_math = [
        "gpuBudgetMs = (1000/fps) - cpuMs - 1.5ms (60Hz: 12.67ms)",
        "targetDPR = min(deviceDPR, 2.0, sqrt(gpuMs/(Mpx*cost)))",
        "bandwidthGBps = W * H * dpr^2 * bpp * passes * fps / 1e9",
        "VAO -> GPUVertexBufferLayout | std140 UBO -> GPUBindGroup",
        "invalidateFramebuffer -> GPURenderPass storeOp: 'discard'",
        "PBO + fenceSync(0ns)  -> GPUBuffer.mapAsync(READ)",
        "裁剪深度 [-1,1]->[0,1] 与左下 UV 翻转收敛于统一相机函数",
    ]
    my = 474
    for line in zh_math:
        draw_fitted_text(d, (510, my), line, f["small"], (226, 232, 240, 255), 360, "zh-CN", False)
        my += 22

    draw_fitted_text(d, (906, 114), "三、6×6 意图路由矩阵 (module-map.json)", f["h3"], (16, 185, 129, 255), 390, "zh-CN", True)
    routes_zh = [
        ("1. architecture (系统架构 · 7模块)", "加载模块: 01, 02, 03, 04, 05, 06, 07", "适用: 多通道渲染管线、SDF光线步进、混合渲染总装"),
        ("2. implementation (功能实现 · 4模块)", "加载模块: 01, 03, 05, 06", "适用: 编写 VAO、16B std140 UBO、FBO 与着色器代码"),
        ("3. debug (故障诊断 · 4模块)", "加载模块: 01, 05, 06, 07", "适用: 排查 FBO 不完整、上下文丢失黑屏、导数接缝与停顿"),
        ("4. optimize (性能调优 · 6模块)", "加载模块: 01, 02, 03, 05, 06, 07", "适用: 移动端高 DPR 掉帧治理、带宽削减、瓦片 GPU 优化"),
        ("5. review (代码审计 · 5模块)", "加载模块: 01, 04, 05, 06, 07", "适用: 审计 P0/P1/P2 视觉层级、GLSL 魔法常数与显存泄漏"),
        ("6. migration (架构迁移 · 5模块)", "加载模块: 01, 03, 05, 06, 07", "适用: WebGL 1.0 -> 2.0 升级或 WebGPU 双后端演进"),
    ]
    ry = 142
    for title, mods, desc in routes_zh:
        draw_glass_panel(img, (906, ry, 1300, ry + 75), fill_rgba=(6, 19, 14, 224), border_rgba=(16, 185, 129, 155), radius=6, border_width=1, blur_px=0)
        d = ImageDraw.Draw(img)
        draw_fitted_text(d, (920, ry + 8), title, f["card_title"], (248, 250, 252, 255), 366, "zh-CN", True)
        draw_fitted_text(d, (920, ry + 31), mods, f["tiny"], (245, 158, 11, 255), 366, "zh-CN", True)
        draw_fitted_text(d, (920, ry + 50), desc, f["small"], (186, 230, 211, 255), 366, "zh-CN", False)
        ry += 83

    draw_glass_panel(img, (78, 652, 1300, 718), fill_rgba=(8, 26, 20, 235), border_rgba=(245, 158, 11, 220), radius=6, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (96, 662), "五步闭环门禁实证：python scripts/validate_repo.py (24项静态检查 + 6项逆向自测)  |  python scripts/verify_browser.py (无头 Chrome WebGL 2.0 实证)", f["card_title"], (245, 158, 11, 255), 1184, "zh-CN", True)
    draw_fitted_text(d, (96, 690), "实测指标：离屏 texStorage2D FBO (0x8CD5) 完整 · 跨帧 PBO fenceSync CONDITION_SATISFIED · WEBGL_lose_context 恢复通过 · 中英日韩 0 禁用词违规", f["small"], (209, 250, 229, 255), 1184, "zh-CN", False)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG", optimize=True)


def build_infographic_ja(plate_path: Path, out_path: Path) -> None:
    """JA Unique Workflow: 墨朱精密 · 厳守/指針二元規律＆五層削減ポカヨケ仕様図 (3-Track Monograph & Poka-Yoke Waterfall)."""
    img = Image.open(plate_path).convert("RGBA").resize((1376, 768), Image.Resampling.LANCZOS)
    f = get_fonts("ja")

    draw_glass_panel(img, (54, 42, 1322, 726), fill_rgba=(8, 10, 15, 204), border_rgba=(255, 77, 46, 215), radius=2, border_width=2, blur_px=2)
    d = ImageDraw.Draw(img)

    draw_fitted_text(d, (78, 56), "墨朱精密仕様書 · 厳守/指針二元規律＆ポカヨケ品質ゲート設計図 (ja)", f["h2"], (248, 250, 252, 255), 1045, "ja", True)
    draw_fitted_text(d, (78, 88), "第I軌道［厳守］ハードウェア不変条件 · 第II軌道［指針］5層被写体削減順序 · 第III軌道［検］6意図ルーティング＆3段ポカヨケ検証", f["body"], (203, 213, 225, 255), 1045, "ja", False)
    d.rectangle((1145, 54, 1298, 90), fill=(215, 48, 32, 240), outline=(255, 160, 140, 255), width=2)
    draw_fitted_text(d, (1158, 64), "［検］墨朱精密規範", f["seal"], (255, 250, 245, 255), 130, "ja", True)

    draw_fitted_text(d, (78, 122), "第I軌道 ［厳守］ 破ると即破綻する5大不変条件", f["h3"], (255, 77, 46, 255), 386, "ja", True)
    invariants = [
        ("［厳守 01］ #version 300 es 先頭バイト宣言", "シェーダー文字列の0バイト目に配置。", "空白・コメント・BOM混入を厳禁とする。"),
        ("［厳守 02］ 専用 VAO ＆ 16B 整列 std140 UBO", "全描画で createVertexArray を束縛し、", "vec3 配列の16B境界パディングズレを防ぐ。"),
        ("［厳守 03］ 非一様分岐前の dFdx / dFdy 計算", "早期 break ループ外でUV勾配を事前計算し、", "ループ内のサンプルには textureGrad を明示。"),
        ("［厳守 04］ 不変 texStorage2D ＆ 同時読書き禁止", "FBO 添付テクスチャの同時サンプルを禁じ、", "checkFramebufferStatus === 0x8CD5 を検証。"),
        ("［厳守 05］ 複数フレーム PBO + fenceSync(0ns)", "同フレーム getBufferSubData や同期", "readPixels によるGPUパイプライン停止を根絶。"),
    ]
    iy = 150
    for title, l1, l2 in invariants:
        draw_glass_panel(img, (78, iy, 468, iy + 88), fill_rgba=(14, 16, 24, 224), border_rgba=(255, 77, 46, 175), radius=2, border_width=1, blur_px=0)
        d = ImageDraw.Draw(img)
        d.rectangle((78, iy, 84, iy + 88), fill=(255, 77, 46, 255))
        draw_fitted_text(d, (94, iy + 10), title, f["card_title"], (248, 250, 252, 255), 364, "ja", True)
        draw_fitted_text(d, (94, iy + 38), l1, f["small"], (226, 232, 240, 255), 364, "ja", False)
        draw_fitted_text(d, (94, iy + 60), l2, f["small"], (180, 194, 212, 255), 364, "ja", False)
        iy += 96

    draw_fitted_text(d, (490, 122), "第II軌道 ［指針］ 5層被写体分解＆削減順序", f["h3"], (56, 189, 248, 255), 388, "ja", True)
    draw_glass_panel(img, (490, 150, 882, 422), fill_rgba=(13, 17, 26, 218), border_rgba=(56, 189, 248, 190), radius=2, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (506, 162), "12.67ms 予算超過時の段階的削減順序 (Mod 04)", f["card_title"], (56, 189, 248, 255), 364, "ja", True)
    steps_ja = [
        ("STEP 1 · P2 微細模様・薄膜干渉オクターブ停止", "高周波ノイズ・二次コースティクスを最初に無効化", (148, 163, 184, 255)),
        ("STEP 2 · ボリュームパスを軸方向 0.5x 解像度へ", "ピクセル数を 25% に削減し深度双線形補間で合成", (56, 189, 248, 255)),
        ("STEP 3 · 動的 targetDPR クランプ (2.0->1.5->1.25)", "高DPIモバイルのタイルメモリ帯域(GB/s)飽和を緩和", (245, 158, 11, 255)),
        ("STEP 4 · P1 補助リムライトを近似式へ簡略化", "副次ローブを Schlick 近似へ置換しALU負荷を節約", (255, 110, 84, 255)),
        ("LOCKED · P0 主シルエット・4点法線は死守", "いかなる負荷下でも被写体の輪郭と主光源を維持", (52, 211, 153, 255)),
    ]
    sy = 194
    for s_title, s_desc, col in steps_ja:
        d.rectangle((506, sy, 512, sy + 36), fill=col)
        draw_fitted_text(d, (520, sy), s_title, f["small"], (248, 250, 252, 255), 350, "ja", True)
        draw_fitted_text(d, (520, sy + 18), s_desc, f["tiny"], (180, 194, 212, 255), 350, "ja", False)
        sy += 44

    draw_glass_panel(img, (490, 434, 882, 630), fill_rgba=(13, 17, 26, 224), border_rgba=(245, 158, 11, 185), radius=2, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (506, 446), "フレーム予算数式 ＆ WebGPU (WGSL) 1:1 移行対照", f["card_title"], (245, 158, 11, 255), 364, "ja", True)
    ja_math = [
        "gpuBudgetMs = (1000/fps) - cpuMs - 1.5ms (60Hz: 12.67ms)",
        "targetDPR = min(deviceDPR, 2.0, sqrt(gpuMs/(Mpx*cost)))",
        "VAO -> GPUVertexBufferLayout | std140 UBO -> GPUBindGroup",
        "invalidateFramebuffer -> GPURenderPass storeOp: 'discard'",
        "PBO + fenceSync(0ns)  -> GPUBuffer.mapAsync(READ)",
        "クリップ空間 Z [-1,1]->[0,1] ＆ UV Y軸反転を単一関数に隔離",
    ]
    my = 476
    for line in ja_math:
        draw_fitted_text(d, (506, my), line, f["small"], (226, 232, 240, 255), 364, "ja", False)
        my += 23

    draw_fitted_text(d, (904, 122), "第III軌道 ［検］ 6意図×最小モジュール編成", f["h3"], (245, 158, 11, 255), 390, "ja", True)
    routes_ja = [
        ("1. architecture (基本設計 · 全7)", "読込モジュール: 01, 02, 03, 04, 05, 06, 07", "新規マルチパス設計・SDFレイマーチ・UBO/FBO設計"),
        ("2. implementation (実装 · 4モジュール)", "読込モジュール: 01, 03, 05, 06", "VAO・16B std140 UBO・シェーダー・FBOの本番実装"),
        ("3. debug (障害解析 · 4モジュール)", "読込モジュール: 01, 05, 06, 07", "FBO不完全・コンテキスト喪失・dFdx境界ノイズの修正"),
        ("4. optimize (性能改善 · 6モジュール)", "読込モジュール: 01, 02, 03, 05, 06, 07", "高DPIモバイルのフレーム落ち対策・帯域削減・タイルGPU"),
        ("5. review (設計監査 · 5モジュール)", "読込モジュール: 01, 04, 05, 06, 07", "P0/P1/P2階層・GLSLマジック定数・VRAMリークの監査"),
        ("6. migration (基盤移行 · 5モジュール)", "読込モジュール: 01, 03, 05, 06, 07", "WebGL 1.0->2.0 移行、または WebGPU 双方向設計"),
    ]
    ry = 150
    for title, mods, desc in routes_ja:
        draw_glass_panel(img, (904, ry, 1298, ry + 74), fill_rgba=(14, 16, 24, 224), border_rgba=(56, 189, 248, 155), radius=2, border_width=1, blur_px=0)
        d = ImageDraw.Draw(img)
        draw_fitted_text(d, (918, ry + 8), title, f["card_title"], (248, 250, 252, 255), 368, "ja", True)
        draw_fitted_text(d, (918, ry + 30), mods, f["tiny"], (56, 189, 248, 255), 368, "ja", True)
        draw_fitted_text(d, (918, ry + 49), desc, f["small"], (190, 202, 218, 255), 368, "ja", False)
        ry += 80

    draw_glass_panel(img, (78, 646, 1298, 710), fill_rgba=(18, 14, 20, 238), border_rgba=(255, 77, 46, 225), radius=2, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (96, 656), "三段ポカヨケ自動品質ゲート：検印1 validate_repo.py (24項目＋6種逆テスト)  |  検印2 JSON契約＆4言語検査  |  検印3 verify_browser.py (ヘッドレスChrome実機)", f["card_title"], (255, 110, 84, 255), 1184, "ja", True)
    draw_fitted_text(d, (96, 682), "実機合格証跡：不変 texStorage2D FBO (0x8CD5) 完全 · 複数フレーム PBO fenceSync CONDITION_SATISFIED · コンテキスト喪失復旧 1回 · 禁止表現 0件", f["small"], (226, 232, 240, 255), 1184, "ja", False)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG", optimize=True)


def build_infographic_ko(plate_path: Path, out_path: Path) -> None:
    """KO Unique Workflow: 청자-인디고 파운드리 · 60Hz/120Hz 고주사율 듀얼 타임라인 & 4-쿼드런트 HBM 인터포저 매트릭스."""
    img = Image.open(plate_path).convert("RGBA").resize((1376, 768), Image.Resampling.LANCZOS)
    f = get_fonts("ko")

    draw_glass_panel(img, (58, 36, 1318, 732), fill_rgba=(5, 9, 20, 200), border_rgba=(45, 212, 191, 215), radius=10, border_width=2, blur_px=2)
    d = ImageDraw.Draw(img)

    draw_fitted_text(d, (82, 50), "청자-인디고 파운드리 · 고주사율(60/120Hz) 타임라인 & HBM 인터포저 아키텍처 (ko)", f["h2"], (248, 250, 252, 255), 1015, "ko", True)
    draw_fitted_text(d, (82, 82), "60Hz(12.67ms) / 120Hz(5.33ms) 프레임 예산 텔레메트리 · 4-다이 인터포저 파이프라인 · 무재패킹 WebGPU 1:1 브릿지", f["body"], (165, 243, 252, 255), 1015, "ko", False)
    d.rounded_rectangle((1110, 50, 1294, 86), radius=6, fill=(14, 28, 56, 235), outline=(45, 212, 191, 225), width=1)
    draw_fitted_text(d, (1126, 61), "KO · HBM3E TELEMETRY", f["tiny"], (45, 212, 191, 255), 156, "ko", True)

    draw_glass_panel(img, (82, 114, 1294, 206), fill_rgba=(9, 15, 32, 225), border_rgba=(129, 140, 248, 190), radius=8, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (100, 124), "고주사율 듀얼 프레임 타임라인 예산 할당 (Module 02 · EXT_disjoint_timer_query_webgl2 3~4프레임 링버퍼)", f["card_title"], (45, 212, 191, 255), 1170, "ko", True)
    d.text((100, 152), "60Hz 표준 (16.67ms)", font=f["small"], fill=(248, 250, 252, 255))
    d.rounded_rectangle((250, 150, 390, 170), radius=4, fill=(56, 189, 248, 210))
    d.text((260, 152), "CPU/Worker 2.5ms", font=f["tiny"], fill=(8, 12, 20, 255))
    d.rounded_rectangle((394, 150, 980, 170), radius=4, fill=(45, 212, 191, 230))
    d.text((560, 152), "순수 GPU 실행 예산 윈도우: 12.67 ms (targetDPR <= 2.0)", font=f["tiny"], fill=(6, 10, 20, 255))
    d.rounded_rectangle((984, 150, 1110, 170), radius=4, fill=(129, 140, 248, 215))
    d.text((994, 152), "컴포지터 1.5ms", font=f["tiny"], fill=(248, 250, 252, 255))

    d.text((100, 178), "120Hz 고주사율 (8.33ms)", font=f["small"], fill=(248, 250, 252, 255))
    d.rounded_rectangle((250, 176, 350, 196), radius=4, fill=(56, 189, 248, 210))
    d.text((258, 178), "CPU 1.5ms", font=f["tiny"], fill=(8, 12, 20, 255))
    d.rounded_rectangle((354, 176, 720, 196), radius=4, fill=(245, 158, 11, 235))
    d.text((405, 178), "GPU 실행 윈도우: 5.33 ms (P2 축소 + 0.5x 볼륨)", font=f["tiny"], fill=(6, 10, 20, 255))
    d.rounded_rectangle((724, 176, 840, 196), radius=4, fill=(129, 140, 248, 215))
    d.text((734, 178), "컴포지터 1.5ms", font=f["tiny"], fill=(248, 250, 252, 255))
    draw_fitted_text(d, (856, 178), "bandwidthGBps = W*H*dpr^2 * bpp * passes * fps / 1e9", f["tiny"], (165, 243, 252, 255), 425, "ko", False)

    quads = [
        (
            (82, 220, 488, 422),
            "DIE Q1 · 6×6 인텐트 라우터 (Module 01)",
            (45, 212, 191, 255),
            [
                "• architecture (7개) : 신규 멀티패스 & SDF 아키텍처 설계",
                "• implementation (4개): VAO / 16B std140 UBO / 셰이더 구현",
                "• debug (4개) : FBO 불완전 / 미분 경계 깨짐 / 컨텍스트 손실",
                "• optimize (6개) : 고주사율 프레임 드롭 & TBDR 대역폭 절감",
                "• review (5개) : P0/P1/P2 계층 / 매직 리터럴 / 리소스 감사",
                "• migration (5개) : WebGL 1.0->2.0 및 WebGPU 하이브리드",
            ],
        ),
        (
            (888, 220, 1294, 422),
            "DIE Q2 · 셰이더 수학 & 피사체 계층 (Mod 04/05)",
            (129, 140, 248, 255),
            [
                "• 0바이트 #version 300 es · 명시적 highp/mediump 정밀도",
                "• 비균일 break 루프 전 dFdx/dFdy 계산 + textureGrad 호출",
                "• 4-탭 사면체 SDF 노멀 (6-탭 대비 평가 비용 33% 절감)",
                "• 5단계 관찰 레이어 분해 및 P0 주 실루엣 최우선 보존",
                "• 예산 초과 시: P2 제거 -> 0.5x 반해상도 -> DPR 클램프",
                "• 모든 물리/수치 상수는 명명된 상수와 유도 주석으로 문서화",
            ],
        ),
        (
            (82, 436, 488, 638),
            "DIE Q3 · 불변 FBO & 타일 GPU (Mod 03/06)",
            (245, 158, 11, 255),
            [
                "• 전용 VAO 상시 바인딩 및 16B 정렬 std140 UBO 일괄 갱신",
                "• 불변 gl.texStorage2D 할당으로 밉맵 재할당 오버헤드 제거",
                "• RGBA16F 타깃은 EXT_color_buffer_float 지원 사전 검증",
                "• 모바일 타일 GPU 패스 종료 직후 invalidateFramebuffer",
                "• 현재 FBO에 바인딩된 깊이/컬러 텍스처 동시 샘플링 금지",
                "• KTX2 BasisU 트랜스코딩 및 Draco 해제는 Web Worker 격리",
            ],
        ),
        (
            (888, 436, 1294, 638),
            "DIE Q4 · 다중 프레임 PBO & WebGPU (Mod 06/07)",
            (45, 212, 191, 255),
            [
                "• Frame N: gl.readPixels -> PIXEL_PACK_BUFFER + fenceSync",
                "• Frame N+k: clientWaitSync(0, 0) 신호 후 getBufferSubData",
                "• VAO -> GPUVertexBufferLayout | std140 UBO -> GPUBindGroup",
                "• invalidateFramebuffer -> GPURenderPass storeOp: 'discard'",
                "• 클립 공간 Z [-1,1]->[0,1] 및 좌하단->좌상단 UV 헬퍼 격리",
                "• WEBGL_lose_context 강제 손실 및 의존성 순서 복구 훈련",
            ],
        ),
    ]
    for box, title, col, bullets in quads:
        draw_glass_panel(img, box, fill_rgba=(9, 15, 32, 224), border_rgba=col, radius=8, border_width=1, blur_px=0)
        d = ImageDraw.Draw(img)
        x0, y0, x1, _ = box
        max_w = (x1 - x0) - 28
        draw_fitted_text(d, (x0 + 14, y0 + 12), title, f["card_title"], col, max_w, "ko", True)
        by = y0 + 40
        for b in bullets:
            draw_fitted_text(d, (x0 + 14, by), b, f["small"], (214, 226, 242, 255), max_w, "ko", False)
            by += 25

    draw_glass_panel(img, (506, 256, 870, 602), fill_rgba=(11, 20, 44, 232), border_rgba=(45, 212, 191, 240), radius=10, border_width=2, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (526, 272), "HBM 인터포저 직렬 제출 코어", f["h3"], (45, 212, 191, 255), 320, "ko", True)
    draw_fitted_text(d, (526, 300), "단일 WebGL2RenderingContext 6-패스", f["small"], (165, 243, 252, 255), 320, "ko", False)
    passes_ko = [
        "Pass 1 · 그림자 / 거리장(SDF) 프리패스",
        "Pass 2 · 불투명 지오메트리 / G-Buffer MRT",
        "Pass 3 · 라이팅 & 0.5x 반해상도 볼륨",
        "Pass 4 · 반투명 정렬 패스 (Depth Write Off)",
        "Pass 5 · 포스트프로세스 & 톤매핑 (ACES)",
        "Pass 6 · 디버그 오버레이 & 최종 화면 Blit",
    ]
    py = 334
    for p_txt in passes_ko:
        d.rounded_rectangle((526, py, 850, py + 34), radius=5, fill=(16, 28, 58, 240), outline=(129, 140, 248, 170), width=1)
        draw_fitted_text(d, (538, py + 8), p_txt, f["small"], (248, 250, 252, 255), 302, "ko", False)
        py += 42

    draw_glass_panel(img, (82, 652, 1294, 716), fill_rgba=(8, 22, 34, 238), border_rgba=(45, 212, 191, 225), radius=8, border_width=1, blur_px=0)
    d = ImageDraw.Draw(img)
    draw_fitted_text(d, (100, 662), "3단계 자동 검증 게이트:  python scripts/validate_repo.py (24개 정적 게이트 + 6종 역테스트)  |  python scripts/verify_browser.py (헤드리스 크롬 실증)", f["card_title"], (45, 212, 191, 255), 1174, "ko", True)
    draw_fitted_text(d, (100, 688), "실증 완료: 오프스크린 texStorage2D FBO (0x8CD5) · 다중 프레임 PBO fenceSync CONDITION_SATISFIED · 컨텍스트 복구 완료 · 한/영/중/일 슬롭 위반 0건", f["small"], (226, 232, 240, 255), 1174, "ko", False)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG", optimize=True)


def main() -> None:
    plates = ensure_plates()

    build_hero_en(plates["hero_en"], ROOT / "docs" / "assets" / "webgl2-systems-hero.png")
    build_hero_zh(plates["hero_zh"], ROOT / "docs" / "assets" / "zh-CN" / "webgl2-systems-hero.png")
    build_hero_ja(plates["hero_ja"], ROOT / "docs" / "assets" / "ja" / "webgl2-systems-hero.png")
    build_hero_ko(plates["hero_ko"], ROOT / "docs" / "assets" / "ko" / "webgl2-systems-hero.png")

    build_infographic_en(plates["info_en"], ROOT / "docs" / "assets" / "webgl2-systems-infographic.png")
    build_infographic_zh(plates["info_zh"], ROOT / "docs" / "assets" / "zh-CN" / "webgl2-systems-infographic.png")
    build_infographic_ja(plates["info_ja"], ROOT / "docs" / "assets" / "ja" / "webgl2-systems-infographic.png")
    build_infographic_ko(plates["info_ko"], ROOT / "docs" / "assets" / "ko" / "webgl2-systems-infographic.png")

    print("[OK] Generated 4 AI-studio Hero images and 4 AI-studio Workflow Infographic images across en, zh-CN, ja, ko.")


if __name__ == "__main__":
    main()
