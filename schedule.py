from apscheduler.schedulers.blocking import BlockingScheduler

import tweetcloud


sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=23)
def scheduled_job():
    tweetcloud.post_word_clouds()


sched.start()
