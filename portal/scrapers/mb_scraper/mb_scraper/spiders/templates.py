"""

TODO: Course IDs are longs, do they need to be? They print on the terminal that can cause confusion to developers
"""

# TODO: Prune the below
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

"""
FIXME: ClassLevelManageBac is actually a useful thing that allows me to cyle through things depending on data in database
But that involves a bunch of variable and method changes: class_id, current_class_id, etc
"""

class ClassLevelManageBac(ManageBacLogin):
    """
    Retrieves class IDs and cycles through all of them
    """
    def __init__(self, *args, **kwargs):
        self.db = Database()
        self.db.DBSession = DBSession

        class_id = kwargs.get('class_id')
        self.student_id = kwargs.get('student_id') or None

        if not class_id:
            rows = self.db.get_rows_in_table('course')
            self.all_course_ids = self._initial_query()
        else:
            rows = self.db.get_rows_in_table('course', id=class_id)
            if rows:
                self.all_course_ids = [class_id]
            else:
                print("Cannot find class with that id")
                exit()

        super(ClassLevelManageBac, self).__init__(*args, **kwargs)
        self.init()

    def _initial_query(self):
        """
        Override me
        """ 
        rows = self.db.get_rows_in_table('course')
        return [s.id for s in rows]

    @property
    def class_id(self):
        return self.current_course_id

    def init(self):
        """
        __init__ is often overridden without super call for these series of classes, so need this init function
        for common code 
        """
        self.manually_do_terms = True  # If this goes to false, can delete this entire method

    def next(self):
        if self.all_course_ids:
            self.current_course_id = self.all_course_ids.pop(0)
        else:
            self.current_course_id = None

    def path_to_url(self, class_id=None):
        return super(ClassLevelManageBac, self).path_to_url(self.path.format(self.class_id, self.program))

    def error_parsing(self, response):
        self.warning("OOOOOOHHHHHH NOOOOOOOOO")

class SecondaryHomeroomAdvisors(ClassLevelManageBac):
    name = "SecondaryHomeroomAdvisors"
    path = "/groups/{}/assign_homeroom_advisors"

    def path_to_url(self):
        return super(ClassLevelManageBac, self).path_to_url(self.path.format(self.class_id))

    def _initial_query(self):
        rows = self.db.get_rows_in_table('IB_Group')
        return [s.id for s in rows]

    def secondary_homeroom_advisors(self):
        self.next()
        if self.current_course_id:
            request = scrapy.Request(
                url=self.path_to_url(), 
                callback=self.parse_items,
                errback=self.error_parsing,
                dont_filter=True
                )
            yield request

    def parse_items(self, response):
        data = response.xpath('//tbody[@class="data"]')
        for row in data.xpath('./tr'):
            student = row.xpath('./td[1]/a/@href').extract()
            if student:
                student = student[0]
                student_id = int(student.split('/')[-1])
                #second
            teacher = row.xpath('./td[2]/select/option[@selected="selected"]/@value').extract()
            if teacher:
                teacher = teacher[0]
                teacher_id = int(teacher)
            if not student or not teacher:
                print('PROBLEM!')
                continue

            item = SecHRItem()
            item['student_id'] = student_id
            item['teacher_id'] = teacher_id

            yield item

        for item in self.secondary_homeroom_advisors():
            yield item

class ClassReports(ClassLevelManageBac):
    #name = 'no name because I don't want this to run separetly'
    program = '#'  # myp, dp, or pyp
    path = '/classes/{{}}/{{}}-gradebook/tasks/term-grades?term={}'.format(gns.config.managebac.current_term_id)

    def _initial_query(self):
        Course = self.db.Course
        with DBSession() as session:
            statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{}%'.format(self.program.upper())))
            return [s.id for s in statement.all()]

    def determine_current_term(self, response):
        """
        FIXME: This buries the code that makes the terms live in the database, far better would be to have a 
        way to launch this seperately through cli code
        """
        return gns.config.managebac.current_term_id  # UGH
        # current_term_id = None # if remove the below block, you'll still need to derive this
        # if self.manually_do_terms:
        #     for term_item in response.xpath("//select[@id='term']//option"):
        #         name = term_item.xpath('.//text()').extract()
        #         if name:
        #             name = name[0]
        #         term_id = term_item.xpath('./@value').extract()
        #         if term_id:
        #             term_id = term_id[0]
        #         current = term_item.xpath("./@selected='selected'").extract() == [u'1']
        #         if current:
        #             current_term_id = term_id
        #             if '(current)' in name:
        #                 # remove (current) and any surrounding whitespace from name if it's there. Ugh. Sorry.
        #                 name = re.sub('\W?\(current\)\W?', '', name)

        #         if not term_id or not name:
        #             # handle this error
        #             pass

        #         exists = self.db.get_rows_in_table('terms', id=term_id)
        #         if not exists:
        #             with DBSession() as session:
        #                 term = self.db.table.Term(
        #                         id=term_id,
        #                         name=name,
        #                         current=current,
        #                         #TODO: Have to get these from the settings
        #                         start_date=None,
        #                         end_date=None
        #                     )
        #                 session.add(term)
        # return current_term_id

    def class_reports(self):
        """
        Provides the mechanism to loop through courses, called at spider start-up and as a callback in parse_items when ready to move on to next
        """
        self.next()
        if self.current_course_id:
            request = scrapy.Request(
                url=self.path_to_url(), 
                callback=self.parse_items,
                errback=self.error_parsing,
                dont_filter=True
                )
            yield request

# TODO: Delete this, not sure why it's there
# class ClassPeriods(ManageBacLogin):
#     name = "ClassPeriods"
#     path = '/classes/{}/edit'
#     data = {}

#     def class_periods(self):
#         request = scrapy.Request(
#             url=self.path_to_url(), 
#             callback=self.parse_items,
#             errback=self.error_parsing,
#             dont_filter=True
#             )
#         self.next()
#         return request

#     def extract_day(self, selection):
#         class_attributes = selection.xpath("./@class").extract()
#         if not class_attributes:
#             from IPython import embed; embed(); exit();
#         else:
#             class_attributes = class_attributes[0]
#         for attr in class_attributes.split(' '):
#             match = re.match('.*day-(\d)+$', attr)
#             if match:
#                 return match.group(1)
#         return None

#     def parse_items(self, response):
#         self.warning("Parsing class edit page: {}".format(response.url))

#         # Select every row with an id, who appears as a child of fileset id='attendance-section'
#         drop_downs = response.xpath("//select[contains(@class, 'period-dropdown-for-day-')]")

#         # Make a dict with keys with the days that have period info we want to store
#         days = defaultdict(list)
#         for dropdown in drop_downs:

#             # We can access boolean attributes with the [@selected='selected'] idiom
#             checked_items = dropdown.xpath("./option[@selected='selected']")
#             for checked_item in checked_items:
#                 values = checked_item.xpath('./@value').extract()
#                 for value in values:
#                     if value:
#                         class_attributes = " ".join(dropdown.xpath('./@class').extract())
#                         dropdown_for_day_x = int(re.search('(\d+)$', class_attributes).group(1))

#                         if value.isdigit():
#                             value = int(value)
#                         days[dropdown_for_day_x].append(value)

#         item = ClassPeriodItem()
#         item['periods'] = days
#         item['course'] = self.current_course_id
#         yield item

#         if self.current_course_id:
#             yield self.class_periods()

#     def done(self, response):
#         pass

class GradeBookDump(ClassReports):
    name = 'GradeBookDump'
    path = '/classes/{}/myp-gradebook/tasks/export_to_excel.xml?term=27814'

    def grade_book_dump(self):
        """
        Provides the mechanism to loop through courses, called at spider start-up and as a callback in parse_items when ready to move on to next
        """
        self.next()
        if self.current_course_id:
            item = GradeBookDataDumpItem()
            item.file_urls = self.path.format(self.current_course_id)
            yield request

# TODO: Delete me if not needed 
# class PYPClassReportTemplate(ClassReports):
#     def _initial_query(self):
#         with DBSession() as session:
#             statement = session.query(self.db.Course.id).\
#                 select_from(Course).\
#                 filter(Course.name.like('%{} Grade%'.format(self.program.upper())))
#             return [s.id for s in statemdent.all()]






