from sqlalchemy.orm import Session
from app.database import get_db
from app.repo.subscription_repo import SubscriptionRepo
from app.models.user import User

# create a DB session
db = get_db()

# fetch the user you want to test
user = db.query(User).filter(User.uid == "uPB2YVOM48fBwlGZSZzqpLOnvdd2").first()

if not user:
    print("User not found")
else:
    try:
        print(user.subscription_id)
        updated_user = SubscriptionRepo.cancel_to_free(db, user)
        print(f"User downgraded successfully. New plan id: {updated_user.subscription_id}")
    except Exception as e:
        print(f"Error: {e}")
