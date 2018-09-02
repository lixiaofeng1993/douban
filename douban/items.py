# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class MoviesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = Field()
    # 电影名称
    movieName = Field()
    # 电影id
    movieId = Field()
    # 海报地址
    img = Field()
    # 电影信息网址
    info_website = Field()
    # 评分
    data_score = Field()
    # 片长
    data_duration = Field()
    # 上映日期
    data_release = Field()
    # 导演
    data_director = Field()
    # 主演
    data_actors = Field()
    # 制作国家/地区
    data_region = Field()
    # 编剧
    data_attrs = Field()
    # 评论人数
    data_number = Field()
    # 简介
    introduction = Field()
    # 类型
    movie_type = Field()
    # 语言
    movie_language = Field()
    # 又名
    also_called = Field()
    # 排名
    movie_ranking = Field()
    # 短评网址
    comment_website = Field()
    # 标记
    mark = Field()


class MoviesCommentItem(scrapy.Item):
    # 网友名称
    netName = Field()
    # 电影名称
    movieName = Field()
    # 电影id
    movieId = Field()
    # 短评内容
    content = Field()
    # 评论时间
    contentTime = Field()
    # 星级
    states = Field()
    # 好评
    praise_rate = Field()
    # 一般
    general_rate = Field()
    # 差评
    negative_rate = Field()
    # 网友头像
    netImg = Field()
    # 短评网址
    comment_website = Field()
    # 海报
    img = Field()
    # 电影信息网址
    info_website = Field()
    # 电影网址
    movie_website = Field()
    # 标记
    mark = Field()


class BooksItem(scrapy.Item):
    # 书名
    book_name = Field()
    # 书籍id
    book_id = Field()
    # 封面
    img = Field()
    # 作者*
    book_author = Field()
    # 出版社*
    book_press = Field()
    # 出品方
    book_party = Field()
    # 原作名
    book_original_name = Field()
    # 译者
    book_translator = Field()
    # 出版年*
    book_publication = Field()
    # 页数*
    book_number = Field()
    # 定价*
    book_price = Field()
    # 装帧*
    book_binding = Field()
    # 丛书
    book_series = Field()
    # 评分
    book_score = Field()
    # 书籍信息网址
    book_info_website = Field()
    # 书籍短评网址
    book_comment_website = Field()
    # 评论人数
    data_number = Field()
    # 标记
    mark = Field()
    # 简介
    introduction = Field()


class BookCommentItem(scrapy.Item):
    # 网友名称
    net_name = Field()
    # 书名
    book_name = Field()
    # 书籍id
    book_id = Field()
    # 封面
    img = Field()
    # 短评内容
    content = Field()
    # 评论时间
    contentTime = Field()
    # 星级
    states = Field()
    # 网友头像
    net_img = Field()
    # 短评网址
    book_comment_website = Field()
    # 书籍信息网址
    book_info_website = Field()
    # 书籍网址
    book_website = Field()
    # 标记
    mark = Field()


class MusicsItem(scrapy.Item):
    # 音乐名
    music_name = Field()
    # 音乐id
    music_id = Field()
    # 封面
    img = Field()
    # 表演者
    music_performer = Field()
    # 流派
    music_schools = Field()
    # 专辑类型
    music_type = Field()
    # 介质
    music_medium = Field()
    # 发行时间
    music_release = Field()
    # 出版者
    music_publisher = Field()
    # 唱片数
    music_number = Field()
    # 条形码
    music_code = Field()
    # 其他版本
    music_Other = Field()
    # ISRC(中国)
    music_ISRC = Field()
    # 评分
    music_score = Field()
    # 音乐信息网址
    music_info_website = Field()
    # 音乐短评网址
    music_comment_website = Field()
    # 评论人数
    data_number = Field()
    # 标记
    mark = Field()
    # 简介
    introduction = Field()
    # 曲目
    song = Field()


class MusicCommentItem(scrapy.Item):
    # 网友名称
    net_name = Field()
    # 音乐名
    music_name = Field()
    # 音乐id
    music_id = Field()
    # 封面
    img = Field()
    # 短评内容
    content = Field()
    # 评论时间
    contentTime = Field()
    # 星级
    states = Field()
    # 网友头像
    net_img = Field()
    # 短评网址
    music_comment_website = Field()
    # 音乐信息网址
    music_info_website = Field()
    # 音乐网址
    music_website = Field()
    # 标记
    mark = Field()


class WenItem(scrapy.Item):
    wen_name = Field()
    wen_time = Field()
    wen_author = Field()
    wen_comment = Field()