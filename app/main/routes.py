import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EmptyForm, PostForm, MessageForm, ServiceForm, UploadForm
from app.models import User, Post, Message, Notification
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


def allowed_image_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['IMAGE_EXTENSIONS']


def allowed_video_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['VIDEO_EXTENSIONS']


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post is now public")
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.index', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title="Home", form=form, posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )
    next_url = url_for('main.explore', page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html', title="Explore", posts=posts.items, next_url=next_url, prev_url=prev_url)


@bp.route('/zodindevelopment', methods=['GET', 'POST'])
def zodindev():
    form = ServiceForm()

    if form.validate_on_submit():
        contact_zodin(message=form.message.data, email=form.email.data, name=form.name.data, phone=form.phone.data)
        flash("Dylan Garrett has been notified of your message and will reach out to you shortly. Thank you!")
        return redirect(url_for('main.zodindev'))

    page_body = current_app.config['ABOUT_TEXT']
    return render_template('zodindev.html', title="Zodin Development", page_body=page_body, form=form)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )    
   #photos = user.photos.order_by(Photo.timestamp.desc()).paginate(
   # 3    page, current_app.config['MEDIA_PER_PAGE'], False
   # )
    #videos = user.videos.order_by(Video.timestamp.desc()).paginate(
    #    page, current_app.config['MEDIA_PER_PAGE'], False
   # )

    next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', posts=posts.items, next_url=next_url, prev_url=prev_url, form=form, user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title="Edit Profile", form=form)


@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("User {} not found.".format(username))
            return redirect(url_for('main.index'))

        if user == current_user:
            flash("You cannot follow yourself!")
            return redirect(url_for('main.user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash("You are now following {}.".format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route("/unfollow/<username>", methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash("User {} not found.".format(username))
            return redirect(url_for('main.index'))

        if user == current_user:
            flash("You cannot unfollow yourself!")
            return redirect(url_for('main.user', username=username))

        current_user.unfollow(user)
        db.session.commit()
        flash("You are no longer following {}.".format(username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = User.query.filter_by(username=recipient).first_or_404()
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count', user.new_messages())
        db.session.commit()
        flash("Your message was successfully delivered.")
        return redirect(url_for('main.user', username=recipient))

    return render_temlpate('send_message.html', title="Private Message", form=form, recipient=recipient)


@bp.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.utcnow()
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()

    page = request.args.get('page', 1, type=int)
    messages = current_user.messages_received.order_by(Message.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False
    )

    next_url = url_for('main.messages', page=messages.next_num) if messages.has_next else None
    prev_url = url_for('main.messages', page=messages.prev_num) if messages.has_prev else None

    return render_template('messages.html', messages=messages.items, next_url=next_url, prev_url=prev_url)


@bp.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    notifications = current_user.notifications.filter(Notification.timestamp > since).order_by(Notification.timestamp.asc())
    return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])


