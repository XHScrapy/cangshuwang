# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import csv
import os
from .items import BookItem, ChapterItem


class CangshuwangPipeline(object):
    def process_item(self, item, spider):
        return item


class CSVPipeline(object):
    def __init__(self):
        #csv文件的位置,无需事先创建
        store_file = "book.csv"
        #打开(创建)文件
        self.file = open(store_file, 'a+', encoding='utf-8')
        #csv写法
        self.writer = csv.writer(self.file)

    def process_item(self, item, spider):
        if not isinstance(item, BookItem):
            return item
        self.writer.writerow([item["name"], item["author"], item["type"], item["label"]])
        return item

    def close_spider(self, spider):
        #关闭爬虫时顺便将文件保存退出
        self.file.close()


class ChapterPipeline(object):
    m_BookDir = "/home/duoyi/spider/cangshuwang/"

    def process_item(self, item, spider):
        if not isinstance(item, ChapterItem):
            return item
        book_dir = os.path.join(self.m_BookDir, item["book"])
        if not os.path.exists(book_dir):
            os.makedirs(book_dir)
        chapter_file = os.path.join(book_dir, item["name"])
        with open(chapter_file, "w", encoding="utf-8") as f:
            f.write(item["content"])
        # print(f"{item['book']}/{item['name']}")
        return item
