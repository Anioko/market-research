from app.models.order import PaystackTransaction
from dominate.dom_tag import attr
from dominate.tags import meta
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
import random
import string
from datetime import datetime, date
from logging import log
from time import time
import requests
from flask_login import current_user, login_required
from app import db
from app.models import (
    Project,
    Order,
    LineItem,
    PaidProject,
)

import stripe
from sqlalchemy import func, desc
from sqlalchemy.orm import with_polymorphic
from paystackapi.paystack import Paystack
from app.decorators import admin_required, respondent_required

main = Blueprint("main", __name__)


STRIPE_PUBLISHABLE_KEY = "pk_test_oqKtiHQipsUaIuR81LYSiDW2"
STRIPE_SECRET_KEY = "sk_test_hqoFMPptGIiQJSuk6Yg6B2Fr"
# STRIPE_ENDPOINT_SECRET="whsec_429KA0GICAAwyH3mVix0HYDLDZk9jybp"


def generate_reference():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(15)
    )


# This is your real test secret API key.
stripe.api_key = "sk_test_hqoFMPptGIiQJSuk6Yg6B2Fr"
PAYSTACK_SECRET = "sk_test_8a72756aa71524066c2ae2974e50dc63c142e075"
paystack = Paystack(secret_key=PAYSTACK_SECRET)

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


@main.route("/payments/failed")
def failed_payment():
    return render_template("main/failed.html")


@main.route("/verify")
def verify_paystack_transaction():
    reference = request.args.get("reference")
    line_item = LineItem.query.filter_by(user_id=current_user.id).first()
    project = Project.query.filter_by(
        user_id=current_user.id, id=line_item.project_id
    ).first()

    try:
        paystack_resp = paystack.transaction.verify(reference)
        data = paystack_resp["data"]
        customer = data["customer"]
        customer_name = f"{customer['first_name']} { customer['last_name']}"
    except Exception as e:
        return render_template("main/failed.html")

    trans = PaystackTransaction(
        currency=data["currency"],
        created_date=data["created_at"],
        paid_date=data["paid_at"],
        customer_email=customer["email"],
        customer_name=customer_name,
        payment_reference=data["reference"],
        payment_method=data["channel"],
        gateway_response=data["gateway_response"],
        payment_status=data["status"],
        payment_fees=data["fees"],
        payment_amount=data["amount"],
    )
    order = Order(
        user_id=current_user.id,
        project_id=line_item.project_id,
        line_item_id=line_item.line_item_id,
        organisation_id=project.organisation_id,
        payment_id=data["id"],
        quantity=line_item.quantity,
        created_at=data["created_at"],
        payment_method=data["channel"],
        currency=data["currency"],
        payment_status=data["status"],
        payment_amount=data["amount"],
        customer_email=customer["email"],
    )
    db.session.add(trans)
    db.session.add(order)
    db.session.commit()
    return redirect(
        url_for(
            "main.thanks",
            line_item_id=line_item.line_item_id,
            project_id=project.id,
            _external=True,
        )
    )


@main.route("/paystack/<project_id>")
def paystack_pay(project_id):
    line_item = LineItem.query.filter_by(project_id=project_id).first()
    project = Project.query.filter_by(
        user_id=current_user.id, id=line_item.project_id
    ).first()
    # if order.created_at == Order.created_at
    currency = line_item.currency
    name = project.name
    unit_amount = line_item.unit_amount * 100

    meta_data = {
        "cancel_action": url_for("main.cancel", _external=True),
        "custom_fields": [
            {
                "display_name": "Project Name",
                "variable_name": "project_name",
                "value": name,
            }
        ],
    }
    ref = generate_reference()
    trans = paystack.transaction.initialize(
        amount=unit_amount,
        email="yekuwilfred@gmail.com",
        reference=ref,
        callback_url=url_for(
            "main.verify_paystack_transaction",
            _external=True,
        ),
        metadata=meta_data,
        currency=currency,
    )
    return jsonify(trans)
    """

    db.session.add(order)
    db.session.commit()
    return {
        "checkout_session_id": session["id"],
        "checkout_public_key": "pk_test_oqKtiHQipsUaIuR81LYSiDW2",
    }"""


@main.route("/thanks/<line_item_id>/<project_id>")
def thanks(line_item_id, project_id):
    order = (
        Order.query.filter_by(user_id=current_user.id)
        .filter_by(project_id=project_id)
        .first()
    )
    project = Project.query.filter_by(id=project_id).first()

    if order:
        project_paid = PaidProject(
            project_id=project_id,
            order_id=order.id,
            project_name=project.name,
        )
        db.session.add(project_paid)
        return render_template("main/thanks.html")

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
