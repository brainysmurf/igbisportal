import scrapy


class TeacherAssignmentItem(scrapy.Item):
    teacher_id = scrapy.Field()
    subject_id = scrapy.Field()
    class_id = scrapy.Field()
