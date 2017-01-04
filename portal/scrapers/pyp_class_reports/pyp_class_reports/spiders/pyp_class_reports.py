"""
"""


# FIX ME: Prune the below
from portal.scrapers.mb_scraper.mb_scraper.spiders.templates import \
    ClassReports
from portal.scrapers.pyp_class_reports.pyp_class_reports.items import \
    PrimaryReportItem, PrimaryReportStrandItem, \
    PrimaryReportOutcomeItem, PrimaryReportSectionItem
from portal.db import \
    Database, DBSession
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

import datetime, re
from collections import defaultdict
from scrapy.exceptions import CloseSpider
import scrapy
import gns


class PYPClassReports(ClassReports):  # Later, re-factor this inheritence?
    """
    FIXME: Early Years and excetera are not complete, may need different processing
    """

    name = "PYPClassReports"
    program = 'pyp'
    path = '/classes/{{}}/pyp-gradebook/tasks/term_grades?term={}'.format(gns.config.managebac.current_term_id)

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

            s = list(statement.all())
            gns.tutorial("Queried database for all pyp courses and got back: {ret}".format(ret=ret))
        return ret

    def build_request(self, **kwargs):
        return scrapy.Request(**kwargs)

    def pyp_class_reports(self):
        """ entry point """
        yield from self.class_reports()

    def parse_items(self, response):
        """
        Entry point, after getting the base url
        """
        # Dispatch to parse_subject per eacfh subject on right side
        # Code this first because this will actually be deferred until last

        gns.tutorial("Received data rom base url: {response.url}".format(response=response), edit=(response.text, '.html'))

        xpath = "//ul[@class='small_right_tabs']/li/a/@href"
        xpaths = response.xpath(xpath)
        gns.tutorial("Scraping response with xpath {xpath}".format(xpath=xpath), edit=(response.text,'.html'))
        gns.tutorial("Found {len(xpath)} url items to follow.", edit=(xpaths.extract(), '.pretty'))

        for subject_url in xpaths.extract():
            url = gns.config.managebac.url + subject_url
            gns.tutorial("Found link, following: {url}".format(url=url.replace(gns.config.managebac.url, '')))
            request = self.build_request(
                url=url,
                callback=self.parse_subject,
                errback=self.error_parsing,
                dont_filter=True,
                meta=dict(class_id = self.class_id)
                )
            yield request

        # Cycle through each student on the left side
        # And dispatch to `parse_student`

        for student_url in response.xpath("//li[@class='selected own-pyp-class']/ul/li/a/@href").extract():
            # If we only have one student in mind,
            # Short-circuit it so that we only end up doing the one request we are interested in

            if self.student_id:

                # Sanity check:
                if not '/' in student_url:
                    print('Expecting "/" in student_url while scraping, found {} instead.'.format(student_url))
                    continue
                #

                # Extract the mb id from the url we scraped
                # anc check the database
                student_mb_id = int(re.search('=(\d+)?', student_url).group(1))
                if student_mb_id != self.student_id:
                    continue
                # if still here, we continue

            url = gns.config.managebac.url + student_url
 
            #

            # Build the request for scrapy
            # and callback
            request = self.build_request(
                url=url,
                callback=self.parse_student,   # callback
                errback=self.error_parsing,
                dont_filter=True,
                meta=dict(class_id = self.class_id)
                )
            # yielding a request will put it in the twisted event loop
            yield request

        # Goes on to the next class
        for item in self.class_reports():
            yield item

    def parse_student(self, response):
        """
        Sets up the database with PrimaryReport objects
        """
        current_term_id = self.determine_current_term(response)

        student_id = int(response.xpath("//input[@id='pyp_final_grade_user_id']/@value")[0].extract())
        if self.student_id and self.student_id != student_id: 
            print("Nothing for this student: {}".format(student_id))
            return

        if student_id is None:
            print("NO STUDENT ID??")
            return

        teacher_id = response.xpath("//div[@class='span2']/div/a/@href").extract()[0].split('/')[-1]

        homeroom_comment = response.xpath('//textarea') or None
        if homeroom_comment is None:
            print("NO HOMEROOM COMMENT???")
            return

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
        url = response.url
        regexp = '\?subject=(\d+)'
        subject_id = re.search(regexp, url).group(1)
        gns.tutorial("Extracted subject_id {subject_id} from the url {url} with reg exp {regexp}".format(subject_id=subject_id, url=url, regexp=regexp))

        subject_name = response.xpath("//h2[@class='vac']")[0].xpath('./text()').extract()
        subject_name = "".join([l.strip('\n') for l in subject_name if l.strip('\n')])

        for student in response.xpath("//td[@class='student-assessment']"):
            student_id = int(student.xpath('./div/@id').extract()[0].split('_')[-1])
            if self.student_id and self.student_id != student_id:
                continue

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

            strands = response.xpath("//div[@id='user_strand_marks_{}']".format(student_id))
            if not strands:
                # This is a single subject that has been changed from strands to just an overall comment
                overall_comment = response.xpath("//div[@id='user_final_grade_marks_{}']".format(student_id))
                if overall_comment:
                    overall_comment = overall_comment[0]
                    selection = overall_comment.xpath("./table/tbody/tr/td/select/option[@selected='selected']/text()").extract()
                    selection = selection[0] if selection else ""
                    item['overall_comment'] = {'G': 'Good', 'O':'Outstanding', 'N':'Needs Improvement'}.get(selection, '')
                else:
                    item['overall_comment'] = "N/A"
            else:
                item['overall_comment'] = "N/A"

            yield item

            for student_strand in strands:
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
