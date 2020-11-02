from monolith.background import celery
from monolith.database import Restaurant, Review, db

@celery.task
def average_review_stars():
    """
        Task run periodically in an async manner, used for computing the
        mean review score of every restaurant.
    """
    # tasks are wrapped in app context
    reviews = Review.query.filter_by(marked=False).join(Restaurant)\
        .with_entities(Review, Restaurant).all()
    for review, restaurant in reviews:
        # compute running mean of reviews
        restaurant.num_reviews += 1
        restaurant.avg_stars = 1/restaurant.num_reviews * \
            (restaurant.avg_stars * (restaurant.num_reviews-1) + review.stars)
    # update rows            
    db.session.commit()