#!/usr/bin/env python3
"""
generate the breezy-skin theme CSS for DSH.

Source palette: WorkBuddy "有风 / Breezy" appearance package (craft series, light).
Token baselines: data/dsh-{alias,specific}-baseline.json
  (extracted from @deepseek-ai/dsh-client-ui-theme@0.2.1-rc.5).

Outputs src/theme.css — the shipped stylesheet — with two blocks:
  body { ...light... }                        -> Breezy 白天
  body[data-ds-dark-theme] { ...dark... }     -> 森林夜 (derived)
All declarations use !important because DSH's ThemePresenter writes the
active token set as *inline* CSS variables on <body>; a stylesheet rule only
wins with !important.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = json.loads((ROOT / "data" / "dsh-alias-baseline.json").read_text())
# `--dsw-specific-*` 是 alias 之上的「组件专用」层：用户气泡、侧栏底色、
# 输入框、Tip 等直接消费这一层，不经过 alias。漏掉它就会出现「大部分变绿、
# 但用户气泡还是 DeepSeek 浅蓝」这种半截效果。
SPECIFIC_BASE = json.loads((ROOT / "data" / "dsh-specific-baseline.json").read_text())

# ── Breezy 白天 ──────────────────────────────────────────────────────────────
# 取自源包的 theme.json 与 skin.css 绿色重映射
L = {
    "brand": "#2e6943",
    "brandDeep": "#256d37",
    "brandDeepest": "#21472b",
    "brandBright": "#59ac65",
    "brandHover": "#4c9358",
    "page": "#f5f8f5",
    "panel": "#ffffff",
    "secondary": "#e8f0e9",
    "inset": "#eef5ef",
    "sidebar": "#e3ece4",
    "border": "#dce7dd",
    "borderStrong": "#cfe0d1",
    "borderStronger": "#bcd2bf",
    "text": "#2f4938",
    "text90": "#2f4938e6",
    "text70": "#2f4938c7",
    "text60": "#2f493899",
    "text40": "#2f493880",
}

# ── 森林夜（由 Breezy 推导的深色变体）──────────────────────────────────────
D = {
    "brand": "#7cc98a",
    "brandDeep": "#a8e6b0",
    "brandDeepest": "#d7f5da",
    "brandBright": "#a8e6b0",
    "brandHover": "#8fd79c",
    "page": "#101613",
    "panel": "#161d18",
    "secondary": "#1d271f",
    "inset": "#1a231c",
    "sidebar": "#131a15",
    "border": "#2b3a2e",
    "borderStrong": "#36473a",
    "borderStronger": "#415446",
    "text": "#e3ece4",
    "text90": "#e3ece4e6",
    "text70": "#e3ece4b3",
    "text60": "#e3ece499",
    "text40": "#e3ece466",
}

# 语义映射：alias 名 -> (light expression, dark expression)
#   {palette} 会在下面被 format 成对应的 hex
MAP = {
    # ── 背景 ──────────────────────────────────────────────────────────────
    "bg-base": ("{page}", "{page}"),
    "bg-document-preview": ("{secondary}", "{page}"),
    "bg-document-selection": ("{brand}33", "{brand}40"),
    "bg-layer-1": ("{panel}", "{panel}"),
    # 设置面板（.VOzbGW_panel）等「抬升表面」消费这一层。
    # DSH 默认 layer-1/2/3 全是 #fff（不区分层级）；Breezy 取近白 #f6f8f5，
    # 让设置面板比页面底 #f5f8f5 略亮一点点，而不是原来偏重的 #e8f0e9。
    "bg-layer-2": ("#f6f8f5", "{secondary}"),
    "bg-layer-3": ("{inset}", "{border}"),
    "bg-mask-1": ("#2f493814", "#00000080"),
    "bg-mask-2": ("#2f49380d", "#0003"),
    "bg-mask-3": ("#2f493866", "#0000007a"),
    "bg-mask-drop": ("#ffffffb3", "#161d18b3"),
    "bg-mask-photo": ("#000000e0", "#000000e0"),
    "bg-module-platform": ("{secondary}", "{border}"),
    "bg-multi-select": ("{secondary}", "{secondary}"),
    "bg-overlay": ("{secondary}", "{borderStrong}"),
    "bg-skeleton": ("#3e8a4f1a", "#7cc98a14"),
    # ── 描边 ──────────────────────────────────────────────────────────────
    "border-inverted": ("#0000", "#ffffff0f"),
    "border-inverted2": ("#0000", "#ffffff14"),
    "border-l1": ("{border}", "{border}"),
    "border-l2": ("{border}", "{border}"),
    "border-l2-darkmode-thin": ("{border}", "{border}"),
    "border-l3": ("{borderStrong}", "{borderStrong}"),
    "border-l4": ("{borderStronger}", "{borderStronger}"),
    # ── 品牌 ──────────────────────────────────────────────────────────────
    "brand-primary": ("{brand}", "{brand}"),
    "brand-primary-invert": ("{brand}", "{brand}"),
    "brand-primary-new-colorprimary-new-color": ("{brand}", "{brand}"),
    "brand-text": ("{brandDeepest}", "{brandDeepest}"),
    # ── 按钮 ──────────────────────────────────────────────────────────────
    "button-contrast-fill": ("{text}", "{text}"),
    "button-elevated-fill": ("{panel}", "{border}"),
    "button-floating-fill": ("{panel}", "{secondary}"),
    "button-floating-hover": ("{inset}", "{border}"),
    "button-ghost-active-border": ("{borderStronger}", "{borderStronger}"),
    "button-ghost-active-fill": ("{secondary}", "{border}"),
    "button-ghost-active-hover": ("{inset}", "{borderStrong}"),
    "button-info-fill": ("{brand}", "{brand}"),
    "button-info-hover": ("{brandHover}", "{brandHover}"),
    "button-primary-dimmed": ("{secondary}", "{border}"),
    "button-primary-fill": ("{brand}", "{brand}"),
    "button-primary-hover": ("{brandHover}", "{brandHover}"),
    "button-tool-bar-fill": ("#2f493880", "#e3ece480"),
    "button-tool-bar-fill-invisible": ("#2f49385c", "#e3ece45c"),
    "button-tool-bar-hover": ("#2f493899", "#e3ece499"),
    # ── 代码 diff ─────────────────────────────────────────────────────────
    "code-diff-added": ("#59ac6514", "#7cc98a1f"),
    "code-diff-deleted": ("#ec131314", "#f25a5a1f"),
    "file-diff-added-bg": ("#e6f4e7", "#1f3124"),
    "file-diff-added-gutter": ("#edf7ed", "#132016"),
    "file-diff-added-marker": ("#2e6943", "#7cc98a"),
    "file-diff-deleted-bg": ("#fce6e2", "#3c1f1b"),
    "file-diff-deleted-gutter": ("#fdece9", "#28130e"),
    "file-diff-deleted-marker": ("#ba2723", "#fa423e"),
    # ── 交互态 ────────────────────────────────────────────────────────────
    "interactive-bg-active": ("#2e69432e", "#7cc98a24"),
    "interactive-bg-hover": ("#2e694314", "#7cc98a14"),
    "interactive-bg-hover-accent": ("#2e694324", "#7cc98a3d"),
    "interactive-bg-hover-danger": ("#ec13130d", "#f25a5a26"),
    "interactive-bg-hover-solid": ("{inset}", "{border}"),
    # ── 文字 ──────────────────────────────────────────────────────────────
    "label-caption": ("{text40}", "{text40}"),
    "label-deep-diving": ("{brandDeep}", "{brand}"),
    "label-deep-diving-shimmer": ("{brandBright}", "{brandBright}"),
    "label-dimmed": ("#dbe7dc", "{borderStrong}"),
    "label-document-preview": ("{text70}", "{text70}"),
    "label-primary": ("{text}", "{text}"),
    "label-primary-bluish": ("{brandDeepest}", "{text}"),
    "label-primary-dimmed": ("{text90}", "{text90}"),
    "label-primary-foreground": ("#ffffff", "#101613"),
    "label-primary-inverted": ("#ffffff", "{border}"),
    "label-secondary": ("{text70}", "{text70}"),
    "label-shimmer": ("#2f49384d", "#e3ece473"),
    "label-tertiary": ("{text60}", "{text60}"),
    "link": ("{brand}", "{brand}"),
    # ── Markdown ──────────────────────────────────────────────────────────
    "markdown-citation": ("{secondary}", "{border}"),
    "markdown-code-block": ("{secondary}", "{page}"),
    "markdown-code-block-banner": ("{inset}", "{secondary}"),
    "markdown-code-segment-selected": ("{panel}", "{border}"),
    "markdown-code-segment-unselected": ("{secondary}", "{page}"),
    # 行内 code：源包用比次级底更浅的薄荷绿 #eef5ef，和代码块顶栏同色
    "markdown-inline-code": ("#eef5ef", "{secondary}"),
    "markdown-placeholder": ("{inset}", "{secondary}"),
    # 可点击路径 chip：源包 --cr-symbol-background #eef5ef / --cr-symbol-color #2e6943
    "markdown-tag": ("#eef5ef", "{secondary}"),
    # ── 菜单 / 浮层 ───────────────────────────────────────────────────────
    "menu-group-header-fill": ("#f5f8f5f0", "#1a231cf0"),
    "menu-icon": ("{text}", "{text70}"),
    "toast-bg": ("{brandDeepest}", "{border}"),
    "toast-label": ("#ffffff", "#e3ece4"),
    "tooltip-bg": ("{brandDeepest}", "{border}"),
    "tooltip-key-bg": ("#2e694366", "#7cc98a40"),
    "turn-trigger-bg": ("{inset}", "#7cc98a14"),
    "turn-trigger-bg-hover": ("{secondary}", "#7cc98a1f"),
    # ── Onboarding ────────────────────────────────────────────────────────
    "onboarding-accent": ("{brand}", "{brand}"),
    "onboarding-card-fill": ("#ffffffe0", "#161d18e0"),
    "onboarding-checkbox-border": ("#2f493833", "#e3ece433"),
    "onboarding-secondary-fill": ("{panel}", "{border}"),
    # ── 滚动条 ────────────────────────────────────────────────────────────
    "scrollbar-bg-l1": ("{border}", "{border}"),
    "scrollbar-bg-l2": ("{border}", "{borderStrong}"),
    "scrollbar-hover-l1": ("{borderStrong}", "{borderStrong}"),
    "scrollbar-hover-l2": ("{borderStronger}", "{borderStronger}"),
    # ── 设置卡片 ──────────────────────────────────────────────────────────
    "settings-card-fill": ("{panel}", "{panel}"),
    "settings-card-stroke": ("{border}", "{border}"),
    # ── 状态色 ────────────────────────────────────────────────────────────
    "state-business-primary": ("{brand}", "{brand}"),
    "state-business-tertiary": ("#e3f0e5", "#1c2f22"),
    "state-error-primary": ("#b83c3c", "#f25a5a"),
    "state-error-secondary": ("#c95656", "#f25a5a"),
    "state-idle-primary": ("{borderStrong}", "{borderStrong}"),
    "state-success-primary": ("#357a43", "{brandBright}"),
    "state-success-secondary": ("#4a9159", "#8fd79c"),
    "state-success-tertiary": ("#e6f4e7", "#1f3124"),
    "state-warn-label": ("#8f5c12", "#e0a556"),
    "state-warn-primary": ("#e0a556", "#e0a556"),
    "state-warn-secondary": ("#eab96f", "#eab96f"),
    "state-warn-tertiary": ("#fdf3e3", "#2b2419"),
    # ── 杂项 ──────────────────────────────────────────────────────────────
    "switch-thumb": ("#ffffff", "{text70}"),
}

# ── --dsw-specific-* 组件专用层 ─────────────────────────────────────────────
# 这一层直接给组件用，不经过 alias。用户气泡（--dsw-specific-bubble）是最典型
# 的例子：DSH 默认取 DeepSeek 品牌浅蓝 #edf3fe，只覆盖 alias 完全碰不到它。
# 值留空（不在本表里）= 保持基线，用于 --dsw-specific-menu 这类 var() 引用。
SPECIFIC_MAP = {
    # 用户消息气泡：Breezy 浅薄荷绿（对应参考 CSS 的 --cr-user-bubble-bg）
    "--dsw-specific-bubble": ("#eef5ef", "#1d271f"),
    # 气泡高亮（跳转到消息时）：比气泡深一档
    "--dsw-specific-bubble-highlight": ("#dce7dd", "#2b3a2e"),
    # 主输入框 / 登录输入框
    "--dsw-specific-input-major": ("#ffffff", "#1d271f"),
    "--dsw-specific-login-input": ("#f5f8f5", "#161d18"),
    # 选择器下拉
    "--dsw-specific-selector": ("#eef5ef", "#2b3a2e"),
    # 左侧栏：Breezy 的 #e3ece4 侧栏底色
    "--dsw-specific-sidebar-fill": ("#e3ece4", "#131a15"),
    "--dsw-specific-sidebar-nav-item-active": ("#d5e4d7", "#2b3a2e"),
    "--dsw-specific-sidebar-nav-item-active-accent": ("#cfe0d1", "#36473a"),
    "--dsw-specific-sidebar-nav-item-hover": ("#dce7dd", "#232f25"),
    # 提示条
    "--dsw-specific-tip": ("#eef5ef", "#2b3a2e"),
}


def render(name: str, expr: str, palette: dict) -> str:
    return expr.format(**palette)


def build_block(selector: str, palette: dict) -> str:
    lines = [f"{selector} {{"]
    for alias in sorted(BASE):
        key = alias.removeprefix("--dsw-alias-")
        lines.append(f"  {alias}: {render(key, MAP[key][0] if palette is L else MAP[key][1], palette)} !important;")
    for specific in sorted(SPECIFIC_BASE):
        pair = SPECIFIC_MAP.get(specific)
        if pair is None:      # 值为 var() 引用的 token 保持原样，不覆盖
            continue
        lines.append(f"  {specific}: {pair[0] if palette is L else pair[1]} !important;")
    lines.append("}")
    return "\n".join(lines)


def main() -> None:
    unmapped = sorted(set(BASE) - {f"--dsw-alias-{k}" for k in MAP})
    if unmapped:
        raise SystemExit(f"baseline aliases without a mapping: {unmapped}")
    extra = sorted(set(MAP) - {k.removeprefix("--dsw-alias-") for k in BASE})
    if extra:
        raise SystemExit(f"mapping names that are not real aliases: {extra}")
    unknown = sorted(set(SPECIFIC_MAP) - set(SPECIFIC_BASE))
    if unknown:
        raise SystemExit(f"specific mapping names that are not real tokens: {unknown}")

    skipped = sorted(set(SPECIFIC_BASE) - set(SPECIFIC_MAP))
    covered_specific = len(SPECIFIC_MAP)

    css = f"""/* breezy-skin — 有风 / Breezy for DeepSeek Harness
   源: WorkBuddy 官方外观包 remap (craft series, light)
   映射: {len(BASE)} 个 --dsw-alias-* 语义 token
       + {covered_specific} 个 --dsw-specific-* 组件 token（用户气泡 / 侧栏 / 输入框 / Tip）
   跳过: {', '.join(skipped) if skipped else '无'}（值是 var() 引用，覆盖会破坏材质推导）
   !important 是必须的 —— DSH ThemePresenter 把活动 token 写成 <body> 的内联
   CSS 变量，只有 !important 的样式表规则才能压过内联样式。 */

{build_block("body", L)}

{build_block("body[data-ds-dark-theme]", D)}
"""
    out = ROOT / "src" / "theme.css"
    out.write_text(css, encoding="utf-8")
    print(
        f"wrote {out.relative_to(ROOT)} — {len(BASE)} aliases + {covered_specific} specific x 2 schemes, {len(css)} bytes"
    )


if __name__ == "__main__":
    main()
