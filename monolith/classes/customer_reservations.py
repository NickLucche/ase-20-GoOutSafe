from monolith.database import db, Reservation, RestaurantTable, ReservationState
from datetime import datetime, time, timedelta, date
from sqlalchemy import func, and_, or_


# Computes the list of reserved tables (filtered by reservation_seats) that overlap with the
# wanted reservation_time and reservation_time
def get_overlapping_tables(restaurant_id: int, reservation_time: datetime,
                           reservation_seats: int, avg_stay_time: time):
    res_time = reservation_time.time()
    inf_limit_time = diff_time(res_time, avg_stay_time)
    sup_limit_time = sum_time(res_time, avg_stay_time)

    inf_limit = datetime.combine(reservation_time.date(), inf_limit_time)
    sup_limit = datetime.combine(reservation_time.date(), sup_limit_time)
    print(inf_limit)
    print(sup_limit)
    overlapping_tables = db.session.query(Reservation.table_no).filter_by(
        restaurant_id=restaurant_id).filter_by(seats=reservation_seats).filter(
            and_(Reservation.reservation_time >= inf_limit,
                 Reservation.reservation_time <= sup_limit)).filter(
                     or_(Reservation.status == ReservationState.ACCEPTED,
                         Reservation.status == ReservationState.PENDING,
                         Reservation.status == ReservationState.SEATED)).all()
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


def get_user_reservations(user_id: int):
    """ 
    Returns a list of all the future reservations performed by a particular user specified by user_id.
    """
    #  No need to filter by Reservation.status != DONE since we are only considering future reservations.

    user_reservations = db.session.query(Reservation).filter_by(
        user_id=user_id).filter(
            Reservation.reservation_time > datetime.now()).order_by(
                Reservation.status.asc(),
                Reservation.reservation_time.asc()).all()
    print(user_reservations)
    return user_reservations


def is_safely_updatable(reservation: Reservation,
                        new_reservation_time: datetime):
    """ 
    Returns True if the reservation can be safely updated, False otherwise.
    A reservation can be safely updated if the new reservation date specified by new_reservation_time
    is in the closed interval [reservation_time - avg_stay_time, reservation_time + avg_stay_time]
    """
    old_res_time = reservation.reservation_time.time()
    avg_stay_time = reservation.restaurant.avg_stay_time

    inf_limit_time = diff_time(old_res_time, avg_stay_time)
    sup_limit_time = sum_time(old_res_time, avg_stay_time)

    inf_limit = datetime.combine(reservation.reservation_time.date(),
                                 inf_limit_time)
    sup_limit = datetime.combine(reservation.reservation_time.date(),
                                 sup_limit_time)

    if (new_reservation_time >= inf_limit
            and new_reservation_time <= sup_limit):
        return True
    else:
        return False


def update_reservation(reservation: Reservation,
                       new_reservation_time: datetime, new_seats: int):
    """ 
    Returns True if the reservion is updated, False otherwise.
    """
    if (new_seats == reservation.seats
            and is_safely_updatable(reservation, new_reservation_time)):
        reservation.reservation_time = new_reservation_time
        reservation.status = ReservationState.PENDING
        db.session.commit()
        return True
    else:
        overlapping_tables = get_overlapping_tables(
            restaurant_id=reservation.restaurant_id,
            reservation_time=new_reservation_time,
            reservation_seats=new_seats,
            avg_stay_time=reservation.restaurant.avg_stay_time)
        if (is_overbooked(restaurant_id=reservation.restaurant_id,
                          reservation_seats=new_seats,
                          overlapping_tables=overlapping_tables)):
            return False
        else:
            new_table = assign_table_to_reservation(
                overlapping_tables=overlapping_tables,
                restaurant_id=reservation.restaurant_id,
                reservation_seats=new_seats)
            reservation.reservation_time = new_reservation_time
            reservation.table_no = new_table.table_id
            reservation.seats = new_seats
            reservation.status = ReservationState.PENDING
            db.session.commit()
            return True


def delete_reservation(reservation_id: int):
    """ 
    Deletes the reservation corresponding to the given reservation_id. 
    Returns True if the reservation is succesfully deleted, False otherwise.
    """
    reservation_to_be_deleted = db.session.query(Reservation).filter_by(
        id=reservation_id).first()
    print(reservation_to_be_deleted)
    if reservation_to_be_deleted == None:
        return False
    else:
        db.session.delete(reservation_to_be_deleted)
        db.session.commit()
        return True


def diff_time(t1: time, t2: time):
    t1_delta = timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second)
    t2_delta = timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second)
    return (datetime.min + (t1_delta - t2_delta)).time()


def sum_time(t1: time, t2: time):
    t1_delta = timedelta(hours=t1.hour, minutes=t1.minute, seconds=t1.second)
    t2_delta = timedelta(hours=t2.hour, minutes=t2.minute, seconds=t2.second)
    return (datetime.min + (t1_delta + t2_delta)).time()
