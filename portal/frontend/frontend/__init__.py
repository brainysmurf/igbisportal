"""
Standard boilerplate stuff for a pyramid instance
"""

from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )

import datetime

from pyramid.renderers import JSON


def datetime_adapter(obj, request):
    return obj.isoformat()


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    
    # include third-party packages here
    config.include('pyramid_chameleon')
    config.include('pyramid_beaker')

    config.add_static_view('static', 'static', cache_max_age=3600)
    json_renderer_with_adapter = JSON()
    json_renderer_with_adapter.add_adapter(datetime.datetime, datetime_adapter)
    config.add_renderer('json_with_date', json_renderer_with_adapter)

    config.add_route('favicon', '/favicon.ico')

    config.add_route('signinCallback', '/signinCallback')
    config.add_route('session_user', '/session_user')
    config.add_route('user_settings', '/user_settings')
    config.add_route('user_data', '/user_data')
    config.add_route('get_user_settings', '/get_user_settings')

    config.add_route('api-students', '/api/students')
    config.add_route('api-teachers', '/api/teachers')
    config.add_route('api-family-info', '/api/family_info')
    config.add_route('api-hapara-integration', '/api/hapara-integration')
    #config.add_route('api-test', '/api-test')

    config.add_route('mb_courses', '/mb_courses')
    config.add_route('mb_homeroom', '/mb_homeroom')
    config.add_route('mb_grade_teachers', '/mb_grade_teachers')
    config.add_route('mb_blogs', '/mb_blogs')

    config.add_route('frontpage', '/')
    config.add_route('auditlog', '/auditlog')
    config.add_route('auditlog_data', '/auditlog_data')

    config.add_route('schedule', '/schedule')
    config.add_route('schedule_data', '/schedule_data')

    config.add_route('grade_course', '/grade_course')
    config.add_route('grade_course_data', '/grade_course_data')

    config.add_route('reports', '/reports')
    config.add_route('reports_ind', '/reports/{id}')
    config.add_route('reports_ind_nice', '/reports/{id}/nice')

    config.add_route('header-html', '/header-html')
    config.add_route('footer-html', '/footer-html')

    config.add_route('students', '/students')
    config.add_route('students_ind', '/students/{id}')
    config.add_route('student_report', '/students/{id}/reports')

    config.add_route('student_pyp_report', '/students/{id}/pyp_report')
    config.add_route('student_pyp_report_with_opt', '/students/{id}/pyp_report/*pdf')
    config.add_route('student_pyp_report_no', '/students/{id}/pyp_report_no')
    config.add_route('student_pyp_ey_report', '/students/{id}/pyp_ey_report')
    #config.add_route('student_pyp_ey_report_no', '/students/{id}/pyp_ey_report_no')

    config.add_route('students_program_list', '/students/program/{program}')

    config.add_route('updateButtons', '/updateButtons')
    config.add_route('getButtons', '/getButtons')

    config.add_route('splash', '/splash')
    config.add_route('get_session_user', '/get_session_user')

    config.add_route('update_report_internal', '/update_report_internal')
    config.add_route('update_report_poll', '/update_report_poll')

    config.add_route('reports_hub', '/reports_hub')
    config.add_route('student_enrollments_by_course_id', '/student_enrollments_by_course_id/{id}')

    config.add_route('lastupdated', '/lastupdated')
    config.add_route('download_pyp_reports', '/download_pyp_reports')

    config.scan()
    return config.make_wsgi_app()
