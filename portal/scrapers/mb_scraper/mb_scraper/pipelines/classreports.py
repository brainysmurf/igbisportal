from portal.db import Database, DBSession  

from portal.scrapers.shared.pipelines import \
    PostgresPipeline
from portal.scrapers.mb_scraper.mb_scraper.items import \
    PrimaryReportItem, PrimaryReportSupplementItem, \
    PrimaryReportSectionItem, PrimaryReportStrandItem, \
    PrimaryReportOutcomeItem

from sqlalchemy.orm.exc import NoResultFound

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
                # If it's already there, nothing to add or modify or update...
            except NoResultFound:            
                teacher_assign = TeacherAssign(
                        teacher_id = teacher_id,
                        subject_id = subject_id,
                        class_id = class_id
                    )
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
                    text = item['text'],
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


class PYPClassReportsPipline(PostgresPipeline):
    """

    """
    BLANK_TOLERANCE = 100   # Could use this for different things

    def allow_this_spider(self, spider):
        return spider.name.startswith('PYPClassReports')

    def database_add(self, key, item):
        Teacher = self.database.table_string_to_class('Advisor')
        TeacherAssignments = self.database.table_string_to_class('Primary_Teacher_Assignments')
        PrimaryReport = self.database.table_string_to_class('Primary_Report')
        PrimaryReportSection = self.database.table_string_to_class('Primary_Report_Section')
        PrimaryReportStrand = self.database.table_string_to_class('Primary_Report_Strand')
        PrimaryReportLo = self.database.table_string_to_class('Primary_Report_Lo')

        if issubclass(item.__class__, PrimaryReportItem):
            term_id = int(item.get('term_id'))
            course_id = int(item.get('course_id'))
            student_id = int(item.get('student_id'))
            with DBSession() as session:
                try:
                    exists = session.query(PrimaryReport).filter_by(term_id=term_id, course_id=course_id, student_id=student_id).one()
                    if exists:
                        exists.homeroom_comment = item['homeroom_comment']
                except NoResultFound:
                    primary_report = PrimaryReport(
                            course_id = course_id,
                            term_id = term_id,
                            homeroom_comment = item['homeroom_comment'],
                            teacher_id = int(item['teacher_id']) if not item['teacher_id'] is None else None,  # When this becomes an int, change it to an int...
                            student_id = student_id
                        )
                    session.add(primary_report)

        elif item.__class__ is PrimaryReportSectionItem:
            term_id = int(item.get('term_id'))
            course_id = int(item.get('course_id'))
            student_id = int(item.get('student_id'))
            subject_id = int(item.get('subject_id'))

            # Just make sure it's already set up
            with DBSession() as session:

                # Set up the teachers
                teachers = []
                teacher_assignments = session.query(TeacherAssignments).filter_by(subject_id=subject_id, class_id=course_id).all()
                for teacher in teacher_assignments:
                    teachers.append( session.query(Teacher).filter_by(id=teacher.teacher_id).one() )

                try:
                    primary_report = session.query(PrimaryReport).filter_by(term_id=term_id, course_id=course_id, student_id=student_id).one()
                except NoResultFound:
                    print("NO PRIMARY REPORT??")
                    from IPython import embed
                    embed()
                try:
                    exists = session.query(PrimaryReportSection).filter_by(primary_report_id=primary_report.id, subject_id=subject_id).one()
                    exists.comment = item['comment']
                    exists.name = item.get('subject_name', '')

                    # Sync the teachers, removing those that are gone, adding if any needed to be added
                    for teacher in exists.teachers:
                        if not teacher in teachers:
                            exists.teachers.remove(teacher)

                    for teacher in teachers:
                        if not teacher in exists.teachers:
                            exists.teachers.append(teacher)

                except NoResultFound:
                    # Shouldn't there be a teacher in here somewhere?
                    primary_report_section = PrimaryReportSection(
                            primary_report_id = primary_report.id,
                            subject_id = subject_id,
                            comment = item['comment'],
                            name = item.get('subject_name', ''),
                        )
                    session.add(primary_report_section)

                    for teacher in teachers:
                        primary_report_section.teachers.append( teacher )
                    

        elif issubclass(item.__class__, PrimaryReportSupplementItem):
            # First get the id of the primary report, for convenience
            term_id = int(item.get('term_id'))
            course_id = int(item.get('course_id'))
            student_id = int(item.get('student_id'))
            subject_id = int(item.get('subject_id'))
            which = item.get('which')

            with DBSession() as session:
                # Primary report should already be in the database
                try:
                    primary_report = session.query(PrimaryReport).filter_by(term_id=term_id, course_id=course_id, student_id=student_id).one()
                    primary_report_section = session.query(PrimaryReportSection).filter_by(primary_report_id=primary_report.id, subject_id=subject_id).one()
                except NoResultFound:
                    print("No Primary / PrimarySection?")
                    from IPython import embed
                    embed()
                primary_report_id = primary_report.id
                primary_report_section_id = primary_report_section.id

            if issubclass(item.__class__, PrimaryReportStrandItem):
                with DBSession() as session:
                    try:
                        exists = session.query(PrimaryReportStrand).filter_by(primary_report_section_id=primary_report_section_id, which=which).one()
                        exists.label = item['strand_label']
                        exists.selection = item['strand_text']
                    except NoResultFound:
                        primary_report_strand = PrimaryReportStrand(
                                primary_report_section_id = primary_report_section_id,
                                label = item['strand_label'],
                                selection = item['strand_text'],
                                which = item['which']
                            )
                        session.add(primary_report_strand)

            elif issubclass(item.__class__, PrimaryReportOutcomeItem):
                with DBSession() as session:
                    try:
                        exists = session.query(PrimaryReportLo).filter_by(primary_report_section_id=primary_report_section_id, which=which).one()
                        exists.heading = item['heading']
                        exists.label = item['outcome_label']
                        exists.selection = item['outcome_text']
                    except NoResultFound:
                        primary_report_outcome = PrimaryReportLo(
                                primary_report_section_id = primary_report_section_id,
                                heading = item['heading'],
                                label = item['outcome_label'],
                                selection = item['outcome_text'],
                                which = item['which']
                            )

                        session.add(primary_report_outcome)


