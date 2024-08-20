from apscheduler.schedulers.background import BackgroundScheduler

def reset_usage():
    db = SessionLocal()
    db.query(User).update({User.usage: 0})
    db.commit()
    db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(reset_usage, 'interval', weeks=1)
scheduler.start()

# Shut down the scheduler when exiting the app
import atexit
atexit.register(lambda: scheduler.shutdown())
