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
    
    if request.method == "POST" and form.validate_on_submit():
        custom_answer = UAnswer.query.filter_by(u_questions_id=question_id).filter_by(user_no=form.user_no.data).first()

        if not custom_answer:
            uanswer = UAnswer(
                u_questions_id=custom_question.id,
                user_id=current_user.id,
                project_id=project_id,
                user_no=form.user_no.data,
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
        else:
            flash(
                "Sorry, the questionaire number provided for this question already has an answer!",
                "error",
            )
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

    if request.method == "POST" and form.validate_on_submit():
        screener_answer = ScreenerAnswer.query.filter_by(screener_questions_id=question_id).filter_by(user_no=form.user_no.data).first()

        if not screener_answer:
            appt = ScreenerAnswer(
                answer_option_one=form.answer_option_one.data,
                screener_questions_id=screener_question.id,
                project_id=project_id,
                user_no=form.user_no.data,
                user_id=current_user.id,
                location_city=form.city.data,
                location_state=form.state.data,
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
        else:
            flash(
                "Sorry, the questionaire number provided for this question already has an answer!",
                "error",
            )
            return redirect(
                url_for(
                    "project.project_questions",
                    project_id=project.id,
                    name=project.name,
                )
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
        project_id=project_id,
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

    if request.method == "POST" and form.validate_on_submit():
        scale_answer = ScaleAnswer.query.filter_by(scale_question_id=question_id).filter_by(user_no=form.user_no.data).first()

        if not scale_answer:
            appt = ScaleAnswer(
                scale_question_id=scale_question.id,
                user_id=current_user.id,
                project_id=project_id,
                user_no=form.user_no.data,
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
        else:
            flash(
                "Sorry, the questionaire number provided for this question already has an answer!",
                "error",
            )
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

    form = AddMultipleChoiceAnswerForm()
    if request.method == "POST" and form.validate_on_submit():
        mcq_answer = (
            MultipleChoiceAnswer.query.filter_by(project_id=project_id)
            .filter_by(multiple_choice_question_id=question_id)
            .filter_by(user_no=form.user_no.data)
            .first()
        )
        if not mcq_answer:
            answer_options = request.form.getlist("mcq_answer")
            answer_one = (
                multiple_choice_question.multiple_choice_option_one
                if multiple_choice_question.multiple_choice_option_one in answer_options
                else None
            )
            answer_two = (
                multiple_choice_question.multiple_choice_option_two
                if multiple_choice_question.multiple_choice_option_two in answer_options
                else None
            )
            answer_three = (
                multiple_choice_question.multiple_choice_option_three
                if multiple_choice_question.multiple_choice_option_three
                in answer_options
                else None
            )
            answer_four = (
                multiple_choice_question.multiple_choice_option_four
                if multiple_choice_question.multiple_choice_option_four
                in answer_options
                else None
            )

            answer_five = (
                multiple_choice_question.multiple_choice_option_five
                if multiple_choice_question.multiple_choice_option_five
                in answer_options
                else None
            )

            mcq = MultipleChoiceAnswer(
                multiple_choice_question_id=multiple_choice_question.id,
                multiple_choice_answer_one=answer_one,
                multiple_choice_answer_two=answer_two,
                multiple_choice_answer_three=answer_three,
                multiple_choice_answer_four=answer_four,
                multiple_choice_answer_five=answer_five,
                user_no=form.user_no.data,
                user_id=current_user.id,
                project_id=project.id,
            )
            db.session.add(mcq)
            db.session.commit()
            flash("Answer submitted.", "success")
            return redirect(
                url_for(
                    "question.question_details",
                    project_id=project.id,
                    name=project.name,
                )
            )
        else:
            flash(
                "Sorry, the questionaire number provided for this question already has an answer!",
                "error",
            )
            return redirect(
                url_for(
                    "project.project_questions",
                    project_id=project.id,
                    name=project.name,
                )
            )
    return render_template(
        "answer/add_multiple_choice_answer.html",
        multiple_choice_question=multiple_choice_question,
        project_id=project_id,
        form=form,
    )
