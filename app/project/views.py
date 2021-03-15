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
from sqlalchemy.orm import with_polymorphic
from sqlalchemy import func

from app import db
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
@login_required
def index():
    """project dashboard page."""
    check_point_org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=Organisation.id)
        .first()
    )
    if check_point_org is None:
        flash(" You now need to add details of your organization.", "error")
        return redirect(url_for("organisations.org_home"))

    check_point_project = (
        Project.query.filter_by(user_id=current_user.id)
        .filter_by(id=Project.id)
        .first()
    )
    if check_point_project is None:
        flash(" You now need create a project.", "error")
        return redirect(url_for("project.new_project", org_id=check_point_org.id))

    org = (
        Organisation.query.filter_by(user_id=current_user.id)
        .filter_by(id=Organisation.id)
        .first_or_404()
    )

    project = db.session.query(Project).filter_by(user_id=current_user.id).all()
    # question = db.session.query(Question).filter_by(user_id=current_user.id).filter(Question.project_id==Project.id).all()
    count_screener_questions = (
        db.session.query(func.count(ScreenerQuestion.id))
        .filter(ScreenerQuestion.project_id == Project.id)
        .scalar()
    )
    questions_poly = with_polymorphic(
        Question, [ScreenerQuestion, ScaleQuestion, MultipleChoiceQuestion]
    )
    count_questions = (
        db.session.query(questions_poly)
        .filter_by(user_id=current_user.id)
        .filter(Question.project_id == Project.id)
        .count()
    )
    # count_questions = Question.query.filter_by(user_id=current_user.id).filter(Question.project_id == Project.id).count()
    return render_template(
        "project/project_dashboard.html",
        project=project,
        org=org,
        question=question,
        count_screener_questions=count_screener_questions,
        count_questions=count_questions,
    )


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


@project.route("/<org_id>/<int:project_id>/details/<name>/", methods=["GET", "POST"])
def project_details(org_id, project_id, name):
    screener_questions_poly = with_polymorphic(Question, [ScreenerQuestion])
    scale_questions_poly = with_polymorphic(Question, [ScaleQuestion])
    mc_questions_poly = with_polymorphic(Question, [MultipleChoiceQuestion])

    check_point = (
        db.session.query(screener_questions_poly)
        .filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .count()
    )
    if check_point is None:
        flash(" You now need to add one screener question.", "success")
        return redirect(
            url_for(
                "question.new_screener_question", org_id=org.id, project_id=project.id
            )
        )

    # screener_question = ScreenerQuestion.query.filter_by(user_id=current_user.id).filter(project_id ==project_id).all()
    screener_question = (
        db.session.query(Question)
        .filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .filter_by(question_type=QuestionTypes.ScreenerQuestion.value)
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

    project_id = project_id
    # count_screener_questions = ScreenerQuestion.query.filter_by(user_id=current_user.id).filter(project_id==project_id).first()
    count_screener_questions = len(screener_question)

    # count_questions = Question.query.filter_by(user_id=current_user.id).filter(project_id == project_id).count()
    count_questions = 0

    ## prepare line items
    project_item = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
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
        # Organisations are restricted to ask only 10 questions then they proceed to make paymemt. This calculates line items required for payment
        question_item = (
            db.session.query(Question)
            .filter_by(user_id=current_user.id)
            .filter(project_id == project_id)
            .first()
        )
        screener_question_item = (
            db.session.query(screener_questions_poly)
            .filter_by(user_id=current_user.id)
            .filter(project_id == project_id)
            .first()
        )

        scale_question_item = (
            db.session.query(scale_questions_poly)
            .filter_by(user_id=current_user.id)
            .filter(project_id == project_id)
            .first()
        )
        multiple_choice_question_item = (
            db.session.query(mc_questions_poly)
            .filter_by(user_id=current_user.id)
            .filter(project_id == project_id)
            .first()
        )
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
                org_id=org.id,
                project_id=project_id,
                name=project.name,
            )
        )

    print(screener_question)

    return render_template(
        "project/project_details.html",
        screener_question=screener_question,
        project_id=project_id,
        org=org,
        project=project,
        scale_question=scale_question,
        multiple_choice_question=multiple_choice_question,
        count_screener_questions=count_screener_questions,
        count_questions=count_questions,
    )


@project.route("/order/<org_id>/<int:project_id>/details/<name>/")
def order_details(org_id, project_id, name):

    screener_question = (
        ScreenerQuestion.query.filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .all()
    )
    scale_question = (
        ScaleQuestion.query.filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .all()
    )
    multiple_choice_question = (
        MultipleChoiceQuestion.query.filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .all()
    )
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

    project_id = project_id
    count_screener_questions = (
        ScreenerQuestion.query.filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .count()
    )

    count_questions = (
        Question.query.filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .count()
    )

    ## prepare line items
    project_item = (
        db.session.query(Project)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )
    order = (
        db.session.query(LineItem)
        .filter_by(user_id=current_user.id)
        .filter(Project.id == project_id)
        .first()
    )
    count_order = (
        Order.query.filter_by(user_id=current_user.id)
        .filter(project_id == project_id)
        .count()
    )
    # if count_order <= 0:
    # flash("You need to submit enough questions first.", 'error')
    # return redirect(url_for('project.project_details', org_id=org.id, project_id=project_id, name=project.name))
    today = date.today()

    return render_template(
        "project/order_details.html",
        screener_question=screener_question,
        project_id=project_id,
        org=org,
        project=project,
        scale_question=scale_question,
        multiple_choice_question=multiple_choice_question,
        count_screener_questions=count_screener_questions,
        count_questions=count_questions,
        order=order,
        today=today,
    )


@project.route("/<org_id>/<int:project_id>/<name>/edit", methods=["Get", "POST"])
@login_required
def edit_project(org_id, project_id, name):

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
        .filter_by(id=org_id)
        .first()
    )
    order = Order.query.filter(Order.project_id == project_id).first()
    project_id = project_id

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


@project.route("/<project_id>/delete", methods=["GET", "POST"])
def delete_project(project_id):
    project = (
        Project.query.filter_by(user_id=current_user.id)
        .filter_by(id=project_id)
        .first_or_404()
    )
    order = (
        Order.query.filter_by(organisation_id=current_user.id)
        .filter_by(id=project_id)
        .first_or_404()
    )
    if current_user.id != project.user_id:
        abort(404)
    db.session.delete(project)
    db.session.commit()
    flash("Delete.", "success")
    return redirect(url_for("project.index"))
