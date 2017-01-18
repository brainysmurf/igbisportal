import scrapy


class PrimaryStudentAbsencesItem(scrapy.Item):
    student_id = scrapy.Field()
    term_id = scrapy.Field()
    absences = scrapy.Field()
    total_days = scrapy.Field()
