# -*- coding: utf-8 -*-

from portal.scrapers.shared.pipelines import \
    PostgresPipeline
from portal.scrapers.pyp_class_reports.pyp_class_reports.items import \
    PrimaryReportItem, PrimaryReportSupplementItem, \
    PrimaryReportSectionItem, PrimaryReportStrandItem, \
    PrimaryReportOutcomeItem

from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from portal.utils import string_to_entities
import datetime

import gns

class PYPClassReportsPipline(PostgresPipeline):
    """

    """
    BLANK_TOLERANCE = 100   # Could use this for different things

    def make_primary_report(self, term_id, course_id, student_id, teacher_id=None, homeroom_comment=None):
        PrimaryReport = self.database.table_string_to_class('Primary_Report')
        homeroom_comment = string_to_entities(homeroom_comment) if not self.fake else self.fake.text(max_nb_chars=len(homeroom_comment) if homeroom_comment and len(homeroom_comment) > 5 else 10)
        exists = None
        with self.DBSession() as session:
            statement = session.query(PrimaryReport).filter_by(term_id=term_id, course_id=course_id, student_id=student_id)
            try:
                exists = statement.one()
                if exists and homeroom_comment is not None:
                    exists.homeroom_comment = homeroom_comment
                if exists and teacher_id is not None:
                    exists.teacher_id = teacher_id
                session.add(exists)
                if homeroom_comment:
                    gns.tutorial('There is already a report available, so execute update on database', edit=(statement, '.sql'))
                ret = exists
            except NoResultFound:
                primary_report = PrimaryReport(
                        course_id = course_id,
                        term_id = term_id,
                        homeroom_comment = homeroom_comment if not self.fake else self.fake.text(max_nb_chars=len(self.homeroom_comment) or 10),
                        teacher_id = teacher_id if not teacher_id is None else None,  # When this becomes an int, change it to an int...
                        student_id = student_id
                    )
                session.add(primary_report)
                gns.tutorial('No report yet, so execute insert on database:\n{}'.format(gns.rawsql(statement)))
                ret = primary_report
        return ret

    def make_primary_report_section(self, term_id, subject_id, course_id, student_id, comment="", name ="", overall_comment=None):
        exists = None
        comment = string_to_entities(comment)
        if comment and self.fake:
            comment = self.fake.text(max_nb_chars=len(comment) if len(comment) > 5 else 10)
        overall_comment = string_to_entities(overall_comment)
        PrimaryReportSection = self.database.table.PrimaryReportSection
        Teacher = self.database.table.Teacher
        TeacherAssignments = self.database.table.TeacherAssign

        with self.DBSession() as session:

            # Set up the teachers
            teachers = []
            teacher_assignments = session.query(TeacherAssignments).filter_by(subject_id=subject_id, class_id=course_id).all()
            for teacher in teacher_assignments:
                teachers.append( session.query(Teacher).filter_by(id=teacher.teacher_id).one() )

            primary_report = self.make_primary_report(term_id, course_id, student_id)

            try:
                exists = session.query(PrimaryReportSection).filter_by(
                        primary_report_id=primary_report.id, 
                        subject_id=subject_id
                    ).one()
                if exists:
                    if comment: 
                        exists.comment = comment
                    if name:
                        exists.name = name
                    if overall_comment is not None:
                        exists.overall_comment = overall_comment

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
                        overall_comment = overall_comment
                    )
                session.add(primary_report_section)

                for teacher in teachers:
                    primary_report_section.teachers.append( teacher )

                return primary_report_section

    def process_item(self, item, spider):
        """
        Entry point, item are sent here
        """
        Teacher = self.database.table.Teacher
        TeacherAssignments = self.database.table.TeacherAssign
        PrimaryReport = self.database.table.PrimaryReport
        PrimaryReportSection = self.database.table.PrimaryReportSection
        PrimaryReportStrand = self.database.table.PrimaryReportStrand
        PrimaryReportLo = self.database.table.PrimaryReportLo

        ret = None

        gns.tutorial("Processsing scraped item", edit=(item, '.pretty'), onlyif=item.get('course_id')==10589151 and item.get('teacher_id')==11256636, banner=True)
        if item.__class__ is PrimaryReportItem:
            term_id = int(item.get('term_id'))
            course_id = int(item.get('course_id'))
            student_id = int(item.get('student_id'))
            teacher_id = int(item.get('teacher_id'))
            homeroom_comment = item.get('homeroom_comment') if not self.fake else self.fake.text(max_nb_chars=len(item.get('homeroom_comment')) if item.get('homeroom_comment') and len(item['homeroom_comment']) > 5 else 10)

            self.make_primary_report(term_id, course_id, student_id, teacher_id, homeroom_comment)
            gns.tutorial("This is the homeroom report", banner=True, edit=(item, '.pretty'))

            with self.DBSession() as session:
                try:
                    statement = session.query(
                        self.database.table.PrimaryReportLastUpdated
                    ).filter(
                        self.database.table.PrimaryReportLastUpdated.student_id == student_id
                    )
                    record = statement.one()
                    record.timestamp = datetime.datetime.now()
                    gns.tutorial("Update last_updated fields", edit=(statement, '.sql'), stop=True)

                except NoResultFound:
                    record = self.database.table.PrimaryReportLastUpdated(
                        student_id=student_id,
                        # timestamp will be automatically added
                    )
                    gns.tutorial("Create last_updated fields:\n{}".format(record), stop=True)

                except MultipleResultsFound:
                    raise Exception("Multiple results found for student_id field, don't I need constraint?")

                session.add(record)

            ret = dict(message="Added primary homeroom report, and updated last_updated")

        elif item.__class__ is PrimaryReportSectionItem:
            term_id = int(item.get('term_id'))
            course_id = int(item.get('course_id'))
            student_id = int(item.get('student_id'))
            subject_id = int(item.get('subject_id'))

            self.make_primary_report_section(term_id, subject_id, course_id, student_id,
                comment=item.get('comment'), name=item.get('subject_name'), overall_comment=item.get('overall_comment')
                )

            ret = dict(message="Added report section")

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

                with self.DBSession() as session:
                    try:
                        exists = session.query(PrimaryReportStrand).filter_by(primary_report_section_id=primary_report_section_id, which=which).one()
                        exists.label = item['strand_label']
                        exists.label_titled = item['strand_label_titled']
                        exists.selection = item['strand_text']
                        session.add(exists)
                        ret = dict(message="Updated primary report strand")


                    except NoResultFound:
                        primary_report_strand = PrimaryReportStrand(
                                primary_report_section_id = primary_report_section_id,
                                label = item['strand_label'],
                                label_titled = item['strand_label_titled'],
                                selection = item['strand_text'],
                                which = item['which']
                            )
                        session.add(primary_report_strand)
                        ret = dict(message="Added primary report strand")

            elif issubclass(item.__class__, PrimaryReportOutcomeItem):

                ol = item['outcome_label']
                outcome_label = string_to_entities(ol)
                outcome_label_titled = string_to_entities(ol)

                with self.DBSession() as session:
                    try:
                        exists = session.query(PrimaryReportLo).filter_by(primary_report_section_id=primary_report_section_id, which=which).one()
                        exists.heading = item['heading']
                        exists.label = outcome_label
                        exists.selection = item['outcome_text']
                        exists.label_titled = outcome_label_titled
                        session.add(exists)
                        ret = dict(message="Updated primary report outcome")

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
                        ret = dict(message="Added primary report outcome")

            else:
                ret = dict(message="Item type not a recognized subclass:\n{}".format(item))

        return ret

