# -*- coding: utf-8 -*-
from portal.db import Database, DBSession  

from portal.scrapers.shared.pipelines import \
    PostgresPipeline
from portal.scrapers.mb_scraper.mb_scraper.items import \
    PrimaryReportItem, PrimaryReportSupplementItem, \
    PrimaryReportSectionItem, PrimaryReportStrandItem, \
    PrimaryReportOutcomeItem, PrimaryStudentAbsences

from sqlalchemy.orm.exc import NoResultFound

from portal.utils import string_to_entities

from scrapy import log

class PYPTeacherAssignments(PostgresPipeline):
    BLANK_TOLERANCE = 1

    def database_add(self, key, item):
        TeacherAssign = self.database.table_string_to_class('Primary_Teacher_Assignments')
        subject_id = int(item['subject_id'])
        teacher_id = int(item['teacher_id'])
        class_id = int(item['class_id'])

        with DBSession() as session:
            try:
                exists = session.query(TeacherAssign).filter_by(class_id=class_id, subject_id=subject_id, teacher_id=teacher_id).one()
                if exists:
                    print("Already: {}".format(item))
            except NoResultFound:
                teacher_assign = TeacherAssign(
                        teacher_id = teacher_id,
                        subject_id = subject_id,
                        class_id = class_id
                    )
                print('Added: {}'.format(item))
                session.add(teacher_assign)

class ClassReportsPipeline(PostgresPipeline):
    BLANK_TOLERANCE = 100

    def allow_this_spider(self, spider):
        """
        Override...
        """
        return spider.name.startswith('ClassReports')

    def database_add(self, key, item):
        ReportComments = self.database.table_string_to_class('Report_Comments')
        AtlComments = self.database.table_string_to_class('Atl_Comments')
        with DBSession() as session:
            report_comment = ReportComments(
                    course_id = int(item['course_id']),
                    term_id = int(item['term_id']),
                    text = string_to_entities(item['text']),
                    teacher_id = int(item['teacher_id']) if not item['teacher_id'] is None else None,  # When this becomes an int, change it to an int...
                    student_id = int(item['student_id'])
                )
            session.add(report_comment)

            for atl_comment in item['atl_comments']:
                alt_comment = AtlComments(
                        label = atl_comment['name'],
                        selection = atl_comment['selection']
                    )
                session.add(alt_comment)

                # okay, now that both records are all good, make the relationship link
                report_comment.atl_comments.append(alt_comment)

class SecHRPipeline(ClassReportsPipeline):
    def allow_this_spider(self, spider):
        return spider.name == 'SecondaryHomeroomAdvisors'

    def database_add(self, key, item):
        SecHrTeachers = self.database.table_string_to_class('secondary_homeroom_teachers')
        student_id = item['student_id']
        teacher_id = item['teacher_id']
        with DBSession() as session:
            try:
                exists = session.query(SecHrTeachers).filter_by(
                    teacher_id=teacher_id,
                    student_id=student_id
                    ).one()
            except NoResultFound:
                exists = False
            if exists:
                return exists

            assign = SecHrTeachers(teacher_id=teacher_id, student_id=student_id)
            session.add(assign)

class PYPClassReportsPipline(PostgresPipeline):
    """

    """
    BLANK_TOLERANCE = 100   # Could use this for different things

    def allow_this_spider(self, spider):
        return spider.name.startswith('PYPClassReports')

    def make_primary_report(self, term_id, course_id, student_id, teacher_id=None, homeroom_comment=None):
        PrimaryReport = self.database.table_string_to_class('Primary_Report')
        homeroom_comment = string_to_entities(homeroom_comment)

        exists = None
        with DBSession() as session:
            try:
                exists = session.query(PrimaryReport).filter_by(term_id=term_id, course_id=course_id, student_id=student_id).one()
                if exists and homeroom_comment is not None:
                    exists.homeroom_comment = homeroom_comment
                if exists and teacher_id is not None:
                    exists.teacher_id = teacher_id
                return exists
            except NoResultFound:
                primary_report = PrimaryReport(
                        course_id = course_id,
                        term_id = term_id,
                        homeroom_comment = homeroom_comment,
                        teacher_id = teacher_id if not teacher_id is None else None,  # When this becomes an int, change it to an int...
                        student_id = student_id
                    )
                session.add(primary_report)
                return primary_report

    def make_primary_report_section(self, term_id, subject_id, course_id, student_id, comment="", name =""):
        exists = None
        comment = string_to_entities(comment)
        PrimaryReportSection = self.database.table_string_to_class('Primary_Report_Section')
        Teacher = self.database.table_string_to_class('Advisor')
        TeacherAssignments = self.database.table_string_to_class('Primary_Teacher_Assignments')

        with DBSession() as session:

            # Set up the teachers
            teachers = []
            teacher_assignments = session.query(TeacherAssignments).filter_by(subject_id=subject_id, class_id=course_id).all()
            for teacher in teacher_assignments:
                teachers.append( session.query(Teacher).filter_by(id=teacher.teacher_id).one() )

            primary_report = self.make_primary_report(term_id, course_id, student_id)

            try:
                exists = session.query(PrimaryReportSection).filter_by(primary_report_id=primary_report.id, subject_id=subject_id).one()
                if exists:
                    if comment: 
                        exists.comment = comment
                    if name:
                        exists.name = name
                session.add(exists)

                # Sync the teachers, removing those that are gone, adding if any needed to be added

                for teacher in exists.teachers:
                    if not teacher in teachers:
                        exists.teachers.remove(teacher)

                for teacher in teachers:
                    if not teacher in exists.teachers:
                        exists.teachers.append(teacher)

                return exists

            except NoResultFound:

                # Shouldn't there be a teacher in here somewhere?
                primary_report_section = PrimaryReportSection(
                        primary_report_id = primary_report.id,
                        subject_id = subject_id,
                        comment = comment,
                        name = name,
                    )
                session.add(primary_report_section)

                for teacher in teachers:
                    primary_report_section.teachers.append( teacher )

                return primary_report_section


    def database_add(self, key, item):
        Teacher = self.database.table_string_to_class('Advisor')
        TeacherAssignments = self.database.table_string_to_class('Primary_Teacher_Assignments')
        PrimaryReport = self.database.table_string_to_class('Primary_Report')
        PrimaryReportSection = self.database.table_string_to_class('Primary_Report_Section')
        PrimaryReportStrand = self.database.table_string_to_class('Primary_Report_Strand')
        PrimaryReportLo = self.database.table_string_to_class('Primary_Report_Lo')

        if item.__class__ is PrimaryReportItem:
            term_id = int(item.get('term_id'))
            course_id = int(item.get('course_id'))
            student_id = int(item.get('student_id'))
            teacher_id = int(item.get('teacher_id'))
            homeroom_comment = item.get('homeroom_comment')

            self.make_primary_report(term_id, course_id, student_id, teacher_id, homeroom_comment)

        elif item.__class__ is PrimaryReportSectionItem:
            term_id = int(item.get('term_id'))
            course_id = int(item.get('course_id'))
            student_id = int(item.get('student_id'))
            subject_id = int(item.get('subject_id'))

            self.make_primary_report_section(term_id, subject_id, course_id, student_id,
                comment=item.get('comment'), name=item.get('subject_name')
                )                    

        elif issubclass(item.__class__, PrimaryReportSupplementItem):
            # First get the id of the primary report, for convenience
            term_id = int(item.get('term_id'))
            course_id = int(item.get('course_id'))
            student_id = int(item.get('student_id'))
            subject_id = int(item.get('subject_id'))
            which = item.get('which')

            # Primary report should already be in the database
            primary_report = self.make_primary_report(term_id, course_id, student_id)
            primary_report_section = self.make_primary_report_section(term_id, subject_id, course_id, student_id)

            primary_report_id = primary_report.id
            primary_report_section_id = primary_report_section.id

            if issubclass(item.__class__, PrimaryReportStrandItem):

                with DBSession() as session:
                    try:
                        exists = session.query(PrimaryReportStrand).filter_by(primary_report_section_id=primary_report_section_id, which=which).one()
                        exists.label = item['strand_label']
                        exists.label_titled = item['strand_label_titled']
                        exists.selection = item['strand_text']
                        session.add(exists)

                    except NoResultFound:
                        primary_report_strand = PrimaryReportStrand(
                                primary_report_section_id = primary_report_section_id,
                                label = item['strand_label'],
                                label_titled = item['strand_label_titled'],
                                selection = item['strand_text'],
                                which = item['which']
                            )
                        session.add(primary_report_strand)

            elif issubclass(item.__class__, PrimaryReportOutcomeItem):

                ol = item['outcome_label']
                outcome_label = string_to_entities(ol)
                outcome_label_titled = string_to_entities(ol)

                with DBSession() as session:
                    try:
                        exists = session.query(PrimaryReportLo).filter_by(primary_report_section_id=primary_report_section_id, which=which).one()
                        exists.heading = item['heading']
                        exists.label = outcome_label
                        exists.selection = item['outcome_text']
                        exists.label_titled = outcome_label_titled
                        session.add(exists)

                    except NoResultFound:
                        primary_report_outcome = PrimaryReportLo(
                                primary_report_section_id = primary_report_section_id,
                                heading = item['heading'],
                                label = outcome_label,
                                label_titled = outcome_label_titled,
                                selection = item['outcome_text'],
                                which = item['which']
                            )

                        session.add(primary_report_outcome)

class PYPStudentAttendance(PostgresPipeline):
    BLANK_TOLERANCE = 100

    def database_add(self, key, item):
        Absences = self.database.table_string_to_class('PrimaryStudentAbsences')

        term_id = item['term_id']
        student_id = item['student_id']
        absences = item['absences']
        total_days = item['total_days']

        with DBSession() as session:

            try:
                exists = session.query(Absences).filter_by(term_id=term_id, student_id=student_id).one()
                if exists:
                    exists.absences = absences
                if exists:
                    exists.total_days = total_days
                session.add(exists)

            except NoResultFound:

                new = Absences(
                    student_id=student_id,
                    term_id = term_id,
                    absences=absences,
                    total_days=total_days
                    )

                session.add(new)
