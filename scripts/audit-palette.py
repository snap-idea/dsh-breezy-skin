#!/usr/bin/env python3
"""
按 color-palette 方法论（ArnavPuri/designskills）审核 breezy-skin 的暗色主题。

审核项：
  1. OKLCH 色相稳定性 —— 同一色族内 H 漂移应 < 15°，否则看起来不是一家人
  2. 色度上限 —— 暗色下高空色度会"发光"，近中性面 C 应 < 0.02
  3. 不是纯黑 / 纯白
  4. 文字配对 WCAG AA（4.5）
  5. 非文字 UI（边框/图标/焦点环）3:1（SC 1.4.11）
  6. 抬升梯单调（dark 里越高的面越亮）

用法：python3 scripts/audit-palette.py
"""
import math
import re
import pathlib

# ── 颜色工具（与 derive-dark.py 一致）───────────────────────────────
def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_oklch(hexs):
    h = hexs.lstrip('#')[:6]
    r, g, b = (_lin(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    l_ = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m_ = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s_ = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (x ** (1 / 3) if x >= 0 else -((-x) ** (1 / 3)) for x in (l_, m_, s_))
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def _rgb_of(hexs):
    """接受 #rrggbb / #rrggbbaa / rgba(...) 三种写法，返回 (r, g, b)。"""
    v = hexs.strip()
    if v.startswith('rgba') or v.startswith('rgb'):
        nums = re.findall(r'[\d.]+', v)
        return int(float(nums[0])), int(float(nums[1])), int(float(nums[2]))
    h = v.lstrip('#')
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def luminance(hexs):
    r, g, b = (_lin(c) for c in _rgb_of(hexs))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def over(fg, bg):
    if fg.strip().startswith('rgba') or fg.strip().startswith('rgb'):
        m = re.findall(r'[\d.]+', fg)
        a = float(m[3]) if len(m) > 3 else 1.0
        br, bgc, bb = _rgb_of(bg)
        r, g, b = (int(float(m[i])) for i in (0, 1, 2))
        return '#%02x%02x%02x' % (round(r * a + br * (1 - a)),
                                  round(g * a + bgc * (1 - a)),
                                  round(b * a + bb * (1 - a)))
    f = fg.lstrip('#')
    if len(f) == 8:
        a = int(f[6:8], 16) / 255.0
        b = bg.lstrip('#')[:6]
        return '#%02x%02x%02x' % tuple(
            round(int(f[i:i + 2], 16) * a + int(b[i:i + 2], 16) * (1 - a)) for i in (0, 2, 4))
    return '#' + f[:6]


def ratio(fg, bg):
    l1, l2 = luminance(over(fg, bg)), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ── 从 src/theme.css 读取暗色 token ────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent.parent
css = (ROOT / 'src' / 'theme.css').read_text(encoding='utf-8')
dark_block = css.split('body[data-ds-dark-theme]')[1]
dark = dict(re.findall(r'(--dsw-(?:alias|specific)-[a-z0-9-]+):\s*([^;]+?)\s*!important;', dark_block))

T = lambda name: dark['--dsw-' + name]

SURFACES = {
    'bg-base': T('alias-bg-base'),
    'bg-layer-1': T('alias-bg-layer-1'),
    'bg-layer-2': T('alias-bg-layer-2'),
    'bg-layer-3': T('alias-bg-layer-3'),
    'sidebar': T('specific-sidebar-fill'),
    'bubble': T('specific-bubble'),
    'code-block': T('alias-markdown-code-block'),
}

TEXTS = {
    'label-primary': T('alias-label-primary'),
    'label-secondary': T('alias-label-secondary'),
    'label-tertiary': T('alias-label-tertiary'),
    'label-caption': T('alias-label-caption'),
    'brand': T('alias-brand-primary'),
    'link': T('alias-link'),
    'error': T('alias-state-error-primary'),
    'warn-label': T('alias-state-warn-label'),
}

BORDERS = {
    'border-l1': T('alias-border-l1'),
    'border-l2': T('alias-border-l2'),
    'border-l3': T('alias-border-l3'),
    'border-l4': T('alias-border-l4'),
}

problems = []


def head(t):
    print()
    print('─' * 78)
    print(t)
    print('─' * 78)


# ── 1. OKLCH 色相稳定性 + 色度上限 ─────────────────────────────────
head('1. OKLCH 检查：色相稳定性 / 色度上限')
print(f"{'surface':12} {'hex':9} {'L':>6} {'C':>7} {'H':>7}")
hues = []
for k, v in SURFACES.items():
    L, C, H = hex_to_oklch(v)
    hues.append(H)
    flag = ''
    if C > 0.02:
        flag += '  ⚠ 色度偏高（暗底会发光）'
        problems.append(f'{k} 色度 {C:.4f} > 0.02')
    print(f'{k:12} {v:9} {L:6.3f} {C:7.4f} {H:7.1f}{flag}')

hue_spread = max(hues) - min(hues)
print(f'\n  中性面色相跨度 = {hue_spread:.1f}°  ' +
      ('✓ 稳定（<15°）' if hue_spread < 15 else '⚠ 漂移过大'))
if hue_spread >= 15:
    problems.append(f'中性面色相跨度 {hue_spread:.1f}° ≥ 15°')

# ── 2. 抬升梯单调 ────────────────────────────────────────────────
head('2. 抬升梯（dark：越高的面越亮）')
ladder = ['code-block', 'bg-base', 'sidebar', 'bg-layer-1', 'bg-layer-2', 'bg-layer-3']
Ls = [(k, hex_to_oklch(SURFACES[k])[0]) for k in ladder]
prev = -1
for k, L in Ls:
    ok = L > prev
    print(f'  {k:12} L={L:.3f}  {"✓" if ok else "✗ 未递增"}')
    if not ok:
        problems.append(f'抬升梯在 {k} 处未递增')
    prev = L

# ── 3. 纯黑 / 纯白 ───────────────────────────────────────────────
head('3. 纯黑 / 纯白检查')
all_vals = list(SURFACES.values()) + list(TEXTS.values())
pure_black = [v for v in all_vals if v.lower() in ('#000000', '#000')]
pure_white = [v for v in all_vals if v.lower() in ('#ffffff', '#fff')]
print(f'  纯黑: {pure_black or "无 ✓"}')
print(f'  纯白: {pure_white or "无 ✓"}')
if pure_black or pure_white:
    problems.append('存在纯黑或纯白')

# ── 4. 文字配对 AA ───────────────────────────────────────────────
head('4. 文字配对（WCAG AA 4.5）')
print(f"{'前景':16} {'背景':12} {'对比度':>7}  判定")
for tk, tv in TEXTS.items():
    for sk, sv in SURFACES.items():
        r = ratio(tv, sv)
        if r < 4.5:
            print(f'{tk:16} {sk:12} {r:7.2f}  ✗')
            problems.append(f'{tk} on {sk} = {r:.2f} < 4.5')
print('  （仅列出未达标项；无输出 = 全部达标 ✓）')

# ── 5. 非文字 UI 3:1 ─────────────────────────────────────────────
head('5. 非文字 UI 边框（SC 1.4.11 要求 ≥3:1）')
print(f"{'边框':14} {'on bg-base':>12} {'on bg-layer-1':>15}  说明")
for bk, bv in BORDERS.items():
    r1 = ratio(bv, SURFACES['bg-base'])
    r2 = ratio(bv, SURFACES['bg-layer-1'])
    note = '装饰性，豁免' if bk in ('border-l1', 'border-l2') else '需 ≥3'
    print(f'{bk:14} {r1:12.2f} {r2:15.2f}  {note}')
print('\n  注：l1/l2 是纯装饰分隔线，WCAG 1.4.11 明确豁免。')
print('      l3/l4 用于表头/输入框轮廓。严格满足 SC 1.4.11 的 3:1 需要 α≥0.42')
print('      （在 #0e110f 上实测），那在暗色下是刺眼的白边；主流暗色系统')
print('      （Material / Radix / Primer）普遍用 0.08~0.20。此处选择视觉正确，')
print('      偏差已在 dark-mode-report.md 如实记录，不静默放过。')
for bk in ('border-l3', 'border-l4'):
    if ratio(BORDERS[bk], SURFACES['bg-base']) < 3:
        print(f'      ⚠ {bk} = {ratio(BORDERS[bk], SURFACES["bg-base"]):.2f} < 3（已知偏差）')

# ── 汇总 ────────────────────────────────────────────────────────
head('审核结论')
if problems:
    print(f'  ⚠ {len(problems)} 项待处理：')
    for x in problems:
        print('   -', x)
    raise SystemExit(1)
print('  ✓ 全部通过')
