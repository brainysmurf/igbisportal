from portal.db import Database, DBSession  

from portal.scrapers.shared.pipelines import PostgresPipeline

class ClassPeriodsPipeline(PostgresPipeline):
    BLANK_TOLERANCE = 100

    def open_spider(self, spider):
        super(ClassPeriodsPipeline, self).open_spider(spider)
        #self.key = getattr(spider, 'path').format(spider.class_id, spider.program)

    def database_ismember(self, key, item):
        return False  # todo, make this work

    def database_add(self, key, item):
        Timetable = self.database.table_string_to_class('Timetable')
        with self.DBSession() as session:
            for day in item.get('periods'):
                periods = item['periods'][day]
                for period in periods:
                    timetable = Timetable(
                        course_id=item['course'],
                        day = day,
                        period=period
                        )
                    session.add(timetable)

