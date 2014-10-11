# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


# TODO: Make this import dependent on settings
import redis
import scrapy
from db import Database, DBSession  

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
        return scrapy.exceptions.DropItem(message)

    def allow_this_spider(self, spider):
        return self.__class__.__name__.startswith(spider.name)

    def process_item(self, item, spider):
        """
        Objective:  To stop the spider as soon as we can, but also take into account possible duplicate items
                    or dirty data (blanks throughout)
                    We can't assume data we have no control over will be solid :)
        """
        if not self.allow_this_spider(spider):
            return self.dropit("This spider not allowed")

        # First check for any data that seems blank.
        blank_fields = [b for b in item.values() if not b or b in self.COUNTS_AS_BLANKS]
        if len(blank_fields) >= self.BLANK_TOLERANCE:
            return self.dropit("Dropping item which has {} fields that are blank {}".format(len(blank_fields), item))

        exists = self.database_ismember(self.key, item)
        if exists == 0:
            self.spider.warning("Adding to database")
            self.database_add(self.key, item)
            return item
        else:
            self.spider.warning("NOT adding to database")
            return self.dropit("We already have this one {}".format(item))    

class RedisSetPipeline(AbstractPipeline):
    def database_open(self):
        self.redis = redis.Redis('localhost')

    def database_ismember(self, key, item):
        return self.redis.sismember(key, item)

    def database_add(self, key, item):
        return self.redis.sadd(self.key, item)

class PostgresPipeLine(AbstractPipeline):
    def database_open(self):
        self.database = Database()
        self.DBSession = DBSession


class AuditlogPipeline(RedisSetPipeline):
    BLANK_TOLERANCE = 1
    COUNTS_AS_BLANKS = [u'\xa0']

    def dropit(self, message):
        self.spider.dropped += 1
        return super(AuditlogPipeline, self).dropit(message)

    def process_item(self, item, spider):
        """
        Objective:  To stop the spider as soon as we can, but also take into account possible duplicate items
                    or dirty data (blanks throughout)
                    We can't assume data we have no control over will be solid :)
        """
        if not self.allow_this_spider(spider):
            return self.dropit("This spider not allowed")

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


class ClassPeriodsPipeline(PostgresPipeLine):
    BLANK_TOLERANCE = 100

    def open_spider(self, spider):
        super(ClassPeriodsPipeline, self).open_spider(spider)
        self.key = getattr(spider, 'path').format(spider.class_id)

    def database_ismember(self, key, item):
        return False  # todo, make this work

    def database_add(self, key, item):
        Timetable = self.database.table_string_to_class('Timetable')
        with self.DBSession() as session:
            for day in item.get('periods'):
                periods = item['periods'][day]
                for period in periods:
                    timetable = Timetable(
                        course_id=item['course'],
                        day = day,
                        period=period
                        )
                    session.add(timetable)

