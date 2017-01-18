from sqlalchemy.orm.exc import NoResultFound

from portal.scrapers.shared.pipelines import \
    PostgresPipeline
from portal.scrapers.pyp_student_attendance.pyp_student_attendance.items import \
    PrimaryStudentAbsencesItem


class PYPClassReportsPipline(PostgresPipeline):
    BLANK_TOLERANCE = 100

    def database_add(self, key, item):
        PrimaryStudentAbsences = self.database.table.PrimaryStudentAbsences

        term_id = item['term_id']
        student_id = item['student_id']
        absences = item['absences']
        total_days = item['total_days']

        with self.DBSession() as session:

            try:
                exists = session.query(PrimaryStudentAbsences).filter_by(term_id=term_id, student_id=student_id).one()
                if exists:
                    exists.absences = absences
                if exists:
                    exists.total_days = total_days
                session.add(exists)

            except NoResultFound:

                new = PrimaryStudentAbsencesItem(
                    student_id=student_id,
                    term_id=term_id,
                    absences=absences,
                    total_days=total_days
                )

                session.add(new)
