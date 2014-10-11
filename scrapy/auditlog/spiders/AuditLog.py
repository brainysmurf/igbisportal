import scrapy
from auditlog.spiders.Login import OpenApplyLogin

class AuditLog(OpenApplyLogin):
    DATE_PARSE = "%d %b %Y at %I:%M %p"
    name = "AuditLog"
    path = '/admin/audit?page={}'
    data = {}

    def __init__(self, *args, **kwargs):
        super(Login, self).__init__(*args, **kwargs)
        self.n = 1

    def path_to_url(self):
        return super(AuditLog, self).path_to_url(self.path.format(self.n))

    def error_parsing(self, response):
        self.warning("OOOOOOHHHHHH NOOOOOOOOO")

    def audit_log(self):
        request = scrapy.Request(
            url=self.path_to_url(), 
            callback=self.parse_items,
            errback=self.error_parsing,
            dont_filter=True    
            )
        self.n += 1
        return request

    @classmethod
    def parse_date(cls, d):
        return datetime.datetime.strptime(d, cls.DATE_PARSE).isoformat()

    def parse_items(self, response):
        self.warning("Parsing next page of audit log: {}".format(response.url))
        items = response.xpath('//table/tbody/tr')
        self.done = False
        self.dropped = 0
        for sel_number in range(len(items)):
            sel = items[sel_number]
            item = AuditLogItem()
            item['date'] = self.parse_date(sel.xpath('td[1]/text()').extract()[0].strip('\n'))
            item['target'] = sel.xpath('td[2]/text()').extract()[0].strip('\n')
            item['administrator'] = sel.xpath('td[3]/a/text()').extract()[0].strip('\n')
            item['applicant'] = sel.xpath('string(td[4])').extract()[0].strip('\n')
            item['action'] = sel.xpath('string(td[5])').extract()[0].replace('\n', ' ').replace('  ', ' ').strip()
            yield item

        if self.dropped == len(items):
            self.done = True

        # continue to load up these items only if we found log items
        # and the pipeline hasn't changed the flag
        if not self.done and items:
            url = self.path_to_url()
            yield self.audit_log()

    def done(self, response):
        pass
