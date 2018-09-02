import faker
from scrapy import log

class RandomUserAgentMiddleware(object):
    """该中间件负责给每个请求随机分配一个user agent"""

    def __init__(self, settings):
        self.faker = faker.Faker()

    @classmethod
    def from_crawler(cls, crawler):
        # 创建一个中间件实例，并返回
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # 设置request头信息内的user-Agent字段
        request.headers['User-Agent'] = self.faker.user_agent()

    def process_response(self, request, response, spider):
        # log.msg(request.headers['User-Agent'])
        return response