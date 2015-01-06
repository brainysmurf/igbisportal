import scrapy
from portal.db import Database, DBSession
try:
    import redis
except ImportError:
    pass
import scrapy

class AbstractPipeline(object):
    KEY = 'spider.path'   # Let the spider determine the key used
    BLANK_TOLERANCE = 0
    COUNTS_AS_BLANKS = []

    def open_spider(self, spider):
        """
        Create connection to redis database and set up the key for the set
        """
        self.database_open()
        self.spider = spider
        if self.KEY.startswith('spider.'):
            _, attr = self.KEY.split('.')   # TODO: What about spider.blah.attr
            self.key = getattr(spider, attr)
        else:
            self.key = self.KEY

    def dropit(self, message):
        self.spider.warning(message)
        raise scrapy.exceptions.DropItem(message)

    def not_allowed(self, message):
        return {}

    def allow_this_spider(self, spider):
        """
        Mechanism that lets us exclude processing through pipelines by convention, i.e. by name
        """
        return self.__class__.__name__.startswith(spider.name)

    def process_item(self, item, spider):
        """
        Objective:  To stop the spider as soon as we can, but also take into account possible duplicate items
                    or dirty data (blanks throughout)
                    We can't assume data we have no control over will be solid :)
        """
        if self.allow_this_spider(spider):
            if item:
                # First check for any data that seems blank.
                blank_fields = [b for b in item.values() if not b or b in self.COUNTS_AS_BLANKS]
                if len(blank_fields) >= self.BLANK_TOLERANCE:
                    return self.dropit("Dropping item which has {} fields that are blank {}".format(len(blank_fields), item))

                exists = self.database_ismember(self.key, item)
                if not exists:
                    self.spider.warning("{} is adding to database".format(self.__class__.__name__))
                    self.database_add(self.key, item)
                    return item
                else:
                    self.spider.warning("NOT adding to database")
                    self.dropit("We already have this one {}".format(item))    
            else:
                return item
        else:
            self.spider.warning("This pipeline {} is not allowed to run with spider {}".format(self.__class__.__name__, spider.name))
            return item


class RedisSetPipeline(AbstractPipeline):
    def database_open(self):
        self.redis = redis.Redis('localhost')

    def database_ismember(self, key, item):
        return self.redis.sismember(key, item)

    def database_add(self, key, item):
        return self.redis.sadd(self.key, item)

class PostgresPipeline(AbstractPipeline):
    def database_open(self):
        self.database = Database()
        self.DBSession = DBSession

    def database_ismember(self, key, item):
        return False
