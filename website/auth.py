from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash(f'Welcome back, {user.user_name}!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password is incorrect', category='error')
        else:
            flash('Email not found.', category='error')
    return render_template('login.html', user=current_user)

@auth.route('/SignUp', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        user_name = request.form.get('userName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Looks like you already have an account.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 charachters.', category='error')
        elif len(user_name) < 2:
            flash('Username must be greater than 1 charachter.', category='error')
        elif password1 != password2:
            flash('Passwords do not match.', category='error')
        elif len(password1) < 7 or len(password1) > 15:
            flash('Password must be between 7 and 15 characters.', category='error')
        else:
            new_user = User(email=email, user_name=user_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template('sign_up.html', user=current_user)

@auth.route('/Logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/DeleteAccount', methods=['GET', 'POST'])
@login_required
def remove_account():
    if request.method == 'POST':
        User.query.filter(User.id == current_user.id).delete()
        db.session.commit()
        logout_user()
        flash('Account Deleted.', category='error')
        return redirect(url_for('auth.login'))
    else:
        flash('Oncec your account is deleted, it cannot be undone.', category='error')
    return render_template('remove_acct.html', user=current_user)