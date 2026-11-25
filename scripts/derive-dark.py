#!/usr/bin/env python3
"""
按 dark-mode-converter 方法论推导 breezy-skin 的暗色主题。

方法论要点（读自 OneWave-AI/claude-skills dark-mode-converter）：
  1. 基色是深灰、不是 #000；朝品牌色相微偏
  2. 抬升面越亮 —— light 用阴影表达层级，dark 用表面亮度表达
  3. 文字是 off-white、不是 #fff
  4. 边框退成低透明度白
  5. 强调色降饱和 + 提亮 1~2 档，避免在深底上"发光"
  6. 每个文字/表面配对过 WCAG AA

本脚本：
  - 用 OKLCH 定位每个角色（感知均匀的 L 通道）
  - 输出 hex + 对比度矩阵
  - 与当前 gen-theme.py 的 D 字典做差异对照

用法：python3 scripts/derive-dark.py
"""
import math

# ─────────────────────────────────────────────────────────────
# sRGB <-> OKLab / OKLCH
# ─────────────────────────────────────────────────────────────
def _srgb_to_linear(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    v = 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055
    return max(0, min(255, round(v * 255)))


def hex_to_oklch(hexs):
    h = hexs.lstrip('#')
    r, g, b = (_srgb_to_linear(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    l_ = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m_ = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s_ = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (x ** (1 / 3) if x >= 0 else -((-x) ** (1 / 3)) for x in (l_, m_, s_))
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    C = math.hypot(a, bb)
    H = math.degrees(math.atan2(bb, a)) % 360
    return L, C, H


def oklch_to_hex(L, C, H):
    a = C * math.cos(math.radians(H))
    b = C * math.sin(math.radians(H))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l_, m_, s_ = l_ ** 3, m_ ** 3, s_ ** 3
    r = +4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_
    g = -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_
    bb = -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_
    return '#%02x%02x%02x' % (_linear_to_srgb(r), _linear_to_srgb(g), _linear_to_srgb(bb))


# ─────────────────────────────────────────────────────────────
# 对比度
# ─────────────────────────────────────────────────────────────
def _luminance(hexs):
    h = hexs.lstrip('#')
    r, g, b = (_srgb_to_linear(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _over(fg, bg):
    """把带 alpha 的前景合成到不透明背景上（8 位 hex 才处理 alpha）。"""
    f = fg.lstrip('#')
    b = bg.lstrip('#')
    if len(f) == 8:
        a = int(f[6:8], 16) / 255.0
        rgb = [round(int(f[i:i + 2], 16) * a + int(b[i:i + 2], 16) * (1 - a)) for i in (0, 2, 4)]
        return '#%02x%02x%02x' % tuple(rgb)
    return '#' + f[:6]


def contrast(fg, bg):
    solid = _over(fg, bg)
    l1, l2 = _luminance(solid), _luminance('#%s' % bg.lstrip('#')[:6])
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


# ─────────────────────────────────────────────────────────────
# 品牌色相：从 light 的 #2e6943 取
# ─────────────────────────────────────────────────────────────
BRAND_LIGHT = '#2e6943'
BRAND_L, BRAND_C, BRAND_H = hex_to_oklch(BRAND_LIGHT)

# 暗色抬升梯：L 值单调递增，间距均匀（dark 里"更高"= 更亮）
# 基色取 0.165（深灰，非纯黑），朝品牌色相微偏（chroma 0.006~0.012）
ROLES = {
    # key          L      C      role 说明
    'page':      (0.175, 0.007),   # 应用底 / 主内容区
    'sidebar':   (0.194, 0.008),   # 侧栏（比底略抬升）
    'panel':     (0.216, 0.009),   # 卡片 / 抬升面 1
    'secondary': (0.252, 0.010),   # 次面 / 抬升面 2
    'inset':     (0.150, 0.006),   # 内凹（代码块底，比底更深）
    'raised3':   (0.292, 0.011),   # 抬升面 3 / 弹层
}

# 文字：off-white（不是 #fff），朝品牌色相微偏
TEXT_L = 0.925
TEXT_C = 0.012

# 强调色：提亮 + 降饱和。light brand L≈0.47 C≈0.09 → dark L 0.78 C 0.116
ACCENT = (0.780, 0.116)


def build():
    palette = {}
    for key, (L, C) in ROLES.items():
        palette[key] = oklch_to_hex(L, C, BRAND_H)

    # 文字阶：同一 hue，靠 alpha 表示层级（与 light 一致的做法）
    text_solid = oklch_to_hex(TEXT_L, TEXT_C, BRAND_H)
    palette['text'] = text_solid
    h = text_solid.lstrip('#')
    for name, alpha in (('90', 0xe6), ('77', 0xc5), ('60', 0x99), ('50', 0x80), ('40', 0x66)):
        palette[f'text{name}'] = f'#{h}{alpha:02x}'

    # 强调色系
    bl, bc = ACCENT
    palette['brand'] = oklch_to_hex(bl, bc, BRAND_H)
    palette['brandHover'] = oklch_to_hex(bl + 0.030, bc * 0.96, BRAND_H)
    palette['brandDeep'] = oklch_to_hex(min(bl + 0.075, 0.95), bc * 0.62, BRAND_H)
    palette['brandDeepest'] = oklch_to_hex(min(bl + 0.140, 0.97), bc * 0.34, BRAND_H)
    palette['brandBright'] = oklch_to_hex(min(bl + 0.075, 0.95), bc * 0.62, BRAND_H)

    return palette


def report(palette):
    TEXT_PAIRS = [
        ('正文 / 页面底',        'text',    'page'),
        ('正文 / 卡片',          'text',    'panel'),
        ('正文 / 次面',          'text',    'secondary'),
        ('正文 / 侧栏',          'text',    'sidebar'),
        ('正文 / 代码块',        'text',    'inset'),
        ('正文 / 抬升面3',       'text',    'raised3'),
        ('次要文字 / 页面底',    'text77',  'page'),
        ('次要文字 / 卡片',      'text77',  'panel'),
        ('次要文字 / 侧栏',      'text77',  'sidebar'),
        ('三级文字 / 页面底',    'text60',  'page'),
        ('说明文字 / 页面底',    'text50',  'page'),
        ('品牌色 / 页面底',      'brand',   'page'),
        ('品牌色 / 卡片',        'brand',   'panel'),
        ('品牌文字 / 页面底',    'brandDeep', 'page'),
    ]

    print(f"{'配对':26} {'前景':9} {'背景':9} {'对比度':>7}  判定")
    print('-' * 70)
    fails = 0
    for label, fk, bk in TEXT_PAIRS:
        r = contrast(palette[fk], palette[bk])
        ok = r >= 4.5
        fails += (not ok)
        print(f"{label:26} {palette[fk]:9} {palette[bk]:9} {r:7.2f}  {'✓ AA' if ok else '✗ 需 ≥4.5'}")
    print('-' * 70)
    print(f"未达标 {fails} 项")

    print()
    print("抬升梯（L 值应单调递增）：")
    import_roles = ['inset', 'page', 'sidebar', 'panel', 'secondary', 'raised3']
    for k in import_roles:
        L, C, H = hex_to_oklch(palette[k])
        print(f"  {k:10} {palette[k]}  L={L:.3f}  C={C:.4f}")
    return fails


if __name__ == '__main__':
    p = build()
    print("=== 推导出的暗色调色板 ===")
    for k, v in p.items():
        print(f"  {k:12} {v}")
    print()
    print("=== 对比度验证 ===")
    report(p)
