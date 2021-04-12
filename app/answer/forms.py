from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
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
    multiple_choice_option_one = StringField('Required answer option e.g "Yes" ')

    multiple_choice_option_two = StringField('Required answer option e.g "No" ')
    multiple_choice_option_three = StringField("Optional answer option. ")
    multiple_choice_option_four = StringField("Optional answer option. ")
    multiple_choice_option_five = StringField("Optional answer option. ")
    submit = SubmitField("Submit")


class AddUAnswerForm(FlaskForm):
    option_one = StringField("Answer Option one")
    option_two = StringField("Answer Option Two")
    option_three = StringField("Answer Option Three")
    option_four = StringField("Answer Option Four")
    option_five = StringField("Answer Option Five")
    submit = SubmitField("Submit")


class AddScaleAnswerForm(FlaskForm):
    option = SelectField(
        u"Please choose one of the following ",
        choices=[
            ("Strongly Agree", "Strongly Agree"),
            ("Agree", "Agree"),
            ("Undecided", "Undecided"),
            ("Disagree", "Disagree"),
            ("Strongly Disagree", "Strongly Disagree"),
        ],
    )
    submit = SubmitField("Submit")


class ReuseForm(FlaskForm):
    option_one_answer = StringField()
    option_two_answer = RadioField(
        u"Please choose your answer options", choices=[("Agree", "Agree")]
    )
    option_three_answer = RadioField(
        u"Please choose your answer options", choices=[("Undecided", "Undecided")]
    )
    option_four_answer = RadioField(
        u"Please choose your answer options", choices=[("Disagree", "Disagree")]
    )
    option_five_answer = RadioField(
        u"Please choose your answer options",
        choices=[("Strongly Disagree", "Strongly Disagree")],
    )
    option_six_answer = SelectField(
        u"Please choose your answer options",
        choices=[("Not at all useful", "Not at all useful")],
    )
    option_seven_answer = SelectField(
        u"Please choose your answer options",
        choices=[("Slightly useful", "Slightly useful")],
    )
    option_eight_answer = SelectField(
        u"Please choose your answer options",
        choices=[("Moderately useful", "Moderately useful")],
    )
    option_nine_answer = SelectField(
        u"Please choose your answer options", choices=[("Very useful", "Very useful")]
    )
    option_ten_answer = SelectField(
        u"Please choose your answer options",
        choices=[("Extremely useful", "Extremely useful")],
    )
    option_eleven_answer = SelectField(
        u"Please choose your answer options", choices=[("Most useful", "Most useful")]
    )
    option_twelve_answer = SelectField(
        u"Please choose your answer options", choices=[("Least useful", "Least useful")]
    )
    submit = SubmitField("Submit")


class LikertScaleForm(FlaskForm):

    option_one = SelectField(
        u"Please choose which answer options should be available to the respondents",
        choices=[
            ("Strongly Agree", "Strongly Agree"),
            ("Agree", "Agree"),
            ("Undecided", "Undecided"),
            ("Disagree", "Disagree"),
            ("Strongly Disagree", "Strongly Disagree"),
            ("Not at all useful", "Not at all useful"),
            ("Slightly useful", "Slightly useful"),
            ("Moderately useful", "Moderately useful"),
            ("Very useful", "Very useful"),
            ("Extremely useful", "Extremely useful"),
            ("Most useful", "Most useful"),
            ("Least useful", "Least useful"),
        ],
    )
    option_one_scale = SelectField(
        u"Please choose the scale for this answer option",
        choices=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
        ],
    )
    option_two = SelectField(
        u"Please choose which answer options should be available to the respondents",
        choices=[
            ("Strongly Agree", "Strongly Agree"),
            ("Agree", "Agree"),
            ("Undecided", "Undecided"),
            ("Disagree", "Disagree"),
            ("Strongly Disagree", "Strongly Disagree"),
            ("Not at all useful", "Not at all useful"),
            ("Slightly useful", "Slightly useful"),
            ("Moderately useful", "Moderately useful"),
            ("Very useful", "Very useful"),
            ("Extremely useful", "Extremely useful"),
            ("Most useful", "Most useful"),
            ("Least useful", "Least useful"),
        ],
    )
    option_two_scale = SelectField(
        u"Please choose the scale for this answer option",
        choices=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
        ],
    )
    option_three = SelectField(
        u"Please choose which answer options should be available to the respondents",
        choices=[
            ("Strongly Agree", "Strongly Agree"),
            ("Agree", "Agree"),
            ("Undecided", "Undecided"),
            ("Disagree", "Disagree"),
            ("Strongly Disagree", "Strongly Disagree"),
            ("Not at all useful", "Not at all useful"),
            ("Slightly useful", "Slightly useful"),
            ("Moderately useful", "Moderately useful"),
            ("Very useful", "Very useful"),
            ("Extremely useful", "Extremely useful"),
            ("Most useful", "Most useful"),
            ("Least useful", "Least useful"),
        ],
    )
    option_three_scale = SelectField(
        u"Please choose the scale for this answer option",
        choices=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
        ],
    )
    option_four = SelectField(
        u"Please choose which answer options should be available to the respondents",
        choices=[
            ("Strongly Agree", "Strongly Agree"),
            ("Agree", "Agree"),
            ("Undecided", "Undecided"),
            ("Disagree", "Disagree"),
            ("Strongly Disagree", "Strongly Disagree"),
            ("Not at all useful", "Not at all useful"),
            ("Slightly useful", "Slightly useful"),
            ("Moderately useful", "Moderately useful"),
            ("Very useful", "Very useful"),
            ("Extremely useful", "Extremely useful"),
            ("Most useful", "Most useful"),
            ("Least useful", "Least useful"),
        ],
    )
    option_four_scale = SelectField(
        u"Please choose the scale for this answer option",
        choices=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
        ],
    )
    option_five = SelectField(
        u"Please choose which answer options should be available to the respondents",
        choices=[
            ("Strongly Agree", "Strongly Agree"),
            ("Agree", "Agree"),
            ("Undecided", "Undecided"),
            ("Disagree", "Disagree"),
            ("Strongly Disagree", "Strongly Disagree"),
            ("Not at all useful", "Not at all useful"),
            ("Slightly useful", "Slightly useful"),
            ("Moderately useful", "Moderately useful"),
            ("Very useful", "Very useful"),
            ("Extremely useful", "Extremely useful"),
            ("Most useful", "Most useful"),
            ("Least useful", "Least useful"),
        ],
    )
    option_five_scale = SelectField(
        u"Please choose the scale for this answer option",
        choices=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
        ],
    )
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
    submit = SubmitField("Submit")
