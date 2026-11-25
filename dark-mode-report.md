# 暗色主题报告 · breezy-skin

按 [dark-mode-converter](https://github.com/OneWave-AI/claude-skills) 方法论生成，
再用 [color-palette](https://github.com/ArnavPuri/designskills) 方法论审核。

生成器：`scripts/derive-dark.py`（OKLCH 推导）
审核器：`scripts/audit-palette.py`

---

## 1. 方法论执行情况

| 规则 | 落实 |
|---|---|
| 基色深灰、非纯黑 | `#0e110f`（OKLCH L=0.173，朝品牌绿相微偏 C=0.0063） |
| 抬升面越亮 | `inset .150 → base .173 → sidebar .195 → layer1 .217 → layer2 .254 → layer3 .291`，单调递增 |
| 文字 off-white、非纯白 | `#e0e9e2`（非 `#ffffff`） |
| 边框退成低透明度白 | `rgba(224,233,226,.08/.20/.28)`，不再用实心绿灰 |
| 强调色提亮 + 降饱和 | `#2e6943`(L.47 C.09) → `#79cd94`(L.78 C.116) |
| 每个文字/表面过 AA | 见第 3 节，14 组配对全部达标 |

## 2. Token 映射（亮 → 暗，按角色）

| 角色 | 亮色 | 暗色 | Token |
|---|---|---|---|
| 页面底 | `#fcfefc` | `#0e110f` | `--dsw-alias-bg-base` |
| 卡片 / 抬升面 1 | `#ffffff` | `#171b18` | `--dsw-alias-bg-layer-1` |
| 次面 / 抬升面 2 | `#f5faf6` | `#1f2420` | `--dsw-alias-bg-layer-2` |
| 抬升面 3 / 弹层 | `#fcfefc` | `#282d29` | `--dsw-alias-bg-layer-3` |
| 侧栏 | `#e3ece4` | `#121613` | `--dsw-specific-sidebar-fill` |
| 用户气泡 | `#eef5ef` | `#1f2420` | `--dsw-specific-bubble` |
| 代码块（内凹） | `#eef5ef` | `#090c0a` | `--dsw-alias-markdown-code-block` |
| 内凹输入 | `#ffffff` | `#1f2420` | `--dsw-specific-input-major` |
| 正文 | `#2f4938e6` | `#e0e9e2` | `--dsw-alias-label-primary` |
| 次要文字 | `#2f4938c5` | `#e0e9e2c5` | `--dsw-alias-label-secondary` |
| 三级文字 | `#2f493899` | `#e0e9e299` | `--dsw-alias-label-tertiary` |
| 说明 / 占位文字 | `#2f493880` | `#e0e9e28c` | `--dsw-alias-label-caption` |
| 品牌主色 | `#2e6943` | `#79cd94` | `--dsw-alias-brand-primary` |
| 链接 | `#2e6943` | `#79cd94` | `--dsw-alias-link` |
| 错误色 | `#b83c3c` | `#f57272` | `--dsw-alias-state-error-primary` |
| 警告文字 | `#8f5c12` | `#e0a556` | `--dsw-alias-state-warn-label` |
| 描边 l1 / l2 | `#eff6f0` | `rgba(224, 233, 226, 0.08)` | `--dsw-alias-border-l1` |
| 描边 l3 | `#dbeadd` | `rgba(224, 233, 226, 0.20)` | `--dsw-alias-border-l3` |
| 描边 l4 | `#bcd2bf` | `rgba(224, 233, 226, 0.28)` | `--dsw-alias-border-l4` |

## 3. 对比度验证

| 配对 | 前景 | 背景 | 对比度 | 判定 |
|---|---|---|---|---|
| 正文 / 页面底 | `#e0e9e2` | `#0e110f` | 15.30 | ✓ |
| 正文 / 卡片 | `#e0e9e2` | `#171b18` | 14.03 | ✓ |
| 正文 / 抬升面3 | `#e0e9e2` | `#282d29` | 11.30 | ✓ |
| 正文 / 代码块 | `#e0e9e2` | `#090c0a` | 15.84 | ✓ |
| 次要文字 / 页面底 | `#e0e9e2c5` | `#0e110f` | 9.36 | ✓ |
| 次要文字 / 卡片 | `#e0e9e2c5` | `#171b18` | 8.77 | ✓ |
| 次要文字 / 侧栏 | `#e0e9e2c5` | `#121613` | 9.10 | ✓ |
| 三级文字 / 页面底 | `#e0e9e299` | `#0e110f` | 6.04 | ✓ |
| 说明文字 / 页面底 | `#e0e9e28c` | `#0e110f` | 5.23 | ✓ |
| 说明文字 / 抬升面3 | `#e0e9e28c` | `#282d29` | 4.52 | ✓ |
| 品牌色 / 页面底 | `#79cd94` | `#0e110f` | 9.92 | ✓ |
| 链接 / 页面底 | `#79cd94` | `#0e110f` | 9.92 | ✓ |
| 错误色 / 抬升面3 | `#f57272` | `#282d29` | 5.03 | ✓ |
| 警告文字 / 页面底 | `#e0a556` | `#0e110f` | 8.76 | ✓ |

## 4. 审核发现并修复的问题

| # | 问题 | 处理 |
|---|---|---|
| 1 | `label-caption` 在抬升面上仅 4.02:1 | 不透明度 50% → 54.9%（`0x8c`），三面全过 |
| 2 | 错误色 `#f25a5a` 在 `#282d29` 上仅 4.26:1 | 提亮到 `#f57272`，最严面 5.03:1 |
| 3 | `--dsw-specific-*` 暗色列仍是旧硬编码 | 全部改用新色阶 |
| 4 | 我的对比度函数未处理 alpha（虚高） | 已修正 alpha 合成 |

## 5. 已知偏差（需要设计判断，未静默放过）

**SC 1.4.11 非文字对比 3:1**：`border-l3` = 1.69:1、`border-l4` = 2.21:1。

- 暗色下表面之间只差 1.04–1.35:1（正常现象），所以组件边界主要靠描边辨识
- 严格满足 3:1 需要 `alpha ≥ 0.42`，实测在 `#0e110f` 上是刺眼的白边
- Material / Radix / GitHub Primer 的暗色描边普遍在 0.08–0.20
- **取舍**：保视觉正确，接受该项偏差。若合规是硬要求，把 `borderMidDark` 调到 0.42 即可（会明显变亮）

## 6. 文件

| 文件 | 作用 |
|---|---|
| `scripts/derive-dark.py` | OKLCH 推导暗色调色板 |
| `scripts/audit-palette.py` | 色相/色度/对比/抬升梯审核 |
| `scripts/gen-theme.py` | 调色板 → `src/theme.css` |
| `dark-swatches.html` | 视觉验证 swatch 表 |

## 7. 后续新组件的要求

按方法论"两种模式都是一等公民"：新增组件必须同时定义亮/暗两套 token，
`npm run audit` 双模式全过才允许合并。
