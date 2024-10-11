# auth.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

# ----------------------- USER AUTHENTICATION-------------------------

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Retrieve User Credentials
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user:
            # Check if hashed password matches
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))  
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template('login.html')

# -----------------------  GENERATE A USER -------------------------

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Retrieve new user's information
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # Check if the user already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters', category='error')
        elif len(username) < 2:
            flash('First name must be greater than 1 characters', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error') 
        else:
            # Generate a password hash
            password_hash = generate_password_hash(password1)

            # Add the new user into the database
            new_user = User(email=email, username=username, password=password_hash)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)  # Login the new user automatically
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
        
    return render_template('login.html')

# -----------------------  LOG OUT -------------------------

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))
