import functools
import types, typing, json, contextlib, base64, re
import copy
import flask

camel_to_snake = lambda s: re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

class SessionData(types.SimpleNamespace, typing.MutableMapping):
    @classmethod
    @property
    def __data_key__(self):
        return camel_to_snake(self.__name__)

    @typing.final
    def __setattr__(self, name, value):
        self.__dict__[name] = value
        flask.session.modified = True

    @typing.final
    def __delattr__(self, name):
        del self.__dict__[name]
        flask.session.modified = True

    @typing.final
    def __encode__(self):
        return json.dumps(self.__dict__, default = lambda o: o.__dict__).encode()

    def encode(self):
        """Override this function if you wish to change the encoding method."""
        return base64.b85encode(self.__encode__()).hex()

    @typing.final
    @classmethod
    def __decode__(cls, string):
        return json.loads(string.decode(), object_hook = lambda d: cls(**d))

    @classmethod
    def decode(cls, string):
        """Override this function if you wish to change the decoding method."""
        return cls.__decode__(base64.b85decode(bytes.fromhex(string)))

    @typing.final
    @classmethod
    @contextlib.contextmanager
    def session(cls):
        if cls.__data_key__ not in flask.session:
            flask.session[cls.__data_key__] = cls(**cls.__default_values__()).encode()
        yield (save_data := cls.decode(flask.session[cls.__data_key__]))
        if flask.session.modified:
            flask.session[cls.__data_key__] = save_data.encode()

    @classmethod
    def __default_values__(cls):
        return {k: copy.deepcopy(getattr(cls, k)) for k in cls.__annotations__}

    __getitem__ = typing.final(lambda self, key: getattr(self, key))
    __setitem__ = typing.final(__setattr__)
    __delitem__ = typing.final(__delattr__)

    __iter__ = lambda self: iter(self.__dict__)
    __len__ = lambda self: len(self.__dict__)
    __repr__ = lambda self: repr(self.__dict__)
    __str__ = types.SimpleNamespace.__repr__

class EncryptedSessionData(SessionData):
    @classmethod
    @property
    @functools.cache
    def fernet(cls):
        import cryptography.fernet
        key = flask.current_app.secret_key
        key += '=' * (32 - len(key))
        return cryptography.fernet.Fernet(
                base64.urlsafe_b64encode(key.encode())
        )
    
    def encode(self):
        return self.fernet.encrypt(base64.b85encode(self.__encode__())).hex()
    
    @classmethod
    def decode(cls, string):
        return cls.__decode__(base64.b85decode(cls.fernet.decrypt(bytes.fromhex(string))))


@contextlib.contextmanager
def session_builder(**session_data_classes):
    data = {}
    with contextlib.ExitStack() as stack:
        for k, v in session_data_classes.items():
            data[k] = stack.enter_context(v.session())
        yield data

def init_app(app):
    session_data_classes = app.config.get(
            'SESSION_DATA_CLASSES',
            {}
    )

    if session_data_classes and not app.secret_key:
        raise ValueError('Secret key not set')

    if app.config.get('SESSION_DATA_API_ENABLED', session_data_classes):
        for k, v in session_data_classes.items():
            if not issubclass(v, SessionData):
                raise TypeError(f'Expected subclass of SessionData, got {v}')

            def session_data_get():
                with v.session() as data:
                    if flask.request.args:
                        try:
                            if len(flask.request.args) == 1:
                                return flask.jsonify(getattr(data, *flask.request.args))
                            return flask.jsonify({k: getattr(data, k) for k in flask.request.args})
                        except AttributeError:
                            for k in flask.request.args:
                                if k not in data:
                                    return {'error': f'No such attribute: {k}'}, 404
                    return flask.jsonify(data.__dict__)

            app.add_url_rule(f'/api/session/{k}', f'session_data_get_{k}', session_data_get, methods = ['GET'])
        
        if not any(r.rule == '/api/routes' for r in app.url_map.iter_rules()):
            @app.route('/api/routes')
            def show_routes():
                return {
                        'endpoints': list(
                                filter(
                                        lambda x: (
                                                x.startswith('/api')
                                        ),
                                        [r.rule for r in app.url_map.iter_rules()]
                                )
                        )
                }

    if app.config.get('INJECT_SESSION_DATA', session_data_classes):
        @app.context_processor
        def inject_session_data():
            with session_builder(**session_data_classes) as session_data:
                return session_data

class SessionDataHandler:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        init_app(app)
        app.extensions['session_data_handler'] = self

if __name__ == '__main__':
    
    class User(SessionData):
        theme: str = 'light'
        metadata: dict = {
                'favorite_color': 'blue'
        }
        
    app = flask.Flask(__name__)
    app.secret_key = 'secret'
    app.config['SESSION_DATA_CLASSES'] = {'user': User}
    
    init_app(app)
    
    @app.route('/')
    def index():
        flask.session.clear()
        return flask.render_template_string('{{ session }}<br>{{ user }}')
    
    app.run(debug=True)
    
    
    