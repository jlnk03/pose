from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from flask_wrapper import db
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
import yagmail
import os
import stripe

auth = Blueprint('auth', __name__)

# change directory to access files correctly
if 'flask_wrapper' not in os.getcwd():
    os.chdir('flask_wrapper')


def send_email(email, subject, message):
    yag  = yagmail.SMTP('swing.analysis23@gmail.com', oauth2_file='email.json')
    body = render_template('mail_mail_verification.html', url=message)
    yag.send(to=email, subject=subject, contents=body)


def send_email_pw(email, subject, message):
    yag  = yagmail.SMTP('swing.analysis23@gmail.com', oauth2_file='email.json')
    # body = render_template('mail_mail_verification.html', url=message)
    yag.send(to=email, subject=subject, contents=message)


@auth.route('/test')
def test():
    return render_template('mail_mail_verification.html')


@auth.route('/login')
def login():
    logout_user()
    return render_template('login.html', title='Login – swinglab')

@auth.route('/login', methods=['POST'])
def login_post():
    # login code goes here
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    login_user(user, remember=remember)
    # if the above check passes, then we know the user has the right credentials
    return redirect(url_for('main.profile'))

@auth.route('/signup')
def signup():
    return render_template('signup.html', title='Get started – swinglab')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # code to validate and add user to database goes here
    email = request.form.get('email').lower()
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), active=False, n_analyses=2, unlimited=False, admin=False)

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    user = User.query.filter_by(email=email).first()

    login_user(user)

    # flash('Please check your email to confirm your account')

    return redirect(url_for('auth.send_mail'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/send_mail')
def send_mail():
    email = current_user.email

    ts = URLSafeTimedSerializer('key')

    token = ts.dumps(email, salt='email-confirm-key')

    subject = 'Confirm your email'
    confirm_url = url_for('auth.verify_mail', token=token, _external=True)

    send_email(email, subject, confirm_url)

    return redirect(url_for('auth.verify'))


@auth.route('/verify_mail')
def verify():
    return render_template('verify_mail.html', title='Verify your email-address – swinglab')


@auth.route('/verify/<token>')
def verify_mail(token):
    ts = URLSafeTimedSerializer('key')
    try:
        email = ts.loads(token, salt='email-confirm-key', max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()
    user.active = True
    db.session.add(user)
    db.session.commit()
    # flash('You have confirmed your account.')
    return render_template('verify_mail_ok.html')


@auth.route('/verify_update/<token>')
def verify_mail_update(token):
    ts = URLSafeTimedSerializer('key')
    try:
        email = ts.loads(token, salt='email-confirm-key', max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email_new=email).first_or_404()
    user.email = user.email_new
    user.email_new = None
    db.session.add(user)
    db.session.commit()
    # flash('You have confirmed your account.')
    return render_template('verify_mail_ok.html')


@auth.route('/reset_password')
def reset_password():
    return render_template('reset_password.html', title='Reset Password – swinglab')


@auth.route('/reset_password', methods=['POST'])
def reset_password_post():
    # code to validate and add user to database goes here
    email = request.form.get('email')

    if User.query.filter_by(email=email).first() is not None:

        ts = URLSafeTimedSerializer('key')

        token = ts.dumps(email, salt='password-reset-key')

        subject = 'Reset your password'
        confirm_url = url_for('auth.reset_password_mail', token=token, _external=True)

        send_email_pw(email, subject, (confirm_url))

        # flash('Please check your email to confirm your account')

        return render_template('new_password_mail.html', email=email)

    else:
        flash('Email address does not exist')
        return redirect(url_for('auth.reset_password'))


@auth.route('/reset_password_mail/<token>')
def reset_password_mail(token):
    ts = URLSafeTimedSerializer('key')
    try:
        email = ts.loads(token, salt='password-reset-key', max_age=86400)
    except:
        abort(404)

    return render_template('new_password.html', token=token, title='New Password – swinglab')


@auth.route('/reset_password_mail/<token>', methods=['POST'])
def reset_password_mail_post(token):
    ts = URLSafeTimedSerializer('key')
    try:
        email = ts.loads(token, salt='password-reset-key', max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()
    user.password = generate_password_hash(request.form.get('password'), method='sha256')
    db.session.add(user)
    db.session.commit()

    flash('You have reset your password.')
    # print('You have reset your password.')

    return redirect(url_for('auth.login'))


@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    email_new = request.form.get('email')
    name_new = request.form.get('name')
    password_new = request.form.get('password_new')
    password_old = request.form.get('password')

    user = User.query.filter_by(email=current_user.email).first()

    if email_new is not None:
        email_new = email_new.lower()

    if email_new != current_user.email.lower() and email_new is not None:
        if User.query.filter_by(email=email_new).first() is not None:
            flash('Email address already exists', 'error')
            # return redirect(url_for('main.profile'))
        else:
            flash('Check your inbox to confirm your email-address', 'success')
            user.email_new = email_new

            ts = URLSafeTimedSerializer('key')

            token = ts.dumps(email_new, salt='email-confirm-key')

            subject = 'Confirm your email'
            confirm_url = url_for('auth.verify_mail_update', token=token, _external=True)

            send_email(email_new, subject, (confirm_url))

    if name_new != current_user.name and name_new is not None:
        user.name = name_new
        flash('Name updated successfully', 'success')

    if (password_new is not None) and (password_old is not None):
        if check_password_hash(current_user.password, password_old):
            # flash('Please check your login details and try again.')
            user.password = generate_password_hash(password_new, method='sha256')
            flash('Password updated successfully', 'success')
            # return redirect(url_for('main.profile'))
        else:
            flash('Please check that your password is spelled correctly', 'error')
            # return redirect(url_for('main.profile'))

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('main.profile'))


@auth.route('/delete_profile')
@login_required
def delete_profile():
    return render_template('delete_user.html')


@auth.route('/delete_profile_final')
@login_required
def delete_profile_final():
    user = User.query.filter_by(email=current_user.email).first()
    db.session.delete(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/console')
@login_required
def console():
    if not current_user.admin:
        abort(403)

    users = User.query
    return render_template('console.html', users=users)


@auth.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    print('Handled event type {}'.format(event['type']))

    return jsonify(success=True)
