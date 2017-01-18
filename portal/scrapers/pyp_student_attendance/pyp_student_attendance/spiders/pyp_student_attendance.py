# FIX ME: Prune the below
from portal.scrapers.shared.spiders import \
    ManageBacLogin
from portal.scrapers.pyp_student_attendance.pyp_student_attendance.items import PrimaryStudentAbsencesItem

import re
import scrapy
import gns


class PYPStudentAttendance(ManageBacLogin):
    name = "PYPStudentAttendance"
    path = '/admin/attendance_manager/reporting?program=pyp&term={}&grade={{}}&cumulative_view=homeroom'.format(gns.config.managebac.current_term_id)

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
        if self.grade is not None:
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

            if absences is not None:
                item = PrimaryStudentAbsencesItem()
                item['student_id'] = user_id
                item['absences'] = absences
                item['total_days'] = total_present
                item['term_id'] = gns.config.managebac.current_term_id

                yield item

        for item in self.pyp_student_attendance():
            yield item