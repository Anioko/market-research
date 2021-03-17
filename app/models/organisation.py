from .. import db
from datetime import datetime


class Organisation(db.Model):
    __tablename__ = "organisations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    org_name = db.Column(db.String(255))
    org_city = db.Column(db.String(255))
    org_state = db.Column(db.String(255))
    org_country = db.Column(db.String(255))
    org_website = db.Column(db.String(255))
    org_industry = db.Column(db.String(255))
    mobile_phone = db.Column(db.BigInteger, unique=True, index=True)
    org_description = db.Column(db.Text)
    user = db.relationship("User", backref="organisations", cascade="all, delete")
    # order = db.relationship('Order', lazy="joined", join_depth=1)
    projects = db.relationship("Project", lazy="joined", join_depth=1)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return u"<{self.__class__.__name__}: {self.id}>".format(self=self)

    def get_staff(self):
        ids = [user.user_id for user in self.staff]
        return User.query.filter(User.id.in_(ids)).all()


class OrgStaff(db.Model):
    __tablename__ = "org_staff"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    invited_by = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"))
    org_id = db.Column(
        db.Integer, db.ForeignKey("organisations.id", ondelete="CASCADE")
    )
    user = db.relationship("User", primaryjoin="User.id==OrgStaff.user_id")
    referer = db.relationship("User", primaryjoin="User.id==OrgStaff.invited_by")
    org = db.relationship(
        "Organisation", primaryjoin="Organisation.id==OrgStaff.org_id", backref="staff"
    )
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
