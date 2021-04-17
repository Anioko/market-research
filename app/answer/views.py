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
from app.answer.forms import *
from app.decorators import admin_required, respondent_required
from app.email import send_email
from app.models import *
from sqlalchemy import func


answer = Blueprint("answer", __name__)


@answer.route(
    "/<int:project_id>/<int:question_id>/<question>/ca/add/", methods=["GET", "POST"]
)
@login_required
def add_custom_answer(project_id, question_id, question):
    project = db.session.query(Project).filter_by(id=project_id).first()
    custom_question = UQuestion.query.filter_by(id=question_id).first()

    form = AddUAnswerForm()
    if request.method == "POST":
        if form.validate_on_submit():
            uanswer = UAnswer(
                u_questions_id=custom_question.id,
                user_id=current_user.id,
                project_id=project_id,
                answer_option=form.option_one.data,
            )
            db.session.add(uanswer)
            db.session.commit()

            flash("Answer submitted.", "success")
            return redirect(
                url_for(
                    "project.project_questions",
                    project_id=project.id,
                    name=project.name,
                )
            )
    return render_template(
        "answer/add_custom_answer.html",
        u_question=custom_question,
        form=form,
        project_id=project_id,
    )


@answer.route("/<int:project_id>/<int:question_id>/add/", methods=["GET", "POST"])
@login_required
def add_screener_answer(project_id, question_id):
    screener_answer_poly = with_polymorphic(Answer, [ScreenerAnswer])
    screener_question = (
        db.session.query(ScreenerQuestion).filter_by(id=question_id).first()
    )

    form = AddScreenerAnswerForm()
    project = db.session.query(Project).filter_by(id=project_id).first()
    """screener_answer = (
        db.session.query(screener_answer_poly).filter(ScreenerAnswer.project_id==project_id).first()
    )"""

    if request.method == "POST":
        if form.validate_on_submit():
            appt = ScreenerAnswer(
                answer_option_one=form.answer_option_one.data,
                screener_questions_id=screener_question.id,
                project_id=project_id,
                user_id=current_user.id,
            )
            db.session.add(appt)
            db.session.commit()
            flash("Answer submitted.", "success")
        answer = (
            db.session.query(ScreenerAnswer)
            .filter_by(user_id=current_user.id)
            .filter(ScreenerAnswer.id == appt.id)
            .first()
        )
        if answer.answer_option_one == screener_question.required_answer:
            return redirect(
                url_for(
                    "project.project_questions",
                    project_id=project.id,
                    name=project.name,
                )
            )
        else:
            flash(
                "Sorry, you cannot proceed with answers project on this project. Choose another project",
                "success",
            )
            return redirect(url_for("question.index"))

    return render_template(
        "answer/add_screener_answer.html",
        question=screener_question,
        form=form,
        project_id=project_id
    )


@answer.route(
    "/<int:project_id>/<int:question_id>/<question>/scl/add/", methods=["GET", "POST"]
)
@login_required
def add_scale_answer(project_id, question_id, question):
    project = db.session.query(Project).filter_by(id=project_id).first()

    scale_question = ScaleQuestion.query.filter_by(id=question_id).first()

    select_answer_form = ScaleQuestion.query.filter_by(id=question_id).first()

    if select_answer_form and (select_answer_form.options == "5 Point Likert Scale"):
        form = AddScaleAnswerForm()
    else:
        form = AddSemanticAnswerForm()

    if request.method == "POST":
        if form.validate_on_submit():
            appt = ScaleAnswer(
                scale_question_id=scale_question.id,
                user_id=current_user.id,
                project_id=project_id,
                option=form.options.data,
            )
            db.session.add(appt)
            db.session.commit()

            flash("Answer submitted.", "success")
            return redirect(
                url_for(
                    "project.project_questions",
                    project_id=project.id,
                    name=project.name,
                )
            )
    return render_template(
        "answer/add_scale_answer.html",
        scale_question=scale_question,
        form=form,
        project_id=project_id,
    )


@answer.route(
    "/<int:project_id>/<int:question_id>/<question>/mcl/add/", methods=["Get", "POST"]
)
@login_required
def add_multiple_choice_answer(project_id, question_id, question):

    project = db.session.query(Project).filter_by(id=project_id).first()
    question = LineItem.query.filter_by(project_id=project_id).all()

    multiple_choice_question = MultipleChoiceQuestion.query.filter_by(
        project_id=project_id
    ).first()
    """answered = (
        db.session.query(MultipleChoiceAnswer)
        .filter_by(user_id=current_user.id)
        .filter(MultipleChoiceAnswer.multiple_choice_question_id == question_id)
        .count()
    )

    if answered >= 1:
        flash("This question has already been answered by you.", "success")
        return redirect(
            url_for(
                "question.question_details", project_id=project.id, name=project.name
            )
        )"""

    form = AddMultipleChoiceAnswerForm()
    if form.validate_on_submit():
        appt = MultipleChoiceAnswer(
            multiple_choice_question_id=multiple_choice_question.id,
            multiple_choice_answer_one=form.multiple_choice_option_one.data,
            multiple_choice_answer_two=form.multiple_choice_option_two.data,
            multiple_choice_answer_three=form.multiple_choice_option_three.data,
            multiple_choice_answer_four=form.multiple_choice_option_four.data,
            multiple_choice_answer_five=form.multiple_choice_option_five.data,
            user_id=current_user.id,
            project_id=project.id,
        )
        db.session.add(appt)
        db.session.commit()
        flash("Answer submitted.", "success")
        return redirect(
            url_for(
                "question.question_details", project_id=project.id, name=project.name
            )
        )
    return render_template(
        "answer/add_multiple_choice_answer.html",
        multiple_choice_question=multiple_choice_question,
        form=form,
    )
