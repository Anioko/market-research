from flask_wtf import FlaskForm
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.fields import (
    PasswordField,
    StringField,
    SubmitField,
    SelectField,
    IntegerField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import (
    Email,
    EqualTo,
    InputRequired,
    Length,
)

from app import db
from app.models import Role, User


class AddProjectForm(FlaskForm):
    name = StringField("Project Name", validators=[InputRequired(), Length(1, 64)])
    order_quantity = IntegerField(
        "Select order qty, min 250 responses"
    )  # , validators=[InputRequired(),
    # Length(3, 4)])
    service_type = SelectField(
        u"Please choose the service category e.g silver",
        choices=[("Silver", "Silver"), ("Gold", "Gold"), ("Platinum", "Platinum")],
    )

    currency = SelectField(
        u"Please choose pricing currency e.g USD",
        choices=[("USD", "USD"), ("NGN", "NGN"), ("GBP", "GBP")],
    )
    submit = SubmitField("Submit")
