from portal.db import Database, DBSession
from pyramid.response import Response, FileResponse
from pyramid.renderers import render
from pyramid.view import view_config
from sqlalchemy.orm import joinedload, joinedload_all

from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPForbidden
from sqlalchemy.orm.exc import NoResultFound
db = Database()
import re
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
    check = request.params.get('check')
    if check and check.lower() == 'true':
        check = True
    else:
        check = False

    internal_check = request.params.get('internal_check')

    # Lock down so that only those who are logged in or those that pass that managebac api can access
    # TODO: shouldn't be done here but in a class somewhere
    if not api_token:
        mb_user = request.session.get('mb_user', None)
        if not mb_user or not mb_user.type.startswith('Advisor'):
            return HTTPForbidden()
    else:
        if api_token != gns.config.managebac.api_token:
            return HTTPForbidden()

    term_id = 42556  # m.get('term_id')
    with DBSession() as session:
        try:
            report = session.query(PrimaryReport).\
                options(joinedload('course')).\
                filter_by(term_id=term_id, student_id=student_id).one()
            student = session.query(Students).filter_by(id=student_id).one()
        except NoResultFound:
            if pdf:
                #raw_input('no report entry for this student: {} with term_id {}'.format(student_id, term_id))
                raise HTTPNotFound()
            else:
                raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

    title = u"IGB International School (June 2016): Student Report for {} {}".format(student.first_name, student.last_name)

    # This bit is the only manual info that isn't on managebac
    uoi_table = {
        -1: {
            1: dict(title="Sharing The Planet", central_idea="We have a responsibility to share our environment for a peaceful world"),
            2: dict(title="Who We Are", central_idea="Knowing about our body helps us keep healthy."),
            3: dict(title="How the World Works", central_idea="Water is all around us and has many uses."),
            4: dict(title="How We Express Ourselves", central_idea="Stories inform, provoke us and provide enjoyment."),
        },
        0: {
            1: dict(title="Who We Are", central_idea="We are part of a community who work, live and learn together"),
            2: dict(title="How We Organise Ourselves", central_idea="People create systems, procedures and routines to fulfill a need."),
            3: dict(title="Where We Are in Place and Time", central_idea="Where we live determines what our home is like."),
            4: dict(title="Sharing the Planet", central_idea="People's choices and actions impact the environment and their community."),
            5: dict(title="How the World Works", central_idea="Our body and man made resources help protect us from the natural environment."),
            6: dict(title="How We Express Ourselves", central_idea="An audience can be engaged through performance.")
        },
        1: {
            1: dict(title="How we organize ourselves", central_idea="Humans use tools and strategies to understand and organise their environment."),
            2: dict(title="Who We Are", central_idea="Exploring how people learn helps individuals understand themselves and others better"),
            3: dict(title="How We Express Ourselves", central_idea="Celebrations are an opportunity to reflect and appreciate cultures and beliefs"),
            4: dict(title="How the World Works", central_idea="Machines make a difference to the way we live our lives."),
            5: dict(title="Sharing the Planet", central_idea="Water is essential to life and is a limited resource to many."),
            6: dict(title="Where We Are in Place and Time", central_idea="Clocks are a universal measurement tool of time that have had an impact in the past and the present."),
        },
        2: {
            1: dict(title="Who We Are", central_idea="All humans have rights and responsibilities which help them live together"),
            2: dict(title="Sharing The Planet", central_idea="Plants sustain life on earth and we have a responsible role to play"),
            3: dict(title="Where we are in Place and Time", central_idea="Influence can change people and their environment."),
            4: dict(title="How the World Works", central_idea="Forces are a vital part of our survival."),
            5: dict(title="How We Express Ourselves", central_idea="Cultures tell stories in different ways and for different reasons."),
            6: dict(title="How We Organize Ourselves", central_idea="Number system provide a common language we can use to make sense of the world."),
        },
        3: {
            1: dict(title="Sharing the Planet", central_idea="People can conserve the world's resources through responsible behaviours"),
            2: dict(title="Where We are in Place and Time", central_idea="Innovations from past civilizations have an influence on the present"),
            3: dict(title="How the World Works", central_idea="Safe structures are designed and built for purpose and consider the environment and materials."),
            4: dict(title="Who We Are", central_idea="Communication connects people and communities."),
            5: dict(title="How We Organise Ourselves", central_idea="Our bodies are made up of systems, which need to be maintained for healthy functioning."),
            6: dict(title="How We Express Ourselves", central_idea="Nature can inspire people to express their creativity."),
        },
        4: {
            1: dict(title="Sharing the Planet", central_idea="Children should have access to equal opportunities"),
            2: dict(title="How We Express Ourselves", central_idea="Media influences how we think and the choices we make"),
            3: dict(title="Where We Are in Place and Time", central_idea="The quest for understanding has led to exploration and discovery."),
            4: dict(title="How The World Works", central_idea="Earth has formed over time and is still changing."),
            5: dict(title="How we Organise Ourselves", central_idea="Societies establish systems for trade and commerce to meet needs and wants."),
            6: dict(title="Who We Are", central_idea="People's beliefs influence their actions."),
        },
        5: {
            1: dict(title="Where We Are in Place and Time", central_idea="The choices people make change their personal histories and shape their future lives"),
            2: dict(title="Sharing The Planet", central_idea="The choices we make during moments of conflict affect our relationships"),
            3: dict(title="How we Organise Ourselves", central_idea="All societies have rules and reasons for these rules"),
            4: dict(title="How the World Works", central_idea="Electricity is an energy source that humans use to enhance their lives."),
            5: dict(title="How We Express Ourselves: Exhibition", central_idea="Artists seek to evoke an emotional response from their audience."),
            6: dict(title="Who We Are", central_idea="External and internal factors cause changes in our lives"),
        },
    }

    chinese_teachers = {11256632: [11173388, 11204340, 11203889, 11324799, 11203892, 11124222, 10893375, 11080391, 11135112, 10856826, 11270692, 11135108, 10834640, 10866877, 10856824, 10865037, 11324785, 11204392, 10986488, 11563304, 11124212, 11538429, 10834648, 11201785, 11203952, 10834651, 10912649, 10837002, 11200870, 10882162, 11204001, 11204385, 10863230, 10867796, 11203954, 10834633, 11609996, 10973671, 10882159, 11204008, 11182305, 11203950, 11153067, 10856827, 10868400, 11221516, 11204401, 10882152, 11203997], 11303618: [11124209, 11204331, 11392152, 11153071, 11203893, 11124216, 11203938, 11203926, 11203933, 11502297, 10867797, 11124210, 11578945, 10882226, 11476123, 10834622, 10834621, 11203946, 11124223, 10836999, 10882227, 11204637, 11203961, 10893379, 11190071, 11182291, 11204641, 10834628, 10836994, 10834616, 10834636, 11153068, 11611847, 11274132, 11274133, 10908165, 10834656, 11204044, 11201788, 11153073], 10792613: [11490303, 11203911, 11471843, 11204634, 11203902, 11204319, 10834635, 10866876, 10837001, 11190340, 11203970, 11203923, 10882225, 11124215, 10834630, 10834649, 11204631, 10834618, 10834617, 11544715, 11274134, 10856823, 10866874, 11204383, 11274137, 11426392, 10863222, 11203979, 11581741, 10834643, 11578839, 11203988, 10834645, 11204609, 11611841, 11204605, 11153066, 11124219, 11364525, 11204000, 11204640, 10856636, 11173915, 10834625, 11274131, 10912651, 10834661, 10866873, 11182284, 11464377, 10834642, 11204017, 10913691, 11080380, 11135103, 11204377, 11204026, 11204303, 11124218, 11173912, 10836998, 10834637, 11204035]}

    students_chinese_teachers = {}

    for teacher_id, student_ids in chinese_teachers.items():
        with DBSession() as session:
            teacher = session.query(Teachers).filter_by(id=teacher_id).one()
            for this_student in student_ids:
                students_chinese_teachers[this_student] = teacher

    bahasa_teachers = {
        10872708: [10908165, 10856828],
    }
    students_bahasa_teachers = {}
    for teacher_id, student_ids in bahasa_teachers.items():
        with DBSession() as session:
            teacher = session.query(Teachers).filter_by(id=teacher_id).one()
            for this_student in student_ids:
                students_bahasa_teachers[this_student] = teacher

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
                if pdf:
                    #raw_input("No K-5 report entry")
                    raise HTTPNotFound()
                else:
                    raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

        subject_rank = {
            'language':0, 
            'mathematics':1, 
            'unit of inquiry 1':2, 
            'unit of inquiry 2':3, 
            'unit of inquiry 3':4, 
            'unit of inquiry 4': 4.1, 
            'unit of inquiry 5': 4.2, 
            'unit of inquiry 6': 4.3, 
            'art':5, 
            'music':6, 
            'physical education':7, 
            'bahasa melayu':8, 
            'chinese':9, 
            'host nation':10, 
            'self-management':10000
            }
        report.sections = sorted([section for section in report.sections if subject_rank.get(section.name.lower()) < 10000], key=lambda x: subject_rank.get(x.name.lower(), 1000))

        # Only output sections that have any data in them
        # Comment out during development
        # report.sections = [section for section in report.sections if section.comment]

        if 'Kindergarten' in report.course.grade:
            grade_norm = 0
        else:
            grade_norm = int(re.sub("[^0-9]", "", report.course.grade))

        if 'Grade 1' in report.course.name:
            # Grade 1 has three uois
            rotate_list = [0, 1, 4.1, 5, 8, 9]   # what about if there is no chinese?
            pagination_list = [0, 1, 4.3, 7, 10]
        else:
            # everyone else has four
            rotate_list = [0, 1, 2, 4, 5, 9]
            pagination_list = [0, 1, 4.2, 4.3, 7, 10]

        for section in report.sections:
            section.rank = subject_rank.get(section.name.lower())

            # Substitute the correct Chinese teachers based on manual info above
            # Do first so all subsequent operations take place properly
            if section.rank == 9 and student.id in students_chinese_teachers:
                section.teachers = [students_chinese_teachers.get(student.id)]

            if section.rank == 8 and student.id in students_bahasa_teachers:
                # Host Nations? and Bahasa mixed up maybe?
                section.teachers = [students_bahasa_teachers.get(student.id)]

            section.append_uoi_table = section.rank == 4.3
            section.display_rotated = section.rank in rotate_list

            if ('Grade 1' in report.course.name and section.rank == 4.1) or (section.rank == 4):
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

        if report.course.grade in ['Kindergarten', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5']:
            # two
            report.sections = [s for s in report.sections if s.rank not in [2,3]]
        elif report.course.grade in ['Grade 1']:
            # three
            report.sections = [s for s in report.sections if s.rank not in [2,3,4]]

    elif 'Early' in report.course.name:
        which_folder = 'early_years'
        template = 'frontend:elem_reports/templates/student_pyp_ey_report.pt'

        # 1/2: semeseter
        # 0/1: early years

        ey_report_indicators = {
            1: {
                0: [
                    {'name': 'Listening & Speaking', 'content': 'Learners show an understanding of the value of speaking and listening to communicate. They are using language to name their environment, to get to know each other, to initiate and explore relationships, to question and inquire.'},
                    {'name': 'Viewing & Presenting', 'content': 'Learners show an understanding that the world around them is full of visual language that conveys meaning. They are able to interpret and respond to visual texts. They are extending and using visual language in more purposeful ways.'},
                    {'name': 'Reading & Writing', 'content': 'Learners show an understanding that print represents the real or the imagined world. They have a concept of a "book", and an awareness of some of its structural elements. They use visual cues to recall sounds and the words they are "reading" to construct meaning.'},
                ],
                1: [
                    {'name': 'Number', 'content': 'Learners will understand that numbers are used for many different purposes in the real world. They will develop an understanding of one-to-one correspondence, be able to count and use number words and numerals to represent quantities.'},
                    {'name': 'Shape and Space',  'content': 'Learners will develop an understanding that shapes have characteristics that can be described and compared.'},
                    {'name': 'Pattern', 'content': 'Learners will develop an understanding that patterns and sequences occur in everyday situations. They will be able to identify and extend patterns in various ways.'},
                    {'name': 'Measurement', 'content': 'Learners will develop an understanding of how measurement involves the comparison of objects and  ordering.They will be able to identify and compare attributes of real objects.'},
                    {'name': 'Data', 'content': 'Learners will develop an understanding of how the collection and organization of information helps to make sense of the world. They will sort and label objects by attributes and discuss information represented in graphs including pictographs and tally marks.'}
                ]
            },
            2: {
                0: [
                    {'name':'Listening & Speaking', 'content': 'Learners will show an understanding of the value of speaking and listening to communicate. They will use language to name their environment, to get to know each other, to initiate and explore relationships, to question and inquire.'},
                    {'name':'Viewing & Presenting', 'content': 'Learners will show an understanding that the world around them is full of visual language that conveys meaning. They will interpret and respond to visual texts. They will be extending and using visual language in more purposeful ways.'},
                    {'name':'Reading & Writing', 'content': 'Learners will show an understanding that print represents the real or the imagined world. They will develop the concept of a &ldquo;book&rdquo;, and an awareness of some of its structural elements. They will use visual cues to recall sounds and the words they are &ldquo;reading&rdquo; to construct meaning.'},
                ],
                1: [
                    {'name':'Number', 'content': 'Learners will understand that numbers are used for many different purposes in the real world. They will develop an understanding of one-to-one correspondence, be able to count and use number words and numerals to represent quantities.'},
                    {'name': 'Shape and Space', 'content': 'Learners will understand and use common language to describe paths, regions and boundaries of their immediate environment.'},
                    {'name': 'Pattern', 'content': 'Learners will understand that patterns and sequences occur in everyday situations. They will be able to identify, describe, extend and create patterns in various ways.'},
                    {'name': 'Measurement', 'content': 'Learners will develop an understanding of how measurement involves the comparison of objects and the ordering and sequencing of events. They will be able to identify, compare and describe attributes of real objects as well as describe and sequence familiar events in their daily routine.'},
                    {'name': 'Data', 'content': 'Learners will develop an understanding of how the collection and organization of information helps to make sense of the world. They will sort and label objects by attributes and discuss information represented in graphs including pictographs and tally marks. The learners will discuss chance in daily events.'},
                ],
            },
        }
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
                if pdf:
                    #raw_input("no ey report found")
                    raise HTTPNotFound()
                else:
                    raise HTTPFound(location=request.route_url("student_pyp_report_no", id=student_id))

        subject_rank = {
            'self-management':-1, 
            'language':0, 
            'mathematics':1, 
            'unit of inquiry 1':2, 
            'unit of inquiry 2':3, 
            'unit of inquiry 3':4, 
            'unit of inquiry 4': 4.1, 
            'unit of inquiry 5': 4.2, 
            'unit of inquiry 6':4.3, 
            'art':5, 
            'music':6, 
            'physical education':7, 
            'bahasa melayu':8, 
            'chinese':9, 
            'host nation':10
            }

        report.sections = sorted([section for section in report.sections if subject_rank.get(section.name.lower()) < 10000], key=lambda x: subject_rank.get(x.name.lower(), 1000))
        #report.sections = report_sections
        # Filter out the un-needed units of inquiry
        #report.sections = [s for s in report.sections if s.rank <= 1 or (s.rank >= 4 and s.rank not in [4,4.1])]


        # Only output sections that have any data in them
        # Comment out during development
        #report.sections = [section for section in report.sections if section.comment and subject_rank.get(section.name.lower()) not in [2, 3]]

        grade_norm = -1

        pagination_list = [0, 4.1,7,10]

        for section in report.sections:

            section.rank = subject_rank.get(section.name.lower())

            if section.rank == -1:
                # blurb for self-management
                section.blurb = "<i><p>Within the PYP, the approaches to learning skill of self management encompasses the development of gross and fine motor skills, spatial awareness, safety, healthy lifestyles, codes of behaviour and informed choices. </p><p>In an Early Years context these are reflected through the play based approach to teaching and learning. Reporting about self management in Early Years focuses on the whole child, stressing the importance of developing independence, social and emotional skills such as making relationships, managing feelings and behaviour, self confidence and self awareness. In addition the development of physical skills (moving and handling, health and self care) are highlighted as well. </p></i>"
            else:
                section.blurb = ""

            if section.rank in [0, 1]:  # Could be Lanugage & Maths, set up the report indicators
                ey = int('Early Years 1' in report.course.name) + 1
                section.report_indicators = ey_report_indicators[ey][section.rank]   # change this to 2 later
            else:
                section.report_indicators = None

            # Substitute the correct Chinese teachers based on manual info above
            if section.rank == 9 and student.id in students_chinese_teachers:
                section.teachers = [students_chinese_teachers.get(student.id)]

            if section.rank in [999999]:    # Turn this off
                section.organization_header = "Units of Inquiry"
                section.name_after = ""
            elif section.rank in [4, 4.1]:
                section.organization_header = 'skip'
                section.name_after = ""
            else:
                section.organization_header = None
                section.name_after = ' (' + " & ".join([s.first_name + ' ' + s.last_name for s in section.teachers]) + ')'

            if section.rank in [2, 3, 4, 4.1, 4.2,4.3,4.4]:
                which_uoi = int(re.sub("[^0-9]", "", section.name))
                section.name = uoi_table.get(grade_norm)[which_uoi]['title']
                section.name_after = ""

            # Determine pagination
            if section.rank in pagination_list:  #TODO What about more than two inquiry units?
                section.pagination = True
            else:
                section.pagination = False

            if section.rank in [2, 3, 4, 4.1, 4.2,4.3,4.4]:
                section.name = section.name.title() 
                section.name_after = uoi_table.get(grade_norm)[which_uoi]['central_idea']

            section.learning_outcomes = sorted(section.learning_outcomes, key=lambda x: x.which)

        # ey sections
        report.sections = [s for s in report.sections if s.rank not in [2,3]]


    options={
        'quiet': '',
        'disable-javascript': '',
        'encoding': 'utf-8',
        'header-html': 'http://igbisportal.vagrant:6543/header-html',
        'header-spacing': '5',


        'footer-html': 'http://igbisportal.vagrant:6543/footer-html?student_id={}'.format(student.id),

        'print-media-type': '',

        'margin-left': '3mm',
        'margin-right': '3mm',
        'margin-bottom': '10mm'
        }


    if check:
        stu = student.first_nickname_last_studentid
        message = []
        for s in report.sections:
            if not s.teachers:
                message.append("No teacher assigned in {}".format(s.name))
                #raise HTTPNotFound("##No teacher assigned for {} in {}##".format(stu, s.name))
            if not s.comment:
                teachers = ",".join([t.username_handle for t in s.teachers])
                message.append('{} missing {} comment'.format(teachers, s.name))
                #raise HTTPNotFound('##{} missing {} comment for {}##'.format(teachers, s.name, stu))

            if s.learning_outcomes and not 'Early' in report.course.name:

                for o in s.learning_outcomes:
                    if hasattr(o, 'effort') and not o.effort:
                        teachers = ",".join([t.username_handle for t in s.teachers])
                        message.append('{} did not enter {} effort for {}'.format(teachers, o.heading, s.name))
                        #raise HTTPNotFound()

                    if not o.selection and 'Early Years' not in report.course.name:
                        teachers = ",".join([t.username_handle for t in s.teachers])

                        message.append('{} did not enter {} indication for {}'.format(teachers, o.heading, s.name))
                        #raise HTTPNotFound('##{} did not enter indication for {} in {}##'.format(teachers, s.name, stu))

        if message:
            raise HTTPNotFound('##\n({}) {}:\n\t{}##'.format(student.grade, student.first_nickname_last_studentid, "\n\t".join(message)))

        raise HTTPFound()

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
        path = u'/home/vagrant/igbisportal/pdf-downloads/{}/{}-Grade {}-{}.pdf'.format(which_folder, '42556', grade_norm, student.first_name + ' ' + student.last_name)
        print(path)
        pdffile = pdfkit.from_string(result, path, options=options)   # render as HTML and return as a string
        if pdf.lower() == "download":
            content_type = "application/octet-stream"

            response = FileResponse(path, request=request, content_type=content_type)
            response.content_disposition = u"attachment; filename='{}.pdf'".format(title)
            return response

        else:
            content_type = "application/pdf"
            response = FileResponse(path, request=request, content_type=content_type, charset='utf-8')
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