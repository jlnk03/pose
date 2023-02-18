import json

import flask
import numpy as np
from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, send_from_directory, jsonify
from flask_login import login_required, current_user
from . import db
import stripe
from .models import User, Transactions
import datetime
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from code_b.process_mem import process_motion
from itsdangerous import URLSafeTimedSerializer

stripe.api_key = 'sk_test_51MOtJiGVoQxCE2O4tyBqLDo3P64ohVzHBnecrrvnJbvPMjIOc0wSklIuOBqWKpaw4HFCUlL57X1Nuwm8KbuRjgMB00Ijxr6CKq'

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, email=current_user.email, title='Profile – swinglab')


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
        price = 'price_1MP78iGVoQxCE2O44gaPjRcu'
    elif product == 'essential':
        price = 'price_1MP79AGVoQxCE2O41nDTF4xu'
    elif product == 'professional':
        price = 'price_1MP79lGVoQxCE2O4ZGQSEnTz'
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
            customer_email=current_user.email,
            payment_method_types=methods,
            mode=mode,
            success_url=url_for('main.success', product=product, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.cancel', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            metadata={
                'product': product,
            }
        )

        checkout_id = checkout_session.id
        db.session.add(Transactions(session_id=checkout_id, time=datetime.datetime.now(), amount=checkout_session.amount_total))
        db.session.commit()

    except Exception as e:
        return str(e)

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

    return render_template('success.html', title='Thank you for your purchase – swinglab')


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


@main.route('/predict/<token>', methods=['POST'])
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

    # Extracting the motion data from the video
    save_pelvis_rotation, save_pelvis_tilt, save_pelvis_lift, save_pelvis_sway, save_pelvis_thrust, \
    save_thorax_lift, save_thorax_bend, save_thorax_sway, save_thorax_rotation, save_thorax_thrust, \
    save_thorax_tilt, save_spine_rotation, save_spine_tilt, save_head_rotation, save_head_tilt, save_left_arm_length, save_wrist_angle, save_wrist_tilt, save_arm_rotation, arm_path, duration = process_motion(
        contents, filename, location)


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
        'arm_path',
        'duration'
    ]

    values = [
        list(save_pelvis_rotation),
        list(save_pelvis_tilt),
        list(save_pelvis_lift),
        list(save_pelvis_sway),
        list(save_pelvis_thrust),
        list(save_thorax_lift),
        list(save_thorax_bend),
        list(save_thorax_sway),
        list(save_thorax_rotation),
        list(save_thorax_thrust),
        list(save_thorax_tilt),
        list(save_spine_rotation),
        list(save_spine_tilt),
        list(save_head_rotation),
        list(save_head_tilt),
        list(save_left_arm_length),
        list(save_wrist_angle),
        list(save_wrist_tilt),
        list(save_arm_rotation),
        arm_path,
        duration
    ]

    prediction = dict(zip(keys, values))

    prediction = json.dumps(prediction)

    return prediction, 200, {'ContentType': 'application/json'}
