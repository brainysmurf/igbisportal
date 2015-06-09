from portal.db import Database, DBSession
from pyramid.response import Response, FileResponse
from pyramid.renderers import render
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, joinedload_all

from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from sqlalchemy.orm.exc import NoResultFound
db = Database()
import re
import portal.settings as settings
import gns


PrimaryReport = db.table_string_to_class('primary_report')
Students = db.table_string_to_class('student')
Teachers = db.table_string_to_class('advisor')
Absences = db.table_string_to_class('PrimaryStudentAbsences')

def get_from_matchdict(key, matchdict, default=None):
    this = matchdict.get(key, default)
    if this and len(this) == 1:
        return this[0]
    return this

@view_config(route_name='student_pyp_report_with_opt', http_cache=0)
@view_config(route_name='student_pyp_report', http_cache=0)
def pyp_reports(request):
    """
    Construct the data into a format that the report format needs for output
    """
    student_id = get_from_matchdict('id', request.matchdict)
    api_token = request.params.get('api_token')
    pdf = get_from_matchdict('pdf', request.matchdict)

    internal_check = request.params.get('internal_check')

    # Lock down so that only those who are logged in or those that pass that managebac api can access
    # TODO: shouldn't be done here but in a class somewhere
    if not api_token:
        mb_user = request.session.get('mb_user', None)
        if not mb_user or not mb_user.type.startswith('Advisor'):
            return HTTPForbidden()
    else:
        if api_token != settings.get('MANAGEBAC', 'mb_api_token'):
            return HTTPForbidden()

    term_id = 27808  # m.get('term_id')

    with DBSession() as session:
        try:
            report = session.query(PrimaryReport).\
                options(joinedload('course')).\
                filter_by(term_id=term_id, student_id=student_id).one()
            student = session.query(Students).filter_by(id=student_id).one()
        except NoResultFound:            
            raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

    title = "IGB International School (February 2015): Student Report for {} {}".format(student.first_name, student.last_name)

    # This bit is the only manual info that isn't on managebac
    uoi_table = {
        -1: {
            1: dict(title="Who We Are", central_idea="Everyday I can learn about who I am with and through others"),
            2: dict(title="Sharing The Planet", central_idea="We share the environment with a variety of creatures and it is important to respect their lives"),
            3: dict(title="How the World Works", central_idea="Understanding the way light works allows us to use it in different ways."),
            4: dict(title="How We Express Ourselves", central_idea="People create art to express how they think and feel."),
        },
        0: {
            1: dict(title="Who We Are", central_idea="We are part of a community who work, live and learn together"),
            2: dict(title="How We Organise Ourselves", central_idea="People can create products or generate new ideas when they are given the opportunity to think and work independently and in groups"),
            3: dict(title="Where We Are in Place and Time", central_idea="Where and how we live determines what our home is like"),
            4: dict(title="Sharing the Planet", central_idea="People's choices and actions impact the environment and their community"),
            5: dict(title="How the World Works", central_idea="Experimenting with the properties of air help us to understanding how it is used in a variety of ways"),
            6: dict(title="How We Express Ourselves", central_idea="Words on a page are intepreted and modified to entertain an audience")
        },
        1: {
            1: dict(title="How we organize ourselves", central_idea="Humans use maps to understand and organize their environment"),
            2: dict(title="Who we are", central_idea="Exploring different learning styles helps individuals understand each other better"),
            3: dict(title="How we express ourselves", central_idea="Celebrations are an opportunity to reflect and appreciate cultures and beliefs"),
            4: dict(title="How the World Works", central_idea="Machines have an impact on time and efficiency in our daily lives"),
            5: dict(title="Sharing the Planet", central_idea="Water is essential to life and is a limited resource to many"),
            6: dict(title="Where We Are in Place and Time", central_idea="Learning from previous generations helps us to understand the present"),
        },
        2: {
            1: dict(title="Who we are", central_idea="All humans have rights and responsibilities which help them live together"),
            2: dict(title="Sharing The Planet", central_idea="Plants sustain life on earth and play a role in our lives"),
            3: dict(title="Where we are in Place and Time", central_idea="Individuals can influence us by their actions and contributions to society"),
            4: dict(title="How the World Works", central_idea="Forces affect movement in our daily lives"),
            5: dict(title="How We Express Ourselves", central_idea="Water is essential to life an dis a limited resource to many"),
            6: dict(title="How We Organize Ourselves", central_idea="Number system provide a common language we can use to make sense of the world"),
        },
        3: {
            1: dict(title="Sharing the Planet", central_idea="Through our actions and lifestyles  we can improve how we care for the world"),
            2: dict(title="Who We Are", central_idea="Exercise and nutrition have an effect on how our body systems operate"),
            3: dict(title="How We Organise Ourselves", central_idea="Technology changes the way in which people work together"),
            4: dict(title="How the World Works", central_idea="People and nature change the states of matter"),
            5: dict(title="Where We are in Place and Time", central_idea="Past civilizations have had an impact on the present"),
            6: dict(title="How We Express Ourselves", central_idea="Nature can inspire people to express their creativity"),
        },
        4: {
            1: dict(title="Who We Are", central_idea="People's beliefs influence their actions"),
            2: dict(title="How We Express Ourselves", central_idea="Media influences how we think and the choices we make"),
            3: dict(title="Where we Are in Place and Time", central_idea="Exploration leads to discovery and develops new understandings"),
            4: dict(title="How the World Works", central_idea="The surface of the Earth has formed over time and is still changing"),
            5: dict(title="How We Organize Ourselves", central_idea="Societies establish systems for trade and commerce to meet needs and wants"),
            6: dict(title="Sharing the Planet", central_idea="Children should have access to equal opportunities"),
        },
        5: {
            1: dict(title="Sharing The Planet", central_idea="The choices we make during moments of conflict affect our relationships"),
            2: dict(title="Where we are in Place and Time", central_idea="Change affects personal histories and the future"),
            3: dict(title="How we Organise Ourselves", central_idea="Understanding time helps us to plan and organize our lives"),
            4: dict(title="Who We Are", central_idea="External and internal factors cause changes in our lives"),
            5: dict(title="How We Express Ourselves", central_idea="Artists seek to evoke an emotional response from their audience"),
            6: dict(title="How the World Works", central_idea="The way humans use energy impacts people and the environment"),
        },
    }

    chinese_teachers = {
        11131269:     # Anderina
            [10893375, 10837001, 11080391, 10866875, 10834622, 11080393, 10882226, 10882227, 10834621, 10866876],
        10792613:     # Xiaoping
            [10834635, 10882225, 10834617, 10834649, 10834618, 10836999, 10867797, 10893379, 10986169, 10837002, 10863230, 10867796, 10882159, 10882159, 10868400, 10834632, 10863220, 10863229, 10863228, 10973671],
        10792617:     # Mu Rong
            [10834645, 10866873, 10912651, 10834633, 10882155, 10834642, 10866172, 10834661],
        10792610:     # Yu Ri
            [10834656, 10834637, 10836998, 10856827, 10912650, 10834665, 10882152, 11153067, 11124218]
    }

    students_chinese_teachers = {}

    for teacher_id, student_ids in chinese_teachers.items():
        with DBSession() as session:
            teacher = session.query(Teachers).filter_by(id=teacher_id).one()
            for this_student in student_ids:
                students_chinese_teachers[this_student] = teacher

    if 'Grade' in report.course.name or 'Kindergarten' in report.course.name:
        which_folder = 'grades'
        template = 'frontend:elem_reports/templates/student_pyp_report.pt'

        with DBSession() as session:
            try:
                report = session.query(PrimaryReport).\
                    options(joinedload('course')).\
                    options(joinedload('sections')).\
                    options(joinedload('sections.learning_outcomes')).\
                    options(joinedload('sections.teachers')).\
                    options(joinedload('sections.strands')).\
                    options(joinedload('teacher')).\
                    filter_by(term_id=term_id, student_id=student_id).one()
                student = session.query(Students).filter_by(id=student_id).one()
                attendance = session.query(Absences).filter_by(term_id=term_id, student_id=student_id).one()
            except NoResultFound:
                raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

        subject_rank = {'language':0, 'mathematics':1, 'unit of inquiry 1':2, 'unit of inquiry 2':3, 'unit of inquiry 3':4, 'unit of inquiry 4': 4.1, 'unit of inquiry 5': 4.2, 'unit of inquiry 6': 4.3, 'art':5, 'music':6, 'physical education':7, 'bahasa melayu':8, 'chinese':9, 'host nation':10, 'self-management':10000}
        report.sections = sorted([section for section in report.sections if subject_rank.get(section.name.lower()) < 10000], key=lambda x: subject_rank.get(x.name.lower(), 1000))

        # Only output sections that have any data in them
        # Comment out during development
        report.sections = [section for section in report.sections if section.comment and subject_rank.get(section.name.lower()) not in [2, 3, 4]]

        if 'Kindergarten' in report.course.grade:
            grade_norm = 0
        else:
            grade_norm = int(re.sub("[^0-9]", "", report.course.grade))

        uoi_units = [r for r in report.sections if 'unit of inquiry' in r.name.lower()]
        if len(uoi_units) == 3:
            pagination_list = [0, 1, 2, 4.3, 7, 10]
        elif len(uoi_units) == 2:
            pagination_list = [0, 1, 2, 3, 4.2, 7, 10]
        elif len(uoi_units) == 1:
            pagination_list = [0, 1, 2, 4, 7, 10]
        else:
            pagination_list = []

        for section in report.sections:
            section.rank = subject_rank.get(section.name.lower())

            # Substitute the correct Chinese teachers based on manual info above
            # Do first so all subsequent operations take place properly
            if section.rank == 9 and student.id in students_chinese_teachers:
                section.teachers = [students_chinese_teachers.get(student.id)]

            section.append_uoi_table = section.rank == 4.3 if len(uoi_units) == 3 else section.rank == 4.2
            section.display_rotated = section.rank in [0, 1, 2, 5, 8, 9]

            if section.rank == 2 or section.rank == 4.1:
                section.organization_header = "Units of Inquiry"
                section.name_after = ""
            elif section.rank in [3, 4, 4.1, 4.2, 4.3]:
                section.organization_header = 'skip'
                section.name_after = ""
            else:
                section.organization_header = None
                section.name_after = ' (' + " & ".join([s.first_name + ' ' + s.last_name for s in section.teachers]) + ')'

            # Set the unit title if it needs to be
            if section.rank in [2, 3, 4, 4.1, 4.2, 4.3]:
                which_uoi = int(re.sub("[^0-9]", "", section.name))
                section.name = uoi_table.get(grade_norm)[which_uoi]['title']

            # Determine pagination
            if section.rank in pagination_list:  #TODO What about more than two inquiry units?
                section.pagination = True
            else:
                section.pagination = False

            section.learning_outcomes = sorted(section.learning_outcomes, key=lambda x: x.which)

            # Standardize the headings
            if section.rank in [2, 3, 4, 4.1, 4.2, 4.3]:
                section.name = section.name.title()
                section.name_after = uoi_table.get(grade_norm)[which_uoi]['central_idea']


            en_dash = u'\u2013'
            for outcome in section.learning_outcomes:

                if section.rank in [2, 3, 4]:
                    # Unit of inquiry
                    outcome.heading = ""

                elif section.rank not in [0, 1]:
                    outcome.heading = ""  # blank

                else:
                    # If it's a subject that we care to keep the data, standardize the format:
                    outcome.heading = outcome.heading.replace(en_dash, '-')
                    match = re.match('(.*)-', outcome.heading)
                    if match:
                        outcome.heading = match.group(1).strip()


            # Evaluates and adds data to items
            old_heading = None
            for outcome in section.learning_outcomes:

                if outcome.heading != old_heading:
                    # Mark that indicates we need to evaluate

                    if section.rank in [0, 1]:
                        # Determine the effort assigned by the teacher for this
                        effort = [s.selection for s in section.strands if s.label_titled.startswith(outcome.heading)]
                        effort = effort[0] if len(effort) == 1 else (effort[0] if len(set(effort))==1 else "<?>")
                    else:
                        effort = [s.selection for s in section.strands if s.selection]
                        effort = effort[0] if len(set(effort)) == 1 else str(effort)
                    outcome.effort = {'G': "Good", 'N': "Needs Improvement", 'O': "Outstanding"}.get(effort, None)

                    if not outcome.effort and internal_check:
                        # Raise a problem here
                        raise ReportIncomplete('something')

                old_heading = outcome.heading

                if not outcome.selection and internal_check:
                    raise ReportIncomplete('something')



    elif 'Early' in report.course.name:
        which_folder = 'early_years'
        template = 'frontend:elem_reports/templates/student_pyp_ey_report.pt'

        with DBSession() as session:
            try:
                report = session.query(PrimaryReport).\
                    options(joinedload('course')).\
                    options(joinedload('sections')).\
                    options(joinedload('sections.learning_outcomes')).\
                    options(joinedload('sections.teachers')).\
                    options(joinedload('teacher')).\
                    filter_by(term_id=term_id, student_id=student_id).one()
                student = session.query(Students).filter_by(id=student_id).one()
                attendance = session.query(Absences).filter_by(term_id=term_id, student_id=student_id).one()
            except NoResultFound:
                raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

        subject_rank = {'self-management':-1, 'language':0, 'mathematics':1, 'unit of inquiry 1':2, 'unit of inquiry 2':3, 'unit of inquiry 3':4, 'unit of inquiry 4': 4.1, 'unit of inquiry 5': 4.2, 'unit of inquiry 6':4.3, 'art':5, 'music':6, 'physical education':7, 'bahasa melayu':8, 'chinese':9, 'host nation':10}
        report.sections = sorted([section for section in report.sections if subject_rank.get(section.name.lower()) < 10000], key=lambda x: subject_rank.get(x.name.lower(), 1000))

        # Only output sections that have any data in them
        # Comment out during development
        report.sections = [section for section in report.sections if section.comment and subject_rank.get(section.name.lower()) not in [2, 3]]

        grade_norm = -1

        uoi_units = [r for r in report.sections if 'unit of inquiry' in r.name.lower()]

        if len(uoi_units) == 3:
            pagination_list = [0, 1, 2, 4.3, 7, 10]
        else:
            pagination_list = [0, 1, 2, 3, 4.2, 7, 10]

        for section in report.sections:

            section.rank = subject_rank.get(section.name.lower())

            # Substitute the correct Chinese teachers based on manual info above
            if section.rank == 9 and student.id in students_chinese_teachers:
                section.teachers = [students_chinese_teachers.get(student.id)]

            if section.rank in [4]:
                section.organization_header = "Units of Inquiry"
                section.name_after = ""
            elif section.rank in [4.1]:
                section.organization_header = 'skip'
                section.name_after = ""
            else:
                section.organization_header = None
                section.name_after = ' (' + " & ".join([s.first_name + ' ' + s.last_name for s in section.teachers]) + ')'

            if section.rank in [3, 4, 4.1]:
                which_uoi = int(re.sub("[^0-9]", "", section.name))
                section.name = uoi_table.get(grade_norm)[which_uoi]['title']
                section.name_after = ""

            # Determine pagination
            if section.rank in pagination_list:  #TODO What about more than two inquiry units?
                section.pagination = True
            else:
                section.pagination = False

            if section.rank in [2, 3, 4, 4.1]:
                section.name = section.name.title() 
                section.name_after = uoi_table.get(grade_norm)[which_uoi]['central_idea']

            section.learning_outcomes = sorted(section.learning_outcomes, key=lambda x: x.which)


    options={
        'quiet': '',
        'encoding': 'utf-8',
        'header-html': 'http://igbisportal.vagrant:6543/header-html',
        'header-spacing': '5',

        'footer-html': 'http://igbisportal.vagrant:6543/footer-html?student_id={}'.format(student.id),

        'print-media-type': '',

        'margin-left': '3mm',
        'margin-right': '3mm',
        'margin-bottom': '10mm'
        }

    if pdf:
 
        result = render(template,
                    dict(
                        title=title,
                        report=report,
                        student=student,
                        attendance=attendance,
                        pdf=True
                        ),
                    request=request)
        import pdfkit   # import here because installation on server is hard
        path = '/home/vagrant/igbisportal/pdf-downloads/{}/{}-{}-{}{}-{}.pdf'.format(which_folder, '27808', grade_norm, student.first_name.replace(' ', ''), student.last_name.replace(' ', ''), student.id)
        pdffile = pdfkit.from_string(result, path, options=options)   # render as HTML and return as a string
        
        if pdf.lower() == "download":
            content_type = "application/octet-stream"

            response = FileResponse(path, request=request, content_type=content_type)
            response.content_disposition = "attachment; filename='{}.pdf'".format(title)
            return response

        else:
            content_type = "application/pdf"

            response = FileResponse(path, request=request, content_type=content_type)
            return response

    else:
        result = render(template,
                    dict(
                        title=title,
                        report=report,
                        student=student,
                        attendance = attendance,
                        pdf=False
                        ),
                    request=request)
        response = Response(result)
        return response


@view_config(route_name="student_pyp_report_no", renderer='frontend:elem_reports/templates/student_pyp_report_no.pt')
def pyp_reports_no(request):
    return dict(title="No Such report")