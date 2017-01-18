# TODO: Prune the below
from portal.scrapers.mb_scraper.mb_scraper.spiders.templates import \
    ClassReports
from portal.scrapers.mb_scraper.mb_scraper.items import TeacherAssignmentItem
from portal.db import DBSession


class PYPTeacherAssignments(ClassReports):
    name = "PYPTeacherAssignments"
    program = 'pyp'
    path = '/classes/{}/teachers'
    pyp_teacher_assignments = ClassReports.class_reports

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
        return super().path_to_url(self.path.format(self.class_id))
