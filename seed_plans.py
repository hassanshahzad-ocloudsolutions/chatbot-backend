
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.subscription_plan import SubscriptionPlan
from datetime import datetime

def seed_plans():
    db: Session = SessionLocal()

    plans = [
        {"name": "Free", "daily_credits": 5, "price_cents": 0},
        {"name": "Pro", "daily_credits": 25, "price_cents": 1000},
        {"name": "Enterprise", "daily_credits": 50, "price_cents": 2500},
    ]

    for plan_data in plans:
        plan = db.query(SubscriptionPlan).filter_by(name=plan_data["name"]).first()
        if not plan:
            plan = SubscriptionPlan(**plan_data, created_at=datetime.utcnow())
            db.add(plan)
    
    db.commit()
    all_plans = db.query(SubscriptionPlan).all()
    db.close()
    print("Seeded subscription plans:")
    for plan in all_plans:
        print(f"- {plan.name} ({plan.daily_credits} credits, {plan.price_cents} cents)")

if __name__ == "__main__":
    seed_plans()
