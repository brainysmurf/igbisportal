"""

TODO: Course IDs are longs, do they need to be? They print on the terminal that can cause confusion to developers
"""

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

import datetime, re
from collections import defaultdict
from scrapy.exceptions import CloseSpider
import scrapy
from scrapy import log
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
    path = '/classes/{}/{}-gradebook/tasks/term-grades?term=55880'

    def _initial_query(self):
        Course = self.db.Course
        with DBSession() as session:
            statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{}%'.format(self.program.upper())))
            return [s.id for s in statement.all()]

    def determine_current_term(self, response):
        return 55880
        current_term_id = None # if remove the below block, you'll still need to derive this
        if self.manually_do_terms:
            for term_item in response.xpath("//select[@id='term']//option"):
                name = term_item.xpath('.//text()').extract()
                if name:
                    name = name[0]
                term_id = term_item.xpath('./@value').extract()
                if term_id:
                    term_id = term_id[0]
                current = term_item.xpath("./@selected='selected'").extract() == [u'1']
                if current:
                    current_term_id = term_id
                    if '(current)' in name:
                        # remove (current) and any surrounding whitespace from name if it's there. Ugh. Sorry.
                        name = re.sub('\W?\(current\)\W?', '', name)

                if not term_id or not name:
                    # handle this error
                    pass

                exists = self.db.get_rows_in_table('terms', id=term_id)
                if not exists:
                    with DBSession() as session:
                        term = self.db.Terms(
                                id=term_id,
                                name=name,
                                current=current,
                                #TODO: Have to get these from the settings
                                start_date=None,
                                end_date=None
                            )
                        session.add(term)
        return current_term_id

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

class PYPClassReportTemplate(ClassReports):
    def _initial_query(self):
        with DBSession() as session:
            statement = session.query(self.db.Course.id).\
                select_from(Course).\
                filter(Course.name.like('%{} Grade%'.format(self.program.upper())))
            return [s.id for s in statemdent.all()]

class PYPStudentAttendance(ManageBacLogin):
    name = "PYPStudentAttendance"
    path = '/admin/attendance_manager/reporting?program=pyp&term=55880&grade={}&cumulative_view=homeroom'

    def __init__(self, *args, **kwargs):
        self.grades = [-2, -1, 0, 1, 2, 3, 4, 5]

        super(ManageBacLogin, self).__init__(*args, **kwargs)

    def next(self):
        self.grade = self.grades.pop() if self.grades else None

    def error_parsing(self, response):
        self.warning("OOOOOOHHHHHH NOOOOOOOOO")

    def path_to_url(self, grade):
        return super(PYPStudentAttendance, self).path_to_url(self.path.format(grade))

    def pyp_student_attendance(self):
        self.next()
        if not self.grade is None:
            request = scrapy.Request(
                url=self.path_to_url(self.grade),
                callback=self.parse_items,
                errback=self.error_parsing,
                dont_filter=True
                )
            yield request

    def parse_items(self, response):
        for row in response.xpath('//tbody/tr'):

            user_id = row.xpath('./td[@class="student"]/@user_id').extract()[0]
            # if user_id == '11392152':
            #     from IPython import embed;embed()
            # Takes a lot of shortcuts here...
            try:
                absent = row.xpath('./td/span/span[@class="absent"]')
                if not absent:
                    absences = 0
                else:
                    absences = int(absent.xpath('./text()').extract()[0].strip('\n'))
                mini_row = row.xpath('./td[@class="tac vac"]')

                late = mini_row[2].extract()
                findall = re.findall('[0-9]+', late)
                if not findall:
                    late = 0
                else:
                    late = int(re.findall('[0-9]+', late)[0])
                present = mini_row[1].extract()
                present = int(re.findall('[0-9]+', present)[0])
                other = mini_row[3].extract()
                other = int(re.findall('[0-9]+', other)[0])

                present = present + other

                total_present = present + absences + late

            except IndexError:
                absences = None


            if not absences is None:
                item = PrimaryStudentAbsences()
                item['student_id'] = user_id
                item['absences'] = absences
                item['total_days'] = total_present
                item['term_id'] = 55880

                yield item

        for item in self.pyp_student_attendance():
            yield item

class PYPTeacherAssignments(PYPClassReportTemplate):
    name = "PYPTeacherAssignments"
    program = 'pyp'
    path = '/classes/{}/teachers'
    
    def _initial_query(self):
        Course = self.db.table_string_to_class('Course')
        ret = []
        with DBSession() as session:
            statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{} Grade%'.format(self.program.upper())))
            for s in statement.all():
                ret.append(s.id)
            statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{} Early Years%'.format(self.program.upper())))
            for s in statement.all():
                ret.append(s.id)
            statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{} Kindergarten%'.format(self.program.upper())))
            for s in statement.all():
                ret.append(s.id)
        return ret

    pyp_teacher_assignments = PYPClassReportTemplate.class_reports

    def parse_items(self, response):

        # Loop through the 0_user_id and 1_user_id available there
        for _id in response.xpath("//select[contains(@id, 'user_id')]/@id").re('.*_user_id'):

            row = response.xpath("//select[@id='{}']".format(_id))

            teacher_subject = row.xpath("../..//td//select//option[@selected='selected']")
            teacher = None
            subjects = None
            checked = None

            if len(teacher_subject) >= 2:
                checked = row.xpath("../..//td//div/label/input[@checked='checked']")
                teacher = teacher_subject[0]
                subjects = teacher_subject[1:]

            if teacher and subjects and checked and checked.xpath('@value').extract()[0] == '1':
                teacher_id = teacher.xpath('@value').extract()[0]

                for subject in subjects:
                    subject_id = subject.xpath('@value').extract()[0]
                    item = TeacherAssignmentItem()
                    item['teacher_id'] = teacher_id
                    item['subject_id'] = subject_id 
                    item['class_id'] = self.class_id

                    yield item

        # Goes on to the next class
        for item in self.class_reports():
            yield item

    def path_to_url(self):
        """
        This class doesn't have to specify the program... having the class id is enough
        """
        return super(ClassLevelManageBac, self).path_to_url(self.path.format(self.class_id))


class PYPClassReports(PYPClassReportTemplate):  # Later, re-factor this inheritence?
    name = "PYPClassReports"
    program = 'pyp'
    path = '/classes/{}/pyp-gradebook/tasks/term_grades?term=55880'

    def _initial_query(self):
        Course = self.db.table_string_to_class('Course')
        ret = []
        with DBSession() as session:
            statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{} Grade%'.format(self.program.upper())))
            for s in statement.all():
                ret.append(s.id)

            statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{} Early Years%'.format(self.program.upper())))

            for s in statement.all():
                ret.append(s.id)

            statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{} Kindergarten%'.format(self.program.upper())))

            for s in statement.all():
                ret.append(s.id)

        return ret

    def pyp_class_reports(self):
        return self.class_reports()

    def parse_items(self, response):
        """
        Cycle through each PYP subject
        """

        # Dispatch to parse_subject per each subject on right side
        # Code this first because this will actually be deferred until last
        for subject_url in response.xpath("//ul[@class='small_right_tabs']/li/a/@href").extract():
            request = scrapy.Request(
                url=gns.config.managebac.url + subject_url,
                callback=self.parse_subject,
                errback=self.error_parsing,
                dont_filter=True,
                meta=dict(class_id = self.class_id)
                )
            yield request

        # Dispatch to parse_student per each student on left side
        for student_url in response.xpath("//li[@class='selected own-pyp-class']/ul/li/a/@href").extract():
            request = scrapy.Request(
                url=gns.config.managebac.url + student_url,
                callback=self.parse_student,
                errback=self.error_parsing,
                dont_filter=True,
                meta=dict(class_id = self.class_id)
                )
            yield request

        # Goes on to the next class
        for item in self.class_reports():
            yield item

    def parse_student(self, response):
        """
        Sets up the database with PrimaryReport objects
        """
        current_term_id = self.determine_current_term(response)

        student_id = response.xpath("//input[@id='pyp_final_grade_user_id']/@value")[0].extract() or None

        if student_id is None:
            print("NO STUDENT ID??")

        teacher_id = response.xpath("//div[@class='span2']/div/a/@href").extract()[0].split('/')[-1]

        homeroom_comment = response.xpath('//textarea') or None
        if homeroom_comment is None:
            print("NO HOMEROOM COMMENT???")

        homeroom_comment = homeroom_comment[0]
        homeroom_comment = homeroom_comment.xpath('./text()').extract() or ""
        if homeroom_comment:
            homeroom_comment = homeroom_comment[0]

        item = PrimaryReportItem()
        item['homeroom_comment'] = homeroom_comment
        item['student_id'] = student_id
        item['course_id'] = response.meta.get('class_id')
        item['teacher_id'] = teacher_id
        item['term_id'] = current_term_id

        yield item


    def parse_subject(self, response):
        """
        Collects the existing PrimaryReport objects and adds data to them
        """
        current_term_id = self.determine_current_term(response)
        subject_id = re.search('\?subject=(\d+)', response.url).group(1)

        subject_name = response.xpath("//h2[@class='vac']")[0].xpath('./text()').extract()
        subject_name = "".join([l.strip('\n') for l in subject_name if l.strip('\n')])


        for student in response.xpath("//td[@class='student-assessment']"):
            student_id = student.xpath('./div/@id').extract()[0].split('_')[-1]

            # First we have to set up and get the report section (subject) in the database
            item = PrimaryReportSectionItem()
            comment = response.xpath("//div[@id='user_comments_{}']".format(student_id))
            comment = comment.xpath('./textarea/text()').extract()
            comment = comment[0] if comment else ""
            item['student_id'] = student_id
            item['course_id'] = response.meta.get('class_id')
            item['term_id'] = current_term_id

            item['subject_id'] = subject_id
            item['subject_name'] = subject_name
            item['comment'] = comment

            yield item

            for student_strand in response.xpath("//div[@id='user_strand_marks_{}']".format(student_id)):
                which = 1
                for strand in student_strand.xpath('./table/tbody/tr'):
                    strand_label = (strand.xpath('./td[1]/text()').extract()[0]).strip('\n').strip()
                    strand_label = strand_label[0].upper() + strand_label[1:]
                    strand_label += "." if strand_label[-1] != '.' else ""
                    value = strand.xpath("./td[2]/select/option[@selected='selected']/text()").extract()
                    strand_value = value[0] if value else ""
 
                    item = PrimaryReportStrandItem()
                    item['student_id'] = student_id
                    item['course_id'] = response.meta.get('class_id')
                    item['term_id'] = current_term_id
                    item['subject_id'] = subject_id
                    item['which'] = which

                    item['strand_label'] = strand_label
                    item['strand_label_titled'] = strand_label.title().replace('And', 'and')
                    item['strand_text'] = strand_value

                    if strand_label:
                        yield item
                    which += 1

            for student_outcome in response.xpath("//div[@id='user_learning_outcomes_marks_{}']".format(student_id)):
                which = 1
                for outcome in student_outcome.xpath('./table'):

                    # For this, we have to inspect the headers to see 

                    for section_num in range(len(outcome.xpath('./thead'))):

                        strand_heading = outcome.xpath('./thead/tr/th/strong/text()').extract()[section_num * 2]
                        outcome_body = outcome.xpath('./tbody')[section_num]

                        for outcome_content in outcome_body.xpath('./tr'):

                            cells = outcome_content.xpath('./td')
                            if len(cells) == 2:
                                outcome_label = (cells[0].xpath('./text()').extract()[0]).strip('\n').strip()
                                outcome_label = outcome_label[0].upper() + outcome_label[1:]
                                outcome_label += '.' if outcome_label[-1] != "." else ""
                                value = cells[1].xpath("./select/option[@selected='selected']/text()").extract()

                                outcome_value = value[0] if value else ""

                                item = PrimaryReportOutcomeItem()
                                item['student_id'] = student_id
                                item['course_id'] = response.meta.get('class_id')
                                item['term_id'] = current_term_id
                                item['subject_id'] = subject_id
                                item['heading'] = strand_heading.title().replace('And', 'and')
                                item['which'] = which
                                item['outcome_label'] = outcome_label
                                item['outcome_label_titled'] = outcome_label.title().replace('And', 'and')
                                item['outcome_text'] = outcome_value

                                if outcome_label.strip('\n'):
                                    yield item
                                which += 1

    # def path_to_url(self):
    #     return super(PYPClassReportTemplate, self).path_to_url(self.path.format(self.class_id, self.student_id))

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
