#!/usr/bin/env python3
"""
日股觀光業報表網站建置腳本
- 為 reports/*.html 加上導覽列
- 產生 index.html
- 產生 history.html (限制近 30 期)
"""
import re
import glob
import os

SITE_DIR = os.path.dirname(os.path.abspath(__file__))
# 預設使用 reports 資料夾存放每日報表
REPORTS_DIR = os.path.join(SITE_DIR, "reports")

# 配合新版 HTML 變數風格的導覽列 CSS
NAV_CSS = """
  .site-nav { max-width: 820px; margin: 16px 0 24px; display: flex; gap: 16px; font-size: 13px; }
  .site-nav a { color: var(--ink, #1C2540); text-decoration: none; font-weight: 700; padding: 6px 14px; background: var(--paper, #FFFFFF); border: 1px solid var(--line, #D9DDE6); border-radius: 4px; }
  .site-nav a:hover { background: var(--wash, #F3F5F9); }
  .site-nav a.active { background: var(--ink, #1C2540); color: var(--paper, #FFFFFF); }
"""

def date_from_filename(path):
    # 支援類似 JP-2026-10-14.html 或直接 2026-10-14.html 的格式
    m = re.search(r"(\d{4}-\d{2}-\d{2})\.html$", path)
    return m.group(1) if m else None

def inject_nav(html, latest_href, history_href, active):
    if "</style>" in html and "site-nav" not in html:
        html = html.replace("</style>", NAV_CSS + "</style>", 1)
    
    nav_html = (
        '\n<nav class="site-nav">'
        f'<a href="{latest_href}"{" class=\"active\"" if active=="latest" else ""}>最新報表</a>'
        f'<a href="{history_href}"{" class=\"active\"" if active=="history" else ""}>歷史報表</a>'
        '</nav>\n'
    )
    
    # 這次的 HTML 結構中有 <header>，我們把導覽列插在 header 之後
    if '</header>' in html and 'class="site-nav"' not in html:
        html = html.replace('</header>', '</header>' + nav_html, 1)
    return html

def main():
    report_files = sorted(glob.glob(os.path.join(REPORTS_DIR, "*.html")))
    dated_files = []
    for f in report_files:
        d = date_from_filename(f)
        if d:
            dated_files.append((d, f))
    dated_files.sort(key=lambda x: x[0])

    if not dated_files:
        print("reports/ 內沒有找到符合格式的檔案，中止。")
        return

    # 1) 幫每個報表加上導覽列
    for d, f in dated_files:
        with open(f, "r", encoding="utf-8") as fh:
            html = fh.read()
        if 'class="site-nav"' not in html:
            html = inject_nav(html, latest_href="../index.html", history_href="../history.html", active=None)
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(html)
            print(f"已加上導覽列: reports/{os.path.basename(f)}")

    # 2) 產生 index.html
    latest_date, latest_file = dated_files[-1]
    with open(latest_file, "r", encoding="utf-8") as fh:
        latest_html = fh.read()
    
    index_html = latest_html.replace('href="../index.html"', 'href="index.html"') \
                            .replace('href="../history.html"', 'href="history.html"')
    index_html = index_html.replace('<a href="index.html">最新報表</a>',
                                    '<a href="index.html" class="active">最新報表</a>')
    index_path = os.path.join(SITE_DIR, "index.html")
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(index_html)
    print(f"已產生 index.html（內容 = {latest_date} 報表）")

    # 3) 產生 history.html（限制近 30 期）
    dated_files_desc = list(reversed(dated_files))[:30]
    list_items = "\n".join(
        f'        <li><a href="reports/{os.path.basename(f)}">{d.replace("-", "/")} 觀光業看盤日報</a></li>'
        for d, f in dated_files_desc
    )
    
    # 歷史紀錄頁面樣式完全套用新版報表的色彩變數
    history_html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>日股觀光業看盤日報歷史紀錄</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;900&display=swap" rel="stylesheet">
<style>
  :root{{
    --ink:#1C2540;
    --ink-soft:#4A5370;
    --muted:#7E869C;
    --line:#D9DDE6;
    --wash:#F3F5F9;
    --paper:#FFFFFF;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ background: var(--paper); color: var(--ink); font-family: "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", sans-serif; font-size: 14px; line-height: 1.65; }}
  .page {{ max-width: 820px; margin: 0 auto; padding: 36px 32px 28px; }}
  header {{ display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; border-bottom: 3px solid var(--ink); padding-bottom: 14px; margin-bottom: 22px; }}
  header h1 {{ margin: 0; font-size: 26px; font-weight: 900; letter-spacing: .02em; }}
  .site-nav {{ display: flex; gap: 16px; font-size: 13px; margin-bottom: 22px; }}
  .site-nav a {{ color: var(--ink); text-decoration: none; font-weight: 700; padding: 6px 14px; background: var(--paper); border: 1px solid var(--line); border-radius: 4px; }}
  .site-nav a:hover {{ background: var(--wash); }}
  .site-nav a.active {{ background: var(--ink); color: var(--paper); }}
  ul {{ list-style: none; border: 1px solid var(--line); border-radius: 6px; overflow: hidden; }}
  li {{ border-bottom: 1px solid var(--line); }}
  li:last-child {{ border-bottom: none; }}
  li a {{ display: block; padding: 14px 20px; color: var(--ink); text-decoration: none; font-family: "JetBrains Mono", monospace; font-size: 15px; font-weight: 700; transition: background 0.2s; }}
  li a:hover {{ background: var(--wash); color: var(--ink-soft); }}
  footer {{ margin-top: 24px; padding-top: 12px; border-top: 1px solid var(--line); font-size: 11.5px; color: var(--muted); text-align: center; }}
</style>
</head>
<body>
<div class="page">
  <header>
    <h1>日股觀光業看盤日報歷史紀錄</h1>
  </header>
  <nav class="site-nav">
    <a href="index.html">最新報表</a>
    <a href="history.html" class="active">歷史報表</a>
  </nav>
  <ul>
{list_items}
  </ul>
  <footer>顯示近 {len(dated_files_desc)} 期報表</footer>
</div>
</body>
</html>
"""
    history_path = os.path.join(SITE_DIR, "history.html")
    with open(history_path, "w", encoding="utf-8") as fh:
        fh.write(history_html)
    print(f"已產生 history.html（共 {len(dated_files_desc)} 期）")

if __name__ == "__main__":
    main()