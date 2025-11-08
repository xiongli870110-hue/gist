import feedparser
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
import os

# 配置
RSS_URL = "https://bloombergnew.buzzing.cc/feed.xml"
OUTPUT_HTML = "/tmp/navpage/rss_news.html"

def check_url_accessible(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"无法访问 URL {url}: {e}")
        return False

def fetch_rss_and_generate_html(max_retries=3, retry_delay=5):
    for attempt in range(max_retries):
        try:
            if not check_url_accessible(RSS_URL):
                print(f"错误：无法访问 RSS 提要 URL {RSS_URL}")
                return
            feed = feedparser.parse(RSS_URL)
            if feed.bozo:
                print(f"错误：无法解析 RSS 提要，原因：{feed.bozo_exception}")
                return
            entries = feed.entries[:10]
            if not entries:
                print("没有获取到消息（可能是提要为空或受限制）")
                return

            # 构建 HTML 内容
            html = "<!DOCTYPE html><html lang='zh'><head><meta charset='UTF-8'>"
            html += "<title>彭博社新闻</title>"
            html += "<style>body{font-family:sans-serif;background:#f4f6f9;padding:2rem;}h2{margin-top:2rem;}a{color:#0077cc;text-decoration:none;}hr{margin:1.5rem 0;}</style>"
            html += "</head><body>"
            html += f"<h1>彭博社最新十条消息（{datetime.now().strftime('%Y-%m-%d %H:%M')}）</h1>"

            for i, entry in enumerate(entries, 1):
                html += f"<h2>{i}. {entry.get('title', '无标题')}</h2>"
                html += f"<p><strong>发布时间：</strong>{entry.get('published', '未知时间')}</p>"
                html += f"<p><strong>摘要：</strong>{entry.get('summary', '无内容')}</p>"
                html += f"<p><a href='{entry.get('link', '#')}' target='_blank'>阅读全文</a></p>"
                html += "<hr>"

            html += "</body></html>"

            os.makedirs(os.path.dirname(OUTPUT_HTML), exist_ok=True)
            with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
                f.write(html)

            print(f"✅ 已生成 HTML：{OUTPUT_HTML}")
            return
        except Exception as e:
            print(f"尝试 {attempt + 1}/{max_retries} 失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            continue
    print(f"错误：在 {max_retries} 次尝试后仍无法获取 RSS 提要")

if __name__ == "__main__":
    fetch_rss_and_generate_html()
