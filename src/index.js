/**
 * breezy-skin — 有风 / Breezy 皮肤 + WorkBuddy 品牌替换 for DeepSeek Harness (DSH) Web.
 *
 * 纯 Host 侧 Cordis 插件，不需要浏览器扩展、CDP 注入或客户端 bundle：
 *   1. `webserver/index-inject` 往 index.html 的 <head> 注入：
 *      - 一张 <style>：覆盖 DSH 的 `--dsw-alias-*` 语义 token 与
 *        `--dsw-specific-*` 组件 token，外加结构性规则；
 *      - 一段经典 <script>：把 DeepSeek 品牌换成 WorkBuddy（见 brand.js）。
 *   2. `webServer.register` 提供同源静态资源：背景图 + 明暗两版 favicon。
 *
 * 为什么不写客户端 bundle：DSH 0.2.x 的客户端插件是
 * `window.__ModuleLoader__.load({ id, factory })` 预编译格式（tsdown 产物），
 * 手写源码产不出来；而 `webserver/index-inject` 的 `{ kind: "style" }` /
 * `{ kind: "script" }` 行直接就能注入，完全绕开客户端 bundle。
 *
 * 健壮性：所有文件读取都延迟到 `apply` 内并用 try/catch 包住。资源缺失时
 * 插件退化为 no-op（只打一条告警），绝不让宿主启动失败 —— 否则半装状态会把
 * 用户挡在 Web UI 外面，只能手改 profile 才能救回来。
 *
 * 卸载：`dsh plugin --profile web remove breezy-skin`。
 *
 * @module breezy-skin
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildBrandScript } from "./brand.js";

/** Cordis 函数插件名。 */
export const name = "breezy-skin";

/** 静态资源路由需要 webServer；没有 Web 服务的 profile 下 Cordis 不会挂载本插件。 */
export const inject = ["webServer"];

const HERE = dirname(fileURLToPath(import.meta.url));
const PREFIX = "/_breezy-skin";
const ASSETS_DIR = join(HERE, "..", "assets");

/** 同源静态资源：路由 -> [文件名, content-type]。 */
const STATIC_ROUTES = {
  [`${PREFIX}/bg.jpg`]: ["background.jpg", "image/jpeg"],
  [`${PREFIX}/icon-light.svg`]: ["icon-light.svg", "image/svg+xml"],
  [`${PREFIX}/icon-dark.svg`]: ["icon-dark.svg", "image/svg+xml"],
};

/**
 * 结构性样式 —— token 表之外必须用选择器补的部分。
 *
 * **1. 欢迎页底图层**
 *
 * 挂载点是 composer 的 `variant="hero"` 变体，编译后是 CSS Module 类
 * `<hash>_composerHero`。用 `[class*="composerHero"]` 匹配那个**语义后缀**，
 * 不绑构建期 hash。用 `:has()` 而不是无条件 `body::before`：无条件固定层会在
 * 应用首帧之前就画出来（欢迎页还没挂载），表现为「加载时闪一下底图」，而且
 * 对话进行中也一直透出。限定后：加载不画、聊天不画、只有停在欢迎页才画。
 *
 * 为什么要先把外壳变透明：`.pI_x6G_frame` 和内层 `.wSkVaW_root` 都画了不透明
 * 的 `--dsw-alias-bg-base`，`body::before` 被压在下面完全看不见。
 * 注意 `[class$="_root"]` 要限定在 `centerCol` 内 —— 侧栏根 `.hHd-Xa_root`
 * 有时也以 `_root` 结尾，误伤会让侧栏在欢迎页变透明。
 *
 * **2. macOS 侧栏底色**
 *
 * `@deepseek-ai/dsh-client-ui-sidebar` 自带
 * `[data-platform="darwin"] .hHd-Xa_root { background: 0 0 }`，把侧栏根节点
 * 置空；同时侧栏列 `.pI_x6G_sidebarCol` 用的是主色的 **40% 透明**版本。
 * 两者叠加后侧栏看起来发白，而不是调色板里的颜色。这里直接给**侧栏列**上
 * 不透明 token 色 —— 它自带稳定的语义后缀 `sidebarCol`，比外壳的
 * `_frame` / `_root` 更精确。
 */
const STRUCTURE_CSS = `
body:has([class*="composerHero"]) [class$="_frame"],
body:has([class*="composerHero"]) [class*="centerCol"] [class$="_root"] {
  background-color: transparent !important;
}
body:has([class*="composerHero"])::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 0;
  background-image: url("${PREFIX}/bg.jpg");
  background-size: cover;
  background-position: center 42%;
  background-repeat: no-repeat;
  opacity: 1;
  pointer-events: none;
}
body[data-ds-dark-theme]:has([class*="composerHero"])::before {
  opacity: 0.30;
}
[data-platform="darwin"] [class*="sidebarCol"] {
  background-color: var(--dsw-specific-sidebar-fill) !important;
}

/* ── 代码块：白底 + 1px 描边 + 薄荷绿顶栏（对齐 WorkBuddy 外观包）──────────
   .md-code-block 是 DSH 手写的稳定类名（同一元素上还挂着构建期 hash 类），
   [data-code-block-banner] 同样稳定，所以不用绑 hash。
   块内 <pre> 与顶栏共享 --dsl-code-block-background，先改这个变量统一底色，
   再把顶栏单独盖回薄荷绿。颜色全部走 token，暗色主题自动跟随。 */
.md-code-block {
  --dsl-code-block-background: var(--dsw-alias-bg-layer-1) !important;
  background: var(--dsw-alias-bg-layer-1) !important;
  border: 1px solid var(--dsw-alias-border-l1) !important;
  margin: 12px 0 !important;
}
.md-code-block [data-code-block-banner] {
  background: var(--dsw-alias-markdown-inline-code) !important;
  height: 36px !important;
  padding: 6px 8px 6px 16px !important;
  box-sizing: border-box;
}
/* 行内 code：参考包规格是 3px 圆角 / 4px 内边距。:not(pre code) 排除块内代码，
   块内由 .md-code-block pre code 自己清空底色与内边距。 */
code:not(pre code) {
  border-radius: 3px !important;
  padding-inline: 4px !important;
}

/* ── 表格：白卡片 + 薄荷绿表头（对齐 WorkBuddy .cr-table-block）────────────
   WorkBuddy 实测结构：
     .cr-table-block__scroller { border:1px solid var(--cr-border-default)=#eff6f0;
                                 background:--cr-bg-primary=#fff; border-radius:16px }
     th { background:var(--cr-bg-code-header)=#eef5ef; font-weight:600 }
     th,td { border-right:1px solid #eff6f0; padding:8px 16px; font-size:15px }
     td { border-top:1px solid #eff6f0 }
     无行 hover（.wb-table--hover 是设置页的数据表格，不是 markdown 表格）
   DSH 的表格外壳带稳定类 .md-table-wide，单元格是 border-bottom 结构，
   这里只对齐「外观色 + 表头底色 + 卡片描边」，不改变 DSH 的行列边框结构。 */
.md-table-wide {
  border: 1px solid var(--dsw-alias-border-l1) !important;
  border-radius: 16px !important;
  background: var(--dsw-alias-bg-layer-1) !important;
}
.md-table-wide table {
  border-collapse: separate;
  border-spacing: 0;
}
.md-table-wide th {
  background: var(--dsw-alias-markdown-inline-code) !important;
  font-weight: 600 !important;
  border-bottom-color: var(--dsw-alias-border-l1) !important;
}
.md-table-wide td {
  border-bottom-color: var(--dsw-alias-border-l1) !important;
}

/* ── 引用块 / 分割线（对齐 WorkBuddy）──────────────────────────────────────
   WorkBuddy:
     .cr-blockquote { border-left:4px solid var(--cr-border-default)=#eff6f0;
                      padding-left:12px }
     .cr-markdown hr { border-top:1px solid #eff6f0; margin:20px 0 }
   DSH 原生是 2px #2f493880 引用条、0.5px #dce7dd 分割线（margin 32px）。
   用 [class*="_markdown_"] 锚定，不依赖构建期 hash 后缀。 */
[class*="_markdown_"] blockquote {
  border-left: 4px solid var(--dsw-alias-border-l1) !important;
  padding-left: 12px !important;
}
[class*="_markdown_"] hr {
  height: 0 !important;
  border: 0 !important;
  border-top: 1px solid var(--dsw-alias-border-l1) !important;
  background: none !important;
  margin: 20px 0 !important;
}

/* ── Skill / 文件引用 chip：内联彩色文字 → 薄荷绿胶囊 ────────────────────
   DSH 的 ReferenceChip 会渲染 data-ref-chip="skill|command|file" 属性，这是稳定
   锚点（类名 _refChip_xxxxx 是构建期 hash）。原生形态是纯内联文字，只有主色
   + 500 字重，没有底色。

   数值来自 WorkBuddy 实机（CDP 直读，非推测）：
     ._skillTag_ { box-sizing:border-box; background:var(--cr-tag-skill-bg);
                   border-radius:100px; height:23px; padding:1px 8px;
                   font-size:13px; font-weight:500; line-height:21px !important;
                   display:inline-flex }
     ._tag_      { color:var(--cr-text-primary)=#2f4938e6; gap:4px;
                   align-items:center; max-width:calc(100% - 4px) }
     ._inlineTag_{ margin-inline:4px }
   实测 --cr-tag-skill-bg = #eef5ef / hover #edf5ee / active #e3efe4。
   注意：WorkBuddy 的 Breezy 只有浅色版，暗色值是按本主题既有色阶推导的。 */
[data-ref-chip="skill"],
[data-ref-chip="command"],
[data-ref-chip="file"] {
  box-sizing: border-box;
  display: inline-flex !important;
  align-items: center !important;
  height: 23px !important;
  padding: 1px 8px !important;
  border: 0 !important;
  border-radius: 100px !important;
  background: #eef5ef !important;
  color: #2f4938e6 !important;
  font-size: 13px;
  font-weight: 500;
  line-height: 21px !important;
  gap: 4px;
  max-width: calc(100% - 4px);
  margin-inline: 4px;
  vertical-align: middle;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  user-select: none;
}
[data-ref-chip="skill"]:hover,
[data-ref-chip="command"]:hover,
[data-ref-chip="file"]:hover {
  background: #edf5ee !important;
}
[data-ref-chip="skill"]:focus-visible,
[data-ref-chip="command"]:focus-visible,
[data-ref-chip="file"]:focus-visible {
  background: #e3efe4 !important;
}
/* 图标：WorkBuddy 是 14×14；DSH 的 refIcon 原生 1em（13px）且带 4px 右边距，
   这里统一成 14px 并去掉右边距，避免与 gap 叠加成 8px。 */
[data-ref-chip="skill"] > svg,
[data-ref-chip="command"] > svg,
[data-ref-chip="file"] > svg {
  width: 14px !important;
  height: 14px !important;
  flex-shrink: 0;
  margin-right: 0 !important;
}
/* 暗色：WorkBuddy 无暗色版，沿用本主题的气泡/侧栏色阶 */
body[data-ds-dark-theme] [data-ref-chip="skill"],
body[data-ds-dark-theme] [data-ref-chip="command"],
body[data-ds-dark-theme] [data-ref-chip="file"] {
  background: #1f2420 !important;
  color: #e0e9e2e6 !important;
}
body[data-ds-dark-theme] [data-ref-chip="skill"]:hover,
body[data-ds-dark-theme] [data-ref-chip="command"]:hover,
body[data-ds-dark-theme] [data-ref-chip="file"]:hover {
  background: #232823 !important;
}
body[data-ds-dark-theme] [data-ref-chip="skill"]:focus-visible,
body[data-ds-dark-theme] [data-ref-chip="command"]:focus-visible,
body[data-ds-dark-theme] [data-ref-chip="file"]:focus-visible {
  background: #2a302b !important;
}
`;

/**
 * 读取皮肤资源。
 * @returns 样式表全文、品牌脚本、静态资源表；任一文件缺失或不可读时返回 undefined。
 */
function loadSkin() {
  try {
    const themeCss = readFileSync(join(HERE, "theme.css"), "utf8");
    if (themeCss.trim() === "") throw new Error("theme.css 是空的");

    const files = {};
    for (const [route, [file]] of Object.entries(STATIC_ROUTES)) {
      const bytes = readFileSync(join(ASSETS_DIR, file));
      if (bytes.length === 0) throw new Error(`assets/${file} 是空的`);
      files[route] = bytes;
    }

    const brandScript = buildBrandScript({
      iconSvg: readFileSync(join(ASSETS_DIR, "icon-light.svg"), "utf8"),
      logoSvg: readFileSync(join(ASSETS_DIR, "logo-black-solid.svg"), "utf8"),
      winkSvg: readFileSync(join(ASSETS_DIR, "wink.svg"), "utf8"),
      avatarSvg: readFileSync(join(ASSETS_DIR, "avatar.svg"), "utf8"),
      iconLightUrl: `${PREFIX}/icon-light.svg`,
      iconDarkUrl: `${PREFIX}/icon-dark.svg`,
    });

    return { css: `${themeCss}\n${STRUCTURE_CSS}`, brandScript, files };
  } catch (error) {
    console.warn(
      `[breezy-skin] 皮肤资源不可用，插件退化为 no-op：${error instanceof Error ? error.message : String(error)}`,
    );
    return undefined;
  }
}

/**
 * 挂载皮肤：注册静态资源路由，并把样式与品牌脚本注入每个 index.html。
 * @param ctx - 所属 Cordis 上下文；所有注册都由本 fiber 的 effect 持有并在销毁时释放。
 */
export function apply(ctx) {
  const skin = loadSkin();
  if (skin === undefined) return;

  for (const [route, [file, contentType]] of Object.entries(STATIC_ROUTES)) {
    const bytes = skin.files[route];
    ctx.effect(
      () =>
        ctx.webServer.register({
          kind: "exact",
          path: route,
          handler(req, res) {
            try {
              if (req.method !== "GET" && req.method !== "HEAD") {
                res.statusCode = 405;
                res.setHeader("allow", "GET, HEAD");
                res.end();
                return;
              }
              res.statusCode = 200;
              res.setHeader("content-type", contentType);
              res.setHeader("content-length", String(bytes.length));
              res.setHeader("cache-control", "public, max-age=31536000, immutable");
              if (req.method === "HEAD") {
                res.end();
                return;
              }
              res.end(bytes);
            } catch (error) {
              // 响应头可能已经发出，此时只能中断连接；不让异常冒泡到 HTTP 分发器。
              console.warn(
                `[breezy-skin] ${file} 响应失败：${error instanceof Error ? error.message : String(error)}`,
              );
              res.destroy();
            }
          },
        }),
      `breezy-skin: GET ${route}`,
    );
  }

  ctx.on("webserver/index-inject", (table) => {
    table.push({ kind: "style", text: skin.css });
    // 经典脚本放 <head>：同步于解析期执行，早于应用 module 脚本，
    // 因此能先接管 title 与 favicon，避免首帧闪一下原品牌。
    table.push({ kind: "script", placement: "head", text: skin.brandScript });
  });
}
