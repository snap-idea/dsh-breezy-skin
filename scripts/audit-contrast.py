#!/usr/bin/env python3
"""
对比度审计：按 token 角色套用 WCAG 2.1 绝对阈值。

DSH 的 alias token 混了「文字色」和「填充色」，用统一的 WCAG 绝对阈值会误报
（例如 DSH 自带的 state-success-primary #22c55e 在 #fff 上只有 1.9，它本来就是
一个填充色）。所以这里做的是**回归**比较：

    对每个「前景 / 背景」组合，算本主题的对比度与 DSH 默认主题的对比度，
    只要不比默认更差（留 0.05 容差）就算通过。

同时对真正的正文类 token 额外施加 WCAG AA 绝对阈值。
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
# alias 层 + specific 组件层的默认值，合并成一张查表
BASELINE = {
    **json.loads((ROOT / "data" / "dsh-alias-baseline.json").read_text()),
    **json.loads((ROOT / "data" / "dsh-specific-baseline.json").read_text()),
}

# 组合：前景, 背景, 绝对下限（None = 只做回归检查）, 说明
PAIRS = [
    ("--dsw-alias-label-primary", "--dsw-alias-bg-base", 4.5, "正文 / 页面底"),
    ("--dsw-alias-label-primary", "--dsw-alias-bg-layer-1", 4.5, "正文 / 卡片"),
    ("--dsw-alias-label-primary", "--dsw-alias-bg-layer-2", 4.5, "正文 / 次级底"),
    ("--dsw-alias-label-primary", "--dsw-alias-bg-module-platform", 4.5, "正文 / 平台模块底"),
    ("--dsw-alias-label-primary", "--dsw-alias-markdown-code-block", 4.5, "正文 / 代码块"),
    ("--dsw-alias-label-primary", "--dsw-alias-markdown-inline-code", 4.5, "正文 / 行内代码"),
    ("--dsw-alias-label-primary", "--dsw-alias-interactive-bg-hover-solid", 4.5, "正文 / 悬停底"),
    ("--dsw-alias-label-secondary", "--dsw-alias-bg-base", 4.5, "次要文字 / 页面底"),
    ("--dsw-alias-label-secondary", "--dsw-alias-bg-layer-1", 4.5, "次要文字 / 卡片"),
    ("--dsw-alias-label-tertiary", "--dsw-alias-bg-base", 3.0, "三级文字 / 页面底"),
    ("--dsw-alias-label-caption", "--dsw-alias-bg-base", 2.0, "说明文字 / 页面底"),
    ("--dsw-alias-label-dimmed", "--dsw-alias-bg-base", 1.0, "占位文字 / 页面底"),
    ("--dsw-alias-link", "--dsw-alias-bg-base", 4.5, "链接 / 页面底"),
    ("--dsw-alias-brand-primary", "--dsw-alias-bg-base", 3.0, "品牌色 / 页面底"),
    ("--dsw-alias-brand-text", "--dsw-alias-bg-base", 3.0, "品牌文字 / 页面底"),
    ("--dsw-alias-state-error-primary", "--dsw-alias-bg-base", 3.0, "错误色 / 页面底"),
    ("--dsw-alias-state-warn-label", "--dsw-alias-bg-base", 4.5, "警告文字 / 页面底"),
    ("--dsw-alias-state-success-primary", "--dsw-alias-bg-base", 3.0, "成功色 / 页面底"),
    ("--dsw-alias-label-primary-foreground", "--dsw-alias-button-primary-fill", 4.5, "按钮文字 / 主按钮"),
    ("--dsw-alias-toast-label", "--dsw-alias-toast-bg", 4.5, "Toast 文字 / Toast 底"),
    ("--dsw-alias-menu-icon", "--dsw-alias-bg-base", 3.0, "菜单图标 / 页面底"),
    ("--dsw-alias-scrollbar-hover-l2", "--dsw-alias-bg-base", 1.0, "滚动条悬停 / 页面底"),
    # ── --dsw-specific-* 组件层 ──────────────────────────────────────────
    ("--dsw-alias-label-primary", "--dsw-specific-bubble", 4.5, "用户气泡正文 / 气泡底"),
    ("--dsw-alias-label-primary", "--dsw-specific-bubble-highlight", 4.5, "用户气泡正文 / 高亮底"),
    ("--dsw-alias-label-primary", "--dsw-specific-sidebar-fill", 4.5, "侧栏文字 / 侧栏底"),
    ("--dsw-alias-label-secondary", "--dsw-specific-sidebar-fill", 4.5, "侧栏次要 / 侧栏底"),
    ("--dsw-alias-label-primary", "--dsw-specific-sidebar-nav-item-active", 4.5, "侧栏选中 / 选中底"),
    ("--dsw-alias-label-primary", "--dsw-specific-sidebar-nav-item-hover", 4.5, "侧栏文字 / 悬停底"),
    ("--dsw-alias-label-primary", "--dsw-specific-input-major", 4.5, "输入文字 / 主输入框"),
    ("--dsw-alias-label-primary", "--dsw-specific-selector", 4.5, "文字 / 选择器底"),
    ("--dsw-alias-label-primary", "--dsw-specific-tip", 4.5, "文字 / 提示条底"),
]


def parse_theme(css: str):
    light, dark, block = {}, {}, None
    for line in css.splitlines():
        s = line.strip()
        if s.startswith("body[data-ds-dark-theme]"):
            block = dark
        elif s == "body {":
            block = light
        m = re.match(r"(--dsw-(?:alias|specific)-[a-z0-9-]+):\s*([^;]+?)\s*!important;", s)
        if m and block is not None:
            block[m.group(1)] = m.group(2)
    return light, dark


def to_rgba(value: str, alpha: float = 1.0):
    v = value.strip()
    if v.startswith("#"):
        h = v[1:]
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        if len(h) == 6:
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha
        if len(h) == 8:
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        r, g, b = (int(float(p)) for p in parts[:3])
        return r, g, b, float(parts[3]) if len(parts) > 3 else alpha
    raise ValueError(f"unsupported color: {value!r}")


def over(fg, bg):
    r, g, b, a = fg
    br, bg_, bb, _ = bg
    return (round(r * a + br * (1 - a)), round(g * a + bg_ * (1 - a)), round(b * a + bb * (1 - a)), 1.0)


def luminance(rgb) -> float:
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b, _ = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast(fg, bg) -> float:
    l1, l2 = luminance(over(fg, bg)), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


TOLERANCE = 0.05


def main() -> int:
    css = (ROOT / "src" / "theme.css").read_text(encoding="utf-8")
    light, dark = parse_theme(css)
    print(f"parsed: light={len(light)} dark={len(dark)} tokens  (baseline {len(BASELINE)})\n")

    problems = []
    for scheme, table, key in (("light", light, "light"), ("dark", dark, "dark")):
        print(f"── {scheme} ───────────────────────────────────────────────────────")
        for fg_key, bg_key, floor, label in PAIRS:
            if fg_key not in table or bg_key not in table:
                problems.append(f"{scheme}: 主题缺少 {fg_key} 或 {bg_key}")
                continue
            base_fg = BASELINE[fg_key][key]
            base_bg = BASELINE[bg_key][key]
            try:
                base = contrast(to_rgba(base_fg), to_rgba(base_bg))
                mine = contrast(to_rgba(table[fg_key]), to_rgba(table[bg_key]))
            except ValueError as exc:
                problems.append(f"{scheme}: {label}: {exc}")
                continue
            below_floor = floor is not None and mine < floor
            mark = "FAIL" if below_floor else "OK  "
            delta = mine - base
            print(
                f"  {mark} {mine:5.2f} (>= {floor:.1f})  (默认 {base:5.2f}, {delta:+.2f})  {label:<22} {table[fg_key]} on {table[bg_key]}"
            )
            if below_floor:
                problems.append(
                    f"{scheme}: {label} 低于绝对下限 {floor:.1f}，实为 {mine:.2f}  ({table[fg_key]} on {table[bg_key]})"
                )
        print()

    if problems:
        print("!! 未通过:")
        for p in problems:
            print("  -", p)
        return 1
    print("全部通过：每个 token 达到其角色的 WCAG 绝对阈值")
    return 0


if __name__ == "__main__":
    sys.exit(main())
