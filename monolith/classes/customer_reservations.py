from monolith.database import db, Restaurant, Like, Reservation, RestaurantTable
from datetime import datetime, time, timedelta, date
from sqlalchemy import func, and_


# Computes the list of reserved tables (filtered by reservation_seats) that overlap with the
# wanted reservation_date and reservation_time
def get_overlapping_tables(restaurant_id: int, reservation_date: datetime,
                           reservation_seats: int, avg_stay_time: time):
    res_time = reservation_date.time()
    inf_limit_time = diff_time(res_time, avg_stay_time)
    sup_limit_time = sum_time(res_time, avg_stay_time)

    inf_limit = datetime.combine(reservation_date.date(), inf_limit_time)
    sup_limit = datetime.combine(reservation_date.date(), sup_limit_time)
    print(inf_limit)
    print(sup_limit)
    overlapping_tables = db.session.query(Reservation.table_no).filter_by(
        restaurant_id=restaurant_id).filter_by(seats=reservation_seats).filter(
            and_(Reservation.reservation_date >= inf_limit,
                 Reservation.reservation_date <= sup_limit)).all()
    print(overlapping_tables)
    overlapping_tables_ids = [id for id, in overlapping_tables]
    print(overlapping_tables_ids)

    return overlapping_tables_ids


def is_overbooked(restaurant_id: int, reservation_seats: int,
                  overlapping_tables):
    n_tables_by_seats = db.session.query(func.count(
        RestaurantTable.table_id)).filter_by(
            restaurant_id=restaurant_id).filter_by(
                seats=reservation_seats).first()[0]
    #The restaurant has no tables with the needed number_of_seats
    if (n_tables_by_seats is None):
        return True
    # All the tables are occupied in the chosen time interval
    if (len(overlapping_tables) == n_tables_by_seats):
        return True
    elif (len(overlapping_tables) < n_tables_by_seats):
        return False


def assign_table_to_reservation(overlapping_tables, restaurant_id: int,
                                reservation_seats: int):
    #  available_tables contains all the tables that do not overlap with the new reservation.
    #  This condition is needed to bind a table to a reservation
    available_tables = db.session.query(RestaurantTable).filter_by(
        restaurant_id=restaurant_id).filter_by(seats=reservation_seats).filter(
            RestaurantTable.table_id.notin_(overlapping_tables))
    return available_tables.first()


def add_reservation(reservation: Reservation):
    db.session.add(reservation)
    db.session.commit()


def diff_time(t1: time, t2: time):
    t1_delta = timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second)
    t2_delta = timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second)
    return (datetime.min + (t1_delta - t2_delta)).time()


def sum_time(t1: time, t2: time):
    t1_delta = timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second)
    t2_delta = timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second)
    return (datetime.min + (t1_delta + t2_delta)).time()
