import functools
import time
import traceback
from typing import Dict

import schedule

from dingding_message import dingding
from dingding_message import log

# 去掉了weeks
interval_list = """
seconds
minutes
hours
days
monday
tuesday
wednesday
thursday
friday
saturday
sunday
""".split()
job_dict = {}

logger = log.get_logger()


@functools.lru_cache(maxsize=100)
def get_ding(token):
    ding = dingding.DingDing(token=token)
    return ding


def send_message(message, token):
    ding = get_ding(token)
    message_type = message["type"]
    logger.info(f"sending : {message}")
    if message_type == "text":
        resp = ding.send_text(**message["message"])
    elif message_type == "markdown":
        resp = ding.send_markdown(**message["message"])
    elif message_type == "link":
        resp = ding.send_link(**message["message"])
    elif message_type == "action_card":
        resp = ding.send_action_card(**message["message"])
    elif message_type == "single_action_card":
        resp = ding.send_single_action_card(**message["message"])
    elif message_type == "feed":
        resp = ding.send_feed_card(**message["message"])
    else:
        logger.fatal(f"unkown message type {message_type}")
        resp = None

    if resp:
        logger.info(f"resp is {resp}")
    if "run_times" in message:
        message["run_times"] -= 1
        if message["run_times"] == 0:
            logger.info("returning cancel job")
            return schedule.CancelJob


def take_effect(time: Dict, message: Dict, token: str, message_id: str) -> schedule.Job:
    """
    使消息生效，如果没有指明interval_count、interval_unit则立即生效
    :param time:
    :param message:
    :param token:
    :return:
    只有在时间单位为days、hours、minutes三者时，才允许调用at函数
    * 如果为days，at的格式为HH:MM:SS或者HH:MM
    * 如果为hours，at的格式为:MM
    * 如果为minutes，at的格式为:SS
    """
    interval_count = time.get("interval_count")
    if interval_count == 0:
        logger.info("立即生效")
        send_message(message, token)
        return
    interval_unit = time["interval_unit"]
    if interval_unit not in interval_list:
        logger.info("interval unit not found")
        send_message(message, token)
        return

    job = schedule.every(interval_count)
    job = getattr(job, interval_unit)  # 此处调用schedule的一个函数
    time = time.get("clock")  # HH:MM:SS, HH:MM,`:MM`, :SS.
    if time in ("days", "hours", "minutes"):
        h, m, s = time.split(":")
        if time == "hours":
            time = f"{m}:{s}"
        elif time == "minutes":
            time = f":{s}"
        job = job.at(time)
    elif time in ("seconds"):  # 如果时间单位是seconds，那么没必要at
        pass
    else:
        job.at(time)
    if interval_count == 0:
        message["run_times"] = 1
    logger.info(f"message take effect {message}")
    job.do(send_message, message, token)
    if message_id in job_dict:
        remove_job_by_id(message_id)
    job_dict[message_id] = job
    return job


def remove_job_by_id(message_id):
    logger.info(
        f"removeing job of message {message_id} meesage_id in job_dict:{message_id in job_dict}"
    )
    if message_id in job_dict:
        schedule.cancel_job(job_dict[message_id])
        del job_dict[message_id]
        logger.info(f"{message_id} is removed F")


def worker():
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except:
            traceback.print_exc()
            pass
