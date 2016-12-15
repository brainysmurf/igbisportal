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

class ClassReportsMYP(ClassReports):
    name = "ClassReportsMYP"
    program = 'myp'
    path = '/classes/{}/{}-gradebook/tasks/term-grades'

    def class_reports_myp(self):
        request = scrapy.Request(
            url=self.path_to_url(), 
            callback=self.parse_items,
            errback=self.error_parsing,
            dont_filter=True
            )
        self.next()
        return request

    def parse_items(self, response):
        # First let's detect the term we're on and make sure that's in the database too
        # TODO: Far better would be to go through the settings pages and scrape it that way, but we can use this method for now
        # Because we're doing this manually, let's directly interface with the database here; don't yield

        current_term_id = self.determine_current_term(response)

        # Okay, so now let's find every textarea here and process them

        for comment in response.xpath('//textarea'):
            student_id = comment.xpath('./@user_id').extract()
            if student_id:
                student_id = student_id[0]
            text = comment.xpath('./text()').extract()
            if text:
                text = text[0]
            teacher_id = None # TODO: No way to get teacher directly, although can do join based on class_id. That assumes that only one teacher did so, though

            item = ClassReportItem()
            if self.class_id:
                item['course_id'] = self.class_id
            elif current_term_id:
                item['course_id'] = self.current_course_id
            else:
                pass # uh oh, shouldn't get here, need to have current_term_id...
            item['teacher_id'] = teacher_id
            item['student_id'] = student_id
            item['text'] = text
            item['term_id'] = current_term_id

            alt_marks = response.xpath("//span[@id='atl_marks_for_user_{}']".format(student_id))

            if len(alt_marks) != 1:
                continue

            alt_marks = alt_marks[0]

            atl_comments = []
            for skill in alt_marks.xpath('div'):
                name = skill.xpath('text()').extract()[0].strip('\n')
                # Get the value of the selected dropdown option list of ATLs
                selection = skill.xpath("select/option[@selected='selected']/@value").extract()
                #assert(len(selection) == 1)   #FIXME: What do I do if there isn't a selection, or more than one?
                if len(selection) != 1:
                    continue

                selection = selection[0]
                atl_comments.append(dict(name=name.title(), selection=selection.upper()))

            item['atl_comments'] = atl_comments
            yield item

        if self.current_course_id:
            method = getattr(self, 'class_reports_{}'.format(self.program.lower()))
            yield method()
