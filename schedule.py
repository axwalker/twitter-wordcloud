from apscheduler.schedulers.blocking import BlockingScheduler

import tweet


sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=3)
def scheduled_job():
    tweet.post_word_clouds()


sched.start()
