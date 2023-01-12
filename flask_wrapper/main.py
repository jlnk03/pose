import flask
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import db
import stripe
from .models import User

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

    YOUR_DOMAIN = 'http://127.0.0.1:8080'
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
            success_url=YOUR_DOMAIN + f'/success/{product}',
            cancel_url=YOUR_DOMAIN + '/profile',
        )
    except Exception as e:
        return str(e)

    id = checkout_session.id

    return redirect(checkout_session.url, code=303)


@main.route('/success/<product>')
@login_required
def success(product):
    user = User.query.filter_by(email=current_user.email).first_or_404()

    if product == 'starter':
        user.n_analyses += 2
    elif product == 'essential':
        user.n_analyses += 5
    elif product == 'professional':
        user.unlimited = True

    db.session.add(user)
    db.session.commit()

    return render_template('success.html')
