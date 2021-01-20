from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from flask_rq import get_queue

from app import db
from app.question.forms import *
from app.decorators import admin_required
from app.email import send_email
from app.models import *
from sqlalchemy import func

question = Blueprint('question', __name__)


@question.route('/')
@login_required
def index():
    """Question dashboard page."""
   
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=Organisation.id).first_or_404()
    orgs = current_user.organisations + Organisation.query.join(OrgStaff, Organisation.id == OrgStaff.org_id). \
        filter(OrgStaff.user_id == current_user.id).all()
    question = db.session.query(Question).filter_by(user_id=current_user.id).all() 
    count = db.session.query(func.count(Question.id)).filter_by(user_id=current_user.id).scalar()
    return render_template('question/question_dashboard.html', orgs=orgs, question=question, org=org, count=count)



@question.route('/<project_id>/create/', methods=['Get', 'POST'])
@login_required
def new_question(project_id):
    #org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first_or_404()
    form = AddQuestionForm()
    if form.validate_on_submit():
        order_id = db.session.query(Project).filter_by(user_id=current_user.id).first()
        appt = Question(
            project_id = project_id,
            question=form.question.data,
            description=form.description.data,
            option_one = form.option_one.data,
            option_two = form.option_two.data,
            option_three = form.option_three.data,
            option_four = form.option_four.data,
            option_five = form.option_five.data,
            user_id=current_user.id
            )
        db.session.add(appt)
        db.session.commit()
        flash('Successfully created'.format(appt.question), 'form-success')
        return redirect(url_for('project.project_details', project_id=appt.project_id, name=appt.question))

        #return redirect(url_for('question.question_details',
                                #question_id=appt.id, name=appt.name))
    else:
        flash('ERROR! Data was not added.', 'error')
    return render_template('question/create_question.html', form=form)

@question.route('/<org_id>/<project_id>/scr/create/', methods=['Get', 'POST'])
@login_required
def new_screener_question(org_id, project_id):
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first_or_404()
    project = db.session.query(Project).filter_by(user_id=current_user.id).filter(Project.id==project_id).first()
    question = ScreenerQuestion.query.filter_by(project_id=project_id).first()
    if question is not None :
        flash('Not allowed! You can only add one screener question.', 'error')
        return redirect(url_for('project.index'))
    q = db.session.query(Question).filter_by(user_id=current_user.id).filter(Project.id==project_id).first()        
    form = AddScreenerQuestionForm()
    if form.validate_on_submit():
        appt = ScreenerQuestion(
            project_id = project.id,
            question_id = db.session.query(Question).filter_by(user_id=current_user.id).filter(Project.id==project_id).first(),
            question=form.question.data,
            description=form.description.data,
            required_answer = form.required_answer.data,
            #options = form.options.data,
            user_id=current_user.id
            )
        db.session.add(appt)
        db.session.commit()
        flash('Successfully created'.format(appt.question), 'form-success')
        return redirect(url_for('project.project_details', org_id=org_id, project_id=project_id, name=appt.question))

        #return redirect(url_for('question.question_details',
                                #question_id=appt.id, name=appt.name))
    else:
        flash('ERROR! Data was not added.', 'error')
    return render_template('question/create_screener_question.html', form=form)

@question.route('/<org_id>/<project_id>/scl/create/', methods=['Get', 'POST'])
@login_required
def new_scale_question(org_id, project_id):
    question = ScreenerQuestion.query.filter_by(project_id=project_id).first()
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first()
    if question is None :
        flash('Not allowed! You can have to start with a sceener question.', 'error')
        return redirect(url_for('question.new_screener_question', org_id=org.id, project_id=project_id))
    
    form = AddScaleQuestionForm()
    if form.validate_on_submit():
        appt = ScaleQuestion(
            project_id = project_id,
            title=form.title.data,
            description=form.description.data,

            option_one = form.option_one.data,
            option_two = form.option_two.data,
            option_three = form.option_three.data,
            option_four = form.option_four.data,
            option_five = form.option_five.data,

            option_one_scale = form.option_one_scale.data,
            option_two_scale = form.option_two_scale.data,
            option_three_scale = form.option_three_scale.data,
            option_four_scale = form.option_four_scale.data,
            option_five_scale = form.option_five_scale.data,
            
            user_id=current_user.id
            )
        db.session.add(appt)
        project = Project.query.filter(Project.id == project_id).first()
        appts = ProjectCounter(
            count_of_questions = 1,
            question_type = "scale question",
            organisation_id=org_id,
            project_id=project.id
            )
        db.session.add(appts)
        db.session.commit()
        flash('Successfully created'.format(appt.title), 'form-success')
        return redirect(url_for('project.project_details', org_id=org_id, project_id=project_id, name=project.name))

        #return redirect(url_for('question.question_details',
                                #question_id=appt.id, name=appt.name))
    else:
        flash('ERROR! Data was not added.', 'error')
    return render_template('question/create_scale_question.html', form=form)


@question.route('/<org_id>/<project_id>/mcq/create/', methods=['Get', 'POST'])
@login_required
def new_multiple_choice_question(org_id, project_id):
    question = ScreenerQuestion.query.filter_by(project_id=project_id).first()
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first()
    if question is None :
        flash('Not allowed! You can have to start with a sceener question.', 'error')
        return redirect(url_for('question.new_screener_question', org_id=org.id, project_id=project_id))
    
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first_or_404()
    form = AddMultipleChoiceQuestionForm()
    if form.validate_on_submit():
        appt = MultipleChoiceQuestion(
            project_id = project_id,
            title=form.title.data,
            description=form.description.data,

            multiple_choice_option_one = form.multiple_choice_option_one.data,
            multiple_choice_option_two = form.multiple_choice_option_two.data,
            multiple_choice_option_three = form.multiple_choice_option_three.data,
            multiple_choice_option_four = form.multiple_choice_option_four.data,
            multiple_choice_option_five = form.multiple_choice_option_five.data,
            
            user_id=current_user.id
            )
        db.session.add(appt)
        project = Project.query.filter(Project.id == project_id).first()
        appts = ProjectCounter(
            count_of_questions = 1,
            question_type = "scale question",
            organisation_id=org_id,
            project_id=project.id
            )
        db.session.add(appts)
        db.session.commit()
        flash('Successfully created'.format(appt.title), 'form-success')
        return redirect(url_for('project.project_details', org_id=org_id, project_id=project_id, name=project.name))

        #return redirect(url_for('question.question_details',
                                #question_id=appt.id, name=appt.name))
    else:
        flash('ERROR! Data was not added.', 'error')
    return render_template('question/create_multiple_choice_question.html', form=form)


@question.route('/<int:question_id>/details/<question>/')
def question_details(question_id, question):
    appts = Question.query.filter(Question.id == question_id).first_or_404()
    org_users = User.query.all()
    #orgs = Organisation.query.filter(Organisation.user_id == User.id).all()
    orgs = current_user.organisations + Organisation.query.join(OrgStaff, Organisation.id == OrgStaff.org_id). \
        filter(OrgStaff.user_id == current_user.id).all()
    return render_template('question/question_details.html', appt=appts, orgs=orgs, org_users=org_users)


@question.route('/scr/<int:question_id>/<question>/edit', methods=['Get', 'POST'])
@login_required
def edit_screener_question(question_id, question):

    question = ScreenerQuestion.query.filter_by(user_id=current_user.id).filter_by(id=question_id).first()
    if not question:
        abort(404)
    if current_user.id != question.user_id:
        abort(404)
        
    form = AddScreenerQuestionForm(obj=question)
    if form.validate_on_submit():
        #order_id = db.session.query(Organisation).filter_by(user_id=current_user.id).first()
        question.question = form.question.data
        question.description = form.description.data
        question.required_answer = form.required_answer.data
        db.session.add(question)
        db.session.commit()
        flash("Edited.", 'success')
        return redirect(url_for('project.index'))
    return render_template('question/edit_screener_question.html', question=question, form=form )


@question.route('/scl/<int:question_id>/<question>/edit', methods=['Get', 'POST'])
@login_required
def edit_scale_question(question_id, question):

    question = ScaleQuestion.query.filter_by(user_id=current_user.id).filter_by(id=question_id).first()
    if not question:
        abort(404)
    if current_user.id != question.user_id:
        abort(404)
        
    form = AddScaleQuestionForm(obj=question)
    if form.validate_on_submit():
        #order_id = db.session.query(Organisation).filter_by(user_id=current_user.id).first()
        question.title = form.title.data
        question.description = form.description.data
        question.option_one = form.option_one.data
        question.option_two = form.option_two.data
        question.option_three = form.option_three.data
        question.option_four = form.option_four.data
        question.option_five = form.option_five.data
        db.session.add(question)
        db.session.commit()
        flash("Edited.", 'success')
        #org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first()
        return redirect(url_for('project.index'))
    return render_template('question/create_scale_question.html', question=question, form=form)    

@question.route('/mcq/<int:question_id>/<question>/edit', methods=['Get', 'POST'])
@login_required
def edit_multiple_choice_question(question_id, question):

    question = MultipleChoiceQuestion.query.filter_by(user_id=current_user.id).filter_by(id=question_id).first_or_404()
    if not question:
        abort(404)
    if current_user.id != question.user_id:
        abort(404)
        
    form = AddMultipleChoiceQuestionForm(obj=question)
    if form.validate_on_submit():
        #order_id = db.session.query(Organisation).filter_by(user_id=current_user.id).first()
        question.title = form.title.data
        question.description = form.description.data
        question.multiple_choice_option_one = form.multiple_choice_option_one.data
        question.multiple_choice_option_two = form.multiple_choice_option_two.data
        question.multiple_choice_option_three = form.multiple_choice_option_three.data
        question.multiple_choice_option_four = form.multiple_choice_option_four.data
        question.multiple_choice_option_five = form.multiple_choice_option_five.data
        db.session.add(question)
        db.session.commit()
        flash("Edited.", 'success')
        return redirect(url_for('project.index'))
    return render_template('question/create_multiple_choice_question.html', question=question, form=form)

@question.route('/<question_id>/delete', methods=['GET', 'POST'])
def delete_question(question_id):
    question = Question.query.filter_by(user_id=current_user.id).filter_by(id=question_id).first_or_404()
    if current_user.id != question.user_id:
        abort(404)
    db.session.delete(question)
    db.session.commit()
    flash("Delete.", 'success')
    return redirect(url_for('question.index'))

@question.route('/<question_id>/delete', methods=['GET', 'POST'])
def delete_screener_question(question_id):
    question = ScreenerQuestion.query.filter_by(user_id=current_user.id).filter_by(id=question_id).first_or_404()
    if current_user.id != question.user_id:
        abort(404)
    db.session.delete(question)
    db.session.commit()
    flash("Delete.", 'success')
    return redirect(url_for('question.index'))
