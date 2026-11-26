#!/usr/bin/env python3
"""
把 src/theme.css 的调色板导出成 palette.json，供 vscode-breezy-theme 仓库消费。

为什么要导出：VS Code 主题已拆到独立仓库
    git@github-snap-idea:snap-idea/vscode-breezy-theme.git
那个仓库要能独立重新生成主题，就不能去读我们这边的 src/theme.css。
所以这里把「角色 → 色值」拍成快照给它，dsh-skin 仍然是调色板的唯一真源。

改色流程：
    1. 改 scripts/gen-theme.py 的调色板
    2. npm run theme            # 重新生成 src/theme.css
    3. npm run export:palette   # 重新导出 palette.json
    4. 把 palette.json 复制到 vscode-breezy-theme 仓库并提交

用法：python3 scripts/export-palette.py
"""
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "src" / "theme.css"
OUT = ROOT / "palette.json"

PAT = r"(--dsw-(?:alias|specific)-[a-z0-9-]+):\s*([^;]+?)\s*!important;"

# DSH token → 主题里的语义角色
ROLES = {
    "page": "alias-bg-base",
    "panel": "alias-bg-layer-1",
    "layer2": "alias-bg-layer-2",
    "layer3": "alias-bg-layer-3",
    "sidebar": "specific-sidebar-fill",
    "inset": "alias-markdown-code-block",
    "bubble": "specific-bubble",
    "text": "alias-label-primary",
    "text2": "alias-label-secondary",
    "text3": "alias-label-tertiary",
    "text4": "alias-label-caption",
    "brand": "alias-brand-primary",
    "link": "alias-link",
    "hairline": "alias-border-l1",
    "borderMid": "alias-border-l3",
    "borderStrong": "alias-border-l4",
    "error": "alias-state-error-primary",
    "warn": "alias-state-warn-label",
    "success": "alias-state-success-primary",
}


def main():
    css = CSS.read_text(encoding="utf-8")
    head, _, tail = css.partition("body[data-ds-dark-theme]")
    light_tbl = dict(re.findall(PAT, head))
    dark_tbl = dict(re.findall(PAT, tail))

    def pick(tbl, token):
        key = "--dsw-" + token
        if key not in tbl:
            raise KeyError(f"theme.css 缺少 {key}")
        return tbl[key].strip()

    out = {
        "_comment": "由 dsh-skin/scripts/export-palette.py 从 src/theme.css 导出，请勿手改",
        "_source": "https://github.com/snap-idea/dsh-breezy-skin",
        "light": {role: pick(light_tbl, tok) for role, tok in ROLES.items()},
        "dark": {role: pick(dark_tbl, tok) for role, tok in ROLES.items()},
    }
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.name}  light={len(out['light'])} dark={len(out['dark'])} 角色")
    for scheme in ("light", "dark"):
        print(f"  {scheme}: page={out[scheme]['page']} brand={out[scheme]['brand']} text={out[scheme]['text']}")


if __name__ == "__main__":
    main()
