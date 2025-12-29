from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Boolean, func
from sqlalchemy.orm import relationship
from app.database import Base

class CronJob(Base):
    __tablename__ = "cron_job"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String,ForeignKey("users.uid", ondelete="CASCADE"),nullable=False,unique=True)
    creation_time = Column(DateTime(timezone=True), server_default=func.now())
    next_run_time = Column(DateTime(timezone=True), nullable=True)  # exact next run
    task_path = Column(String, nullable=False)  # e.g., tasks.reset_credits.reset_credits
    status = Column(String, default="active")  # active / inactive

    user = relationship("User", back_populates="cron_job",uselist=False,)