from .. import db


class TrackingScript(db.Model):
    __tablename__ = "tracking_script"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    script = db.Column(db.String(500), nullable=False)
