"""
Global Name Space
Simple way to have global variables defined, used throughout the app
Reads in settings.ini and provides logging as well

"""

import contextlib, os, logging
import configparser
import datetime
import click
import inspect
import functools
import pprint

class GNS(object):
    def __init__(self, *args, **kwargs):
        self.COLON = ':'
        self.CLN = ':'
        self.COMMA = ','
        self.CMMA = ','
        self.SEMICOLON = ';'
        self.NEWLINE = '\n'
        self.NWLNE = '\n'
        self.SPACE = ' '
        self.SPCE = ' '
        self.TAB = '\t'
        self.TB = '\t'
        self.SLASH = '/'
        self.LPARENS = '('
        self.RPARENS = ')'
        self.AT = '@'

        # Useful regexp phrases
        self.DOT = '.'
        self.ASTER = '*'

        self._tutorial_id = 0

        # Now, create namespaces associated with setting.ini and config

        self.set_namespace('config')
        self.set_namespace('config.paths')

        self.config.paths.home = os.sep.join(os.path.realpath(__file__).split(os.sep)[:-2]) + os.sep
        self.config.paths.settings_ini = self.config.paths.home + 'settings.ini'
        settings = configparser.ConfigParser()
        results = settings.read(self.config.paths.settings_ini)

        if not settings.sections():
            # If no settings file or a file without settings, we should exit early
            print("No sections named, is there any legit file at {}?".format(self.config.paths.settings_ini))
            os._exit()

        for SECTION in [s for s in settings.sections()]:
            section = SECTION.lower()
            self.set_namespace('config.{}'.format(section))
            for OPTION in settings.options(SECTION):
                option = OPTION.lower()
                value = settings.get(SECTION, OPTION)
                setattr(getattr(self.config, section), option, self.pythonize(value))

        path_to_logging = self('{config.paths.logging}/{date}', date=datetime.datetime.now().strftime('%x--%X').replace('/', '-'))
        #used to keep this in a file, let's just set it up right, shall we?
        log_level = self.config.logging.log_level
        numeric_level = getattr(logging, log_level.upper())
        if numeric_level is None:
            raise ValueError('Invalid log level: {}'.format(loglevel))

        logging.basicConfig(filename=path_to_logging, filemode='a+', level=numeric_level)

        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            # running with an attached terminal, automatically
            # set stdout debugging to full verbosity
            root = logging.getLogger()
            stdout_level = logging.DEBUG
            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(logging.INFO)
            root.addHandler(stdout_handler)

        # Look at settings to see what to do in terms of the step debugger
        self.set_debug(self.config.defaults.debug or False)

        env_var = os.environ.get('GNS_TUTORIAL_STOPS')
        if env_var:
            try:
                self._tutorial_stops = sorted([int(v) for v in env_var.split(' ')])
            except ValueError:
                click.echo("BAD ENV VAR GNS_TUTORIAL_STOPS passed MUST BE INTEGER")
                exit()
        else:
            self._tutorial_stops = []
        env_var = os.environ.get("GNS_TUTORIAL_ON")
        if env_var and env_var == "1":
            self.set_debug(True)

    def rawsql(self, statement, dialect=None, reindent=True):
        """Generate an SQL expression string with bound parameters rendered inline
        for the given SQLAlchemy statement. The function can also receive a
        `sqlalchemy.orm.Query` object instead of statement.
        can 

        WARNING: Should only be used for debugging. Inlining parameters is not
                 safe when handling user created data.

        TODO: Colors?
        """
        import sqlparse
        import sqlalchemy.orm
        if isinstance(statement, sqlalchemy.orm.Query):
            if dialect is None:
                dialect = statement.session.get_bind().dialect
            statement = statement.with_labels().statement
        compiled = statement.compile(dialect=dialect,
                                     compile_kwargs={'literal_binds': True})
        return sqlparse.format(str(compiled), reindent=reindent)

    def set_debug(self, value):
        self._debug = value

    def tut_defaultAcceptable(self):
        return 'codx'

    def tut_defaultMessage(self):
        highlight = functools.partial(click.style, fg='green')
        return highlight('C') + 'ontinue execution, turn ' + highlight('O') + 'ff tutorial, ' + highlight('D') + 'ebug here, or e' + highlight('x') + 'it completely?: '

    def tut_defaultHandler(self, answer):
        # Doens't do anything special
        return answer

    def tut_editAcceptable(self):
        return 'vcodx'

    def tut_editMessage(self):
        highlight = functools.partial(click.style, fg='green')
        return highlight('V') + 'iew text, ' + highlight('C') + 'ontinue execution, turn ' + highlight('O') + 'ff tutorial, ' + highlight('D') + 'ebug here, or e' + highlight('x') + 'it completely?: '

    def tut_editHandler(self, answer, edit):
        # Doens't do anything special
        if answer == 'v':
            extension = '.txt'
            if hasattr(edit, '__len__') and len(edit) == 2:
                edit, extension = edit
            if extension == '.pretty':
                # convert to pprint for us, ext is text
                edit = pprint.pformat(edit)
                extension = '.py'
            if extension == '.sql':
                edit = self.rawsql(edit)

            if edit.startswith('filename:'):
                _, edit = edit.split(':')
                click.edit(filename=edit, editor='/usr/bin/nano', require_save=False)
            click.edit(text=edit, editor='/usr/bin/nano', require_save=False, extension=extension)
            return None
        return answer

    @property
    def tutorial_on(self):
        return self._debug

    def tutorial(self, *args, bool=False, edit=None, pretty=[], stop=False, sql=None, banner=False, onlyif=None, **kwargs):
        """
        Put this in your code for two purposes:
        (1) To document it
        (2) To be able to step through just by changing a value
        """
        # If environment variable is defined, we act on that
        if not self.tutorial_on:
            return

        self._tutorial_id += 1

        if onlyif is False:
            return

        frame = inspect.currentframe().f_back

        filename = frame.f_code.co_filename.replace(self.config.paths.home, '~')
        class_name = frame.f_locals['self'].__class__.__name__ + '.' if frame.f_locals.get('self', False) else ""
        where = click.style(' ' + class_name + frame.f_code.co_name, fg="green")
        fileinfo = click.style(' ({0} L#{1.f_lineno})'.format(filename, frame), fg="yellow")
        prefix = click.style(' ' + str(self._tutorial_id) + ' ', bg="green", fg="black")
        indent = " " * (len(str(self._tutorial_id)) + 3)
        if banner:
            click.echo()
            click.echo(prefix + where + fileinfo)
            stop=True
        else:
            click.echo(prefix + " ", nl=False)
            #stop = True
        msg = " ".join(args)
        message = indent + msg + '\n' + pprint.pformat(pretty) if pretty else "" + msg

        if bool:
            return click.confirm(message)

        if edit is not None:
            m, h = self.tut_editMessage, self.tut_editHandler
        else:
            m, h = self.tut_defaultMessage, self.tut_defaultHandler

        if banner: 
            click.echo(indent, nl=False)
        click.echo(message)

        if sql:
            click.echo(self.rawsql(sql))
        prompt = m()

        if not stop and not self._tutorial_stops:
            return True

        if not stop and self._tutorial_id not in self._tutorial_stops:
            # short circuit
            return True

        answer = None
        while answer == None:
            # handler can return None if we wish to recurse
            click.echo(prompt, nl=False)
            answer = click.getchar().lower()
            click.secho(answer, fg="green")
            if edit is not None:
                answer = h(answer, edit)
            else:
                answer = h(answer)

            if answer == "d":
                # stolen from http://stackoverflow.com/questions/16867347/step-by-step-debugging-with-ipython
                # adapted after depreciation warnings
     
                # First import the embed function
                from IPython.terminal.embed import InteractiveShellEmbed
                from traitlets.config.loader import Config

                # Configure the prompt so that I know I am in a nested (embedded) shell
                cfg = Config()

                # Messages displayed when I drop into and exit the shell.
                # banner_msg = ("\n**Nested Interpreter:\n"
                # "Hit Ctrl-D to exit interpreter and continue program.\n"
                # "Note that if you use %kill_embedded, you can fully deactivate\n"
                # "This embedded instance so it will never turn on again")   
                banner_msg = ''
                exit_msg = ''

                ipshell = InteractiveShellEmbed(config=cfg, banner1=banner_msg, exit_msg=exit_msg)
                frame = inspect.currentframe().f_back
                msg   = 'Debugging in fail {0.f_code.co_filename} L#{0.f_lineno}'.format(frame)
                # Go back one level! 
                # This is needed because the call to ipshell is inside this function!
                ipshell(msg, stack_depth=2)
                answer = None

            elif answer == "o":
                # Let it go after this if desired
                self.set_debug(False)

            elif answer == "x":
                os._exit(0)

            elif answer == "i":
                # inspect what was passed
                click.echo(pprint.pprint(frame.f_locals))
                answer = None

            elif answer == "c":
                pass # no need to process

            else:
                answer == None

    @staticmethod
    def pythonize(value):
        if isinstance(value, str) or isinstance(value, unicode):
            return {
                'true':True, 'false':False, 
                'on':True, 'off':False, 
                'yes':True, 'no':False
                }.get(value.lower().strip(), value)
        return value

    def setup_verbosity(self, obj):
        obj.verbose = self.config.defaults.verbose
        if obj.verbose:
            obj.default_logger = lambda *args, **kwargs: sys.stdout.write("".join(args) + '\n')
        else:
            obj.default_logger = lambda *args, **kwargs: ()

    @property
    def dict_not_underscore_not_upper(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_') and not key.isupper()}

    def set_namespace(self, ns):
        if not '.' in ns:
            setattr(self, ns, type(ns, (), {}))
        else:
            class_name = []
            prev_class = self
            for inner in ns.split('.'):
                class_name.append(inner)
                if not hasattr(prev_class, inner):
                    setattr(prev_class, inner, type(".".join(class_name), (), {}))
                prev_class = getattr(prev_class, inner)

    def new(self):
        for key in self.dict_not_underscore_not_upper:
            del self.__dict__[key]

    def local(self):
        return self.__class__()        

    @contextlib.contextmanager
    def block(self):
        """TODO: Return __dict__ to original? """
        yield self.__class__()

    @property
    def dict_from_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    def __call__(self, *args, **kwargs):
        d = self.dict_from_dict
        d.update(kwargs)
        return ''.join(args).format(**d)

    @classmethod
    def string(cls, astring, *args, **kwargs):
        for arg in args:
            kwargs.update(arg.__dict__)
        return cls(*args, **kwargs)(astring)

    def get(self, path, default=None, required=True):
        me = self
        for inner in path.split('.'):
            if not hasattr(me, inner):
                if required:
                    raise TypeError(self('This app requires a setting for {path}', path=path))
                return default
            else:
                me = getattr(me, inner)
        return me

    @property
    def kwargs(self):
        return {key: value for key, value in self.__dict__.items() if key.islower() and not key.startswith('_')}

    @property
    def declared_kwargs(self):
        return {key: value for key, value in self.__dict__.items() if key.islower() and not key.startswith('_')}

    def __repr__(self):
        """
        VERY MEAGER WAY TO OUTPUT THIS DATA
        """
        return str(self.dict_not_underscore_not_upper)

import sys
sys.modules['gns'] = GNS()e