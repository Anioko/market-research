from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from app.models import *

public = Blueprint("public", __name__)


@public.route("/")
def home():

    tracking_script = TrackingScript.query.all()

    return render_template("public/temp.html", tracking_script=tracking_script)

    # @public.route("/", methods=["GET", "POST"])
    # def home():
    """Home page."""
    # slideshows = SlideShowImage.query.all()
    # hometext = HomeText.query.first()
    # logo = Logo.query.first()
    # techno_img = TechnologiesImage.query.all()
    # text_techno = TechnologiesText.query.first()
    # return render_template("public/temp.html", slideshows=slideshows, home_title=hometext, logo=logo, techno_img=techno_img, text_techno=text_techno)


@public.route("/product/<int:product_id>/<product_name>")
def view_product(product_id, product_name):
    product = Module.query.get_or_404(product_id)
    return render_template("public/product.html", product=product)


@public.route("/cart/")
def cart_details():
    # cart = get_current_cart()
    logo = Logo.query.first()
    return render_template(
        "public/cart/view.html",
        # cart=cart,
        logo=logo,
    )


@public.route("/about")
def about():
    editable_html_obj = EditableHTML.get_editable_html("about")
    return render_template("public/about.html", editable_html_obj=editable_html_obj)


@public.route("/faq")
def faq():
    editable_html_obj = EditableHTML.get_editable_html("faq")
    return render_template("public/faq.html", editable_html_obj=editable_html_obj)


@public.route("/terms")
def terms():
    editable_html_obj = EditableHTML.get_editable_html("terms")
    return render_template("public/terms.html", editable_html_obj=editable_html_obj)


@public.route("/privacy")
def privacy():
    editable_html_obj = EditableHTML.get_editable_html("privacy")
    return render_template("public/privacy.html", editable_html_obj=editable_html_obj)


@public.route("/pricing")
def pricing():
    editable_html_obj = EditableHTML.get_editable_html("pricing")
    return render_template("public/pricing.html", editable_html_obj=editable_html_obj)


@public.route("/testimonial")
def testimonial():
    editable_html_obj = EditableHTML.get_editable_html("testimonial")
    return render_template(
        "public/testimonial.html", editable_html_obj=editable_html_obj
    )


@public.route("/contact")
def contact():
    editable_html_obj = EditableHTML.get_editable_html("contact")
    return render_template("public/contact.html", editable_html_obj=editable_html_obj)


@public.route("/under_construction")
def under_construction():
    editable_html_obj = EditableHTML.get_editable_html("under_construction")
    return render_template("public/about.html", editable_html_obj=editable_html_obj)


@public.route("/<city>/")
def city(city):
    city = city
    return render_template("public/city.html", city=city)
