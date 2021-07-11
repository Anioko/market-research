import io
from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    Response
)
import pandas as pd
from flask.json import jsonify
from flask_login import current_user, login_required
from flask_rq import get_queue
from sqlalchemy.orm import with_polymorphic
from sqlalchemy import func, or_

from app import answer, db
from app.project.forms import *
from app.main.forms import *
from app.decorators import admin_required
from app.email import send_email
from app.models import *
from app.constants import QuestionTypes

import stripe

from datetime import date

project = Blueprint("project", __name__)


@project.route("/")
@project.route("/org/<org_id>")
@login_required
def index(org_id=None):
    """project dashboard page."""
    org_ids = []
    if not org_id:
        check_point_org = Organisation.query.filter_by(user_id=current_user.id).first()
        orgs = Organisation.query.filter_by(user_id=current_user.id).all()
        org_ids = [_org.id for _org in orgs]
        if check_point_org is None:
            flash(" You now need to add details of your organisation.", "error")
            return redirect(url_for("organisations.org_home"))

        check_point_project = (
            Project.query.filter_by(user_id=current_user.id)
            .filter(Organisation.id.in_(org_ids))
            .first()
        )
        if check_point_project is None:
            flash(" You now need create a project.", "error")
            return redirect(url_for("organisations.org_home"))
    else:
        org_ids = [org_id]

    projects = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter(Organisation.id.in_(org_ids))
        .all()
    )

    count_screener_questions = (
        db.session.query(func.count(ScreenerQuestion.id))
        .filter(ScreenerQuestion.project_id == Project.id)
        .scalar()
    )
    answers_poly = with_polymorphic(Answer, "*")
    paid_questions = db.session.query(Question).join(Project).join(PaidProject).all()

    data_project = []

    for project in projects:
        # answers = db.session.query(Answer).filter_by(question_id=pq.id).count()
        answers = (
            db.session.query(answers_poly)
            .filter(Answer.project_id == project.id)
            .count()
        )
        project = {
            "id": project.id,
            "name": project.name,
            "currency": project.currency,
            "order_quantity": project.order_quantity,
            "service_type": project.service_type,
            "answers_count": answers,
        }
        data_project.append(project)

    return render_template(
        "project/project_dashboard.html",
        project=data_project,
        count_screener_questions=count_screener_questions,
    )


@project.route("/<project_id>/answered", methods=["GET", "POST"])
@login_required
def questions_answered(project_id):
    project = db.session.query(Project).filter_by(id=project_id).first()
    questions_poly = with_polymorphic(
        Question, [UQuestion, MultipleChoiceQuestion, ScaleQuestion, ScreenerQuestion]
    )
    questions = db.session.query(questions_poly).filter_by(project_id=project_id).all()
    return render_template(
        "respondents/answered.html", project=project, questions=questions
    )


@project.route("/<project_id>/paid/questions", methods=["GET"])
@login_required
def paid_questions_answered(project_id):
    answers_poly = with_polymorphic(Answer, "*")
    paid_questions = (
        db.session.query(Question)
        .join(Project)
        .join(PaidProject)
        .filter(Project.id == project_id)
        .all()
    )
    project = db.session.query(Project).filter_by(id=project_id).first()

    questions_stats = []
    for pq in paid_questions:
        # answers = db.session.query(Answer).filter_by(question_id=pq.id).count()
        answers = (
            db.session.query(answers_poly)
            .filter(
                or_(
                    answers_poly.UAnswer.u_questions_id == pq.id,
                    answers_poly.MultipleChoiceAnswer.multiple_choice_question_id
                    == pq.id,
                    answers_poly.ScreenerAnswer.screener_questions_id == pq.id,
                    answers_poly.ScaleAnswer.scale_question_id == pq.id,
                )
            )
            .count()
        )
        q_stat = {"title": pq.title, "answers": answers, "id": pq.id}
        questions_stats.append(q_stat)


    return render_template(
        "project/questions_answered_stats.html",
        project=project,
        questions=questions_stats,
    )


@project.route("/export/<id>", methods=["GET"])
def export(id):
    answers_poly = with_polymorphic(Answer, "*")
    paid_questions = (
        db.session.query(Question)
        .join(Project)
        .join(PaidProject)
        .filter(Project.id == id)
        .all()
    )

    questions_stats = []
    answers_count = []
    for pq in paid_questions:
        answers = (
            db.session.query(answers_poly)
            .filter(
                or_(
                    answers_poly.UAnswer.u_questions_id == pq.id,
                    answers_poly.MultipleChoiceAnswer.multiple_choice_question_id
                    == pq.id,
                    answers_poly.ScreenerAnswer.screener_questions_id == pq.id,
                    answers_poly.ScaleAnswer.scale_question_id == pq.id,
                )
            )
            .all()
        )
        ex_answers = []
        for answer in answers:
            if answer.answer_type == "scale_answers":
                ex_answers.append(answer.option)
            elif answer.answer_type == "screener_answers":
                ex_answers.append(answer.answer_option_one)
            elif answer.answer_type == "multiple_choice_answers":
                mcq_list = [answer.multiple_choice_answer_one,
                            answer.multiple_choice_answer_two,
                            answer.multiple_choice_answer_three,
                            answer.multiple_choice_answer_four,
                            answer.multiple_choice_answer_five]
                data = list(filter(None, mcq_list))
                ex_answers.append(data)
            elif answer.answer_type == "u_answers":
                ex_answers.append(answer.answer_option)

        q_stat = { "id": pq.id, "question": pq.title, "answers": ex_answers}
        answers_count.append(answers)
        questions_stats.append(q_stat)

    bio = io.BytesIO()
    pd.DataFrame(questions_stats).to_excel(bio)
    bio.seek(0)

    headers = {"Content-disposition": "attachment; filename=data.xlsx"}
    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    return Response(bio, mimetype=mimetype, headers=headers, direct_passthrough=True)


@project.route("/<org_id>/create/", methods=["Get", "POST"])
@login_required
def new_project(org_id):
    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=org_id)
        .first_or_404()
    )
    form = AddProjectForm()
    form2 = AddOrderForm()
    if form.validate_on_submit():
        order = db.session.query(Project).filter_by(user_id=current_user.id).count()
        appt = Project(
            organisation_id=org.id,
            name=form.name.data,
            order_quantity=form.order_quantity.data,
            service_type=form.service_type.data,
            currency=form.currency.data,
            user_id=current_user.id,
        )
        db.session.add(appt)
        db.session.commit()
        flash("Successfully created".format(appt.name), "form-success")
        return redirect(url_for("project.index"))

        # return redirect(url_for('project.project_details',
        # project_id=appt.id, name=appt.name))
    else:
        flash("ERROR! Data was not added.", "error")

    return render_template("project/create_project.html", form=form, org=org)


@project.route("/<int:project_id>/")
def project_questions(project_id):
    """ display all the questions for a project which has been paid for """
    project = db.session.query(Project).filter_by(id=project_id).first()
    screener_q = (
        db.session.query(ScreenerQuestion).filter_by(project_id=project_id).first()
    )
    screener_a = (
        db.session.query(ScreenerAnswer).filter_by(project_id=project_id).first()
    )

    screener_passed = False
    if screener_a and (screener_q.required_answer == screener_a.answer_option_one):
        screener_passed = True

    questions = db.session.query(Question).filter_by(project_id=project_id).all()

    return render_template(
        "question/question_details.html",
        questions=questions,
        project=project,
        screener_passed=screener_passed,
    )


@project.route("/<int:project_id>/details/<name>/", methods=["GET", "POST"])
def project_details(project_id, name):
    screener_questions_poly = with_polymorphic(Question, [ScreenerQuestion])

    check_point = (
        db.session.query(screener_questions_poly)
        .filter(ScreenerQuestion.user_id == current_user.id)
        .filter(ScreenerQuestion.project_id == project_id)
        .count()
    )
    if check_point is None:
        flash(" You now need to add one screener question.", "success")
        return redirect(
            url_for("question.new_screener_question", project_id=project_id)
        )

    # screener_question = ScreenerQuestion.query.filter_by(user_id=current_user.id).filter(project_id ==project_id).all()
    screener_question = (
        db.session.query(Question)
        .filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .filter_by(question_type=QuestionTypes.ScreenerQuestion.value)
        .all()
    )

    custom_questions = (
        db.session.query(UQuestion)
        .filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .all()
    )

    scale_question = (
        db.session.query(Question)
        .filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .filter_by(question_type=QuestionTypes.ScaleQuestion.value)
        .all()
    )
    multiple_choice_question = (
        db.session.query(Question)
        .filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .filter_by(question_type=QuestionTypes.MultipleChoiceQuestion.value)
        .all()
    )
    project = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter_by(id=project_id)
        .first()
    )

    # count_screener_questions = ScreenerQuestion.query.filter_by(user_id=current_user.id).filter(project_id==project_id).first()
    count_screener_questions = len(screener_question)

    # count_questions = Question.query.filter_by(user_id=current_user.id).filter(project_id == project_id).count()
    count_questions = (
        db.session.query(Question)
        .filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .count()
    )

    ## prepare line items
    project_item = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter_by(id=project_id)
        .first()
    )
    ## calculate currency
    currency = project_item.currency
    if currency == "NGN" and project_item.service_type == "Silver":
        unit_amount = 6600
    elif currency == "NGN" and project_item.service_type == "Gold":
        unit_amount = 9000
    elif currency == "NGN" and project_item.service_type == "Platinum":
        unit_amount = 12000
    elif currency == "USD" and project_item.service_type == "Silver":
        unit_amount = 200
    elif currency == "USD" and project_item.service_type == "Gold":
        unit_amount = 250
    elif currency == "USD" and project_item.service_type == "Platinum":
        unit_amount = 300
    elif currency == "GBP" and project_item.service_type == "Silver":
        unit_amount = 200
    elif currency == "GBP" and project_item.service_type == "Gold":
        unit_amount = 250
    elif currency == "GBP" and project_item.service_type == "Platinum":
        unit_amount = 300
    else:
        unit_amount = 2500

    if count_questions >= 10:
        # Organisations are restricted to ask only 10 questions then they proceed to make paymemt.
        # This calculates line items required for payment
        line_item_exists = LineItem.query.filter_by(project_id=project_item.id).first()

        if not line_item_exists:
            lineitems_1 = LineItem(
                project_id=project_item.id,
                quantity=project_item.order_quantity,
                currency=project_item.currency,
                service_type=project_item.service_type,
                unit_amount=unit_amount,
                name=project_item.name,
                user_id=current_user.id,
            )
            db.session.add(lineitems_1)
            db.session.commit()

        return redirect(
            url_for(
                "project.order_details",
                project_id=project_id,
                name=project.name,
                email=current_user.email
            )
        )

    return render_template(
        "project/project_details.html",
        screener_question=screener_question,
        project_id=project_id,
        project=project,
        custom_questions=custom_questions,
        scale_question=scale_question,
        multiple_choice_question=multiple_choice_question,
        count_screener_questions=count_screener_questions,
        count_questions=count_questions,
    )


@project.route("/order/<int:project_id>/details/<name>/")
def order_details(project_id, name):
    project = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter_by(id=project_id)
        .first()
    )
    org = Organisation.query.filter_by(id=project.organisation_id).first_or_404()
    line_item = (
        db.session.query(LineItem)
        .filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .first()
    )
    order = (
        db.session.query(Order)
        .filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .first()
    )
    paid_project = PaidProject.query.filter_by(project_id=project.id).first()
    project_is_paid = True if paid_project else False

    today = date.today()

    return render_template(
        "project/order_details.html",
        project_id=project_id,
        org=org,
        project=project,
        line_item=line_item,
        order=order,
        is_paid=project_is_paid,
        today=today,
    )


@project.route("/<int:project_id>/<name>/edit", methods=["Get", "POST"])
@login_required
def edit_project(project_id, name):

    project = (
        Project.query.filter_by(user_id=current_user.id)
    .filter_by(id=project_id)
        .first_or_404()
    )
    if not project:
        abort(404)
    if current_user.id != project.user_id:
        abort(404)

    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=project.organisation_id)
        .first()
    )
    order = Order.query.filter(Order.project_id == project_id).first()

    form = AddProjectForm(obj=project)
    if form.validate_on_submit():
        # order_id = db.session.query(Organisation).filter_by(user_id=current_user.id).first()
        form.populate_obj(project)
        db.session.add(project)
        db.session.commit()
        flash("Edited.", "success")
        return redirect(url_for("project.index"))
    return render_template(
        "project/create_project.html", project=project, form=form, org=org, order=order
    )


@project.route("<project_id>/delete", methods=["GET", "POST"])
def delete_project(org_id, project_id):
    project = (
        Project.query.filter_by(user_id=current_user.id)
        .filter_by(id=project_id)
        .first_or_404()
    )
    order = (
        Order.query.filter_by(organisation_id=org_id)
        .filter_by(id=project_id)
        .first_or_404()
    )
    if current_user.id != project.user_id:
        abort(404)
    db.session.delete(project)
    db.session.commit()
    flash("Delete.", "success")
    return redirect(url_for("project.index", org_id=project.organisation_id))
