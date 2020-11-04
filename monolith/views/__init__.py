from .home import home
from .auth import auth
from .users import users
from .restaurants import restaurants
from .authority import authority
from .reservations import reservations
from .customer_reservations import customer_reservations

blueprints = [home, auth, users, restaurants, reservations, authority, customer_reservations]
