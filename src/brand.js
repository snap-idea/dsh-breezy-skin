/**
 * 浏览器侧品牌替换脚本。
 *
 * DSH 把品牌（DeepSeek 鲸鱼标、「deepseek HARNESS」字标、欢迎页标题、启动页
 * 文字、页面标题、favicon）全部写死在客户端 bundle 里，Host 侧没有对应的
 * 配置项。所以这里在 `<head>` 注入一段**经典脚本**，用 MutationObserver 在
 * 节点挂载后原地替换 —— 不改 DSH 安装包，也不需要构建客户端 bundle。
 *
 * 为什么放 `<head>`：经典脚本在解析时同步执行，早于 body 解析和 `type=module`
 * 的应用脚本，因此能先接管 `document.title` 与 favicon，避免首帧闪一下原品牌。
 *
 * 每个替换点都打 `data-breezy="1"` 标记，防止 innerHTML 写回时触发观察器
 * 自激（MutationObserver 会对自己的写入再次回调）。
 *
 * @param {object} assets - 内联素材与同源 URL
 * @param {string} assets.iconSvg - 侧栏 mark：WorkBuddy 图标（currentColor）
 * @param {string} assets.logoSvg - 侧栏字标：WorkBuddy 横版 logo（黑色 path）
 * @param {string} assets.winkSvg - 欢迎页 mark：带眨眼动画的图标
 * @param {string} assets.avatarSvg - 账号头像：WorkBuddy 应用图标
 * @param {string} assets.iconLightUrl - 亮色 favicon URL
 * @param {string} assets.iconDarkUrl - 暗色 favicon URL
 * @returns {string} 可直接作为 `<script>` 文本的脚本源码
 */
export function buildBrandScript({ iconSvg, logoSvg, winkSvg, avatarSvg, iconLightUrl, iconDarkUrl }) {
  return `(function () {
  "use strict";
  if (window.__breezyBrand) return;
  window.__breezyBrand = true;

  var ICON = ${JSON.stringify(iconSvg)};
  var LOGO = ${JSON.stringify(logoSvg)};
  var WINK = ${JSON.stringify(winkSvg)};
  var AVATAR = ${JSON.stringify(avatarSvg)};
  var ICON_LIGHT = ${JSON.stringify(iconLightUrl)};
  var ICON_DARK = ${JSON.stringify(iconDarkUrl)};
  var HERO_TEXT = "WorkBuddy，我帮你";
  var OLD_HERO = "探索未至之境";
  var OLD_BOOT = "HARNESS";
  var NEW_BOOT = "WorkBuddy";
  var OLD_TITLE = "DeepSeek Harness";
  var NEW_TITLE = "WorkBuddy";

  var STYLE = [
    /* 侧栏品牌 mark：24×24，跟随 currentColor */
    '[data-slot="sidebar.brand.mark"] > svg { width: 24px; height: 24px; display: block; }',
    /* 侧栏字标：高度压到 14px，宽度按 logo 原始宽高比（1200/136 ≈ 8.82）自动等比，
       约 123px。用 width:auto 而不是写死宽度，避免 preserveAspectRatio 上下留白。 */
    '[data-slot="sidebar.brand.name"] > svg { height: 14px; width: auto; display: block; }',
    '[data-slot="sidebar.brand.name"] > svg path { fill: currentColor; }',
    /* 账号头像：WorkBuddy 应用图标（圆形，撑满 24×24 的 span） */
    '[class$="_avatar"] > svg { width: 100%; height: 100%; display: block; }',
    /* 原底色是主色 10% 的浅绿垫底，图标本身不透明，去掉避免描边 */
    '[class$="_avatar"] { background-color: transparent !important; }',
    /* 欢迎页 mark：眨眼动画（移植自 workbuddyicon-wink.html） */
    '[data-slot="conversation.hero.brand.mark"] > svg { width: 34px; height: 34px; display: block; overflow: visible; outline: none; color: inherit; }',
    '[data-slot="conversation.hero.brand.mark"] > svg > path { pointer-events: bounding-box; transform-origin: center; transform: scale(1) rotate(0deg); transition: transform .18s cubic-bezier(.34,1.5,.64,1); }',
    '[data-slot="conversation.hero.brand.mark"] > svg:is(:hover,:focus-visible,.is-winking) > path { transform: scale(.985) rotate(-6deg); }',
    '[data-slot="conversation.hero.brand.mark"] .wb-eye { transform-box: fill-box; transform-origin: center; transform: scale(1); opacity: 1; transition: transform .30s cubic-bezier(.34,1.4,.64,1) .05s, opacity .24s ease .05s; }',
    '[data-slot="conversation.hero.brand.mark"] .wb-wink { opacity: 0; transition: opacity .06s ease; }',
    '[data-slot="conversation.hero.brand.mark"] > svg:is(:hover,:focus-visible,.is-winking) .wb-eye { transform: scale(.66,.08); opacity: 0; transition: transform .15s cubic-bezier(.4,0,.7,.35), opacity .10s ease; }',
    '[data-slot="conversation.hero.brand.mark"] > svg:is(:hover,:focus-visible,.is-winking) .wb-wink { opacity: 1; transition: opacity .07s ease .03s; }',
    '@media (prefers-reduced-motion: reduce) {',
    '  [data-slot="conversation.hero.brand.mark"] > svg > path,',
    '  [data-slot="conversation.hero.brand.mark"] .wb-eye,',
    '  [data-slot="conversation.hero.brand.mark"] .wb-wink { transition: none !important; }',
    '  [data-slot="conversation.hero.brand.mark"] > svg:is(:hover,:focus-visible,.is-winking) > path { transform: none; }',
    '}'
  ].join("\\n");

  function injectStyle() {
    if (document.getElementById("breezy-brand-style")) return;
    var style = document.createElement("style");
    style.id = "breezy-brand-style";
    style.textContent = STYLE;
    (document.head || document.documentElement).appendChild(style);
  }

  /* ── 1 + 2：侧栏品牌 ─────────────────────────────────────────── */
  function swapBrand() {
    var mark = document.querySelector('[data-slot="sidebar.brand.mark"]');
    if (mark && mark.dataset.breezy !== "1") {
      mark.dataset.breezy = "1";
      mark.innerHTML = ICON;
    }
    var name = document.querySelector('[data-slot="sidebar.brand.name"]');
    if (name && name.dataset.breezy !== "1") {
      name.dataset.breezy = "1";
      name.innerHTML = LOGO;
    }
  }

  /* ── 4：欢迎页 mark（悬停 / 聚焦 / 点击眨眼）──────────────────── */
  function swapHeroMark() {
    var slot = document.querySelector('[data-slot="conversation.hero.brand.mark"]');
    if (!slot || slot.dataset.breezy === "1") return;
    slot.dataset.breezy = "1";
    slot.innerHTML = WINK;
    var svg = slot.querySelector("svg");
    if (!svg) return;
    /* 触屏没有 hover：点一下 wink 1.4s */
    svg.addEventListener("click", function () {
      svg.classList.add("is-winking");
      clearTimeout(svg.__winkTimer);
      svg.__winkTimer = setTimeout(function () {
        svg.classList.remove("is-winking");
      }, 1400);
    });
  }

  /* ── 8：账号头像 ─────────────────────────────────────────────── */
  function swapAvatar() {
    var avatar = document.querySelector('[class$="_avatar"]');
    if (avatar && avatar.dataset.breezy !== "1") {
      avatar.dataset.breezy = "1";
      avatar.innerHTML = AVATAR;
    }
  }

  /* ── 3 + 5：文本节点替换 ─────────────────────────────────────── */
  function replaceText() {
    if (!document.body) return;
    var walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, null);
    var node;
    while ((node = walker.nextNode())) {
      var text = node.nodeValue;
      if (!text) continue;
      var trimmed = text.trim();
      if (trimmed === OLD_HERO) {
        node.nodeValue = text.replace(OLD_HERO, HERO_TEXT);
      } else if (trimmed === OLD_BOOT) {
        node.nodeValue = text.replace(OLD_BOOT, NEW_BOOT);
      }
    }
  }

  /* ── 6：页面标题 ─────────────────────────────────────────────── */
  function fixTitle() {
    var title = document.querySelector("title");
    if (!title || !title.textContent) return;
    if (title.textContent.indexOf(OLD_TITLE) === -1) return;
    title.textContent = title.textContent.split(OLD_TITLE).join(NEW_TITLE);
  }

  /* ── 7：favicon 跟随 DSH 明暗主题 ────────────────────────────── */
  function syncFavicon() {
    var dark = !!(document.body && document.body.hasAttribute("data-ds-dark-theme"));
    var link = document.getElementById("breezy-favicon");
    if (!link) {
      /* 摘掉 DSH 自带的两个 media 版 favicon，换成受主题驱动的单条 */
      var originals = document.querySelectorAll('link[rel~="icon"]');
      for (var i = 0; i < originals.length; i += 1) originals[i].parentNode.removeChild(originals[i]);
      link = document.createElement("link");
      link.id = "breezy-favicon";
      link.rel = "icon";
      link.type = "image/svg+xml";
      (document.head || document.documentElement).appendChild(link);
    }
    var want = dark ? ICON_DARK : ICON_LIGHT;
    if (link.getAttribute("href") !== want) link.setAttribute("href", want);
  }

  function apply() {
    injectStyle();
    swapBrand();
    swapHeroMark();
    swapAvatar();
    replaceText();
    fixTitle();
    syncFavicon();
  }

  /* ── 观察器：rAF 合批，避免 innerHTML 写回自激 ───────────────── */
  var pending = false;
  function schedule() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(function () {
      pending = false;
      apply();
    });
  }

  function start() {
    apply();
    new MutationObserver(schedule).observe(document.documentElement, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true,
      attributeFilter: ["data-ds-dark-theme"]
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})();`;
}
