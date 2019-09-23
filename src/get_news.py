#!/usr/bin/env python3
# coding: utf8
# PythonでRSSからニュースを取得しSQLite3DBに保存する。
# 第1引数: 必須。RSS URL
# 第2引数: 任意。DB出力ディレクトリパス（デフォルト＝カレントディレクトリ）
import feedparser
import sys
import os
from mod import get_html
from mod import NewsDb
from mod import NewsImagesDb
from mod import HtmlContentExtractor
from mod import DateTimeString

if len(sys.argv) < 2:
    raise Error('第1引数にRSSのURLを指定してください。')
    exit()
rss = sys.argv[1]
db_dir_path = sys.argv[2] if (2 < len(sys.argv)) else os.getcwd()

entries = feedparser.parse(rss).entries
news_db = NewsDb.NewsDb(db_dir_path)
#extractor = HtmlContentExtractor.HtmlContentExtractor()
extractor = HtmlContentExtractor.HtmlContentExtractor(option={"threshold":50})
dtcnv = DateTimeString.DateTimeString()
for entry in entries:
    # RDF形式のときpublishedがない。代わりにupdatedがある
#    published = get_iso_8601(entry.published)
#    published = get_iso_8601(entry.published if hasattr(entry, 'published') else entry.updated)
    published = dtcnv.convert_utc((
            entry.published 
            if hasattr(entry, 'published') 
            else entry.updated)
        ).strftime('%Y-%m-%dT%H:%M:%SZ')
    url = entry.link
    title = entry.title
    body = extractor.extract(get_html.get_html(url))
    news_db.append_news(published, url, title, body);
#    break; # HTML取得を1件だけでやめる
news_db.insert();

