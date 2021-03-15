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

from app import db
from app.admin.forms import (
    ChangeAccountTypeForm,
    ChangeUserEmailForm,
    InviteUserForm,
    NewUserForm,
    TrackingScriptForm
)
from app.decorators import admin_required
from app.email import send_email
from app.models import *
admin = Blueprint('admin', __name__)


@admin.route('/')
@login_required
@admin_required
def index():
    """Admin dashboard page."""
    return render_template('admin/index.html')


@admin.route('/new-user', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    """Create a new user."""
    form = NewUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User {} successfully created'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/invite-user', methods=['GET', 'POST'])
@login_required
@admin_required
def invite_user():
    """Invites a new user to create an account and set their own password."""
    form = InviteUserForm()
    if form.validate_on_submit():
        user = User(
            role=form.role.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        invite_link = url_for(
            'account.join_from_invite',
            user_id=user.id,
            token=token,
            _external=True)
        get_queue().enqueue(
            send_email,
            recipient=user.email,
            subject='You Are Invited To Join',
            template='account/email/invite',
            user=user,
            invite_link=invite_link,
        )
        flash('User {} successfully invited'.format(user.full_name()),
              'form-success')
    return render_template('admin/new_user.html', form=form)


@admin.route('/users', defaults={'page': 1})
@admin.route('/users/<int:page>')
@login_required
@admin_required
def registered_users(page):
    """View all registered users."""
    users = User.query.paginate(page, per_page=50)
    users_count = User.query.count()
    roles = Role.query.all()
    return render_template(
        'admin/registered_users.html', users=users, roles=roles, users_count=users_count)


@admin.route('/orders', defaults={'page': 1})
@admin.route('/orders/<int:page>')
@login_required
@admin_required
def orders(page):
    """View all orders."""
    orders = Order.query.paginate(page, per_page=50)
    orders_count = Order.query.count()
    return render_template(
        'admin/registered_orders.html', orders=orders, orders_count=orders_count)

@admin.route('/user/<int:user_id>')
@admin.route('/user/<int:user_id>/info')
@login_required
@admin_required
def user_info(user_id):
    """View a user's profile."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)


@admin.route('/user/<int:user_id>/change-email', methods=['GET', 'POST'])
@login_required
@admin_required
def change_user_email(user_id):
    """Change a user's email."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    form = ChangeUserEmailForm()
    if form.validate_on_submit():
        user.email = form.email.data
        db.session.add(user)
        db.session.commit()
        flash('Email for user {} successfully changed to {}.'.format(
            user.full_name(), user.email), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route(
    '/user/<int:user_id>/change-account-type', methods=['GET', 'POST'])
@login_required
@admin_required
def change_account_type(user_id):
    """Change a user's account type."""
    if current_user.id == user_id:
        flash('You cannot change the type of your own account. Please ask '
              'another administrator to do this.', 'error')
        return redirect(url_for('admin.user_info', user_id=user_id))

    user = User.query.get(user_id)
    if user is None:
        abort(404)
    form = ChangeAccountTypeForm()
    if form.validate_on_submit():
        user.role = form.role.data
        db.session.add(user)
        db.session.commit()
        flash('Role for user {} successfully changed to {}.'.format(
            user.full_name(), user.role.name), 'form-success')
    return render_template('admin/manage_user.html', user=user, form=form)


@admin.route('/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user_request(user_id):
    """Request deletion of a user's account."""
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        abort(404)
    return render_template('admin/manage_user.html', user=user)

@admin.route('/scale_questions', defaults={'page': 1}, methods=['GET'])
@admin.route('/scale_questions/<int:page>', methods=['GET'])
@login_required
@admin_required
def scale_questions(page):
    questions_result = ScaleQuestion.query.paginate(page, per_page=100)
    return render_template('admin/scale_questions/browse.html', questions=questions_result)


@admin.route('/scl/<int:question_id>/_delete',  methods=['GET', 'POST'])
@login_required
@admin_required
def delete_scale_questions(questions_id):
    question = ScaleQuestion.query.filter_by(id=question_id).first()
    db.session.delete(question)
    db.session.commit()
    flash('Successfully deleted a scaled question.', 'success')
    return redirect(url_for('admin.scale_questions'))

@admin.route('/scq', defaults={'page': 1}, methods=['GET'])
@admin.route('/scq/<int:page>', methods=['GET'])
@login_required
@admin_required
def screener_questions(page):
    questions_result = ScreenerQuestion.query.paginate(page, per_page=100)
    return render_template('admin/screener_questions/browse.html', questions=questions_result)


@admin.route('/scl/<int:question_id>/_delete',  methods=['GET', 'POST'])
@login_required
@admin_required
def delete_screener_questions(questions_id):
    question = ScreenerQuestion.query.filter_by(id=question_id).first()
    db.session.delete(question)
    db.session.commit()
    flash('Successfully deleted a multi choice question.', 'success')
    return redirect(url_for('admin.screener_questions'))

@admin.route('/mcq', defaults={'page': 1}, methods=['GET'])
@admin.route('/mcq/<int:page>', methods=['GET'])
@login_required
@admin_required
def multiple_choice_questions(page):
    questions_result = MultipleChoiceQuestion.query.paginate(page, per_page=100)
    return render_template('admin/multiple_choice_questions/browse.html', questions=questions_result)


@admin.route('/scl/<int:question_id>/_delete',  methods=['GET', 'POST'])
@login_required
@admin_required
def delete_multiple_choice_questions(questions_id):
    question = MultipleChoiceQuestion.query.filter_by(id=question_id).first()
    db.session.delete(question)
    db.session.commit()
    flash('Successfully deleted a multi choice question.', 'success')
    return redirect(url_for('admin.multiple_choice_questions'))

@admin.route('/questions', defaults={'page': 1}, methods=['GET'])
@admin.route('/questions/<int:page>', methods=['GET'])
@login_required
@admin_required
def questions(page):
    questions_poly = with_polymorphic(Question, [ScreenerQuestion, ScaleQuestion, MultipleChoiceQuestion])
    questions_result = db.session.query(Question).paginate(page, per_page=100)
    print(questions_result)
    return render_template('admin/questions/browse.html', questions=questions_result)


@admin.route('/question/<int:question_id>/_delete',  methods=['GET', 'POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.filter_by(id=question_id).first()
    db.session.delete(question)
    db.session.commit()
    flash('Successfully deleted question.', 'success')
    return redirect(url_for('admin.questions'))


@admin.route('/projects', defaults={'page': 1}, methods=['GET'])
@admin.route('/projects/<int:page>', methods=['GET'])
@login_required
@admin_required
def projects(page):
    projects_result = Project.query.paginate(page, per_page=100)
    return render_template('admin/projects/browse.html', projects=projects_result)


@admin.route('/project/<int:project_id>/_delete',  methods=['GET', 'POST'])
@login_required
@admin_required
def delete_project(project_id):
    project = Project.query.filter_by(id=project_id).first()
    db.session.delete(project)
    db.session.commit()
    flash('Successfully deleted project.', 'success')
    return redirect(url_for('admin.projects'))



@admin.route('/user/<int:user_id>/_delete')
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user's account."""
    if current_user.id == user_id:
        flash('You cannot delete your own account. Please ask another '
              'administrator to do this.', 'error')
    else:
        user = User.query.filter_by(id=user_id).first()
        db.session.delete(user)
        db.session.commit()
        flash('Successfully deleted user %s.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))


@admin.route('/text/<text_type>', methods=['GET'])
@login_required
@admin_required
def text(text_type):
    editable_html_obj = EditableHTML.get_editable_html(text_type)
    return jsonify({
        'status': 1,
        'editable_html_obj': editable_html_obj.serialize
    })


@admin.route('/texts', methods=['POST', 'GET'])
@login_required
@admin_required
def texts():
    editable_html_obj = EditableHTML.get_editable_html('contact')
    if request.method == 'POST':
        edit_data = request.form.get('edit_data')
        editor_name = request.form.get('editor_name')

        editor_contents = EditableHTML.query.filter_by(
            editor_name=editor_name).first()
        if editor_contents is None:
            editor_contents = EditableHTML(editor_name=editor_name)
        editor_contents.value = edit_data

        db.session.add(editor_contents)
        db.session.commit()
        flash('Successfully updated text.', 'success')
        return redirect(url_for('admin.texts'))
    return render_template('admin/texts/index.html', editable_html_obj=editable_html_obj)

@admin.route('/_update_editor_contents', methods=['POST'])
@login_required
@admin_required
def update_editor_contents():
    """Update the contents of an editor."""

    edit_data = request.form.get('edit_data')
    editor_name = request.form.get('editor_name')

    editor_contents = EditableHTML.query.filter_by(
        editor_name=editor_name).first()
    if editor_contents is None:
        editor_contents = EditableHTML(editor_name=editor_name)
    editor_contents.value = edit_data

    db.session.add(editor_contents)
    db.session.commit()

    return 'OK', 200


@admin.route('/trackingscript-list')
@login_required
@admin_required
def added_trackingscript():
    """View added tracking script."""
    data = TrackingScript.query.all()
    if data is None:
        return redirect(url_for('admin.add_trackingscript'))
    return render_template(
        'admin/trackingscript/added_trackingscript.html', data=data)

# Add TrackingScript 
@admin.route('/trackingscript/add', methods=['POST', 'GET'])
@admin_required
def add_trackingscript():
    form = TrackingScriptForm()
    if form.validate_on_submit():
        data = TrackingScript(
            name=form.name.data,
            script=form.script.data
            )
        db.session.add(data)
        db.session.commit()
        flash("Tracking Script Added Successfully.", "success")
        return redirect(url_for('admin.added_trackingscript'))
    return render_template('admin/trackingscript/add_trackingscript.html', form=form)


# Edit SEO 
@admin.route('/trackingscript/<int:id>/edit', methods=['POST', 'GET'])
@login_required
@admin_required
def edit_trackingscript(id):
    data = TrackingScript.query.filter_by(id=id).first()
    form = TrackingScriptForm(obj=data)
    if form.validate_on_submit():
        data.name=form.name.data
        data.script=form.script.data
        db.session.add(data)
        db.session.commit()
        flash("Edit successfully.", "success")
        return redirect(url_for('admin.added_trackingscript'))
    else:
        flash('ERROR! Text was not edited.', 'error')
    return render_template('admin/trackingscript/add_trackingscript.html', form=form)

@admin.route('/trackingscript/<int:id>/_delete', methods=['GET', 'POST'])
@admin_required
def delete_trackingscript(id):
    """Delete the item """
    data = TrackingScript.query.filter_by(id=id).first()
    db.session.commit()
    db.session.delete(data)
    flash('Successfully deleted ' , 'success')
    return redirect(url_for('admin.added_trackingscript'))


@admin.route('/user/<int:user_id>/_respondent')
@login_required
@admin_required
def toggle_user_respondent(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.is_respondent = not user.is_respondent
    db.session.add(user)
    db.session.commit()
    flash('Successfully Changes user %s Seller Status.' % user.full_name(), 'success')
    return redirect(url_for('admin.registered_users'))
