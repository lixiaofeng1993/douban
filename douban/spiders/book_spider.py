# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import BooksItem, BookCommentItem
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from scrapy import log


class BookSpiderSpider(CrawlSpider):
# class BookSpiderSpider(scrapy.Spider):
    name = 'book_spider'
    # allowed_domains = ['https://book.douban.com/']
    start_urls = ['https://book.douban.com/top250']
    # start_urls = ['https://book.douban.com/subject/3156549/']
    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 3,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, sdch",
            'Accept-Language': "zh-CN,zh;q=0.8",
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Host': "book.douban.com",
            'Pragma': "no-cache",
            'Upgrade-Insecure-Requests': "1",
        }
    }
    rules = (
        Rule(LinkExtractor(allow=r'^https://book.douban.com/subject/\d+/$'), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(BookSpiderSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.PhantomJS()

    def __del__(self):
        self.driver.close()

    def parse_item(self, response):
    # def parse(self, response):
        response = response.replace(body=response.body.decode("utf-8").replace('\t', '').replace('\n', ''))
        info_url = response.url
        log.msg('url列表:{}'.format(info_url))
        item = self.selenium_js(info_url)
        url_list = info_url.split('/')
        for i in url_list:
            if i == '':
                url_list.remove(i)
        # 书籍id
        item['book_id'] = url_list[-1]
        book_introduction = response.xpath('//*[@id="link-report"]/span[2]/div/div/p/text()').extract()
        introduction = ''
        for i in book_introduction:
            introduction += i.strip().replace('\n', '').replace('\t', '')
        if not introduction:
            book_introduction = response.xpath('//*[@id="link-report"]/div[1]/div/p/text()').extract()
            for i in book_introduction:
                introduction += i.strip().replace('\n', '').replace('\t', '')
        # 书籍简介
        item['introduction'] = introduction
        # 书籍信息网址
        book_info_website = 'http://longlove.wang/book/{}/'.format(item['book_id'])
        # book_info_website = 'http://localhost:8888/book/{}/'.format(item['book_id'])
        item['book_info_website'] = book_info_website
        # 书籍名称
        item['book_name'] = response.xpath('//*[@id="wrapper"]/h1/span/text()').extract()
        # 封面
        item['img'] = response.xpath('//*[@id="mainpic"]/a/img/@src').extract()
        # 评分
        book_score = response.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()').extract()
        for i in book_score:
            item['book_score'] = i.strip()
        douban_url = 'https://book.douban.com/subject/{}/comments/'.format(item['book_id'])
        comment_url = 'http://longlove.wang/book/{}/comments'.format(item['book_id'])
        # comment_url = 'http://localhost:8888/book/{}/comments'.format(item['book_id'])
        # 书籍短评网址
        item['book_comment_website'] = comment_url
        request = scrapy.Request(douban_url, callback=self.parse_comment)
        # 标记
        item['mark'] = '1'
        # log.msg(item)
        request.meta['book_id'] = item['book_id']
        request.meta['book_name'] = item['book_name']
        request.meta['book_comment_website'] = item['book_comment_website']
        request.meta['img'] = item['img']
        request.meta['book_info_website'] = item['book_info_website']
        yield request
        yield item

    def parse_comment(self, response):
        response = response.replace(body=response.body.decode("utf-8").replace('\t', '').replace('\n', ''))
        item_comment = BookCommentItem()
        info = response.xpath('//*[@id="comments"]')[0]
        # 短评内容
        content_list = info.xpath('./ul/li/div[2]/p/text()').extract()
        content_format = []
        for content in content_list:
            content = content.strip().replace('\n', '').replace('\t', '').replace('\r', '')
            if content != '':
                content_format.append(content)
        item_comment['content'] = content_format
        # 网友名
        item_comment['net_name'] = info.xpath('./ul/li/div[2]/h3/span[2]/a/text()').extract()
        # 评论时间
        item_comment['contentTime'] = info.xpath('./ul/li/div[2]/h3/span[2]/span[2]/text()').extract()
        # 星级
        item_comment['states'] = info.xpath('./ul/li/div[2]/h3/span[2]/span[1]/@class').extract()
        # 头像
        item_comment['net_img'] = info.xpath('./ul/li/div[1]/a/img/@src').extract()
        # 书籍id
        item_comment['book_id'] = response.meta['book_id']
        # 书籍名称
        item_comment['book_name'] = response.meta['book_name']
        # 短评网址
        item_comment['book_comment_website'] = response.meta['book_comment_website']
        # 海报
        item_comment['img'] = response.meta['img']
        # 书籍信息网址
        item_comment['book_info_website'] = response.meta['book_info_website']
        # 标记
        item_comment['mark'] = '2'
        # log.msg('短评:{}'.format(item_comment))
        yield item_comment

    def selenium_js(self, info_url):
        item = BooksItem()
        self.driver.get(info_url)
        self.driver.implicitly_wait(10)
        locator = ('xpath', '//*[@id="info"]')
        time.sleep(3)
        data = self.get_text(locator)
        data_list = data.split('\n')
        for d in data_list:
            if d != '':
                j = d.split(':', 1)
                if '作者' in j[0]:
                    item['book_author'] = j[1]
                elif '出版社' in j:
                    item['book_press'] = j[1]
                elif '原作名' in j:
                    item['book_original_name'] = j[1]
                elif '副标题' in j:
                    item['book_original_name'] = j[1]
                elif '译者' in j:
                    item['book_translator'] = j[1]
                elif '出版年' in j:
                    item['book_publication'] = j[1]
                elif '页数' in j:
                    item['book_number'] = j[1]
                elif '定价' in j:
                    item['book_price'] = j[1]
                elif '装帧' in j:
                    item['book_binding'] = j[1]
                elif '丛书' in j:
                    item['book_series'] = j[1]
                elif '出品方' in j:
                    item['book_party'] = j[1]
                else:
                    pass
        # 评论人数
        locator = ('xpath', '//*[@id="interest_sectl"]/div/div[2]/div/div[2]/span/a/span')
        data = self.get_text(locator)
        item['data_number'] = data
        return item

    def find_element(self, locator, timeout=5):
        """重写元素定位方法"""
        try:
            element = WebDriverWait(self.driver, timeout, 1).until(EC.presence_of_element_located(locator))
            return element
        except:
            return ""

    def get_text(self, locator):
        """获取文本"""
        element = self.find_element(locator)
        if element:
            return element.text
        else:
            return ''
