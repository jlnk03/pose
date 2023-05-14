import datetime
import json
import os
import shutil
import smtplib
import ssl
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import stripe
from flask import Blueprint, render_template, redirect, url_for, request, flash, abort, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash

from flask_wrapper import db
from .models import User

auth = Blueprint('auth', __name__)

stripe.api_key = os.getenv('STRIPE_API_KEY')
endpoint_secret = os.getenv('ENDPOINT_SECRET')

# change directory to access files correctly
if 'flask_wrapper' not in os.getcwd():
    os.chdir('flask_wrapper')


def send_mail_smtp(toaddr, subject, message, name=None, manual=False):
    # create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr(('Swinglab', 'info@swinglab.app'))
    msg['To'] = toaddr
    if manual:
        html = render_template('mail_mail_verification_failed.html', url=message, name=name)
    else:
        html = render_template('mail_mail_verification.html', url=message, name=name)
    msg.attach(MIMEText(message, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    port = 587  # For TLS
    password = os.getenv('MAIL_AUTH')

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.zoho.eu", port) as server:
        server.starttls(context=context)
        server.login('info@swinglab.app', password)
        server.sendmail('info@swinglab.app', toaddr, msg.as_string())


def send_email_pw(toaddr, subject, message):
    # create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = formataddr(('Swinglab', 'info@swinglab.app'))
    msg['To'] = toaddr
    html = render_template('mail_reset_pw.html', url=message)
    msg.attach(MIMEText(message, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    port = 587  # For TLS
    password = os.getenv('MAIL_AUTH')

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP("smtp.zoho.eu", port) as server:
        server.starttls(context=context)
        server.login('info@swinglab.app', password)
        server.sendmail('info@swinglab.app', toaddr, msg.as_string())


# send email to all users that are not active yet
@auth.route('/console/send_verification_mails', methods=['POST'])
def send_verification_mails():
    # reverse order
    users = User.query.filter_by(active=False).all()
    users.reverse()
    for user in users:
        ts = URLSafeTimedSerializer('key')
        token = ts.dumps(user.email, salt='email-confirm-key')
        confirm_url = url_for('auth.verify_mail', token=token, _external=True)
        send_mail_smtp(user.email, 'Having trouble signing up?', confirm_url, user.name, manual=True)

    return jsonify({'success': True})


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
        return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

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

    user = User.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt'), active=False,
                    n_analyses=0, analyzed=0, unlimited=True, signup_date=datetime.now(), admin=False)

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

    subject = 'Swinglab – Verify your email'
    confirm_url = url_for('auth.verify_mail', token=token, _external=True)

    # send_email(email, subject, confirm_url)
    try:
        send_mail_smtp(email, subject, confirm_url, name=current_user.name)
    except Exception as e:
        # flash('Something went wrong. Please try again.')
        return render_template('mail_overload.html')

    return redirect(url_for('auth.verify'))


@auth.route('/verify_mail')
def verify():
    return render_template('verify_mail.html', title='Verify your email-address – swinglab')


@auth.route('/verify/<token>')
def verify_mail(token):
    ts = URLSafeTimedSerializer('key')
    try:
        # expires in 3 days
        email = ts.loads(token, salt='email-confirm-key', max_age=259200)
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

        subject = 'Swinglab – Reset your password'
        confirm_url = url_for('auth.reset_password_mail', token=token, _external=True)

        send_email_pw(email, subject, confirm_url)

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

    return render_template('new_password.html', token=token, title='New Password – Swinglab')


@auth.route('/reset_password_mail/<token>', methods=['POST'])
def reset_password_mail_post(token):
    ts = URLSafeTimedSerializer('key')
    try:
        email = ts.loads(token, salt='password-reset-key', max_age=86400)
    except:
        abort(404)

    user = User.query.filter_by(email=email).first_or_404()
    user.password = generate_password_hash(request.form.get('password'), method='scrypt')
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
            flash('Check your inbox to confirm your email address', 'success')
            user.email_new = email_new

            ts = URLSafeTimedSerializer('key')

            token = ts.dumps(email_new, salt='email-confirm-key')

            subject = 'Swinglab – Confirm your email'
            confirm_url = url_for('auth.verify_mail_update', token=token, _external=True)

            send_mail_smtp(email_new, subject, (confirm_url), name=current_user.name)

    if name_new != current_user.name and name_new is not None:
        user.name = name_new
        flash('Name updated successfully', 'success')

    if (password_new is not None) and (password_old is not None):
        if check_password_hash(current_user.password, password_old):
            # flash('Please check your login details and try again.')
            user.password = generate_password_hash(password_new, method='scrypt')
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

    if current_user.subscription is not None:
        stripe.Subscription.delete(current_user.subscription)

        # check if subscription is canceled
        for i in range(20):
            # Getting database updates
            db.session.refresh(user)

            time.sleep(0.5)

            # Refresh the user
            user = User.query.filter_by(email=current_user.email).first_or_404()
            if user.subscription is None:
                break

            if i == 19:
                flash('Something went wrong, please try again', 'error')
                return redirect(url_for('main.profile'))

    # Delete user files in asset folder
    if os.path.exists(url_for('static', filename=user.id)):
        shutil.rmtree(url_for('static', filename=user.id))

    db.session.delete(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/console')
@login_required
def console():
    if not current_user.admin:
        abort(403)

    # users = User.query
    # first 50 users
    users = User.query.limit(50)
    total_users = User.query.count()
    active_users = User.query.filter_by(active=True).count()
    subscribers = User.query.filter_by(unlimited=True).count()

    return render_template('console.html', users=users, total_users=total_users, active_users=active_users,
                           subscribers=subscribers)


@auth.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data

    try:
        event = json.loads(payload)
    except Exception as e:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return jsonify(success=False)

    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        email = event['data']['object']['customer_details']['email']
        product = event['data']['object']['metadata']['product']
        user = User.query.filter_by(email=email).first_or_404()

        if product == 'starter':
            user.n_analyses += 2
            db.session.commit()
        elif product == 'essential':
            user.n_analyses += 5
            db.session.commit()

    elif event['type'] == 'customer.subscription.updated':
        # print('Subscription updated')
        # get the customer id
        customer_id = event['data']['object']['customer']
        # retrieve the customer
        customer = stripe.Customer.retrieve(customer_id)
        # get the email
        email = customer['email']
        user = User.query.filter_by(email=email).first_or_404()
        # check if the subscription is active
        if event['data']['object']['status'] == 'active':
            # print('Subscription active')
            user.unlimited = True
            user.subscription = event['data']['object']['id']
            db.session.commit()

        # Unsubscribe
        if event['data']['object']['cancel_at_period_end']:
            user.canceled = True
            db.session.commit()

        # Reactivate
        if event['data']['object']['cancel_at_period_end'] is False:
            # print('Reactivated')
            user.canceled = False
            db.session.commit()

    # Delete subscription
    elif event['type'] == 'customer.subscription.deleted':
        # print('Subscription deleted')
        # get the customer id
        customer_id = event['data']['object']['customer']
        # retrieve the customer
        customer = stripe.Customer.retrieve(customer_id)
        # get the email
        email = customer['email']
        user = User.query.filter_by(email=email).first_or_404()
        # check if the subscription is active
        if event['data']['object']['status'] == 'canceled':
            user.unlimited = False
            user.subscription = None
            user.canceled = False
            db.session.commit()

    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)


@auth.route('/unsubscribe')
@login_required
def unsubscribe():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    subscription = user.subscription
    if subscription is not None:
        stripe.Subscription.modify(
            subscription,
            cancel_at_period_end=True,
        )
    # check if canceled is false
    for i in range(20):
        # Getting database updates
        db.session.refresh(user)

        time.sleep(0.5)

        # Refresh the user
        user = User.query.filter_by(email=current_user.email).first_or_404()
        if user.canceled:
            break

        if i == 19:
            flash('Something went wrong, please try again', 'error')

    flash('You have successfully unsubscribed. The subscription will be terminated by the end of the billing period.',
          'success')
    return redirect(url_for('main.profile'))


@auth.route('/reactivate')
@login_required
def reactivate():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    subscription = user.subscription
    if subscription is not None:
        stripe.Subscription.modify(
            subscription,
            cancel_at_period_end=False,
        )
    # check if canceled is false
    for i in range(20):
        # Getting database updates
        db.session.refresh(user)

        time.sleep(0.5)

        # Refresh the user
        user = User.query.filter_by(email=current_user.email).first_or_404()
        if not user.canceled:
            break

        if i == 19:
            flash('Something went wrong, please try again', 'error')

    flash('You have successfully reactivated your subscription.', 'success')
    return redirect(url_for('main.profile'))


@auth.route('/set_signup_date', methods=['POST'])
def set_signup_date():
    users = User.query.all()

    for user in users:
        if user.signup_date is None:
            user.signup_date = datetime.now()

    db.session.commit()

    return jsonify(success=True)
