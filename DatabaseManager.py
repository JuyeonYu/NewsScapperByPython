import pymysql


class DatabaseManager:
    def __init__(self, host, id, pw, db_name):
        self.conn = pymysql.connect(host=host, user= id, password=pw, db=db_name,charset='utf8')
        self.curs = self.conn.cursor()

    def insert_test(self, test):
        sql = 'insert into test(test) values(%s)'
        self.curs.execute(sql, test)
        self.conn.commit()

    def insert_latest_news_time_with_keyword(self, time, keyword):
        sql = 'insert into latestNewsTime (time, keyword, searchTime) values(%s, %s) ON DUPLICATE KEY UPDATE time = %s'
        self.curs.execute(sql, (time, keyword, time))
        self.conn.commit()

    def select_latest_news_time_with_keyword(self, keyword):
        sql = 'select time from latestNewsTime where keyword = %s'
        self.curs.execute(sql, keyword)
        self.conn.commit()
        row = self.curs.fetchone()

        if row is None:
            return ''
        else:
            return row[0]

    def insert_scrapped_news(self, title, link, keyword):
        sql = 'insert into scrappedNews(title, link, keyword) values(%s, %s, %s)'
        self.curs.execute(sql, (title, link, keyword))
        self.conn.commit()

    def is_latest_news(self, title):
        sql = 'select EXISTS (select * from latestNews where title=%s) as success'
        self.curs.execute(sql, title)
        self.conn.commit()
        row = self.curs.fetchone()
        return row[0]

    def select_latest_news(self, keyword):
        sql = 'select title from latestNews where keyword = %s'
        self.curs.execute(sql, keyword)
        self.conn.commit()
        row = self.curs.fetchone()

        if row is None:
            return ''
        else:
            return row[0]

    def insert_latest_news(self, keyword, title):
        sql = 'INSERT INTO latestNews(keyword, title) VALUES(%s, %s) ON DUPLICATE KEY UPDATE title = %s'
        self.curs.execute(sql, (keyword, title, title))
        self.conn.commit()
        rows = self.curs.fetchall()
        print(rows)

    def select_sub_keyword(self, keyword):
        sql = 'select sub from subKeyword where main = %s'
        self.curs.execute(sql, keyword)
        self.conn.commit()
        rows = [item[0] for item in self.curs.fetchall()]

        if rows is None:
            return ''
        else:
            return rows