from monolith.background import celery
from monolith.database import User

@celery.task
def check_visited_places(user: User):
    print("Checking visited places")


class Notifications:

    def __init__(self) -> None:
        pass