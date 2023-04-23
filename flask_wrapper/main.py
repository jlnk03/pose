import datetime
import json
import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import flask
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import stripe
from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from itsdangerous import URLSafeTimedSerializer

from code_b.process import process_motion
from . import db
from .models import User, Transactions

# import memory_profiler

stripe.api_key = os.getenv('STRIPE_API_KEY')

main = Blueprint('main', __name__)


def send_mail_smtp(toaddr, subject, message):
    # create message
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Contact form – {subject}'
    msg['From'] = formataddr(('Swinglab', 'info@swinglab.app'))
    msg['To'] = toaddr
    html = render_template('contact_form_mail.html', message=message)
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


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, email=current_user.email, title='Profile – Swinglab')


@main.route('/dash')
@login_required
def dashboard():
    # print(f'url is{flask.request.host_url}')
    # return render_template('dashboard.html', name=current_user.name, url=f'{flask.request.host_url}/dashboard')
    if current_user.active:
        return flask.redirect('/dashboard')

    # flash('Please confirm your email to access the dashboard')
    # return render_template('verify_mail.html')
    return flask.redirect('/verify_mail')


@main.route('/payment/<product>/<mode>')
def payment(product, mode):
    if mode == 'subscription':
        methods = ['card', 'sepa_debit']
    else:
        methods = ['card', 'klarna', 'sepa_debit', 'giropay']

    if product == 'starter':
        price = os.getenv('STRIPE_PRICE_STARTER')
    elif product == 'essential':
        price = os.getenv('STRIPE_PRICE_ESSENTIAL')
    elif product == 'professional':
        price = os.getenv('STRIPE_PRICE_PROFESSIONAL')
    else:
        return redirect(url_for('main.profile'))

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': price,
                    'quantity': 1,
                },
            ],
            automatic_tax={
                'enabled': True
            },
            customer_email=current_user.email,
            payment_method_types=methods,
            mode=mode,
            allow_promotion_codes=True,
            success_url=url_for('main.success', product=product, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.cancel', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            metadata={
                'product': product,
            }
        )

        checkout_id = checkout_session.id
        db.session.add(
            Transactions(session_id=checkout_id, time=datetime.datetime.now(), amount=checkout_session.amount_total))
        db.session.commit()

    except Exception as e:
        return str(e)
        # return 'Sorry, something went wrong. Please try again later.'

    return redirect(checkout_session.url, code=303)


@main.route('/success/<product>', methods=['GET'])
@login_required
def success(product):
    user = User.query.filter_by(email=current_user.email).first_or_404()
    id = request.args.get('session_id')
    session = db.session.query(Transactions).filter_by(session_id=id).first()

    response = stripe.checkout.Session.retrieve(id)
    # print(type(response))

    if session is None:
        abort(404)

    if response['payment_status'] != 'paid':
        db.session.delete(session)
        db.session.commit()
        flash('Payment failed')
        return redirect(url_for('main.profile'))

    if session.booked:
        flash('This purchase has already been booked')
        return redirect(url_for('main.profile'))

    # if product == 'starter':
    #     user.n_analyses += 2
    # elif product == 'essential':
    #     user.n_analyses += 5
    # elif product == 'professional':
    #     user.unlimited = True

    # db.session.add(user)
    session.booked = True
    db.session.commit()

    return render_template('success.html', title='Thank you for your purchase – Swinglab')


@main.route('/cancel', methods=['GET'])
@login_required
def cancel():
    user = User.query.filter_by(email=current_user.email).first_or_404()
    id = request.args.get('session_id')
    session = db.session.query(Transactions).filter_by(session_id=id).first()

    if session is None:
        abort(404)

    db.session.delete(session)
    db.session.commit()

    return redirect(url_for('main.profile'))


@main.route('/history')
@login_required
def history():
    id = current_user.id
    files = []

    if os.path.exists(f'../save_data/{id}'):
        files = os.listdir(f'../save_data/{id}')

    return render_template('saved.html', files=files)


@main.route('/history_saved/<file>')
@login_required
def history_saved(file):
    data = pd.read_parquet(f'../save_data/{current_user.id}/{file}')
    duration = data['duration'][0]
    duration = np.linspace(0, duration, len(data['duration']))
    fig = go.Figure(data=[go.Scatter(x=duration, y=data['pelvis_rotation'])])
    fig_json = pio.to_json(fig)

    return render_template('saved_plot.html', fig_json=fig_json)


@main.route('/privacy')
def privacy():
    return render_template('privacy.html', title='Privacy Policy – Swinglab')


@main.route('/terms')
def terms():
    return render_template('terms.html', title='Terms of use – Swinglab')


@main.route('/impressum')
def impressum():
    return render_template('impressum.html', title='Impressum – Swinglab')


@main.route('/guide')
def guide():
    return render_template('guide.html', title='Guide – Swinglab')


@main.route('/contact')
def contact():
    return render_template('contact.html', title='Contact Us – Swinglab')


@main.route('/contact', methods=['POST'])
def contact_post():
    subject = request.form.get('subject')
    message = request.form.get('message')

    send_mail_smtp('info@swinglab.app', subject, message)

    # return render_template('contact.html', title='Contact Us – Swinglab')
    return redirect(request.referrer)


@main.route('/practice')
def practice():
    return render_template('livePoseView.html', title='Practice – Swinglab')


@main.route('/predict/<token>', methods=['POST'])
# @memory_profiler.profile
def predict(token):
    ts = URLSafeTimedSerializer('key')
    try:
        email = ts.loads(token, salt='verification-key', max_age=1200)
    except:
        abort(403)

    user = User.query.filter_by(email=email).first_or_404()

    if user.n_analyses == 0 and not user.unlimited:
        abort(403)

    contents, filename, location = request.get_json().values()

    # profiler = cProfile.Profile()
    # profiler.enable()

    # Extracting the motion data from the video
    result = process_motion(contents, filename, location)
    # print(result)

    result = [value.tolist() if isinstance(value, np.ndarray) else value for value in result]

    if result == -1:
        return 413

    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_sway, save_pelvis_thrust, save_pelvis_lift, \
        save_thorax_rotation, save_thorax_bend, save_thorax_tilt, save_thorax_sway, save_thorax_thrust, \
        save_thorax_lift, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, \
        save_wrist_angle, save_wrist_tilt, save_left_arm_length, save_arm_rotation, save_arm_to_ground, \
        arm_position, duration, fps, impact_ratio = result

    keys = [
        'save_pelvis_rotation',
        'save_pelvis_tilt',
        'save_pelvis_lift',
        'save_pelvis_sway',
        'save_pelvis_thrust',
        'save_thorax_lift',
        'save_thorax_bend',
        'save_thorax_sway',
        'save_thorax_rotation',
        'save_thorax_thrust',
        'save_thorax_tilt',
        'save_spine_rotation',
        'save_spine_tilt',
        'save_head_rotation',
        'save_head_tilt',
        'save_left_arm_length',
        'save_wrist_angle',
        'save_wrist_tilt',
        'save_arm_rotation',
        'save_arm_to_ground',
        'arm_position',
        'duration',
        'fps',
        'impact_ratio'
    ]

    values = [
        save_pelvis_rotation,
        save_pelvis_tilt,
        save_pelvis_lift,
        save_pelvis_sway,
        save_pelvis_thrust,
        save_thorax_lift,
        save_thorax_bend,
        save_thorax_sway,
        save_thorax_rotation,
        save_thorax_thrust,
        save_thorax_tilt,
        save_spine_rotation,
        save_spine_tilt,
        save_head_rotation,
        save_head_tilt,
        save_left_arm_length,
        save_wrist_angle,
        save_wrist_tilt,
        save_arm_rotation,
        save_arm_to_ground,
        arm_position,
        duration,
        fps,
        impact_ratio
    ]

    prediction = dict(zip(keys, values))

    prediction = json.dumps(prediction)

    return prediction, 200, {'ContentType': 'application/json'}
