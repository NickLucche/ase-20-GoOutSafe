from monolith.background import celery
from monolith.database import Restaurant

@celery.task
def average_review_stars():
    """
        Task run periodically in an async manner, used for computing the
        mean review score of every restaurant.
    """
    pass