#!/usr/bin/env python3
"""Render public documents. Install: python -m pip install Markdown==3.7"""
from pathlib import Path
import argparse
import html

import markdown

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    "proposal": "КПО «Восток»: аналитическая записка и план действий",
    "appeal": "КПО «Восток»: обращение и памятка заявителю",
}
STYLE = """
*{box-sizing:border-box}
body{margin:0;background:#f4f1e8;color:#17221f;font:17px/1.65 system-ui,sans-serif}
main,nav{max-width:1100px;margin:auto;padding:24px}
main{background:#fffdf7}nav{display:flex;gap:20px;flex-wrap:wrap}
a{color:#234b63;overflow-wrap:anywhere}
a:focus-visible{outline:3px solid #923913;outline-offset:4px}
h1,h2,h3{line-height:1.2}h1{font-size:clamp(1.8rem,4vw,2.8rem)}
h2{margin-top:2em}table{border-collapse:collapse;width:100%;font-size:.9em}
td,th{border:1px solid #aab4aa;padding:10px;text-align:left;vertical-align:top;overflow-wrap:anywhere}
.table-scroll{overflow-x:auto}blockquote{border-left:4px solid #315b75;margin-left:0;padding-left:20px}
@media(max-width:650px){main,nav{padding:16px}table{min-width:650px}}
@media print{
@page{size:A4;margin:16mm}body{background:white;font-size:10pt}
nav{display:none}main{padding:0;max-width:none}h1{font-size:22pt}h2{font-size:16pt}
h1,h2,h3{break-after:avoid}tr{break-inside:avoid}thead{display:table-header-group}
table{min-width:0;font-size:8pt}.table-scroll{overflow:visible}a{color:inherit}
}
"""


def render(name, title):
    source = (ROOT / "docs" / f"{name}.md").read_text(encoding="utf-8")
    body = markdown.markdown(source, extensions=["tables"])
    # Markdown sources remain editable; public HTML links stay within the site.
    for document in TITLES:
        body = body.replace(f'href="{document}.md"', f'href="{document}.html"')
    body = body.replace(
        "<table>", '<div class="table-scroll" role="region" aria-label="Таблица данных" tabindex="0"><table>'
    ).replace("</table>", "</table></div>")
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{STYLE}</style>
</head>
<body>
<nav aria-label="Материалы">
<a href="../index.html#proposal">На главную</a>
<a href="proposal.html">Записка</a>
<a href="appeal.html">Обращение</a>
<a href="presentation.html">Презентация</a>
<a href="{name}.md" download>Исходник Markdown</a>
<span>Печать / сохранить PDF: Ctrl+P или ⌘P</span>
</nav>
<main>
{body}
</main>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if committed HTML differs")
    args = parser.parse_args()
    stale = []
    for name, title in TITLES.items():
        target = ROOT / "docs" / f"{name}.html"
        expected = render(name, title)
        if args.check:
            if not target.exists() or target.read_text(encoding="utf-8") != expected:
                stale.append(str(target.relative_to(ROOT)))
        else:
            target.write_text(expected, encoding="utf-8")
            print(f"Generated {target.relative_to(ROOT)}")
    if stale:
        raise SystemExit("Rebuild documents: " + ", ".join(stale))
    if args.check:
        print("Generated documents are up to date")


if __name__ == "__main__":
    main()
