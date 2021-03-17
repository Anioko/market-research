from .. import db
import datetime as dt


class Module(db.Model):
    __tablename__ = "modules"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(256), nullable=False)
    long_description = db.Column(db.Text, nullable=False)
    demo_url = db.Column(db.String(256), nullable=False)
    code_path = db.Column(db.String(256), nullable=False)
    price = db.Column(db.Float, nullable=False)
    support_price = db.Column(db.Float, nullable=False)
    image_filename = db.Column(db.String(256), nullable=False)
    tags = db.Column(db.Text, nullable=False)
    # release_date = db.Column(db.Date, server_default='current_timestamp', default=db.func.now(), nullable=False)
    # last_update_date = db.Column(db.Date, server_default='current_timestamp', default=db.func.now(), nullable=False)
    release_date = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    last_update_date = db.Column(
        db.DateTime, nullable=False, default=dt.datetime.utcnow
    )
    # module_images = db.relationship("ModuleImage", backref="module", lazy='dynamic')

    @property
    def image_url(self):
        return url_for(
            "_uploads.uploaded_file",
            setname="images",
            filename=self.image_filename,
            _external=True,
        )

    @property
    def image_path(self):
        from flask import current_app

        return os.path.join(
            current_app.config["UPLOADED_IMAGES_DEST"], self.image_filename
        )

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"


class ModuleImage(db.Model):
    __tablename__ = "module_images"
    id = db.Column(db.Integer, primary_key=True)

    image_filename = db.Column(db.String(256), nullable=False)

    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=True)
    module = db.relationship("Module")

    @property
    def image_url(self):
        return url_for(
            "_uploads.uploaded_file",
            setname="images",
            filename=self.image_filename,
            _external=True,
        )

    @property
    def image_path(self):
        from flask import current_app

        return os.path.join(
            current_app.config["UPLOADED_IMAGES_DEST"], self.image_filename
        )


class SlideShowImage(db.Model):
    __tablename__ = "slide_show_images"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    image_filename = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for(
            "_uploads.uploaded_file",
            setname="images",
            filename=self.image_filename,
            _external=True,
        )

    @property
    def image_path(self):
        from flask import current_app

        return os.path.join(
            current_app.config["UPLOADED_IMAGES_DEST"], self.image_filename
        )


class Seo(db.Model):
    __tablename__ = "seo"
    id = db.Column(db.Integer, primary_key=True)
    meta_tag = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(256), nullable=False)


class Setting(db.Model):
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    display_name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(512), nullable=True)


#####################################################
# Front End chage models


class HomeText(db.Model):
    __tablename__ = "hometext"
    id = db.Column(db.Integer, primary_key=True)
    firstext = db.Column(db.String(80), nullable=False)
    secondtext = db.Column(db.String(80), nullable=False)


class TechnologiesText(db.Model):
    __tablename__ = "technologies_text"
    id = db.Column(db.Integer, primary_key=True)
    firstext = db.Column(db.String(80), nullable=False)
    secondtext = db.Column(db.String(80), nullable=False)


class TechnologiesImage(db.Model):
    __tablename__ = "technologies_images"
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for(
            "_uploads.uploaded_file",
            setname="images",
            filename=self.image,
            _external=True,
        )

    @property
    def image_path(self):
        from flask import current_app

        return os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], self.image)


class Logo(db.Model):
    _tablename_ = "logo"
    id = db.Column(db.Integer, primary_key=True)
    logo_image = db.Column(db.String(256), nullable=False)

    @property
    def image_url(self):
        return url_for(
            "_uploads.uploaded_file",
            setname="images",
            filename=self.logo_image,
            _external=True,
        )

    @property
    def image_path(self):
        from flask import current_app

        return os.path.join(current_app.config["UPLOADED_IMAGES_DEST"], self.logo_image)


# Schemas
# class ModuleSchema(ma.Schema):
# class Meta:
# fields = ("id", "name", "description", "price", "support_price", "image_url")
# module = Module
