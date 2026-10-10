#!/usr/bin/env python3
"""Search for education app wrong question export capabilities."""
import urllib.request
import urllib.parse
import re
import html

queries = [
    "夸克 错题本 导出 格式 数据 结构化",
    "作业帮 错题本 导出 API 开放平台",
    "小猿搜题 猿题库 错题导出 数据格式",
    "有道 错题本 OCR 导出 学习APP",
    "学而思 错题本 导出 拍照搜题",
]

for q in queries:
    print(f"\n{'='*60}")
    print(f"Query: {q}")
    print(f"{'='*60}")
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            # Extract result titles and snippets
            results = re.findall(
                r'<a[^>]*class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                content, re.DOTALL
            )
            snippets = re.findall(
                r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
                content, re.DOTALL
            )
            for i, (url_match, title) in enumerate(results[:3]):
                title_clean = re.sub(r'<[^>]+>', '', title).strip()
                snip = ""
                if i < len(snippets):
                    snip = re.sub(r'<[^>]+>', '', snippets[i]).strip()
                print(f"  [{i+1}] {title_clean}")
                print(f"      {html.unescape(url_match)}")
                if snip:
                    print(f"      {snip[:200]}")
            if not results:
                print("  (no results)")
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone.")
