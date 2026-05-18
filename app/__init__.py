from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from datetime import timedelta
import os

db = SQLAlchemy()

def create_app():
    app = Flask(
        __name__,
        static_folder='Static',       
        static_url_path='/static'     
    )

    app.permanent_session_lifetime = timedelta(minutes=10)

    app.config.from_object(Config)

    # 📸 Configuración de subida de imágenes
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'Static', 'img')

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app