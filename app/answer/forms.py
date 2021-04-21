from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    IntegerField,
    SubmitField,
    SelectField,
    RadioField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from app import db
from app.models import Role, User, ScaleQuestion, ScreenerQuestion


class AddScreenerAnswerForm(FlaskForm):
    answer_option_one = RadioField(
        u"Please choose either Yes or No or Maybe options",
        choices=[("Yes", "Yes"), ("No", "No"), ("Maybe", "Maybe")],
    )
    state = StringField("State", [InputRequired()], render_kw={"placeholder": "City"})
    city = StringField("City", [InputRequired()], render_kw={"placeholder": "State"})
    user_no = IntegerField("Enter Questionaire No: e.g 12 ", [InputRequired()])
    submit = SubmitField("Submit")

    def screener_query():
        return ScreenerQuestion.query


class TestAnswerForm(FlaskForm):
    answer_option_one = QuerySelectField(
        "Answer Options",
        get_label="answer_option_one",
        allow_blank=False,
        # query_factory=screener_query,
        query_factory=lambda: db.session.query(ScreenerQuestion).order_by("id"),
    )
    submit = SubmitField("Submit")


class AddMultipleChoiceAnswerForm(FlaskForm):
    user_no = IntegerField("Enter Questionaire No: e.g 12 ", [InputRequired()])
    multiple_choice_option_one = StringField('Required answer option e.g "Yes" ')
    multiple_choice_option_two = StringField('Required answer option e.g "No" ')
    multiple_choice_option_three = StringField("Optional answer option. ")
    multiple_choice_option_four = StringField("Optional answer option. ")
    multiple_choice_option_five = StringField("Optional answer option. ")
    submit = SubmitField("Submit")


class AddUAnswerForm(FlaskForm):
    option_one = StringField("Answer Option one", validators=[InputRequired()])
    user_no = IntegerField("Enter Questionaire No: e.g 12 ", [InputRequired()])

    submit = SubmitField("Submit")


class AddSemanticAnswerForm(FlaskForm):
    options = SelectField(
        u"Please choose your answer options",
        choices=[
            ("Very Pleasant", "Very Pleasant"),
            ("Somewhat Pleasant", "Neither Pleasant nor Unpleasant"),
            ("Somewhat Unpleasant", "Somewhat Unpleasant"),
            ("Very Unpleasant", "Very Unpleasant"),
        ],
    )
    user_no = IntegerField("Enter Questionaire No: e.g 12 ", [InputRequired()])
    submit = SubmitField("Submit")


class AddScaleAnswerForm(FlaskForm):
    options = SelectField(
        u"Please choose one of the following ",
        choices=[
            ("Strongly Agree", "Strongly Agree"),
            ("Agree", "Agree"),
            ("Undecided", "Undecided"),
            ("Disagree", "Disagree"),
            ("Strongly Disagree", "Strongly Disagree"),
        ],
    )
    user_no = IntegerField("Enter Questionaire No: e.g 12 ", [InputRequired()])
    submit = SubmitField("Submit")
