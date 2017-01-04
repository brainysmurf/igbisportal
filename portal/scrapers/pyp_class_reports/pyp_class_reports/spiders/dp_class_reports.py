from portal.scrapers.mb_scraper.mb_scraper.spiders.templates import \
    ClassReports
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

