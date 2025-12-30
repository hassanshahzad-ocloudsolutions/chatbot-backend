from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.user import User
import logging 
from app.services.cron_service import schedule_job  
from app.models.cron_job import CronJob

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__) 

def reset_user_credits(user_id: str):
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.uid == user_id).first()
        if not user:
            return 
        
        if user.subscription_id==1:
            now = datetime.utcnow()
            if now - user.last_reset >= timedelta(days=1):
                user.credits_left = user.plan.daily_credits
                user.last_reset = now
                db.commit()
                logger.info(f"Credits reset successfully for user {user_id}. New credits: {user.credits_left}")
        else:
            return 
        
        cron = db.query(CronJob).filter(CronJob.user_id == user_id, CronJob.status == "active").first()
        if cron:
            # Schedule for the same time next day
            cron.next_run_time = cron.next_run_time + timedelta(minutes=3)
            db.commit()
            logger.info(f"Rescheduling next credit reset for user {user_id} at {cron.next_run_time}")
            schedule_job(db, cron)  # Schedule in APScheduler

    except Exception as e:
        logger.error(f"Error resetting credits for user {user_id}: {e}")
        db.rollback()

    finally:
        db.close()
        
