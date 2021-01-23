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
from app.project.forms import *
from app.decorators import admin_required
from app.email import send_email
from app.models import *
from sqlalchemy import func

project = Blueprint('project', __name__)


@project.route('/')
@login_required
def index():
    """project dashboard page."""
    check_point = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=Organisation.id).first()
    if check_point is None :
        flash(' You now need to add details of your organization.', 'error')
        return redirect(url_for('organisations.org_home'))   
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=Organisation.id).first_or_404()
    orgs = current_user.organisations + Organisation.query.join(OrgStaff, Organisation.id == OrgStaff.org_id). \
        filter(OrgStaff.user_id == current_user.id).all()
    
    project = db.session.query(Project).filter_by(user_id=current_user.id).all()
    question = db.session.query(Question).filter_by(user_id=current_user.id).filter(Question.project_id==Project.id).all()
    count_screener_questions = db.session.query(func.count(ScreenerQuestion.id)).filter(ScreenerQuestion.project_id == Project.id).scalar()
    count_questions = db.session.query(func.count(Question.id)).filter(Question.project_id == Project.id).scalar()
    return render_template('project/project_dashboard.html', orgs=orgs, project=project, org=org, question=question,
                           count_screener_questions=count_screener_questions, count_questions=count_questions)



@project.route('/<org_id>/create/', methods=['Get', 'POST'])
@login_required
def new_project(org_id):
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first_or_404()
    form = AddProjectForm()
    if form.validate_on_submit():
        order = db.session.query(Project).filter_by(user_id=current_user.id).count()
        appt = Project(
            organisation_id=org.id,
            name=form.name.data,
            user_id=current_user.id
            )
        db.session.add(appt)
        db.session.commit()
        flash('Successfully created'.format(appt.name), 'form-success')
        return redirect(url_for('project.index'))

        #return redirect(url_for('project.project_details',
                                #project_id=appt.id, name=appt.name))
    else:
        flash('ERROR! Data was not added.', 'error')
    return render_template('project/create_project.html', form=form, org=org)



@project.route('/<org_id>/<int:project_id>/details/<name>/')
def project_details(org_id, project_id, name):
    screener_question = ScreenerQuestion.query.filter(ScreenerQuestion.project_id == project_id).all()
    scale_question = ScaleQuestion.query.filter(ScaleQuestion.project_id == project_id).all()
    multiple_choice_question = MultipleChoiceQuestion.query.filter(MultipleChoiceQuestion.project_id == project_id).all()
    org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first_or_404()
    #count = question = Question.query.filter(Question.project_id == project_id).count()
    #question = db.session.query(Question).filter_by(user_id=current_user.id).filter(Question.project_id==Project.id).all()
    project = db.session.query(Project).filter_by(user_id=current_user.id).filter(Project.id==project_id).all()
    check_point = ScreenerQuestion.query.filter_by(user_id=current_user.id).filter_by(project_id=project_id).count()
    if check_point is None :
        flash(' You now need to add one screener question.', 'success')
        return redirect(url_for('question.new_screener_question',org_id=org.id, project_id=project.id))
    project_id=project_id
    count_screener_questions = db.session.query(func.count(ScreenerQuestion.id)).filter(ScreenerQuestion.project_id == project_id).scalar()
    count_questions = db.session.query(func.count(Question.id)).filter(Question.project_id == project_id).scalar()
    return render_template('project/project_details.html', screener_question=screener_question, project_id=project_id,
                           org=org, project=project,
                           scale_question=scale_question,
                           multiple_choice_question=multiple_choice_question,
                           count_screener_questions=count_screener_questions,
                           count_questions=count_questions)


@project.route('/<int:project_id>/<name>/edit', methods=['Get', 'POST'])
@login_required
def edit_project(project_id, name):

    project = Project.query.filter_by(user_id=current_user.id).filter_by(id=project_id).first_or_404()
    if not project:
        abort(404)
    if current_user.id != project.user_id:
        abort(404)
        
    form = AddProjectForm(obj=project)
    if form.validate_on_submit():
        #order_id = db.session.query(Organisation).filter_by(user_id=current_user.id).first()
        project.name = form.name.data
        db.session.add(project)
        db.session.commit()
        flash("Edited.", 'success')
        return redirect(url_for('project.index'))
    return render_template('project/edit_project.html', project=project,
                           form=form
                           )

@project.route('/<project_id>/delete', methods=['GET', 'POST'])
def delete_project(project_id):
    project = project.query.filter_by(user_id=current_user.id).filter_by(id=project_id).first_or_404()
    if current_user.id != project.user_id:
        abort(404)
    db.session.delete(project)
    db.session.commit()
    flash("Delete.", 'success')
    return redirect(url_for('project.index'))
