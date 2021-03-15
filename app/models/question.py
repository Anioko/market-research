from .. import db
from datetime import datetime
from time import time


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
    question_type = db.Column(db.String(50), nullable=False)

    timestamp = db.Column(db.DateTime, index=True, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete="CASCADE"))
    organisation_id = db.Column(db.Integer, db.ForeignKey('organisations.id', ondelete="CASCADE"), nullable=True)

    __mapper_args__ = {
        'polymorphic_identity':'questions',
        'polymorphic_on': question_type
    }

    """    multiple_choice_option_one = db.Column(db.String(64))
        multiple_choice_option_two = db.Column(db.String(64))
        multiple_choice_option_three = db.Column(db.String(64))
        multiple_choice_option_four = db.Column(db.String(64))
        multiple_choice_option_five = db.Column(db.String(64))

        option_one = db.Column(db.String(64))
        option_two = db.Column(db.String(64))
        option_three = db.Column(db.String(64))
        option_four = db.Column(db.String(64))
        option_five = db.Column(db.String(64))
        
        option_one_scale = db.Column(db.Integer)
        option_two_scale = db.Column(db.Integer)
        option_three_scale = db.Column(db.Integer)
        option_four_scale = db.Column(db.Integer)
        option_five_scale = db.Column(db.Integer)   
        

        
        screener_question = db.relationship("ScreenerQuestion", backref=db.backref('questions'))
        scale_question = db.relationship("ScaleQuestion", backref=db.backref('questions'))
        multiple_choice_question = db.relationship("MultipleChoiceQuestion", backref=db.backref('questions'))
    """



    @property
    def org_name(self):
        from app.models import Organisation
        return Organisation.get(self.organisation_id).org_name

    @property
    def project_name(self):
        from app.models import Project
        return Project.get(self.project_id).name

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.id}>'.format(self=self)

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    location_city = db.Column(db.String, index=True)
    location_state = db.Column(db.String, index=True)
    location_ip_address = db.Column(db.String, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"))
    scale_questions_id = db.Column(db.Integer, db.ForeignKey('scale_questions.id'))
    multiple_choice_questions_id = db.Column(db.Integer, db.ForeignKey('multiple_choice_questions.id'))
    respondent = db.relationship('User')

    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    answer_type = db.Column(db.String(50), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity':'answers',
        'polymorphic_on': answer_type
    }

    """ multiple_choice_answer_one = db.Column(db.String(64), index=True)
        multiple_choice_answer_two = db.Column(db.String(64), index=True)
        multiple_choice_answer_three = db.Column(db.String(64), index=True)
        multiple_choice_answer_four = db.Column(db.String(64), index=True)
        multiple_choice_answer_five = db.Column(db.String(64), index=True)

        option_one_answer = db.Column(db.String(64), index=True)
        option_two_answer = db.Column(db.String(64), index=True)
        option_three_answer = db.Column(db.String(64), index=True)
        option_four_answer = db.Column(db.String(64), index=True)
        option_five_answer = db.Column(db.String(64), index=True)
    """

    

    
