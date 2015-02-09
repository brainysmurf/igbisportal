import scrapy
from ordereditem import OrderedItem

class AuditLogItem(OrderedItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    date = scrapy.Field()
    target = scrapy.Field()
    administrator = scrapy.Field()
    applicant = scrapy.Field()
    action = scrapy.Field()

class ClassPeriodItem(scrapy.Item):
    course = scrapy.Field()
    periods = scrapy.Field()

class ClassReportItem(scrapy.Item):
    student_id = scrapy.Field()
    course_id = scrapy.Field()	
    teacher_id = scrapy.Field()	
    text = scrapy.Field()	
    term_id = scrapy.Field()
    atl_comments = scrapy.Field()

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
    strand_text = scrapy.Field()

class PrimaryReportOutcomeItem(PrimaryReportSupplementItem):
    heading = scrapy.Field()
    outcome_label = scrapy.Field()
    outcome_text = scrapy.Field()   

class TeacherAssignmentItem(scrapy.Item):
    teacher_id = scrapy.Field()
    subject_id = scrapy.Field()
    class_id = scrapy.Field()

class PrimaryStudentAbsences(scrapy.Item):
    student_id = scrapy.Field()
    term_id = scrapy.Field()
    absences = scrapy.Field()
    total_days = scrapy.Field()