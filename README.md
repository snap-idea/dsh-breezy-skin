# breezy-skin

**有风 / Breezy** 皮肤 for [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（DSH）Web。

把 WorkBuddy「有风 Breezy」外观包的配色完整移植到 DSH 的原生 token 体系，并把自然底图
限定在**新建会话欢迎页**；同时把 DSH 的 DeepSeek 品牌整体替换成 WorkBuddy。
纯 Host 侧 Cordis 插件 —— 不改 DSH 安装包、不需要浏览器扩展、不需要 CDP 注入、
没有客户端 bundle。

```
DSH Web Loader
└── breezy-skin (Host)
    ├── webserver/index-inject  → <head> 注入 <style>（token + 结构规则）
    │                             和 <script>（品牌替换，见 brand.js）
    └── webServer.register      → GET /_breezy-skin/{bg.jpg,icon-light.svg,icon-dark.svg}
```

## 安装

```bash
# 从 GitHub
dsh plugin --profile web add github:USER/breezy-skin

# 或本地路径
dsh plugin --profile web add "$PWD"
```

装完**重启 `dsh web`**（Host 插件只在启动时装载，没有热重载路径）。之后在
**设置 → 已安装插件** 里就能看到它（带图标、可停用）。

## 卸载

```bash
dsh plugin --profile web remove breezy-skin
```

## 它到底覆盖了什么

DSH 的颜色不是一个平面，而是**两层**，只覆盖 alias 会漏：

| 层 | 数量 | 消费者 | 漏掉会怎样 |
|---|---|---|---|
| `--dsw-alias-*` | 107 | 大部分组件（通过语义别名） | 主界面不变色 |
| `--dsw-specific-*` | 11（覆盖 10） | **用户气泡**、侧栏底色、输入框、选择器、Tip | 主界面变绿，**用户气泡还是 DeepSeek 浅蓝 `#edf3fe`** |

外加 3 条**结构性规则**（token 表达不了、必须用选择器补）：

外加**代码块**对齐（`.md-code-block` / `[data-code-block-banner]` 都是 DSH 手写的稳定类名）：

| 属性 | 值 | 来源 token |
|---|---|---|
| 块底色 | 白 / `#161d18` | `--dsw-alias-bg-layer-1` |
| 块描边 | `1px` `#dce7dd` / `#2b3a2e` | `--dsw-alias-border-l1` |
| 块圆角 / 外边距 | `16px` / `12px 0` | — |
| 顶栏底色 | `#eef5ef` / `#1d271f` | `--dsw-alias-markdown-inline-code` |
| 顶栏高度 / 内边距 | `36px` / `6px 8px 6px 16px` | — |
| 行内 code | `#eef5ef`，`3px` 圆角、`4px` 内边距 | `--dsw-alias-markdown-inline-code` |

> 块内 `<pre>` 与顶栏共享 `--dsl-code-block-background`，所以先改这个变量统一底色，
> 再把顶栏单独盖回薄荷绿。颜色全部走 token，暗色主题自动跟随。

| 规则 | 为什么 |
|---|---|
| `body:has([class*="composerHero"])::before` | 底图只在**新建会话欢迎页**出现，加载阶段和对话页都不画 |
| `body:has(…) [class$="_frame"], … [class*="centerCol"] [class$="_root"] { background: transparent }` | 应用外壳画了不透明的 `--dsw-alias-bg-base`，不先透明化底图会被完全盖住 |
| `[data-platform="darwin"] [class*="sidebarCol"]` | macOS Desktop 把侧栏根置空、侧栏列用 40% 透明主色，叠加后发白；这里改回不透明 token 色 |

> 选择器都用 **CSS Module 的语义后缀**（`composerHero` / `sidebarCol` / `_frame` / `_root`），
> 不绑构建期 hash，DSH 升级只要没重命名 CSS Module key 就还生效。

## 品牌替换（8 处）

DSH 把品牌写死在客户端 bundle 里，Host 侧没有对应配置项。`src/brand.js` 在 `<head>`
注入一段**经典脚本**，用 MutationObserver 在节点挂载后原地替换：

| # | 位置 | 替换为 |
|---|---|---|
| 1 | `[data-slot="sidebar.brand.mark"]` | WorkBuddy 图标（`currentColor`，跟随主题文字色） |
| 2 | `[data-slot="sidebar.brand.name"]` | WorkBuddy 横版字标 |
| 3 | 欢迎页 `.titleGroup` 标题 | `探索未至之境` → **WorkBuddy，我帮你** |
| 4 | `[data-slot="conversation.hero.brand.mark"]` | 眨眼动画：悬停时右眼收缝成 `＜`，整标轻微缩放并逆时针偏转 |
| 5 | 启动页 `HARNESS` | → **WorkBuddy** |
| 6 | 页面标题 | `DeepSeek Harness` → **WorkBuddy**（`<task> — WorkBuddy`） |
| 7 | favicon | 跟随 DSH 明暗主题：亮色 `icon-light.svg` / 暗色 `icon-dark.svg` |
| 8 | 账号头像 `[class$="_avatar"]` | WorkBuddy 应用图标（圆形，24×24） |

实现要点：

- 脚本放 **`<head>`**：经典脚本同步于解析期执行，早于 `type=module` 的应用脚本，
  因此能先接管 `document.title` 与 favicon，**首帧不会闪一下原品牌**。
- 每个替换点打 `data-breezy="1"` 标记，防止 `innerHTML` 写回触发观察器**自激**。
- 观察器用 `requestAnimationFrame` 合批，`attributeFilter` 只盯
  `data-ds-dark-theme`，避免全量属性回调。
- 眨眼动画的 mask id 重命名为 `breezy-wink-mask`，避免多实例 id 冲突。
- 尊重 `prefers-reduced-motion`：关闭缩放与描线过渡。

## 配色

| 角色 | 亮色 | 暗色（推导） | token |
|---|---|---|---|
| 页面底 | `#f5f8f5` | `#101613` | `--dsw-alias-bg-base` |
| 卡片 / 抬升表面 | `#ffffff` / `#f6f8f5` | `#161d18` / `#1d271f` | `--dsw-alias-bg-layer-1` / `-2` |
| 侧栏 | `#e3ece4` | `#131a15` | `--dsw-specific-sidebar-fill` |
| **用户气泡** | `#eef5ef` | `#1d271f` | `--dsw-specific-bubble` |
| 品牌主色 | `#2e6943` | `#7cc98a` | `--dsw-alias-brand-primary` |
| 正文 | `#2f4938` | `#e3ece4` | `--dsw-alias-label-primary` |
| 次要文字 | `#2f4938c7` | `#e3ece4b3` | `--dsw-alias-label-secondary` |
| 描边 | `#dce7dd` | `#2b3a2e` | `--dsw-alias-border-l1` |

暗色是**推导**的「森林夜」——源包只有浅色，推导保持同一色相与层级关系。

## 验证

```bash
npm run theme   # 重新生成 src/theme.css
npm run audit   # WCAG 2.1 对比度审计（31 组配对 × 亮暗 = 62 项）
npm run check   # 插件语法
```

审计按 token 角色套用绝对阈值：正文 9.21:1（AA 需 4.5）、次要 5.05:1、三级 3.19:1、
链接 6.10:1、主按钮 6.53:1、用户气泡 8.89:1、侧栏 8.16:1；暗色正文 15.17:1。
**62 项全部达标。**

## 为什么必须有 `!important`

DSH 的 `ThemePresenter`（`@deepseek-ai/dsh-client-ui-theme` + `dsh-client-ui-layout`）把
当前主题 token 写成 `<body>` 上的**内联** CSS 变量（`style="--dsw-alias-bg-base: …"`）。
内联样式优先级最高，样式表规则只有加 `!important` 才能压过。亮/暗两套都带
`!important`，由选择器特异性决定胜负（`body[data-ds-dark-theme]` > `body`）。

## 目录

```
src/
├── index.js        # Cordis Host 插件（静态路由 + index 注入）
├── brand.js        # 品牌替换脚本生成器（内联 SVG，输出经典脚本）
└── theme.css       # 生成物：117 个 token × 亮暗
assets/
├── icon.png        # 插件列表图标 560×560 RGBA（设置 → 已安装插件）
├── background.jpg  # 欢迎页底图，2560w JPEG q70，457 KB
├── icon-light.svg  # favicon（亮）
├── icon-dark.svg   # favicon（暗）
├── logo-black-solid.svg  # 侧栏字标
├── avatar.svg      # 账号头像（40×40 应用图标）
└── wink.svg        # 欢迎页 mark（含眨眼动画）
locale/
├── en.json         # 插件列表标题 / 描述
└── zh.json
scripts/
├── gen-theme.py    # 调色板 → theme.css
└── audit-contrast.py
data/
├── dsh-alias-baseline.json     # DSH 0.2.1-rc.5 的 107 个 alias 默认值
└── dsh-specific-baseline.json  # 11 个 specific 默认值
```

## 已知限制

- **只在 Web profile 生效**。插件 `inject: ["webServer"]`，headless profile 下不挂载。
- **重启才生效**。Host 插件没有热重载；客户端插件才有 HMR。
- **`--dsw-specific-menu` 故意不覆盖**。它的值是 `var(--dsw-menu-surface-fill)`，
  强行去引用会破坏菜单材质（模糊 / 半透明）的推导链。
- **DSH 升级可能失效**。语义后缀稳定，但若上游重命名 CSS Module key
  （`composerHero` / `sidebarCol`），底图作用域需要跟着调。
- **品牌替换是 DOM 层**。依赖 `data-slot` 名称与固定文案（`探索未至之境` /
  `HARNESS` / `DeepSeek Harness`）。DSH 改文案或多语言时会静默失效 —— 但这正是
  它安全的地方：失效只是回到原品牌，不会白屏。

## 素材与授权

代码以 MIT 发布。`assets/background.jpg`、`assets/icon.png` 与配色取自 WorkBuddy 官方
外观包（`有风 / Breezy`，craft 系列），**版权归原权利人所有**，本仓库仅用于本机换肤与
备份。如需商用请自行确认素材授权。
