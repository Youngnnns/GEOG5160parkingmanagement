from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django_apscheduler.jobstores import DjangoJobStore
import logging
from .models import Reservation

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), alias="default")


def increase_available_spaces(reservation_id):
    try:
        reservation = Reservation.objects.get(id=reservation_id)
        parking_lot = reservation.parking_lot
        if parking_lot.available_spaces < parking_lot.capacity:
            parking_lot.available_spaces += 1
            parking_lot.save()
            logger.info(f"Available spaces increased for reservation {reservation_id}. Now: {parking_lot.available_spaces}")
        else:
            logger.warning(f"No update needed. Parking lot {parking_lot.objectid} already at capacity.")
    except Reservation.DoesNotExist:
        logger.error(f"Reservation with id {reservation_id} does not exist")


def set_reservation_end_task(reservation_id, end_time):
    trigger = DateTrigger(run_date=end_time)
    scheduler.add_job(
        increase_available_spaces,
        trigger,
        args=[reservation_id],
        id=str(reservation_id)
    )
    logger.info(f"Set task to increase available spaces for reservation {reservation_id} at {end_time}")


def start():
    scheduler.start()
    logger.info("Scheduler started")


