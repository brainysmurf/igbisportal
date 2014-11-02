# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from portal.scrapers.shared.pipelines import PostgresPipeline

class AuditLogPipeline(PostgresPipeLine):
    BLANK_TOLERANCE = 1
    COUNTS_AS_BLANKS = [u'\xa0']

    def dropit(self, message):
        self.spider.dropped += 1
        return super(AuditLogPipeline, self).dropit(message)

    def database_add(self, key, item):
        AuditLog = self.database.table_string_to_class('AuditLog')
        with self.DBSession() as session:
            log = AuditLog(
                date=item['date'],
                target=item['target'],
                administrator=item['administrator'],
                applicant=item['applicant'],
                action=item['action']
                )
            session.add(log)

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

        exists = self.database_ismember(self.key, item.tojson)
        if not exists:
            self.database_add(self.key, item)
            return item
        else:
            return self.dropit("We already have this one {} and dropped = {}".format(item, spider.dropped))


