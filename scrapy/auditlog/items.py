import scrapy
from ordereditem import OrderedItem

class AuditLogItem(OrderedItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date = scrapy.Field()
    target = scrapy.Field()
    administrator = scrapy.Field()
    applicant = scrapy.Field()
    action = scrapy.Field()

class ClassPeriodItem(scrapy.Item):
    course = scrapy.Field()
    periods = scrapy.Field()