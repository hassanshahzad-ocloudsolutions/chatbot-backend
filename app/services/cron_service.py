from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.cron_job import CronJob
from app.models.user import User
from importlib import import_module
from apscheduler.triggers.date import DateTrigger
from apscheduler.schedulers.background import BackgroundScheduler
import logging
from sqlalchemy.exc import IntegrityError



logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__) 

scheduler = BackgroundScheduler(timezone="UTC")
scheduler.start()

RESET_TASK = "app.tasks.reset_credits.reset_user_credits"


def schedule_job(db:Session,cron: CronJob):
    if cron.status != "active" or not cron.next_run_time:
        logger.info(f"Skipping scheduling for user_id={cron.user_id}, status={cron.status}, next_run_time={cron.next_run_time}")
        return

    module_name, func_name = cron.task_path.rsplit(".", 1)
    func = getattr(import_module(module_name), func_name)

    job_id = f"cron_{cron.id}"
    try:
        scheduler.add_job(
            func=func,
            trigger=DateTrigger(run_date=cron.next_run_time),
            args=[cron.user_id],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Scheduled cron job '{job_id}' for user_id={cron.user_id} at {cron.next_run_time}")
    except Exception as e:
        logger.error(f"Failed to schedule cron job '{job_id}' for user_id={cron.user_id}: {e}")

class CronService:
    @staticmethod
    def create_cron_for_user(db: Session, user_id:str):

        cron = db.query(CronJob).filter(CronJob.user_id == user_id).first()
        if cron:
            schedule_job(db,cron)
            return 

        try:
            cron = CronJob(user_id=user_id,task_path=RESET_TASK,next_run_time= datetime.now(timezone.utc) + timedelta(minutes=3),status="active")
            db.add(cron)
            db.commit()
            db.refresh(cron)
            logger.info(f"Created new cron job id={cron.id} for user_id={user_id}, next_run_time={cron.next_run_time}")
            schedule_job(db,cron)
        
        except IntegrityError:
            db.rollback()

    @staticmethod
    def activate_cron(db: Session, user_id: int):
        cron = db.query(CronJob).filter(CronJob.user_id == user_id).first()
        if not cron:
            return

        cron.status = "active"
        cron.next_run_time = datetime.now(timezone.utc) + timedelta(minutes=3)
        db.commit()
        logger.info(f"Cron job id={cron.id} activated for user_id={user_id}, next_run_time={cron.next_run_time}")
        schedule_job(db,cron)

    @staticmethod
    def deactivate_cron(db: Session, user_id: int):
        cron = db.query(CronJob).filter(CronJob.user_id == user_id).first()
        if cron:
            cron.status = "inactive"
            db.commit()
            logger.info(f"Cron job id={cron.id} deactivated and removed from scheduler for user_id={user_id}")
            scheduler.remove_job(f"cron_{cron.id}")
