import scrapy

class PrimaryReportItem(scrapy.Item):
    student_id = scrapy.Field()
    course_id = scrapy.Field()  
    teacher_id = scrapy.Field() 
    text = scrapy.Field()   
    term_id = scrapy.Field()
    homeroom_comment = scrapy.Field()

class PrimaryReportSectionItem(scrapy.Item):
    student_id = scrapy.Field()
    course_id = scrapy.Field()  
    term_id = scrapy.Field()
    subject_id = scrapy.Field()
    subject_name = scrapy.Field()
    overall_comment = scrapy.Field()

    name = scrapy.Field()
    comment = scrapy.Field()

class PrimaryReportSupplementItem(scrapy.Item):
    """
    Shared info about all of these
    """
    student_id = scrapy.Field()
    course_id = scrapy.Field()  
    term_id = scrapy.Field()
    subject_id = scrapy.Field()
    which = scrapy.Field()

class PrimaryReportStrandItem(PrimaryReportSupplementItem):
    strand_label = scrapy.Field()
    strand_label_titled = scrapy.Field()
    strand_text = scrapy.Field()

class PrimaryReportOutcomeItem(PrimaryReportSupplementItem):
    heading = scrapy.Field()
    outcome_label = scrapy.Field()
    outcome_label_titled = scrapy.Field()
    outcome_text = scrapy.Field()   

