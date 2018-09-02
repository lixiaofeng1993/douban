# -*- coding: utf-8 -*-
import scrapy
import time
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor
from ..items import MusicsItem, MusicCommentItem
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from scrapy import log
cookies = {'ll': '"108288"', 'bid': 'mnGmiFyXsLE', 'ps': 'y', '__yadk_uid': 'acZ7lPVoBFwEe9zUuxkinAxWvej2x8K7', '_ga': 'GA1.2.827897887.1520173858', 'ct': 'y', 'gr_user_id': '0e8f7746-0140-4637-8537-9bb1479b5832', '_pk_ref.100001.afe6': '%5B%22%22%2C%22%22%2C1521099189%2C%22https%3A%2F%2Fwww.douban.com%2F%22%5D', '_vwo_uuid_v2': 'D41AEFDAFE3A1CD5BC697DA60910AF62D|c2ce6896173876a294f190fc01198a6e', 'viewed': '"1762969_1403307_7065468_1394549_1394590_1427374_5275059_2995812_1770782_5363767"', 'RT': 'nu', '__utmt': '1', 'dbcl2': '"154238054:cii0KhoERCM"', 'ck': 'WD8J', '_pk_id.100001.afe6': '60929c71e9f86111.1520413476.4.1521104155.1521096971.', '_pk_ses.100001.afe6': '*', 'push_noty_num': '0', 'push_doumail_num': '0', '__utma': '30149280.827897887.1520173858.1521089735.1521094057.40', '__utmb': '30149280.60.10.1521094057', '__utmc': '30149280', '__utmz': '30149280.1521082742.38.16.utmcsr', '__utmv': '30149280.15423', 'ap': '1'}

class MusicSpiderSpider(CrawlSpider):
# class MusicSpiderSpider(scrapy.Spider):
    name = 'music_spider'
    # allowed_domains = ['https://music.douban.com/']
    start_urls = ['https://music.douban.com/top250']
    # start_urls = ['https://music.douban.com/subject/1762969/']
    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 5,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, sdch",
            'Accept-Language': "zh-CN,zh;q=0.8",
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Host': "music.douban.com",
            'Pragma': "no-cache",
            'Upgrade-Insecure-Requests': "1",
            }
    }
    rules = (
            Rule(LinkExtractor(allow=r'^https://music.douban.com/subject/\d+/$'), callback='parse_item', follow=True),
    )

    def __init__(self, *args, **kwargs):
        super(MusicSpiderSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.PhantomJS(executable_path=r'/usr/local/phantomjs/bin/phantomjs')

    def __del__(self):
        self.driver.close()

    def parse_item(self, response):
    # def parse(self, response):
        info_url = response.url
        item = self.selenium_js(info_url)
        url_list = info_url.split('/')
        for i in url_list:
            if i == '':
                url_list.remove(i)
        # 音乐id
        item['music_id'] = url_list[-1]
        # 音乐名称
        item['music_name'] = response.xpath('//*[@id="wrapper"]/h1/span/text()').extract()
        # 封面
        img_list = response.xpath('//*[@id="mainpic"]/span/a/img/@src').extract()
        for i in img_list:
            item['img'] = i.replace('view/subject/m/public', 'lpic')
        # 评分
        item['music_score'] = response.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()').extract()
        music_introduction = response.xpath('//*[@id="link-report"]/span[2]/text()').extract()
        introduction = ''
        for i in music_introduction:
            introduction += i.strip().replace('\n', '').replace('\t', '')
        if not introduction:
            music_introduction = response.xpath('//*[@id="link-report"]/span/text()').extract()
            for i in music_introduction:
                introduction += i.strip().replace('\n', '').replace('\t', '')
        # 简介
        item['introduction'] = introduction
        song_list = response.xpath('//*[@id="content"]/div/div[1]/div[3]/div[3]/div/div/div/text()').extract()
        songs = ''
        for song in song_list:
            songs += song.strip() + ' | '
        if not songs:
            song_list = response.xpath('//*[@id="content"]/div/div[1]/div[3]/div[2]/div/div/div/text()').extract()
            for i in song_list:
                songs += i.strip().replace('\n', '').replace('\t', '') + ' | '
        # 曲目
        item['song'] = songs
        # 音乐信息网址
        music_info_website = 'http://longlove.wang/music/{}/'.format(item['music_id'])
        # music_info_website = 'http://localhost:8888/music/{}/'.format(item['music_id'])
        item['music_info_website'] = music_info_website
        # 音乐短评网址
        douban_url = 'https://music.douban.com/subject/{}/comments/'.format(item['music_id'])
        comment_url = 'http://longlove.wang/music/{}/comments'.format(item['music_id'])
        # comment_url = 'http://localhost:8888/music/{}/comments'.format(item['music_id'])
        item['music_comment_website'] = comment_url
        request = scrapy.Request(douban_url, callback=self.parse_comment)
        # 标记
        item['mark'] = '1'
        # log.msg(item)
        request.meta['music_id'] = item['music_id']
        request.meta['music_name'] = item['music_name']
        request.meta['music_comment_website'] = item['music_comment_website']
        request.meta['img'] = item['img']
        request.meta['music_info_website'] = item['music_info_website']
        yield request
        yield item

    def parse_comment(self, response):
        response = response.replace(body=response.body.decode("utf-8").replace('\t', '').replace('\n', ''))
        item_comment = MusicCommentItem()
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
        # 音乐id
        item_comment['music_id'] = response.meta['music_id']
        # 音乐名称
        item_comment['music_name'] = response.meta['music_name']
        # 短评网址
        item_comment['music_comment_website'] = response.meta['music_comment_website']
        # 海报
        item_comment['img'] = response.meta['img']
        # 音乐信息网址
        item_comment['music_info_website'] = response.meta['music_info_website']
        # 标记
        item_comment['mark'] = '2'
        # log.msg('短评:{}'.format(item_comment))
        yield item_comment

    def selenium_js(self, info_url):
        item = MusicsItem()
        self.driver.get(info_url)
        self.driver.implicitly_wait(10)
        locator = ('xpath', '//*[@id="info"]')
        time.sleep(2)
        data = self.get_text(locator)
        data_list = data.split('\n')
        for d in data_list:
            if d != '':
                j = d.split(':', 1)
                if '表演者' in j[0]:
                    item['music_performer'] = j[1]
                elif '流派' in j:
                    item['music_schools'] = j[1]
                elif '专辑类型' in j:
                    item['music_type'] = j[1]
                elif '介质' in j:
                    item['music_medium'] = j[1]
                elif '发行时间' in j:
                    item['music_release'] = j[1]
                elif '出版者' in j:
                    item['music_publisher'] = j[1]
                elif '唱片数' in j:
                    item['music_number'] = j[1]
                elif '条形码' in j:
                    item['music_code'] = j[1]
                elif 'ISRC(中国)' in j:
                    item['music_ISRC'] = j[1]
                elif '其他版本' in j:
                    item['music_Other'] = j[1]
                else:
                    pass
        # 评论人数
        locator = ('xpath', '//*[@id="interest_sectl"]/div/div[2]/div/div[2]/a/span')
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
