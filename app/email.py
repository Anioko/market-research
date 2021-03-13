import os

from flask import render_template
from flask_mail import Message
from flask_mail import Mail

from app import create_app
from sendgrid import From
from app.models import User

##from app import mail
##
##
##def send_email(recipient, subject, template, **kwargs):
##    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
##    with app.app_context():
##        msg = Message(
##            app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
##            sender=app.config['EMAIL_SENDER'],
##            recipients=[recipient])
##        msg.body = render_template(template + '.txt', **kwargs)
##        msg.html = render_template(template + '.html', **kwargs)
##        mail.send(msg)

mail = Mail()

env_file = os.path.dirname(os.path.realpath(__file__))+'/../config.env'
if os.path.exists(env_file):
    for line in open(env_file):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


def send_email(recipient, subject, template, **kwargs):
    app = create_app(os.getenv('FLASK_CONFIG') or 'default')
    app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME') or 'www.marketresearch.com.ng'
    app.config['PREFERRED_URL_SCHEME'] = os.environ.get('PREFERRED_URL_SCHEME') or 'http'
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER') or 'smtp.sendgrid.net'
    app.config['MAIL_PORT'] = os.environ.get('MAIL_PORT') or 587
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS') or True
    app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL') or False
    app.config['SSL_DISABLE'] = os.environ.get('SSL_DISABLE') or False
    app.config['MAIL_AUTH_TYPE'] = os.environ.get('MAIL_AUTH_TYPE') or 'sendgrid'
    app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY') or None
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER') or 'MarketResearch.com.ng'
    app.config['MAIL_DEFAULT_SENDER_NAME'] = os.environ.get('MAIL_DEFAULT_SENDER_NAME') or 'MarketResearch Ng Team'
    app.config['EMAIL_SENDER'] = app.config['MAIL_DEFAULT_SENDER']
    app.config['MAIL_SUPPRESS_SEND'] = False
    mail.init_app(app)
    with app.app_context():
        print()
        msg = Message(
            app.config['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
            sender=app.config['EMAIL_SENDER'],
            recipients=[recipient])
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        mail.send(msg)
