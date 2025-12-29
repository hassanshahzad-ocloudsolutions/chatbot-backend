from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
import logging 

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)

logger = logging.getLogger(__name__) 

def reset_user_credits(user_id: str) -> bool:
    try:
        db = SessionLocal()
        user = db.query(User).filter(User.uid == user_id).first()
        if not user:
            return False
        
        if user.subscription_id==1:
            now = datetime.utcnow()
            if now - user.last_reset >= timedelta(days=1):
                user.credits_left = user.plan.daily_credits
                user.last_reset = now
                db.commit()
                logger.info(f"Credits reset successfully for user {user_id}. New credits: {user.credits_left}")
                return True
        else:
            return False
    
    except Exception as e:
        logger.info(f"Error resetting credits for user {user_id}: {str(e)}")
        db.rollback()
        return False
            
