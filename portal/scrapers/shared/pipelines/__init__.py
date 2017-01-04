import scrapy
from portal.db import Database, DBSession
try:
    import redis
except ImportError:
    pass
import scrapy

class RedisSetPipeline():
    def open_spider(self, spider):
        self.redis = redis.Redis('localhost')

    def database_ismember(self, key, item):
        return self.redis.sismember(key, item)

    def database_add(self, key, item):
        return self.redis.sadd(self.key, item)
 
class PostgresPipeline():
    def open_spider(self, spider):
        self.database = Database()
        self.DBSession = DBSession
        self.fake = spider.fake
        if self.fake:
            from faker import Faker
            self.fake = Faker()
        else:
            self.fake = False

    def database_ismember(self, key, item):
        return False
