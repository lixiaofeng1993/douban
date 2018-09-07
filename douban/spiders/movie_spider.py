# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule, CrawlSpider
from ..items import MoviesItem, MoviesCommentItem
from scrapy.linkextractors import LinkExtractor
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from scrapy import log


class MovieSpiderSpider(CrawlSpider):
    name = 'movie_spider'
    # allowed_domains = ['https://movie.douban.com/']
    # start_urls = ['https://movie.douban.com/top250']
    # start_urls = ['https://movie.douban.com/subject/1291828/']
    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 3,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, sdch",
            'Accept-Language': "zh-CN,zh;q=0.8",
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Host': "movie.douban.com",
            'Pragma': "no-cache",
            'Upgrade-Insecure-Requests': "1",
        }
    }
    rules = (
        Rule(LinkExtractor(allow=r'^https://movie.douban.com/subject/\d+/$'), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(MovieSpiderSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.PhantomJS(executable_path=r'D:\phantomjs-2.1.1-windows\bin\phantomjs.exe')

    def __del__(self):
        self.driver.close()

    def start_requests(self):
        for i in range(0, 250, 25):
            url = 'https://movie.douban.com/top250?start={}&filter='.format(i)
            request = scrapy.Request(url)
            yield request

    def parse_item(self, response):
        response = response.replace(body=response.body.decode("utf-8").replace('\t', '').replace('\n', ''))
        info_url = response.url
        log.msg('url列表:{}'.format(info_url))
        item = self.selenium_js(info_url)
        url_list = info_url.split('/')
        for i in url_list:
            if i == '':
                url_list.remove(i)
        # 电影id
        item['movieId'] = url_list[-1]
        info_website = 'http://localhost:8000/movie/{}/'.format(item['movieId'])
        # info_website = 'http://longlove.wang/movie/{}/'.format(item['movieId'])
        # 电影信息网址
        item['info_website'] = info_website
        movie_introduction = response.xpath('//*[@id="link-report"]/span[1]/text()').extract()
        introduction = ''
        for i in movie_introduction:
            introduction += i.strip().replace('\n', '').replace('\t', '')
        if not introduction:
            movie_introduction = response.xpath('//*[@id="link-report"]/span[1]/span/text()').extract()
        for i in movie_introduction:
            introduction += i.strip().replace('\n', '').replace('\t', '')
        # 电影简介
        item['introduction'] = introduction
        # 排名
        item['movie_ranking'] = response.xpath('//*[@id="content"]/div[1]/span[1]/text()').extract()
        img_list = response.xpath('//*[@id="mainpic"]/a/img/@src').extract()
        # 电影名称
        item['movieName'] = response.xpath('//*[@id="content"]/h1/span[1]/text()').extract()
        for img in img_list:
            # 电影海报
            item['img'] = img.replace('.webp', '.jpg')
        # 评分
        data_score = response.xpath('//*[@id="interest_sectl"]/div[1]/div[2]/strong/text()').extract()
        for i in data_score:
            item['data_score'] = i.strip()
        douban_url = 'https://movie.douban.com/subject/{}/comments'.format(item['movieId'])
        comment_url = 'http://localhost:8000/movie/{}/comments'.format(item['movieId'])
        # comment_url = 'http://longlove.wang/movie/{}/comments'.format(item['movieId'])
        request = scrapy.Request(douban_url, callback=self.parse_comment)
        # 短评网址
        item['comment_website'] = comment_url
        item['mark'] = '1'
        # log.msg(item)
        request.meta['movieId'] = item['movieId']
        request.meta['movieName'] = item['movieName']
        request.meta['comment_website'] = item['comment_website']
        request.meta['img'] = item['img']
        request.meta['info_website'] = item['info_website']
        yield request
        yield item

    def parse_comment(self, response):
        response = response.replace(body=response.body.decode("utf-8").replace('\t', '').replace('\n', ''))
        item_comment = MoviesCommentItem()
        # 好评
        item_comment['praise_rate'] = response.xpath('//*[@id="content"]/div/div[1]/div[3]/label[2]/span[2]/text()').extract()
        # 一般
        item_comment['general_rate'] = response.xpath('//*[@id="content"]/div/div[1]/div[3]/label[3]/span[2]/text()').extract()
        # 差评
        item_comment['negative_rate'] = response.xpath('//*[@id="content"]/div/div[1]/div[3]/label[4]/span[2]/text()').extract()
        info = response.xpath('//*[@id="comments"]')[0]
        # 短评内容  //*[@id="comments"]/div[1]/div[2]/p/span/text()
        # item_comment['content'] = info.xpath('./div/div[@class="comment"]/p/span/text()').extract()
        content_list = info.xpath('./div/div[@class="comment"]/p/span/text()').extract()
        content_format = []
        for content in content_list:
            content = content.strip().replace('\n', '').replace('\t', '')
            # print('content', content)
            if content != '':
                content_format.append(content)
        item_comment['content'] = content_format
        # 网友名称
        item_comment['netName'] = info.xpath('./div/div[2]/h3/span[2]/a/text()').extract()
        # 评论时间
        item_comment['contentTime'] = info.xpath('./div/div[2]/h3/span[2]/span[3]/text()').extract()
        # 星级
        item_comment['states'] = info.xpath('./div/div[2]/h3/span[2]/span[2]/@class').extract()
        # 头像
        item_comment['netImg'] = info.xpath('./div/div/a/img/@src').extract()
        # 电影id
        item_comment['movieId'] = response.meta['movieId']
        # 电影名称
        item_comment['movieName'] = response.meta['movieName']
        # 短评网址
        item_comment['comment_website'] = response.meta['comment_website']
        # 海报
        item_comment['img'] = response.meta['img']
        # 电影信息网址
        item_comment['info_website'] = response.meta['info_website']
        # 标记
        item_comment['mark'] = '2'
        # log.msg('短评:{}'.format(item_comment))
        yield item_comment

    def selenium_js(self, info_url):
        item = MoviesItem()
        self.driver.get(info_url)
        self.driver.implicitly_wait(10)
        locator = ('xpath', '//div[@class="subject clearfix"]/div[2]')
        data = self.get_text(locator)
        data_list = data.split('\n')
        for d in data_list:
            if d != '':
                j = d.split(':', 1)
                if '导演' in j[0]:
                    item['data_director'] = j[1]
                elif '编剧' in j:
                    item['data_attrs'] = j[1]
                elif '主演' in j:
                    item['data_actors'] = j[1]
                elif '类型' in j:
                    item['movie_type'] = j[1]
                elif '制片国家/地区' in j:
                    item['data_region'] = j[1]
                elif '语言' in j:
                    item['movie_language'] = j[1]
                elif '上映日期' in j:
                    item['data_release'] = j[1]
                elif '片长' in j:
                    item['data_duration'] = j[1]
                elif '又名' in j:
                    item['also_called'] = j[1]
                else:
                    pass
        # 评论人数
        locator = ('xpath', '//*[@id="interest_sectl"]/div[1]/div[2]/div/div[2]/a/span')
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
