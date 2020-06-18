# -*- coding:utf-8 -*-
'''
@Description: 保存书籍爬取信息，增量式处理
@Author: lamborghini1993
@Date: 2019-08-14 16:21:09
@UpdateDate: 2019-08-14 16:34:32
'''

import yaml

g_BookMgr = None


class BookMgr:
    m_Path = "book.yaml"

    def __init__(self):
        self.m_Info = {}
        with open(self.m_Path, "r", encoding="utf-8") as f:
            self.m_Info = yaml.load(f)

    def __del__(self):
        with open(self.m_Path, "w", encoding="utf-8") as f:
            yaml.dump(self.m_Info, stream=f)

    def has_crawl(self, name: str, chapter_url: str)->bool:
        if name not in self.m_Info:
            return False
        book_info = self.m_Info[name]
        return book_info.get(chapter_url, False)

    def add_book_info(self, name: str, chapter_url: str, status: bool=False):
        book_info = self.m_Info.setdefault(name, {})
        book_info[chapter_url] = status


def GetBookMgr()->BookMgr:
    global g_BookMgr
    if not g_BookMgr:
        g_BookMgr = BookMgr()
    return g_BookMgr
