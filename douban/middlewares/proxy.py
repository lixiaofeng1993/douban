# !/usr/bin/env python
# coding=utf-8
import random
from urllib.request import _parse_proxy
import requests
from scrapy.exceptions import NotConfigured
from scrapy import log


def reform_url(url):
    # 重组url,返回不带用户名和密码的格式
    proxy_type, *_, hostport = _parse_proxy(url)
    return '{}://{}'.format(proxy_type, hostport)


class RandomProxyMiddleware:
    # 代理的最多失败次数,超过此值,从代理池删除
    max_failed = 3

    def __init__(self, settings):
        # 从设置中获取代理池
        # self.proxies = settings.getlist('PROXIES')
        self.proxies = self.choice_proxies()

    def choice_proxies(self):
        self.proxies = []
        # 1个ip
        url = 'http://piping.mogumiao.com/proxy/api/get_ip_al?appKey=9d5b899f72a34004bc8a30c813b70dc0&count=1&expiryDate=0&format=1&newLine=2'
        # 5个
        # url = 'http://piping.mogumiao.com/proxy/api/get_ip_al?appKey=3a062088f5aa48d8b696819103e7579b&count=5&expiryDate=0&format=1'
        r = requests.get(url)
        # eval() 计算字符串中的有效表达式
        ip_dict = eval(r.text)
        if ip_dict['code'] == '0':
            for i in ip_dict['msg']:
                # 拼接成有效的代理ip
                ip = 'http://' + i['ip'] + ':' + i['port']
                self.proxies.append(ip)
            log.msg(self.proxies)
            if self.proxies:
                # 初始化统计信息，一开始失败次数都是0
                self.stats = {}.fromkeys(map(reform_url, self.proxies), 0)
            return self.proxies
        elif ip_dict['code'] == '3006':
            log.msg(ip_dict['msg'])
            return '-2'
        else:
            log.msg('代理ip接口返回状态码异常...{}'.format(ip_dict['code']))
            return '-1'

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # 如果request.meta中没有设置proxy，则从代理池中随机设置一个，作为本次请求的代理
        if 'proxy' not in request.meta:
            request.meta['proxy'] = random.choice(self.proxies)

    def process_response(self, request, response, spider):
        # 获取当前使用的proxy
        cur_proxy = request.meta['proxy']
        # 判断http code是否大于400，响应是否出错
        if response.status in [301, 302]:
            log.msg('访问被重定向:{}'.format(response))
            return response
        if response.status >= 400:
            # 将该代理的失败次数加1
            self.stats[cur_proxy] += 1
            # 判断该代理的总失败次数是否已经超过最大失败次数
            if self.stats[cur_proxy] >= self.max_failed:
                log.msg('{} 获得一个 {} 返回结果'.format(cur_proxy, response.status))
                # 从代理池中删除该代理
                # if cur_proxy in self.proxies:
                #     self.proxies.remove(cur_proxy)
                for proxy in self.proxies:
                    if reform_url(proxy) == cur_proxy:
                        self.proxies.remove(proxy)
                        break
                log.msg('{} 超过最大失败次数,从代理列表删除'.format(cur_proxy))
            # 将本次请求重新设置一个代理，并返回
            if not self.proxies:
                self.proxies = self.choice_proxies()
                log.msg('超过最大失败次数,代理池为空...再次请求api')
                # return
            request.meta['proxy'] = random.choice(self.proxies)
            return request
        return response

    def process_exception(self, request, exception, spider):
        cur_proxy = request.meta['proxy']
        # 如果出现网络超时或者链接被拒绝，则删除该代理
        if cur_proxy in self.proxies:
            self.proxies.remove(cur_proxy)
        log.msg('{} 代理ip出现错误,从代理列表删除'.format(cur_proxy))
        # 将本次请求重新设置一个d代理并返回
        if not self.proxies:
            self.proxies = self.choice_proxies()
            log.msg('代理ip出现错误,代理池为空...再次请求api')
            # return
        request.meta['proxy'] = random.choice(self.proxies)
        return request
