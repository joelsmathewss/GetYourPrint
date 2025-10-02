import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret'

    # Database path inside Flask's instance folder
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'database.sqlite')
    app.config['UPLOAD_FOLDER'] = 'uploads'
    
    # Ensure required folders exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # Import models so tables are created
    from models import User, PrintJob
    with app.app_context():
        db.create_all()

    # Import routes
    import routes
    app.register_blueprint(routes.bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
