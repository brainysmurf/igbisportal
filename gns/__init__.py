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

    @property
    def dict_not_underscore_not_upper(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_') and not key.isupper()}

    def set_namespace(self, ns):
        setattr(self, ns, type(ns, (), {}))

    def new(self):
        for key in self.dict_not_underscore_not_upper:
            del self.__dict__[key]

    @property
    def dict_from_dict(self):
        return {key: value for key, value in self.__dict__.items() if not key.startswith('_')}

    def __call__(self, *args, **kwargs):
        return ''.join(args).format(**self.dict_from_dict)

    @classmethod
    def string(cls, astring, *args, **kwargs):
        for arg in args:
            kwargs.update(arg.__dict__)
        return cls(*args, **kwargs)(astring)

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
sys.modules['gns'] = GNS()