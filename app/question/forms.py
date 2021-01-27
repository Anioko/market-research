from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    SelectField
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from app import db
from app.models import Role, User


class AddProjectForm(FlaskForm):
    name = StringField(
        'Project Name', validators=[InputRequired(),
                                  Length(1, 64)])
    submit = SubmitField('Submit')

class AddQuestionForm(FlaskForm):
    title = StringField(
        'Question Title', validators=[InputRequired(),
                                  Length(1, 90)])
    description = StringField(
        'Description', validators=[InputRequired(),
                                  Length(1, 90)])

    multiple_choice_option_one = StringField(
        'Optional answer option e.g "Yes" ')

    multiple_choice_option_two = StringField(
        'Optional answer option e.g "No" ')
    multiple_choice_option_three = StringField(
        'Optional answer option. You can leave it empty if you selected "Yes" or "No" in the previous ones ')
    multiple_choice_option_four = StringField(
        'Optional answer option. You can leave it empty if you selected "Yes" or "No" in the previous ones')
    multiple_choice_option_five = StringField(
        'Optional answer option. You can leave it empty if you selected "Yes" or "No" in the previous ones')
    
    option_one = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_one_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    option_two = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_two_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    option_three = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_three_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    option_four = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_four_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    option_five = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_five_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    submit = SubmitField('Submit')

class EditQuestionForm(FlaskForm):
    question = StringField(
        'Question Title e.g "What is the your favourite color"')
    description = StringField(
        'Descriptions of the question e.g " This question is required so we can determine what colors you like" ')
    option_one = StringField(
        'Option One')

    option_two = StringField(
        'Option Two')
    option_three = StringField(
        'Option Three')
    option_four = StringField(
        'Option Four')
    option_five = StringField(
        'Option Five')
    submit = SubmitField('Submit')
    
class AddScreenerQuestionForm(FlaskForm):
    question = StringField(
        'Screener Question Title E.g Do you eat pancakes?', validators=[InputRequired(),
                                  Length(1, 90)])
    description = StringField(
        'Description', validators=[InputRequired(),
                                  Length(1, 90)])
    required_answer = SelectField(u'What is the required screener answer option? I.e if a respondent choses that option, we should or should not proceed with the rest of the questions. If you choose e.g "yes", we will only ask the rest of the question to respondents who answered yes to this screener question.',
                                  choices=[('Yes', 'Yes'), ('No', 'No'), ('Maybe', 'Maybe')])
    #options = SelectField(u'Please choose either Yes or No options', choices=[('Yes', 'Yes'), ('No', 'No')])
    submit = SubmitField('Submit')


class AddMultipleChoiceQuestionForm(FlaskForm):
    title = StringField(
        'Question', validators=[InputRequired(),
                                  Length(1, 90)])
    description = StringField(
        'Description', validators=[InputRequired(),
                                  Length(1, 90)])
    multiple_choice_option_one = StringField(
        'Required answer option e.g "Yes" ', validators=[InputRequired(),
                                  Length(1, 64)])

    multiple_choice_option_two = StringField(
        'Required answer option e.g "No" ', validators=[InputRequired(),
                                  Length(1, 64)])
    multiple_choice_option_three = StringField(
        'Optional answer option. You can leave it empty if you selected "Yes" or "No" in the previous ones ')
    multiple_choice_option_four = StringField(
        'Optional answer option. You can leave it empty if you selected "Yes" or "No" in the previous ones')
    multiple_choice_option_five = StringField(
        'Optional answer option. You can leave it empty if you selected "Yes" or "No" in the previous ones')
    submit = SubmitField('Submit')
      


class AddScaleQuestionForm(FlaskForm):
    title = StringField(
        'Scale-based Question Title . 60 words max, keep it short please.', validators=[InputRequired(),
                                  Length(1, 140)])
    description = StringField(
        'Description', validators=[InputRequired(),
                                  Length(1, 90)])
    option_one = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_one_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    option_two = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_two_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    option_three = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_three_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    option_four = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_four_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    option_five = SelectField(u'Please choose which answer options should be available to the respondents', choices=[('Strongly Agree', 'Strongly Agree'), ('Agree', 'Agree'),
                                                                     ('Undecided', 'Undecided'), ('Disagree', 'Disagree'),
                                                                     ('Strongly Disagree', 'Strongly Disagree'), ('Not at all useful', 'Not at all useful'),
                                                                     ('Slightly useful', 'Slightly useful'), ('Moderately useful', 'Moderately useful'),
                                                                     ('Very useful', 'Very useful'), ('Extremely useful', 'Extremely useful'),
                                                                     ('Most useful', 'Most useful'), ('Least useful', 'Least useful')])
    option_five_scale = SelectField(u'Please choose the scale for this answer option', choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10')])
    submit = SubmitField('Submit')
