# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import WenItem


# class DangdangSpider(CrawlSpider):
class DangdangSpider(scrapy.Spider):
    name = 'dangdang'
    # allowed_domains = ['http://bang.dangdang.com/books/']
    # start_urls = ['https://www.jj59.com/jingdianmeiwen']
    # start_urls = ['https://www.jj59.com/jjart/422861.html']
    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 3,
        'DEFAULT_REQUEST_HEADERS': {
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, sdch",
            'accept-language': "zh-CN,zh;q=0.8",
            'Cache-Control': "no-cache",
            'pragma': "no-cache",
            'upgrade-insecure-requests': "1",
            }

    }
    # rules = {
    #     Rule(LinkExtractor(allow='^/jjart/\d+\.html$'), callback='parse_item', follow=True)
    # }

    def start_requests(self):
        for i in range(1,5):
            url = 'https://www.jj59.com/jingdianmeiwen/list_67_{}.html'.format(i)
            request = scrapy.Request(url)
            yield request

    # def parse_item(self, response):
    def parse(self, response):
        url_list = response.xpath('/html/body/div[2]/div[1]/div[2]/ul/li/h3/a/@href').extract()
        for url in url_list:
            url = 'https://www.jj59.com' + url
            request = scrapy.Request(url, callback=self.parse_item)
            yield request

    def parse_item(self, response):
        item = WenItem()
        item['wen_name'] = response.xpath('/html/body/div[2]/div[1]/div[1]/div[2]/h1/text()').extract()
        item['wen_time'] = response.xpath('/html/body/div[2]/div[1]/div[1]/div[3]/text()[1]').extract()
        item['wen_author'] = response.xpath('/html/body/div[2]/div[1]/div[1]/div[3]/a/text()').extract()
        item['wen_comment'] = response.xpath('/html/body/div[2]/div[1]/div[1]/div[4]/p/text()').extract()
        print(item)
