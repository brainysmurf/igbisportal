# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import redis
import scrapy

class RedisSetPipeline(object):
    KEY = 'spider.path'   # Let the spider determine the key used
    BLANK_TOLERANCE = 0
    COUNTS_AS_BLANKS = []

    def open_spider(self, spider):
        """
        Create connection to redis database and set up the key for the set
        """
        self.redis = redis.Redis('localhost')
        self.spider = spider
        if self.KEY.startswith('spider.'):
            _, attr = self.KEY.split('.')   # TODO: What about spider.blah.attr
            self.key = getattr(spider, attr)
        else:
            self.key = self.KEY

    def dropit(self, message):
        self.spider.dropped += 1
        return scrapy.exceptions.DropItem(message)

    def process_item(self, item, spider):
        """
        Objective:  To stop the spider as soon as we can, but also take into account possible duplicate items
                    or dirty data (blanks throughout)
                    We can't assume data we have no control over will be solid :)
        """
        # First check for any data that seems blank.
        blank_fields = [b for b in item.values() if not b or b in self.COUNTS_AS_BLANKS]
        if len(blank_fields) >= self.BLANK_TOLERANCE:
            return self.dropit("Dropping item which has {} fields that are blank {}".format(len(blank_fields), item))

        exists = self.redis.sismember(self.key, item.tojson)
        if exists == 0:
            self.redis.sadd(self.key, item.tojson)
            return item
        else:
            return self.dropit("We already have this one {} and dropped = {}".format(item, spider.dropped))

class AuditlogPipeline(RedisSetPipeline):
    BLANK_TOLERANCE = 1
    COUNTS_AS_BLANKS = [u'\xa0']
