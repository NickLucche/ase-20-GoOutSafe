from celery import Celery
from celery.schedules import crontab
from monolith.database import db, User, Restaurant

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


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

def register_positive(user_id):
    print("Celery call...")
    celery.add_periodic_task(30.0, nop("hello"), expires=30)
    print("Celery registered")

@celery.task
def nop(user_id):
    print(user_id)

@celery.task
def unmark_positive(user_id):
    print("unmark called")
    user = User.query.filter_by(id=user_id).first()
    if user != None and user.is_markedPositive == True:
        user.is_markedPositive = False
        db.session.commit()
        print("unregistered")
