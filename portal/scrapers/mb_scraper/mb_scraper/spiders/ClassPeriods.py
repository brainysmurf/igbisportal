"""

TODO: Course IDs are longs, do they need to be? They print on the terminal that can cause confusion to developers
"""

import scrapy
from portal.scrapers.shared.spiders import ManageBacLogin
from portal.scrapers.mb_scraper.mb_scraper.items import ClassPeriodItem, ClassReportItem
from portal.db import Database, DBSession
import datetime, re
from collections import defaultdict

class ClassLevelManageBac(ManageBacLogin):
    """
    Retrieves class IDs and cycles through all of them
    """
    def __init__(self, class_id=None, *args, **kwargs):
        self.class_id = class_id
        self.db = Database()
        self.db.DBSession = DBSession
        if not self.class_id:
            rows = self.db.get_rows_in_table('course')
            self.all_course_ids = [s.id for s in rows()]
            self.next()
        else:
            self.all_course_ids = None
            self.current_course_id = None

        super(ClassLevelManageBac, self).__init__(*args, **kwargs)

    def next(self):
        if self.class_id:
            pass
        else:
            if self.all_course_ids:
                self.current_course_id = self.all_course_ids.pop(0)
            else:
                self.current_course_id = None

    def path_to_url(self, class_id=None):
        if self.current_course_id:
            return super(ClassLevelManageBac, self).path_to_url(self.path.format(self.current_course_id, self.program))
        else:
            return super(ClassLevelManageBac, self).path_to_url(self.path.format(self.class_id, self.program))

    def error_parsing(self, response):
        self.warning("OOOOOOHHHHHH NOOOOOOOOO")

class ClassReports(ClassLevelManageBac):
    #name = 'no name because I don't want this to run separetly'
    program = '#'  # myp, dp, or pyp
    path = '/classes/{}/{}-gradebook/tasks/term-grades'

    def __init__(self, class_id=None, **kwargs):
        self.class_id = class_id
        self.db = Database()
        if not self.class_id:
            self.db.DBSession = DBSession
            Course = self.db.table_string_to_class('Course')
            with DBSession() as session:
                statement = session.query(Course.id).select_from(Course).filter(Course.name.like('%{}%'.format(self.program.upper())))
                self.all_course_ids = [s[0] for s in statement.all()]
                print(self.all_course_ids)
            self.next()
        else:
            self.all_course_ids = None
            self.current_course_id = None
        self.manually_do_terms = True  # If this goes to false, can delete this entire method

    def parse_items(self, response):
        # First let's detect the term we're on and make sure that's in the database too
        # TODO: Far better would be to go through the settings pages and scrape it that way, but we can use this method for now
        # Because we're doing this manually, let's directly interface with the database here; don't yield

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
                        Terms = self.db.table_string_to_class('terms')
                        term = Terms(
                                id=term_id,
                                name=name,
                                current=current,
                                #TODO: Have to get these from the settings
                                start_date=None,
                                end_date=None
                            )
                        session.add(term)

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

            assert(len(alt_marks) == 1)
            alt_marks = alt_marks[0]

            atl_comments = []
            for skill in alt_marks.xpath('div'):
                name = skill.xpath('text()').extract()[0].strip('\n')
                # Get the value of the selected dropdown option list of ATLs
                selection = skill.xpath("select/option[@selected='selected']/@value").extract()
                assert(len(selection) == 1)
                selection = selection[0]
                atl_comments.append(dict(name=name.title(), selection=selection.upper()))

            item['atl_comments'] = atl_comments
            yield item

        if self.current_course_id:
            method = getattr(self, 'class_reports_{}'.format(self.program.lower()))
            yield method()


    def class_reports(self):
        request = scrapy.Request(
            url=self.path_to_url(), 
            callback=self.parse_items,
            errback=self.error_parsing,
            dont_filter=True
            )
        self.next()
        return request

class ClassReportsPYP(ClassReports):
    #name = "ClassReportsPYP"
    program = 'pyp'
    path = '/classes/{}/{}-gradebook/tasks/term-grades'

    def class_reports_pyp(self):
        if self.class_id or self.current_course_id:
            request = scrapy.Request(
                url=self.path_to_url(), 
                callback=self.parse_items,
                errback=self.error_parsing,
                dont_filter=True
                )
            self.next()
            return request
        return None


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
