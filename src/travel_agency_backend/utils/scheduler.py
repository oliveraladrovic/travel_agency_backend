from apscheduler.schedulers.background import BackgroundScheduler

from ..db.session import SessionFactory
from ..services.booking_services import expire_due_bookings


def run_expire_due_bookings():
    session = SessionFactory()
    try:
        expire_due_bookings(session)
    finally:
        session.close()


scheduler = BackgroundScheduler()

scheduler.add_job(run_expire_due_bookings, "cron", hour=0, minute=0)
