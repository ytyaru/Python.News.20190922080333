import sqlite3
import os
import operator

class NewsDb:
    def __init__(self, root):
        path = os.path.join(root, 'news.db')
        self.conn = sqlite3.connect(path)
        self.create_table()
        self.news = []
    def __del__(self): self.conn.close()
    def create_table(self):    
        cur = self.conn.cursor()
        cur.executescript(self.__create_table_sql())
    def __create_table_sql(self):
        return '''
create table if not exists news(
  id         integer primary key,
  published  text, 
  url        text,
  title      text,
  body       text, -- URL先から本文だけを抽出したプレーンテキスト
  UNIQUE(published,url) -- 記事の一意確認
);
create index if not exists idx_news on 
  news(published desc, id desc, url, title);
create table if not exists sources(
  id       integer primary key,
  domain   text, -- URLのドメイン名
  name     text, -- 情報源名
  created  text  -- 登録日時（同一ドメイン名が複数あるとき新しいほうを表示する）
);
create index if not exists idx_sources on 
  sources(domain, created desc, id desc, name);
'''
    def __get_latest_sql(self): return '''
with 
  latest(max_published) as (
    select max(published) max_published from news
  )
select 
  published as latest_published, 
  max(id) as latest_id 
from news,latest
where news.published=latest.max_published;
'''
    def __insert_sql(self): 
        return 'insert or fail into news(published,url,title,body) values(?,?,?,?)'
    def append_news(self, published, url, title, body):
        self.news.append((published, url, title, body))
    def insert(self):
        if 0 == len(self.news): return
        try:
            self.news = sorted(self.news, key=operator.itemgetter(1)) # 第2キー: URL昇順
            self.news = sorted(self.news, key=operator.itemgetter(0), reverse=True) # 第1キー: 公開日時降順
            self.conn.cursor().executemany(self.__insert_sql(), self.news)
            self.conn.commit()
        except sqlite3.IntegrityError as err_sql_integ:
            import traceback
            import sys
            msg = str(err_sql_integ.with_traceback(sys.exc_info()[2])).lower() # UNIQUE constraint failed: news.published, news.url
            # DB既存と重複した時点で中断する
            if ('UNIQUE'.lower() in msg and 'published' in msg and 'url' in msg): pass
            # それ以外ならエラー表示＆ロールバックする
            else: 
                traceback.print_exc()
                self.conn.rollback() 
        except: # それ以外
            import traceback
            traceback.print_exc()
            self.conn.rollback() # ロールバックする
        finally: self.news.clear()

