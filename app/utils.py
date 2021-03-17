import datetime
import json
import os
import random
import string
from html.parser import HTMLParser

# import cv2
from flask import url_for, abort, session, current_app, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from wtforms.fields import Field
from wtforms.widgets import HiddenInput
from wtforms.compat import text_type

# from app.models import MCart

db = SQLAlchemy()
login_manager = LoginManager()
basedir = os.path.abspath(os.path.dirname(__file__))


def get_lang_name(code):
    with open(os.path.join(basedir, "static", "json", "languages.json")) as f:
        data = json.load(f)
        try:
            return data[code]["name"]
        except:
            return None


def get_langs():
    languages = []
    with open(os.path.join(basedir, "static", "json", "languages.json")) as f:
        data = json.load(f)
        for e in data.keys():
            languages.append((e, data[e]["name"]))
    return languages


def register_template_utils(app):
    """Register Jinja 2 helpers (called from __init__.py)."""

    @app.template_test()
    def equalto(value, other):
        return value == other

    @app.template_global()
    def is_hidden_field(field):
        from wtforms.fields import HiddenField

        return isinstance(field, HiddenField)

    @app.template_filter("full_date")
    def full_date(o):
        return datetime.datetime.strptime(o.ctime(), "%a %b %d %H:%M:%S %Y").strftime(
            "%d. %B %Y"
        )

    @app.template_filter("day")
    def day(o):
        return datetime.datetime.strptime(o.ctime(), "%a %b %d %H:%M:%S %Y").day

    @app.template_filter("mon")
    def mon(o):
        return datetime.datetime.strptime(o.ctime(), "%a %b %d %H:%M:%S %Y").strftime(
            "%B"
        )

    @app.template_filter("year")
    def year(o):
        return datetime.datetime.strptime(o.ctime(), "%a %b %d %H:%M:%S %Y").year

    @app.template_filter("user")
    def user(o):
        """check if object is user"""
        from app.models import User

        return o.__class__ == User

    app.add_template_global(index_for_role)
    app.jinja_env.globals.update(
        json_load=json_load
    )  # , image_size=image_size, get_cart=get_cart)


def index_for_role(role):
    return url_for(role.index)


class CustomSelectField(Field):
    widget = HiddenInput()

    def __init__(
        self,
        label="",
        validators=None,
        multiple=False,
        choices=[],
        allow_custom=True,
        **kwargs
    ):
        super(CustomSelectField, self).__init__(label, validators, **kwargs)
        self.multiple = multiple
        self.choices = choices
        self.allow_custom = allow_custom

    def _value(self):
        return text_type(self.data) if self.data is not None else ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = valuelist[1]
            self.raw_data = [valuelist[1]]
        else:
            self.data = ""


def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime

    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ""

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"


def jsonify_object(item, only_date=False):
    new_item = {}
    for item_attr in item.__dict__:
        if not item_attr.startswith("_"):
            value = (
                item.__dict__[item_attr]
                if type(item.__dict__[item_attr]) is not datetime.datetime
                else (
                    str(item.__dict__[item_attr])
                    if not only_date
                    else str(item.__dict__[item_attr].strftime("%d. %B %Y"))
                )
            )
            new_item[item_attr] = value
    return new_item


def get_paginated_list(results):
    return_value = jsonify_object(results)
    items = []
    for item in results.items:
        items.append(jsonify_object(item))
    items.reverse()
    return_value["items"] = items
    del return_value["query"]
    return return_value


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return "".join(self.fed)


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def json_load(string):
    return json.loads(string)


def random_char(y):
    return "".join(random.choice(string.ascii_letters) for x in range(y))


class Struct:
    items = []

    def __init__(self, items=None):
        if items is None:
            items = []
        self.items = items


def redirect_url(default="index"):
    return request.args.get("next") or request.referrer or url_for(default)
