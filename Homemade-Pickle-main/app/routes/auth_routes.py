"""
Authentication Routes - DynamoDB Version
Handles user registration, login, and logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.models.user_model import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('product.index'))

    if request.method == 'POST':

        username         = request.form.get('username', '').strip()
        email            = request.form.get('email', '').strip()
        password         = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        errors = []

        if not username:
            errors.append("Username required")
        elif len(username) < 3:
            errors.append("Username must be at least 3 characters")
        elif User.find_by_username(username):
            errors.append("Username already exists")

        if not email:
            errors.append("Email required")
        elif User.find_by_email(email):
            errors.append("Email already registered")

        if not password:
            errors.append("Password required")
        elif len(password) < 6:
            errors.append("Password must be at least 6 characters")
        elif password != confirm_password:
            errors.append("Passwords do not match")

        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template('auth/register.html', username=username, email=email)

        User.create_user(username=username, email=email, password=password, role="user")
        flash("Account created successfully. Please login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('product.index'))

    if request.method == 'POST':

        username_or_email = request.form.get('username_or_email', '').strip()
        password          = request.form.get('password', '')

        user = User.find_by_username_or_email(username_or_email)

        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('product.index'))

        flash("Invalid login credentials", "danger")

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out successfully", "success")
    return redirect(url_for('product.index'))
