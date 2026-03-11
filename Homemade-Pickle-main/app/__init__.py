# """
# Flask Application Factory - DynamoDB Version
# """

# import os
# from flask import Flask, render_template
# from flask_login import LoginManager
# from dotenv import load_dotenv

# load_dotenv()

# login_manager = LoginManager()


# def create_app():

#     app = Flask(__name__)
#     app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "secretkey")

#     login_manager.init_app(app)
#     login_manager.login_view = "auth.login"
#     login_manager.login_message = "Please log in to access this page."
#     login_manager.login_message_category = "warning"

#     from app.models.user_model import User

#     @login_manager.user_loader
#     def load_user(user_id):
#         return User.find_by_id(user_id)

#     # Register blueprints
#     from app.routes.auth_routes import auth_bp
#     from app.routes.product_routes import product_bp
#     from app.routes.order_routes import order_bp

#     app.register_blueprint(auth_bp)
#     app.register_blueprint(product_bp)
#     app.register_blueprint(order_bp)

#     # Error handlers
#     @app.errorhandler(404)
#     def not_found(e):
#         return render_template("404.html"), 404

#     @app.errorhandler(500)
#     def server_error(e):
#         return render_template("500.html"), 500

#     # Create default admin on startup
#     with app.app_context():
#         _create_admin()

#     return app


# def _create_admin():
#     """Create default admin user in DynamoDB if not exists"""
#     from app.models.user_model import User
#     try:
#         admin_username = os.getenv("ADMIN_USERNAME", "admin")
#         if not User.find_by_username(admin_username):
#             User.create_user(
#                 username=admin_username,
#                 email=os.getenv("ADMIN_EMAIL", "admin@picklesnacks.com"),
#                 password=os.getenv("ADMIN_PASSWORD", "admin123"),
#                 role="admin"
#             )
#             print(f"  ✓ Admin user '{admin_username}' created.")
#     except Exception as e:
#         print(f"  ⚠ Admin creation skipped: {e}")




"""
Flask Application Factory - DynamoDB Version
"""

import os
from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()

login_manager = LoginManager()


def create_app():
    """Create and configure Flask application"""

    app = Flask(__name__)

    # Basic configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "super-secret-key")

    # Initialize Login Manager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    from app.models.user_model import User

    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login session"""
        return User.find_by_id(user_id)

    # ─────────────────────────────
    # Register Blueprints
    # ─────────────────────────────
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import product_bp
    from app.routes.order_routes import order_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(order_bp)

    # ─────────────────────────────
    # Error Handlers
    # ─────────────────────────────

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("500.html"), 500

    # ─────────────────────────────
    # Create default admin user
    # ─────────────────────────────

    with app.app_context():
        create_admin()

    return app


def create_admin():
    """Create default admin user in DynamoDB if not exists"""

    from app.models.user_model import User

    try:
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@picklesnacks.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")

        existing_admin = User.find_by_username(admin_username)

        if not existing_admin:
            User.create_user(
                username=admin_username,
                email=admin_email,
                password=admin_password,
                role="admin"
            )
            print(f"✓ Admin user '{admin_username}' created.")

    except Exception as e:
        print(f"⚠ Admin creation skipped: {e}")