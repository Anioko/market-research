from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
    current_app,
    send_from_directory,
)
from datetime import datetime, date
from logging import log
from time import time

from flask_login import current_user, login_required
from app import db
from app.models import (
    EditableHTML,
    Project,
    Organisation,
    Order,
    User,
    Question,
    ScaleQuestion,
    LineItem,
    PaidProject,
    MultipleChoiceQuestion,
    ScreenerQuestion,
)
from app.main.forms import AddOrderForm
from app.constants import QuestionTypes

import stripe
import os
from sqlalchemy import func, desc
from sqlalchemy.orm import with_polymorphic

from app.decorators import admin_required, respondent_required

main = Blueprint("main", __name__)


STRIPE_PUBLISHABLE_KEY = "pk_test_oqKtiHQipsUaIuR81LYSiDW2"
STRIPE_SECRET_KEY = "sk_test_hqoFMPptGIiQJSuk6Yg6B2Fr"
# STRIPE_ENDPOINT_SECRET="whsec_429KA0GICAAwyH3mVix0HYDLDZk9jybp"

# This is your real test secret API key.
stripe.api_key = "sk_test_hqoFMPptGIiQJSuk6Yg6B2Fr"


today = date.today()

# @main.route('/order/<int:org_id>/<int:project_id>/')
# def index(org_id, project_id):
@main.route("/index")
@login_required
def index():
    if current_user.is_authenticated:
        return render_template("main/index.html")
    else:

        return redirect(url_for("public.home"))


@main.route("/cancel")
def cancel():
    return render_template("main/cancel.html")


@main.route("/stripe_pay/<project_id>")
def stripe_pay(project_id):
    line_item = LineItem.query.filter_by(project_id=project_id).first()
    project = Project.query.filter_by(
        user_id=current_user.id, id=line_item.project_id
    ).first()
    # if order.created_at == Order.created_at
    quantity = line_item.quantity
    currency = line_item.currency
    name = project.name
    unit_amount = line_item.unit_amount
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {
                        "name": name,
                    },
                    "unit_amount": unit_amount,
                },
                "quantity": quantity,
            }
        ],
        mode="payment",
        success_url=url_for(
            "main.thanks",
            line_item_id=line_item.line_item_id,
            project_id=project.id,
            _external=True,
        )
        + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=url_for("main.cancel", _external=True),
    )

    order = Order(
        user_id=current_user.id,
        project_id=line_item.project_id,
        line_item_id=line_item.line_item_id,
        organisation_id=project.organisation_id,
        session_id=session["id"],
        start_date=today.strftime("%B %d, %Y"),
        payment_method=session["payment_method_types"],
        currency=session["currency"],
        total_amount=session["amount_total"],
        customer_email=session["customer_email"],
        payment_intent=session["payment_intent"],
    )

    db.session.add(order)
    db.session.commit()
    return {
        "checkout_session_id": session["id"],
        "checkout_public_key": "pk_test_oqKtiHQipsUaIuR81LYSiDW2",
    }


@main.route("/thanks/<line_item_id>/<project_id>")
def thanks(line_item_id, project_id):
    order = Order.query.filter_by(user_id=current_user.id).filter_by(project_id=project_id).first()
    project = Project.query.filter_by(id=project_id).first()

    project_paid = PaidProject(
                project_id=project_id,
                order_id=order.id,
                project_name=project.name,
            )
    db.session.add(project_paid)

    return render_template("main/thanks.html")


@main.route("/webhook/endpoint")
def order():
    session = stripe.checkout.Session.list(limit=3)
    for stripe_session in session["data"]:
        session = stripe_session

    payment_status = stripe_session.get("payment_status")
    quantity = stripe_session.get("quantity")
    payment_method_types = stripe_session.get("payment_method_types")
    payment_intent = stripe_session.get("payment_intent")
    currency = stripe_session.get("currency")

    return render_template("main/thanks.html")


@main.route("/upload", methods=["POST"])
def upload():
    f = request.files.get("upload")
    image_filename = images.save(f)
    url = url_for(
        "_uploads.uploaded_file",
        setname="images",
        filename=image_filename,
        _external=True,
    )
    return upload_success(url=url)
