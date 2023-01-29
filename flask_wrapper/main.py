import flask
import numpy as np
from flask import Blueprint, render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from . import db
import stripe
from .models import User, Transactions
import datetime
import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

stripe.api_key = 'sk_test_51MOtJiGVoQxCE2O4tyBqLDo3P64ohVzHBnecrrvnJbvPMjIOc0wSklIuOBqWKpaw4HFCUlL57X1Nuwm8KbuRjgMB00Ijxr6CKq'

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name, email=current_user.email)


@main.route('/dash')
@login_required
def dashboard():
    # print(f'url is{flask.request.host_url}')
    # return render_template('dashboard.html', name=current_user.name, url=f'{flask.request.host_url}/dashapp')
    if current_user.active:
        return flask.redirect('/dashapp')

    # flash('Please confirm your email to access the dashboard')
    # return render_template('verify_mail.html')
    return flask.redirect('/verify_mail')


@main.route('/payment/<product>/<mode>')
def payment(product, mode):

    # YOUR_DOMAIN = 'http://127.0.0.1:8080'
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
            success_url=url_for('main.success', _external=True) + f'/{product}' + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('main.cancel', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
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
    # print(response)
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

    if product == 'starter':
        user.n_analyses += 2
    elif product == 'essential':
        user.n_analyses += 5
    elif product == 'professional':
        user.unlimited = True

    # db.session.add(user)
    session.booked = True
    db.session.commit()

    return render_template('success.html')


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