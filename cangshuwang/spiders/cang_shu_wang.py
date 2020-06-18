# -*- coding:utf-8 -*-
'''
@Description: 
    scrapy crawl cang_shu_wang
    scrapy crawl cang_shu_wang -s JOBDIR=Job_8-13
@Author: lamborghini1993
@Date: 2019-08-15 14:21:22
@UpdateDate: 2019-08-19 21:14:40
'''

import scrapy
import re
from ..items import BookItem, ChapterItem


class CangShuWangSpider(scrapy.Spider):
    name = 'cang_shu_wang'
    allowed_domains = ['99lib.net']
    start_urls = ['https://www.99lib.net/book/index.php']
    m_Dir = "/home/duoyi/spider/cangshuwang/"
    m_adv = set()

    def parse(self, response):
        i = 0
        for oType in response.xpath('//*[@id="right"]/ul[1]/li'):
            i += 1
            if i not in range(4, 5):
                continue
            url = oType.xpath('./a/@href').get()
            # book_type = oType.xpath('./a/text()').get()
            # print(f"{book_type} {url}")
            yield response.follow(url, callback=self.parse_books_type, priority=i, meta={"i": i})

    def parse_books_type(self, response):
        i = response.meta["i"]
        for book in response.xpath('//ul[@id="list_box"]/li'):
            book_url = book.xpath('./a/@href').get()
            book_id = int(book_url.split("/")[-2])
            # book_name = book.xpath('./a/@title').get()
            # print(f"book:{book_name} {book_url} {book_id}")
            # book_author = book.xpath('./h4/a/@title').get()
            yield response.follow(book_url, callback=self.parse_book, priority=book_id)
            # return

        next_url = response.xpath('//*[@id="right"]/div[@class="page"]/a[text()="下一页"]/@href').get()
        if next_url:
            yield response.follow(next_url, callback=self.parse_books_type, priority=i, meta={"i": i})

    def parse_book(self, response):
        bookItem = BookItem()
        bookItem["type"] = response.xpath('/html/body/div[2]/a[2]/text()').get().strip()
        book_name = bookItem["name"] = response.xpath('//div[@id="book_info"]/h2/text()').get().strip()
        author = response.xpath('//div[@id="book_info"]/h4[1]/a/text()').get()  # 有作者为空的情况
        author = author.strip() if author else ""
        bookItem["author"] = author
        lstLable = response.xpath('//div[@id="book_info"]/h4[3]/a/text()').getall()
        bookItem["label"] = " ".join(lstLable)
        # yield bookItem

        book_name = re.sub(r'[\/:*?"<>|]', '', book_name).strip()
        book_id = int(response.url.split("/")[-2]) * 100
        i = 0
        for chapter in response.xpath('//*[@id="dir"]/dd'):
            i += 1
            chapter_url = chapter.xpath('./a/@href').get()
            # chapter_name = chapter.xpath('./a/text()').get()
            # chapter_name = re.sub('[\/:*?"<>|]', '', chapter_name).strip()
            chapterItem = ChapterItem()
            chapterItem["book"] = book_name + "_" + author
            # chapterItem["name"] = "%04d_%s.txt" % (i, chapter_name)
            chapterItem["name"] = "%04d.txt" % i
            yield response.follow(chapter_url, callback=self.parse_chapter, meta={"item": chapterItem, "i": i}, priority=book_id - i)
            # return

    def parse_chapter(self, response):
        CRLF = "\r\n" * 2
        chapterItem = response.meta["item"]
        cha_i = response.meta["i"]
        lstTitle = response.xpath('//*[@id="content"]/h2/text()').getall()
        title = "——".join(lstTitle)
        title = "第%s章 %s %s" % (cha_i, title, CRLF)
        parts = response.xpath('//*[@id="content"]/div')
        base = response.xpath('/html/head/meta[5]/@content').get()
        lstOrder = get_order(decode(base))
        i = 0
        bError = False
        content = ""
        for v in lstOrder:
            i += 1
            if v >= len(parts):
                bError = True
                continue
            part = parts[v]

            # 第一种-这种会包含很多广告，需要过滤问题
            # lines = part.xpath('string(.)').get()
            # lines = lines.replace("九九藏书网", "").replace("九九藏书", "").replace("藏书网", "")

            # 第二种-这种会导致很多内嵌标签缺失
            # lstLine = part.xpath('./text()').getall()
            # lines = "".join(lstLine)

            # 第三种-手动排除部分广告内容
            # lstLine = part.xpath('.//text()').getall()
            # lines = ""
            # for line in lstLine:
            #     if not_adv(line):
            #         lines += line

            # content += lines + CRLF

            result = part.xpath('.//*')
            if result:
                for t in result:
                    if not t.root.text:
                        continue
                    info = (t.root.tag, t.root.text)
                    if info not in self.m_adv:
                        self.logger.warning(t.root.tag + "," + t.root.text)
                        self.m_adv.add(info)

        # if bError:
        #     warn_info = f"{response.url} {len(lstOrder)} {len(parts)} {chapterItem['book']}-{cha_i}.txt"
        #     self.logger.warning(warn_info)
        #     title += "本章节有内容缺失，请上 %s 查看" % response.url + CRLF
        # chapterItem["content"] = title + content
        # yield chapterItem


def decode(a):
    my_map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    info = {
        1: '00000',
        2: '0000',
        3: '000',
        4: '00',
        5: '0',
        6: '',
    }
    d = ""
    for t in a:
        if t == "=":
            break
        i = my_map.find(t)
        c = bin(i)[2:]
        d += info[len(c)] + c

    i = 0
    LEN = 8
    b = ""
    while i + LEN <= len(d):
        t = int(d[i:i + LEN], 2)
        b += chr(t)
        i += LEN
    return b


def get_order(s):
    lst = re.split("[A-Z]+%", s)
    lst = list(map(int, lst))
    result = [-1 for _ in range(len(lst))]
    j = 0
    for i, v in enumerate(lst):
        if v < 3:
            result[v] = i
            j += 1
        else:
            result[v - j] = i
            j += 2
    return result


def not_adv(msg: str)->bool:
    if len(msg) > 20:
        return True
    return True
