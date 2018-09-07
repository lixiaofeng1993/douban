# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import time
import redis
from scrapy.exceptions import DropItem
from scrapy import log


class DoubanPipeline(object):
    def __init__(self):
        self.check = 0

    def process_item(self, item, spider):
        # 判断如果没有本科人数字段，则丢弃该item
        if spider.name == 'movie_spider':

            if not item.get('img'):
                raise DropItem('缺少字段：{}'.format('img'))
            # 判断如果没有研究生人数字段，则丢弃该item
            if not item.get('movieName'):
                raise DropItem('缺少字段：{}'.format('movieName'))
            if item['mark'] == '1':
                if not item.get('also_called'):
                    item['also_called'] = '无'
                if not item.get('movie_type'):
                    item['movie_type'] = '无'
                if not item.get('data_duration'):
                    item['data_duration'] = '无'
                if item.get('movie_type').strip() == '纪录片':
                    item['data_actors'] = '无'
            return item
        if spider.name == 'book_spider':
            if item['mark'] == '1':
                if not item.get('book_party'):
                    item['book_party'] = '无'
                if not item.get('book_original_name'):
                    item['book_original_name'] = '无'
                if not item.get('book_translator'):
                    item['book_translator'] = '无'
                if not item.get('book_series'):
                    item['book_series'] = '无'
                if not item.get('introduction'):
                    item['introduction'] = '无'
                if not item.get('book_binding'):
                    item['book_binding'] = '无'
                if not item.get('book_score'):
                    item['book_score'] = '无'
                if not item.get('data_number'):
                    item['data_number'] = '无'
                if not item.get('book_price'):
                    item['book_price'] = '无'
                if not item.get('book_author'):
                    item['book_author'] = '无'
                if not item.get('book_number'):
                    item['book_number'] = '无'
                if not item.get('book_publication'):
                    item['book_publication'] = '无'
                if not item.get('book_press'):
                    item['book_press'] = '无'
            return item
        if spider.name == 'music_spider':
            if item['mark'] == '1':
                if not item.get('introduction'):
                    item['introduction'] = '无'
                if not item.get('music_Other'):
                    item['music_Other'] = '无'
                if not item.get('music_ISRC'):
                    item['music_ISRC'] = '无'
                if not item.get('music_schools'):
                    item['music_schools'] = '无'
                if not item.get('music_code'):
                    item['music_code'] = '无'
                if not item.get('music_number'):
                    item['music_number'] = '无'
                if not item.get('music_release'):
                    item['music_release'] = '无'
                if not item.get('music_type'):
                    item['music_type'] = '无'
                if not item.get('music_medium'):
                    item['music_medium'] = '无'
                if not item.get('music_publisher'):
                    item['music_publisher'] = '无'
                if not item.get('music_performer'):
                    item['music_performer'] = '无'
            return item


class RedisPipeline(object):
    def __init__(self):
        self.r = redis.Redis(host='localhost', port=6379)

    def process_item(self, item, spider):
        if spider.name == 'u6':
            self.r.wait(item['website'], timeout=10)
            self.r.sadd(spider.name, item['movieName'])
            return item


class MysqlPipeline(object):
    def __init__(self):
        """"初始化mysql链接和游标对象"""
        self.conn = None
        self.cur = None
        self.movies = False
        self.commentary = False
        self.states = []

    def open_spider(self, spider):
        """"初始化mysql链接"""
        self.conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='123456',
            db='douban',
            charset='utf8mb4',
        )
        # 初始化游标对象
        self.cur = self.conn.cursor()
        if spider.name == 'movie_spider':
            self.delete_data('movieId', 'movie_home')
            self.delete_data('movieId', 'movie_info')
            self.delete_data('movieId', 'movie_comment')
        if spider.name == 'book_spider':
            self.delete_data('book_id', 'book_home')
            self.delete_data('book_id', 'book_info')
            self.delete_data('book_id', 'book_comment')
        if spider.name == 'music_spider':
            self.delete_data('music_id', 'music_home')
            self.delete_data('music_id', 'music_info')
            self.delete_data('music_id', 'music_comment')

    def delete_data(self, field, table):
        """在保存爬取数据前,清空库   递归清空"""
        sql = 'select {} from {}'.format(field, table)
        self.cur.execute(sql)
        if self.cur.fetchone():
            sql = 'delete from {}'.format(table)
            self.cur.execute(sql)
            self.conn.commit()
            time.sleep(1)
            self.delete_data(field, table)
        else:
            log.msg('{}, 数据库初始化完成!'.format(table))

    def check_data(self, field, table):
        sql = 'select {} from {}'.format(field, table)
        self.cur.execute(sql)
        self.conn.commit()
        s = self.cur.fetchall()
        id_list = []
        # 判断数据是否已经存在
        for i in range(len(s)):
            for j in s[i]:
                id_list.append(j)
        return set(id_list)

    def process_item(self, item, spider):
        if spider.name == 'movie_spider':
            if item['mark'] == '1':
                sql = 'insert into `movie_info`(`movieName`, `movieId`, `img`,`info_website`,`data_score`, ' \
                      '`data_duration`, `data_release`, `data_director`, `data_actors`, `data_region`, `data_attrs`, ' \
                      '`data_number`, `introduction`, `movie_type`, `movie_language`, `also_called`, `movie_ranking`, ' \
                      '`comment_website`) values ' \
                      '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                self.cur.execute(sql, (item['movieName'], item['movieId'], item['img'], item['info_website'],
                                       item['data_score'], item['data_duration'], item['data_release'],
                                       item['data_director'], item['data_actors'], item['data_region'],
                                       item['data_attrs'], item['data_number'], item['introduction'],
                                       item['movie_type'],
                                       item['movie_language'], item['also_called'], item['movie_ranking'],
                                       item['comment_website']))
                self.conn.commit()
                log.msg('movie_info  {},保存成功!'.format(item['movieName']))
            if item['mark'] == '2':
                # 处理item['states'], 显示成中文
                if item['states']:
                    self.states = self.format_states(item['states'])
                for i in range(len(item['contentTime'])):
                    sql = 'insert into `movie_comment`(`movieName`, `movieId`, `netName`,`states`,`content`, ' \
                          '`contentTime`, `comment_website`, `netImg`) values ' \
                          '(%s, %s, %s, %s, %s, %s, %s, %s)'
                    self.cur.execute(sql, (item['movieName'], item['movieId'], item['netName'][i], self.states[i],
                                           item['content'][i], item['contentTime'][i].strip(), item['comment_website'],
                                           item['netImg'][i]))
                id_list = self.check_data('movieId', 'movie_home')
                if int(item['movieId']) not in id_list:
                    sql = 'insert into `movie_home`(`movieName`, `movieId`, `praise_rate`,`general_rate`,' \
                          '`negative_rate`, `comment_website`, `img`, `info_website`) values ' \
                          '(%s, %s, %s, %s, %s, %s, %s, %s)'
                    self.cur.execute(sql,
                                     (item['movieName'], item['movieId'], item['praise_rate'], item['general_rate'],
                                      item['negative_rate'], item['comment_website'], item['img'],
                                      item['info_website']))
                self.conn.commit()
                log.msg('movie_comment, movie_home  {},保存成功!'.format(item['movieName']))
                return item
        if spider.name == 'book_spider':
            # print(item)
            if item['mark'] == '1':
                sql = 'insert into `book_info`(`book_name`, `book_id`, `img`,`book_author`,`book_press`, ' \
                      '`book_party`, `book_original_name`, `book_translator`, `book_publication`, `book_number`, ' \
                      '`book_price`, `book_binding`, `book_series`, `book_score`, `book_info_website`, ' \
                      '`book_comment_website`, `data_number`, `introduction`) values ' \
                      '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                self.cur.execute(sql, (item['book_name'], item['book_id'], item['img'], item['book_author'],
                                       item['book_press'], item['book_party'], item['book_original_name'],
                                       item['book_translator'], item['book_publication'], item['book_number'],
                                       item['book_price'], item['book_binding'], item['book_series'],
                                       item['book_score'],
                                       item['book_info_website'], item['book_comment_website'], item['data_number'],
                                       item['introduction']))
                self.conn.commit()
                log.msg('book_info  {},保存成功!'.format(item['book_name']))
            if item['mark'] == '2':
                # 处理item['states'], 显示成中文
                if item['states']:
                    self.states = self.format_states(item['states'])
                for i in range(len(item['contentTime'])):
                    sql = 'insert into `book_comment`(`book_name`, `book_id`, `net_name`,`states`,`content`, ' \
                          '`contentTime`, `book_comment_website`, `net_img`) values ' \
                          '(%s, %s, %s, %s, %s, %s, %s, %s)'
                    self.cur.execute(sql, (item['book_name'], item['book_id'], item['net_name'][i], self.states[i],
                                           item['content'][i], item['contentTime'][i].strip(),
                                           item['book_comment_website'], item['net_img'][i]))
                id_list = self.check_data('book_id', 'book_home')
                if int(item['book_id']) not in id_list:
                    sql = 'insert into `book_home`(`book_name`, `book_id`, `book_comment_website`, `img`, ' \
                          '`book_info_website`) values (%s, %s, %s, %s, %s)'
                    self.cur.execute(sql,
                                     (item['book_name'], item['book_id'], item['book_comment_website'], item['img'],
                                      item['book_info_website']))
                self.conn.commit()
                log.msg('book_comment, book_home  {},保存成功!'.format(item['book_name']))
                return item
        if spider.name == 'music_spider':
            # print(item)
            if item['mark'] == '1':
                sql = 'insert into `music_info`(`music_name`, `music_id`, `img`,`music_performer`,`music_schools`, ' \
                      '`music_type`, `music_medium`, `music_release`, `music_publisher`, `music_number`, ' \
                      '`music_code`, `music_Other`, `music_ISRC`, `music_score`, `music_info_website`, ' \
                      '`music_comment_website`, `data_number`, `introduction`, `song`) values ' \
                      '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                self.cur.execute(sql, (item['music_name'], item['music_id'], item['img'], item['music_performer'],
                                       item['music_schools'], item['music_type'], item['music_medium'],
                                       item['music_release'], item['music_publisher'], item['music_number'],
                                       item['music_code'], item['music_Other'], item['music_ISRC'], item['music_score'],
                                       item['music_info_website'], item['music_comment_website'], item['data_number'],
                                       item['introduction'], item['song']))
                id_list = self.check_data('music_id', 'music_home')
                if int(item['music_id']) not in id_list:
                    sql = 'insert into `music_home`(`music_name`, `music_id`, `music_comment_website`, `img`, ' \
                          '`music_info_website`) values (%s, %s, %s, %s, %s)'
                    self.cur.execute(sql,
                                     (item['music_name'], item['music_id'], item['music_comment_website'], item['img'],
                                      item['music_info_website']))
                self.conn.commit()
                log.msg('music_info, music_home  {},保存成功!'.format(item['music_name']))
            if item['mark'] == '2':
                # 处理item['states'], 显示成中文
                if item['states']:
                    self.states = self.format_states(item['states'])
                for i in range(len(item['contentTime'])):
                    sql = 'insert into `music_comment`(`music_name`, `music_id`, `net_name`,`states`,`content`, ' \
                          '`contentTime`, `music_comment_website`, `net_img`) values ' \
                          '(%s, %s, %s, %s, %s, %s, %s, %s)'
                    self.cur.execute(sql, (item['music_name'], item['music_id'], item['net_name'][i], self.states[i],
                                           item['content'][i], item['contentTime'][i].strip(),
                                           item['music_comment_website'], item['net_img'][i]))

                self.conn.commit()
                log.msg('music_comment {},保存成功!'.format(item['music_name']))
                return item

    def format_states(self, states_list):

        for i in states_list:
            if '10' in i:
                i = '一星级'
            elif '15' in i:
                i = '一星半'
            elif '20' in i:
                i = '二星级'
            elif '25' in i:
                i = '二星半'
            elif '30' in i:
                i = '三星级'
            elif '35' in i:
                i = '三星半'
            elif '40' in i:
                i = '四星级'
            elif '45' in i:
                i = '四星半'
            elif '50' in i:
                i = '五星级'
            else:
                i = '三星半'
            self.states.append(i)
        return self.states
