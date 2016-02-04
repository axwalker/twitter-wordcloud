from apscheduler.schedulers.blocking import BlockingScheduler

import tweet


sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=22)
def scheduled_job():
    tweet.post_word_clouds()


sched.start()
