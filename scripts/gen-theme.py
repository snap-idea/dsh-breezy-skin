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
    # 页面底色：WorkBuddy 主内容区/顶栏/输入框区实测 #fcfefc
    # （zip 的 theme.json 写 #f5f8f5，但线上外观包已更新）
    "page": "#fcfefc",
    "panel": "#ffffff",
    "secondary": "#e8f0e9",
    "inset": "#eef5ef",
    "sidebar": "#e3ece4",
    "border": "#dce7dd",
    # WorkBuddy: --cr-border-default / --cb-stroke-secondary / --cb-input-border-color
    "hairline": "#eff6f0",
    # WorkBuddy: --cb-border-default（卡片/表头等实心边框）
    "borderMid": "#dbeadd",
    "borderStrong": "#cfe0d1",
    "borderStronger": "#bcd2bf",
    "text": "#2f4938",
    "text90": "#2f4938e6",
    # 次要文字：WorkBuddy 原值 #2f4938b3（70%），但在侧栏底 #e3ece4 上只有
    # 3.82:1，低于 WCAG AA 4.5。取 77.25%（#2f4938c5）—— 这是逐字节扫描出的
    # 最小达标值，能同时过页面底/卡片/侧栏三面（5.09 / 5.16 / 4.56）。
    # 注释里写 77% 即可，c5 = 197/255 = 0.7725。
    "text70": "#2f4938c5",
    "text60": "#2f493899",
    "text40": "#2f493880",
}

# ── 森林夜（由 Breezy 推导的深色变体）──────────────────────────────────────
D = {
    # ── 按 dark-mode-converter 方法论推导（scripts/derive-dark.py）──────────
    # 1) 基色深灰非纯黑，朝品牌色相（绿）微偏
    # 2) 抬升面越亮：inset .150 < page .173 < sidebar .195 < panel .217
    #    < secondary .254 < raised3 .291（L 值为 OKLCH 明度，单调递增）
    # 3) 文字 off-white #e0e9e2，不用纯白
    # 4) 边框用低透明度白（见 hairlineDark / borderMidDark）
    # 5) 强调色提亮 + 降饱和：#2e6943 → #79cd94
    "page": "#0e110f",
    "sidebar": "#121613",
    "panel": "#171b18",
    "secondary": "#1f2420",
    "inset": "#090c0a",
    "raised3": "#282d29",
    # 以下三个是"填充"用途的实心色（按钮/浮层底），不是描边
    "border": "#2a302b",
    "borderStrong": "#343a35",
    "borderStronger": "#3f453f",
    # 描边专用：低透明度白，替代实心绿灰
    "hairlineDark": "rgba(224, 233, 226, 0.08)",
    "borderMidDark": "rgba(224, 233, 226, 0.20)",
    "borderStrongDark": "rgba(224, 233, 226, 0.28)",
    "text": "#e0e9e2",
    "text90": "#e0e9e2e6",
    "text70": "#e0e9e2c5",
    "text60": "#e0e9e299",
    "text40": "#e0e9e28c",
    "brand": "#79cd94",
    "brandHover": "#86d69f",
    "brandDeep": "#acdeba",
    "brandDeepest": "#d2edd8",
    "brandBright": "#acdeba",
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
    # 次面：WorkBuddy --cb-bg-secondary #f5faf6
    "bg-layer-2": ("#f5faf6", "{secondary}"),
    # 抬升面：WorkBuddy --cb-bg-tertiary #fcfefc
    "bg-layer-3": ("#fcfefc", "{raised3}"),
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
    "border-l1": ("{hairline}", "{hairlineDark}"),
    "border-l2": ("{hairline}", "{hairlineDark}"),
    "border-l2-darkmode-thin": ("{hairline}", "{hairlineDark}"),
    "border-l3": ("{borderMid}", "{borderMidDark}"),
    "border-l4": ("{borderStronger}", "{borderStrongDark}"),
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
    "label-primary": ("{text90}", "{text}"),
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
    # 代码块基色：WorkBuddy --cb-markdown-code-block-bg #eef5ef
    # （块级外壳由 .md-code-block 结构规则覆盖成白卡片）
    "markdown-code-block": ("{inset}", "{inset}"),
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
    "state-error-primary": ("#b83c3c", "#f57272"),
    "state-error-secondary": ("#c95656", "#f88a8a"),
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
    # 亮色列沿用 WorkBuddy Breezy 实测值；暗色列改用 derive-dark.py 推导的
    # 新色阶（page .173 / sidebar .195 / panel .217 / secondary .254 / raised3 .291）
    # —— 早期版本这里是硬编码的旧暗色，与本轮暗色主题不一致。
    "--dsw-specific-bubble": ("#eef5ef", "#1f2420"),            # 气泡底 = 次面
    "--dsw-specific-bubble-highlight": ("#dce7dd", "#2a302b"),  # 高亮 = 抬升填充
    "--dsw-specific-input-major": ("#ffffff", "#1f2420"),       # 主输入框
    "--dsw-specific-login-input": ("#f5f8f5", "#171b18"),       # 登录输入框 = 卡片
    "--dsw-specific-selector": ("#eef5ef", "#282d29"),          # 选择器 = 抬升面3
    "--dsw-specific-sidebar-fill": ("#e3ece4", "#121613"),      # 侧栏
    "--dsw-specific-sidebar-nav-item-active": ("#d5e4d7", "#282d29"),
    "--dsw-specific-sidebar-nav-item-active-accent": ("#cfe0d1", "#343a35"),
    "--dsw-specific-sidebar-nav-item-hover": ("#dce7dd", "#232823"),
    "--dsw-specific-tip": ("#eef5ef", "#282d29"),               # 提示条 = 抬升面3
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
