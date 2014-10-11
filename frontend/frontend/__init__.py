from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.include('pyramid_redis')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('auditlog', '/auditlog')
    config.add_route('auditlog_data', '/auditlog_data')
    # config.add_route('test_polling', '/test_polling')
    # config.add_route('poll', '/poll')

    config.add_route('schedule', '/schedule')
    config.add_route('schedule_data', '/schedule_data')

    config.add_route('grade_course', '/grade_course')
    config.add_route('grade_course_data', '/grade_course_data')

    config.scan()
    return config.make_wsgi_app()
