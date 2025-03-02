# my_app/__init__.py
from flask import Flask
from celery import Celery
import pandas as pd


celery = None

def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Initialize Celery only once
    init_celery(app)

    # Register your blueprints, etc.
    from my_app.churn import churn_bp
    app.register_blueprint(churn_bp)

    return app

def init_celery(app=None):
    global celery
    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL"),
        backend=app.config.get("CELERY_RESULT_BACKEND"),
    )
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        """Make Celery tasks work with Flask’s application context."""

        def __call__(self, *args, **kwargs):
            if app:
                with app.app_context():
                    return TaskBase.__call__(self, *args, **kwargs)
            else:
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
