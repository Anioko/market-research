from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    send_from_directory,
)
from flask_login import current_user, login_required
from flask_rq import get_queue
from sqlalchemy.orm import with_polymorphic

from app import db
from app.question.forms import *
from app.decorators import admin_required, respondent_required
from app.email import send_email
from app.models import *
from sqlalchemy import func
from app.constants import QuestionTypes

question = Blueprint("question", __name__)


@question.route("/projects", defaults={"page": 1}, methods=["GET"])
@question.route("/projects/<int:page>", methods=["GET"])
@login_required
def index(page):
    """Question dashboard page."""
    # return redirect(url_for('project.index'))

    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=Organisation.id)
        .first_or_404()
    )
    orgs = (
        current_user.organisations
        + Organisation.query.join(OrgStaff, Organisation.id == OrgStaff.org_id)
        .filter(OrgStaff.user_id == current_user.id)
        .all()
    )
    # question = db.session.query(Question).filter_by(user_id=current_user.id).all()
    question = LineItem.query.paginate(page, per_page=10)
    count = (
        db.session.query(func.count(Question.id))
        .filter_by(user_id=current_user.id)
        .scalar()
    )
    return render_template(
        "question/question_dashboard.html",
        orgs=orgs,
        question=question,
        org=org,
        count=count,
    )


@question.route("/<org_id>/<project_id>/question/create/", methods=["GET", "POST"])
@login_required
def new_question(org_id, project_id):
    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first_or_404()
    )
    project = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )
    q = (
        db.session.query(Question)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )
    form = AddQuestionForm()
    if form.validate_on_submit():
        try:
            appt = Question(
                project_id=project.id,
                question_id=db.session.query(Question)
                .filter_by(user_id=current_user.id)
                .filter(Project.id == project_id)
                .first(),
                title=form.title.data,
                description=form.description.data,
                organisation_id=org_id,
                multiple_choice_option_one=form.multiple_choice_option_one.data,
                multiple_choice_option_two=form.multiple_choice_option_two.data,
                multiple_choice_option_three=form.multiple_choice_option_three.data,
                multiple_choice_option_four=form.multiple_choice_option_four.data,
                multiple_choice_option_five=form.multiple_choice_option_five.data,
                option_one=form.option_one.data,
                option_two=form.option_two.data,
                option_three=form.option_three.data,
                option_four=form.option_four.data,
                option_five=form.option_five.data,
                option_one_scale=form.option_one_scale.data,
                option_two_scale=form.option_two_scale.data,
                option_three_scale=form.option_three_scale.data,
                option_four_scale=form.option_four_scale.data,
                option_five_scale=form.option_five_scale.data,
                user_id=current_user.id,
            )
            db.session.add(appt)
            db.session.commit()
            flash("Successfully created".format(appt.question), "form-success")
            return redirect(
                url_for(
                    "project.project_details",
                    org_id=org_id,
                    project_id=project_id,
                    name=appt.question,
                )
            )
        except Exception as e:
            flash("ERROR! Data was not added.", "error")
            print(e)
    return render_template("question/create_question.html", form=form)


@question.route("/<org_id>/<project_id>/scr/create/", methods=["GET", "POST"])
@login_required
def new_screener_question(org_id, project_id):
    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first_or_404()
    )
    project = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )
    screener_questions_poly = with_polymorphic(Question, [ScreenerQuestion])

    question = (
        db.session.query(screener_questions_poly)
        .filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .first()
    )
    if question is not None:
        flash("Not allowed! You can only add one screener question.", "error")
        return redirect(url_for("project.index"))
    q = (
        db.session.query(Question)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )
    form = AddScreenerQuestionForm()
    if form.validate_on_submit():
        appt = ScreenerQuestion(
            project_id=project.id,
            title=form.question.data,
            description=form.description.data,
            required_answer=form.required_answer.data,
            answer_option_one=form.answer_option_one.data,
            answer_option_two=form.answer_option_two.data,
            answer_option_three=form.answer_option_three.data,
            question_type=QuestionTypes.ScreenerQuestion.value,
            user_id=current_user.id,
        )
        db.session.add(appt)
        db.session.commit()
        flash("Successfully created".format(appt.title), "form-success")
        return redirect(
            url_for(
                "project.project_details",
                org_id=org_id,
                project_id=project_id,
                name=appt.title,
            )
        )

        # return redirect(url_for('question.question_details',
        # question_id=appt.id, name=appt.name))
    else:
        flash("ERROR! Data was not added.", "error")
    return render_template("question/create_screener_question.html", form=form)


@question.route("/<org_id>/<project_id>/scl/create/", methods=["Get", "POST"])
@login_required
def new_scale_question(org_id, project_id):
    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first()
    )
    question = (
        db.session.query(Question)
        .filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .filter_by(question_type=QuestionTypes.ScreenerQuestion.value)
        .first()
    )
    if question is None:
        flash("Not allowed! You can have to start with a sceener question.", "error")
        return redirect(
            url_for(
                "question.new_screener_question", org_id=org.id, project_id=project_id
            )
        )

    # count_questions = db.session.query(func.count(Question.id)).filter(Question.project_id == project_id).scalar()
    # if count_questions >= 10 :
    # flash('Not allowed! You can only add a total of 10 questions.', 'error')
    # return redirect(url_for('project.index'))

    form = AddScaleQuestionForm()
    if form.validate_on_submit():
        appt = ScaleQuestion(
            project_id=project_id,
            title=form.title.data,
            description=form.description.data,
            options=form.options.data,
            user_id=current_user.id,
        )
        db.session.add(appt)

        appts = Question(
            project_id=project_id,
            organisation_id=org_id,
            title=form.title.data,
            description=form.description.data,
            question_type="Scale questions",
            user_id=current_user.id,
        )
        db.session.add(appts)
        project = Project.query.filter(Project.id == project_id).first()
        db.session.commit()
        flash("Successfully created".format(appt.title), "form-success")
        return redirect(
            url_for(
                "project.project_details",
                org_id=org_id,
                project_id=project_id,
                name=project.name,
            )
        )
        # return redirect(url_for('question.question_details',
        # question_id=appt.id, name=appt.name))
    else:
        flash("ERROR! Data was not added.", "error")
    return render_template("question/create_scale_question.html", form=form)


@question.route("/<project_id>/<question_id>/scl/create/", methods=["Get", "POST"])
@login_required
def new_scale_option(org_id, project_id):
    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first()
    )
    question = (
        ScreenerQuestion.query.filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .first()
    )
    if question is None:
        flash("Not allowed! You can have to start with a sceener question.", "error")
        return redirect(
            url_for(
                "question.new_screener_question", org_id=org.id, project_id=project_id
            )
        )

    # count_questions = db.session.query(func.count(Question.id)).filter(Question.project_id == project_id).scalar()
    # if count_questions >= 10 :
    # flash('Not allowed! You can only add a total of 10 questions.', 'error')
    # return redirect(url_for('project.index'))

    form = AddScaleQuestionForm()
    if form.validate_on_submit():
        appt = ScaleQuestion(
            project_id=project_id,
            title=form.title.data,
            description=form.description.data,
            options=form.options.data,
            user_id=current_user.id,
        )
        db.session.add(appt)

        appts = Question(
            project_id=project_id,
            organisation_id=org_id,
            title=form.title.data,
            description=form.description.data,
            question_type="Scale questions",
            option_one=form.option_one.data,
            option_two=form.option_two.data,
            option_three=form.option_three.data,
            option_four=form.option_four.data,
            option_five=form.option_five.data,
            option_one_scale=form.option_one_scale.data,
            option_two_scale=form.option_two_scale.data,
            option_three_scale=form.option_three_scale.data,
            option_four_scale=form.option_four_scale.data,
            option_five_scale=form.option_five_scale.data,
            user_id=current_user.id,
        )
        db.session.add(appts)
        project = Project.query.filter(Project.id == project_id).first()
        db.session.commit()
        flash("Successfully created".format(appt.title), "form-success")
        return redirect(
            url_for(
                "project.project_details",
                org_id=org_id,
                project_id=project_id,
                name=project.name,
            )
        )
        # return redirect(url_for('question.question_details',
        # question_id=appt.id, name=appt.name))
    else:
        flash("ERROR! Data was not added.", "error")
    return render_template("question/create_scale_option.html", form=form)


@question.route("/<org_id>/<project_id>/mcq/create/", methods=["Get", "POST"])
@login_required
def new_multiple_choice_question(org_id, project_id):
    question = (
        ScreenerQuestion.query.filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .first()
    )
    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first()
    )
    if question is None:
        flash("Not allowed! You can have to start with a sceener question.", "error")
        return redirect(
            url_for(
                "question.new_screener_question", org_id=org.id, project_id=project_id
            )
        )

    # count_questions = db.session.query(func.count(Question.id)).filter(Question.project_id == project_id).scalar()
    # if count_questions >= 10 :
    # flash('Not allowed! You can only add a total of 10 questions.', 'error')
    # return redirect(url_for('project.index'))

    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first_or_404()
    )
    form = AddMultipleChoiceQuestionForm()
    if form.validate_on_submit():
        appt = MultipleChoiceQuestion(
            project_id=project_id,
            title=form.title.data,
            description=form.description.data,
            multiple_choice_option_one=form.multiple_choice_option_one.data,
            multiple_choice_option_two=form.multiple_choice_option_two.data,
            multiple_choice_option_three=form.multiple_choice_option_three.data,
            multiple_choice_option_four=form.multiple_choice_option_four.data,
            multiple_choice_option_five=form.multiple_choice_option_five.data,
            user_id=current_user.id,
        )
        db.session.add(appt)
        """appts = Question(
            project_id = project_id,
            title=form.title.data,
            description=form.description.data,
            question_type="Multiple choice questions",

            multiple_choice_option_one = form.multiple_choice_option_one.data,
            multiple_choice_option_two = form.multiple_choice_option_two.data,
            multiple_choice_option_three = form.multiple_choice_option_three.data,
            multiple_choice_option_four = form.multiple_choice_option_four.data,
            multiple_choice_option_five = form.multiple_choice_option_five.data,
            
            user_id=current_user.id
            )
        db.session.add(appts)"""
        project = Project.query.filter(Project.id == project_id).first()
        db.session.commit()
        flash("Successfully created".format(appt.title), "form-success")
        return redirect(
            url_for(
                "project.project_details",
                org_id=org_id,
                project_id=project_id,
                name=project.name,
            )
        )

        # return redirect(url_for('question.question_details',
        # question_id=appt.id, name=appt.name))
    else:
        flash("ERROR! Data was not added.", "error")
    return render_template("question/create_multiple_choice_question.html", form=form)


@question.route("/<int:project_id>/<name>/")
def question_details(project_id, name):
    """ display all the questions for a project which has been paid for """
    project = db.session.query(Project).filter_by(id=project_id).first()
    questions = PaidProject.query.filter_by(project_id=project_id).all()
    for question in questions:
        question = question

    return render_template(
        "question/question_details.html", question=question, project=project
    )


##    answer = db.session.query(ScreenerAnswer).filter_by(user_id=current_user.id).filter(ScreenerAnswer.screener_questions_id==screener_question.id).first()
##    scale_answer = db.session.query(ScaleAnswer).filter_by(user_id=current_user.id).all()
##    multiple_choice_answer = db.session.query(MultipleChoiceAnswer).filter_by(user_id=current_user.id).all()
##    if answer is None:
##        return render_template('question/question_details.html',
##                               project=project, question=question, screener_question=screener_question,
##                               multiple_choice_question =multiple_choice_question,
##                               scale_question = scale_question, screener_answer=answer,
##                               multiple_choice_answer = multiple_choice_answer, scale_answer = scale_answer)
##
##    elif not answer.answer_option_one == screener_question.required_answer:
##        flash("Sorry, you cannot proceed with answers project on this project. Choose another project", 'success')
##        return redirect(url_for('question.index'))
##    else:
##        return render_template('question/question_details.html',
##                           project=project, question=question, screener_question=screener_question,
##                           multiple_choice_question =multiple_choice_question,
##                           scale_question = scale_question, screener_answer=answer,
##                           multiple_choice_answer = multiple_choice_answer, scale_answer = scale_answer)
##


@question.route(
    "/<org_id>/<project_id>/<int:question_id>/<question>/scr/edit/",
    methods=["Get", "POST"],
)
@login_required
def edit_screener_question(org_id, project_id, question_id, question):

    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first_or_404()
    )
    project = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )

    question = (
        ScreenerQuestion.query.filter_by(user_id=current_user.id)
        .filter_by(id=question_id)
        .first()
    )
    if not question:
        abort(404)
    if current_user.id != question.user_id:
        abort(404)

    form = AddScreenerQuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.add(question)
        db.session.commit()
        flash("Edited.", "success")
        return redirect(
            url_for(
                "project.project_details",
                org_id=org_id,
                project_id=project.id,
                name=project.name,
            )
        )
    return render_template(
        "question/edit_screener_question.html",
        question=question,
        form=form,
        org=org,
        project=project,
    )


@question.route(
    "/<org_id>/<project_id>/<int:question_id>/<question>/scl/edit/",
    methods=["Get", "POST"],
)
@login_required
def edit_scale_question(org_id, project_id, question_id, question):
    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first_or_404()
    )
    project = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )

    question = (
        ScaleQuestion.query.filter_by(user_id=current_user.id)
        .filter_by(id=question_id)
        .first()
    )
    if not question:
        abort(404)
    if current_user.id != question.user_id:
        abort(404)

    form = AddScaleQuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.add(question)
        question.project_id = project_id
        question.organisation_id = org_id
        question.title = form.title.data
        question_id = question.id
        question.description = form.description.data
        question.option_one = form.option_one.data
        question.option_two = form.option_two.data
        question.option_three = form.option_three.data
        question.option_four = form.option_four.data
        question.option_five = form.option_five.data
        question.user_id = current_user.id
        db.session.add(question)
        db.session.commit()
        flash("Edited.", "success")
        # org = Organisation.query.filter_by(user_id=current_user.id).filter_by(id=org_id).first()
        return redirect(
            url_for(
                "project.project_details",
                org_id=org_id,
                project_id=project.id,
                name=project.name,
            )
        )
    return render_template(
        "question/create_scale_question.html", question=question, form=form
    )


@question.route(
    "/<org_id>/<project_id>/<int:question_id>/<question>/mcq/edit/",
    methods=["Get", "POST"],
)
@login_required
def edit_multiple_choice_question(org_id, project_id, question_id, question):
    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first_or_404()
    )
    project = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )

    question = (
        MultipleChoiceQuestion.query.filter_by(user_id=current_user.id)
        .filter_by(id=question_id)
        .first_or_404()
    )
    if not question:
        abort(404)
    if current_user.id != question.user_id:
        abort(404)

    form = AddMultipleChoiceQuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.add(question)
        db.session.commit()
        flash("Edited.", "success")
        return redirect(
            url_for(
                "project.project_details",
                org_id=org_id,
                project_id=project.id,
                name=project.name,
            )
        )
    return render_template(
        "question/create_multiple_choice_question.html", question=question, form=form
    )


@question.route("/<question_id>/delete", methods=["GET", "POST"])
def delete_question(question_id):
    question = (
        Question.query.filter_by(user_id=current_user.id)
        .filter_by(id=question_id)
        .first_or_404()
    )
    if current_user.id != question.user_id:
        abort(404)
    db.session.delete(question)
    db.session.commit()
    flash("Delete.", "success")
    return redirect(url_for("question.index"))


@question.route("/<question_id>/delete", methods=["GET", "POST"])
def delete_screener_question(question_id):
    question = (
        ScreenerQuestion.query.filter_by(user_id=current_user.id)
        .filter_by(id=question_id)
        .first_or_404()
    )
    if current_user.id != question.user_id:
        abort(404)
    db.session.delete(question)
    db.session.commit()
    flash("Delete.", "success")
    return redirect(url_for("question.index"))
