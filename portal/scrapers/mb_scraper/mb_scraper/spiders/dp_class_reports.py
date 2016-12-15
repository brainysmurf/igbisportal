from portal.scrapers.shared.spiders import \
    ManageBacLogin
from portal.scrapers.mb_scraper.mb_scraper.items import \
    ClassPeriodItem, ClassReportItem, GradeBookDataDumpItem
from portal.scrapers.mb_scraper.mb_scraper.items import \
    PrimaryReportItem, PrimaryReportStrandItem, \
    PrimaryReportOutcomeItem, PrimaryReportSectionItem, \
    TeacherAssignmentItem, PrimaryStudentAbsences, \
    SecHRItem
from portal.db import \
    Database, DBSession
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import datetime, re
from collections import defaultdict
from scrapy.exceptions import CloseSpider
import scrapy
import gns


class ClassReportsDP(ClassReports):
    #name = "ClassReportsDP"
    program = 'dp'
    path = '/classes/{}/{}-gradebook/tasks/term-grades'
    def class_reports_dp(self):
        request = scrapy.Request(
            url=self.path_to_url(), 
            callback=self.parse_items,
            errback=self.error_parsing,
            dont_filter=True
            )
        self.next()
        return request

class ClassPeriods(ManageBacLogin):
    name = "ClassPeriods"
    path = '/classes/{}/edit'
    data = {}

    def class_periods(self):
        request = scrapy.Request(
            url=self.path_to_url(), 
            callback=self.parse_items,
            errback=self.error_parsing,
            dont_filter=True
            )
        self.next()
        return request

    def extract_day(self, selection):
        class_attributes = selection.xpath("./@class").extract()
        if not class_attributes:
            from IPython import embed; embed(); exit();
        else:
            class_attributes = class_attributes[0]
        for attr in class_attributes.split(' '):
            match = re.match('.*day-(\d)+$', attr)
            if match:
                return match.group(1)
        return None

    def parse_items(self, response):
        self.warning("Parsing class edit page: {}".format(response.url))

        # Select every row with an id, who appears as a child of fileset id='attendance-section'
        drop_downs = response.xpath("//select[contains(@class, 'period-dropdown-for-day-')]")

        # Make a dict with keys with the days that have period info we want to store
        days = defaultdict(list)
        for dropdown in drop_downs:

            # We can access boolean attributes with the [@selected='selected'] idiom
            checked_items = dropdown.xpath("./option[@selected='selected']")
            for checked_item in checked_items:
                values = checked_item.xpath('./@value').extract()
                for value in values:
                    if value:
                        class_attributes = " ".join(dropdown.xpath('./@class').extract())
                        dropdown_for_day_x = int(re.search('(\d+)$', class_attributes).group(1))

                        if value.isdigit():
                            value = int(value)
                        days[dropdown_for_day_x].append(value)

        item = ClassPeriodItem()
        item['periods'] = days
        item['course'] = self.current_course_id
        yield item

        if self.current_course_id:
            yield self.class_periods()

    def done(self, response):
        pass