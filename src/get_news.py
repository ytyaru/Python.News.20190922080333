#!/usr/bin/env python3
# coding: utf8
# PythonでRSSからニュースを取得しSQLite3DBに保存する。
# 第1引数: 必須。RSS URL
# 第2引数: 任意。DB出力ディレクトリパス（デフォルト＝カレントディレクトリ）
import feedparser
import datetime
import time
import sys
import os
from mod import get_html
from mod import NewsDb
from mod import NewsImagesDb
from mod import HtmlContentExtractor

# RSS/Atomの日付テキストをISO-8601にして返す
def get_iso_8601(date_str):
    try: return (datetime.datetime
            .strptime(date_str, 
                      '%a, %d %b %Y %H:%M:%S %z')
            .strftime('%Y-%m-%dT%H:%M:%SZ%z'))
    except ValueError as ve: 
        return (datetime.datetime
            .strptime(date_str, 
                      '%Y-%m-%dT%H:%M:%SZ%z')
            .strftime('%Y-%m-%dT%H:%M:%SZ%z'))

if len(sys.argv) < 2:
    raise Error('第1引数にRSSのURLを指定してください。')
    exit()
rss = sys.argv[1]
db_dir_path = sys.argv[2] if (2 < len(sys.argv)) else os.getcwd()

entries = feedparser.parse(rss).entries
news_db = NewsDb.NewsDb(db_dir_path)
extractor = HtmlContentExtractor.HtmlContentExtractor()
for entry in entries:
    published = get_iso_8601(entry.published)
    url = entry.link
    title = entry.title
    body = extractor.extract(get_html.get_html(url))
    news_db.append_news(published, url, title, body);
    break; # HTML取得を1件だけでやめる
news_db.insert();

