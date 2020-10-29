from monolith.app import create_app
from celery import Celery
from celery.schedules import crontab
from monolith.database import db, User, Restaurant
from datetime import datetime, timedelta

UNMARK_DAYS = 14

# BACKEND = BROKER = 'redis://localhost:6379'
def make_celery(app):
    # create celery object from single flask app configuration
    celery = Celery(__name__, backend=app.config['CELERY_RESULT_BACKEND'], 
    broker=app.config['CELERY_BROKER_URL'], 
    include=['monolith.classes.notifications', 'monolith.background']) # include list of modules to import when worker tarts

    celery.conf.update(app.config)
    # subclass celery task so that each task execution is wrapped in an app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery.conf.beat_schedule = {
    # Executes every minute
    'add-every-monday-morning': {
        'task': 'tasks.unmark_positive',
        'schedule': crontab(minute='*/1'),
        'args': (1),
    },
}

@celery.task
def do_task():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        
        db.init_app(app)
    else:
        app = _APP

    return []


# TODO XXX: TBT
def register_positive(user_id: int):
    print("Celery call...")
    celery.add_periodic_task(10.0, unmark_positive.s(user_id), name='14 days delay')
    print("Celery registered")


# TODO XXX: TBT
@celery.task
def unmark_positive(user_id):
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP

    with app.app_context():
        user = User.query.filter_by(id=user_id).first()
        if user != None and user.is_positive == True:
            user.is_positive = False
            db.session.commit()

    return []
celery = make_celery(create_app())

# _APP = None


# @celery.task
# def do_task():
#     global _APP
#     # lazy init
#     if _APP is None:
#         from monolith.app import create_app
#         app = create_app()
#         db.init_app(app)
#     else:
#         app = _APP

#     return []

# TODO XXX: TBT
@celery.task
def unmark_AllPositives():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP

    now = datetime.now()
    time_limit = now - timedelta(days=UNMARK_DAYS)
    with app.app_context():
        users = User.query.filter_by(is_positive=True).\
            filter(User.reported_positive_date >= time_limit).all()
        for user in users:
            if user != None and user.is_positive == True:
                user.is_positive = False
        db.session.commit()

    return []