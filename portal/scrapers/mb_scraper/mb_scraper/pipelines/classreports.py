from portal.db import Database, DBSession  

from portal.scrapers.shared.pipelines import PostgresPipeline

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
