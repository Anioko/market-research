import os
import sys

from raygun4py.middleware import flask as flask_raygun

PYTHON_VERSION = sys.version_info[0]
if PYTHON_VERSION == 3:
    import urllib.parse
else:
    import urlparse

basedir = os.path.abspath(os.path.dirname(__file__))

if os.path.exists('config.env'):
    print('Importing environment from .env file')
    for line in open('config.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


class Config:
    APP_NAME = os.environ.get('APP_NAME', 'MarketResearch.ng')

    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.sendgrid.net')
    MAIL_PORT = os.environ.get('MAIL_PORT', 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', True)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', False)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Analytics
    GOOGLE_ANALYTICS_ID = os.environ.get('GOOGLE_ANALYTICS_ID', '')
    SEGMENT_API_KEY = os.environ.get('SEGMENT_API_KEY', '')

    # Admin account
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'password')
    ADMIN_EMAIL = os.environ.get(
        'ADMIN_EMAIL', 'flask-base-admin@example.com')
    EMAIL_SUBJECT_PREFIX = '[{}]'.format(APP_NAME)
    EMAIL_SENDER = '{app_name} Admin <{email}>'.format(
        app_name=APP_NAME, email=MAIL_USERNAME)

    STRIPE_PUBLISHABLE_KEY="pk_test_oqKtiHQipsUaIuR81LYSiDW2"
    STRIPE_SECRET_KEY="sk_test_hqoFMPptGIiQJSuk6Yg6B2Fr"

    REDIS_URL = os.getenv('REDISTOGO_URL', 'http://localhost:6379')
    CKEDITOR_FILE_UPLOADER = os.environ.get('CKEDITOR_FILE_UPLOADER') or 'main.upload'
    CKEDITOR_SERVE_LOCAL = os.environ.get('CKEDITOR_SERVE_LOCAL') or True
    CKEDITOR_HEIGHT = os.environ.get('CKEDITOR_HEIGHT') or 400
    CKEDITOR_ENABLE_CSRF = os.environ.get('CKEDITOR_ENABLE_CSRF') or True

    RAYGUN_APIKEY = os.environ.get('RAYGUN_APIKEY')

    # Parse the REDIS_URL to set RQ config variables
    if PYTHON_VERSION == 3:
        urllib.parse.uses_netloc.append('redis')
        url = urllib.parse.urlparse(REDIS_URL)
    else:
        urlparse.uses_netloc.append('redis')
        url = urlparse.urlparse(REDIS_URL)

    RQ_DEFAULT_HOST = url.hostname
    RQ_DEFAULT_PORT = url.port
    RQ_DEFAULT_PASSWORD = url.password
    RQ_DEFAULT_DB = 0

    UPLOADED_IMAGES_DEST = '../market-research/app/static/images/' if \
        not os.environ.get('UPLOADED_IMAGES_DEST') else os.path.dirname(os.path.realpath(__file__)) + os.environ.get(
        'UPLOADED_IMAGES_DEST')
    UPLOADED_DOCS_DEST = '../market-research/app/static/docs/' if \
        not os.environ.get('UPLOADED_DOCS_DEST') else os.path.dirname(os.path.realpath(__file__)) + os.environ.get(
        'UPLOADED_DOCS_DEST')
    docs = UPLOADED_DOCS_DEST
    UPLOADED_PATH = os.path.join(basedir, 'uploads')


    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    ASSETS_DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://wilfred:weezybaby@localhost:5432/marketresearch'
    #os.environ.get('DEV_DATABASE_URL',
        #'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite'))

    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN DEBUG MODE. \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite'))
    WTF_CSRF_ENABLED = False

    @classmethod
    def init_app(cls, app):
        print('THIS APP IS IN TESTING MODE.  \
                YOU SHOULD NOT SEE THIS IN PRODUCTION.')


class ProductionConfig(Config):
    DEBUG = False
    USE_RELOADER = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'data.sqlite'))
    SSL_DISABLE = (os.environ.get('SSL_DISABLE', 'True') == 'True')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.environ.get('SECRET_KEY'), 'SECRET_KEY IS NOT SET!'

        flask_raygun.Provider(app, app.config['RAYGUN_APIKEY']).attach()


class HerokuConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Handle proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # Log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'heroku': HerokuConfig,
    'unix': UnixConfig
}
